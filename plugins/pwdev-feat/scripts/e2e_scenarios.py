#!/usr/bin/env python3
"""pwdev-feat E2E scenarios: validate, export to Playwright Test, coverage.

Scenarios are declarative JSON files (``*.scenario.json``) validated against
``schemas/e2e-scenario.schema.json``. Stdlib only (Python >= 3.9).

Usage:
  e2e_scenarios.py validate <file|dir> [--plan plan.md]
  e2e_scenarios.py export --to playwright <file|dir> --out <dir>
  e2e_scenarios.py coverage <plan.md> <file|dir>

Every command prints JSON on stdout. Exit codes: 0 ok, 1 validation errors,
2 usage or I/O error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PLUGIN_ROOT / "schemas" / "e2e-scenario.schema.json"
SUFFIX = ".scenario.json"

TOKEN_RE = re.compile(r"\$\{(env:[A-Z][A-Z0-9_]*|data(?:\.[A-Za-z0-9_]+)+)\}")
SENSITIVE_FIELD_RE = re.compile(r"pass(word)?|senha|secret|token|api[ _-]?key", re.I)
SECRET_VALUE_RES = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]
NEEDS_TARGET = {"click", "fill", "select", "check", "uncheck", "upload", "hover"}
NEEDS_VALUE = {"goto", "fill", "select", "upload"}
ASSERT_NEEDS_VALUE = {"text", "url", "count", "value"}
AC_ROW_RE = re.compile(r"^\|\s*(AC-\d{3,})\s*\|", re.M)


# --------------------------------------------------------------------------
# Minimal JSON Schema validator for the subset used by the scenario schema.
# --------------------------------------------------------------------------

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
}


def _is_type(value: Any, name: str) -> bool:
    if name in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, _TYPES[name])


def _resolve(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def schema_errors(value: Any, schema: dict, root: dict, path: str = "$") -> list[str]:
    if "$ref" in schema:
        return schema_errors(value, _resolve(root, schema["$ref"]), root, path)
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is_type(value, t) for t in types):
            return errors + [f"{path}: expected {'/'.join(types)}"]
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: must not be empty")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if _is_type(value, "number") and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{path}: must be >= {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            sub = f"{path}.{key}"
            if key in props:
                errors += schema_errors(item, props[key], root, sub)
            elif extra is False:
                errors.append(f"{path}: unexpected property '{key}'")
            elif isinstance(extra, dict):
                errors += schema_errors(item, extra, root, sub)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if schema.get("uniqueItems"):
            seen = [json.dumps(v, sort_keys=True) for v in value]
            if len(seen) != len(set(seen)):
                errors.append(f"{path}: items must be unique")
        if "items" in schema:
            for i, item in enumerate(value):
                errors += schema_errors(item, schema["items"], root, f"{path}[{i}]")
        if "contains" in schema and not any(
            not schema_errors(item, schema["contains"], root) for item in value
        ):
            errors.append(f"{path}: must contain an item matching {json.dumps(schema['contains'])}")
    return errors


# --------------------------------------------------------------------------
# Loading and semantic checks
# --------------------------------------------------------------------------

def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def collect(target: Path) -> list[Path]:
    if target.is_dir():
        return sorted(p for p in target.rglob(f"*{SUFFIX}") if p.is_file())
    return [target]


def plan_acs(plan: Path) -> set[str]:
    return set(AC_ROW_RE.findall(plan.read_text(encoding="utf-8")))


def plan_slug(plan: Path) -> str | None:
    match = re.search(r"^slug:\s*([a-z0-9-]+)\s*$", plan.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else plan.parent.name


def _walk_strings(value: Any, path: str):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _walk_strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_strings(v, f"{path}[{i}]")


def _data_has(data: dict, dotted: str) -> bool:
    node: Any = data
    for part in dotted.split(".")[1:]:
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def semantic_errors(doc: dict, source: Path) -> list[str]:
    errors: list[str] = []
    if not source.name.startswith(f"{doc.get('id', '')}-") and source.name != f"{doc.get('id')}{SUFFIX}":
        errors.append(f"$.id: file name must start with '{doc.get('id')}'")
    for path, text in _walk_strings(doc, "$"):
        if any(r.search(text) for r in SECRET_VALUE_RES):
            errors.append(f"{path}: looks like a literal secret — use ${{env:NAME}}")
        for token in TOKEN_RE.findall(text):
            if token.startswith("data") and not _data_has(doc.get("data", {}), token):
                errors.append(f"{path}: ${{{token}}} not found in 'data'")
    names = [v.get("name") for v in doc.get("variants", [])]
    if len(names) != len(set(names)):
        errors.append("$.variants: variant names must be unique")
    roles = {u.get("role") for u in doc.get("preconditions", {}).get("users", [])}
    steps = [("$.setup_steps", i, s) for i, s in enumerate(doc.get("setup_steps", []))]
    for vi, variant in enumerate(doc.get("variants", [])):
        base = f"$.variants[{vi}]"
        if variant.get("as_user") and variant["as_user"] not in roles:
            errors.append(f"{base}.as_user: role '{variant['as_user']}' not in preconditions.users")
        steps += [(f"{base}.steps", i, s) for i, s in enumerate(variant.get("steps", []))]
        for ai, assertion in enumerate(variant.get("assertions", [])):
            apath = f"{base}.assertions[{ai}]"
            kind = assertion.get("expect")
            if kind != "url" and "target" not in assertion:
                errors.append(f"{apath}: '{kind}' needs a target")
            if kind in ASSERT_NEEDS_VALUE and "value" not in assertion:
                errors.append(f"{apath}: '{kind}' needs a value")
            if kind == "count" and not isinstance(assertion.get("value"), int):
                errors.append(f"{apath}: 'count' value must be an integer")
    for base, i, step in steps:
        spath = f"{base}[{i}]"
        action = step.get("action")
        if action in NEEDS_TARGET and "target" not in step:
            errors.append(f"{spath}: '{action}' needs a target")
        if action in NEEDS_VALUE and "value" not in step:
            errors.append(f"{spath}: '{action}' needs a value")
        if action == "press" and "key" not in step:
            errors.append(f"{spath}: 'press' needs a key")
        if action == "wait" and not ({"target", "value", "timeout_ms"} & step.keys()):
            errors.append(f"{spath}: 'wait' needs a target, a url value or timeout_ms")
        target = step.get("target", {})
        label = f"{target.get('value', '')} {target.get('name', '')}"
        value = step.get("value", "")
        if action == "fill" and SENSITIVE_FIELD_RE.search(label) and value and not TOKEN_RE.fullmatch(value):
            errors.append(f"{spath}: sensitive field filled with a literal — use ${{env:NAME}}")
    return errors


def validate(target: Path, plan: Path | None) -> dict:
    schema = load_schema()
    files = collect(target)
    acs = plan_acs(plan) if plan else None
    slug = plan_slug(plan) if plan else None
    results, ids = [], {}
    for path in files:
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            results.append({"file": str(path), "valid": False, "errors": [f"cannot parse: {exc}"]})
            continue
        errors = schema_errors(doc, schema, schema)
        if not errors:
            errors += semantic_errors(doc, path)
        if isinstance(doc, dict) and doc.get("id"):
            if doc["id"] in ids:
                errors.append(f"$.id: duplicate id {doc['id']} (also in {ids[doc['id']]})")
            ids.setdefault(doc["id"], str(path))
            if acs is not None:
                for ac in doc.get("ac_refs", []):
                    if ac not in acs:
                        errors.append(f"$.ac_refs: {ac} is not an acceptance criterion of {plan}")
            if slug and doc.get("feature_slug") not in (None, slug):
                errors.append(f"$.feature_slug: '{doc.get('feature_slug')}' differs from plan slug '{slug}'")
        results.append({"file": str(path), "id": doc.get("id") if isinstance(doc, dict) else None,
                        "valid": not errors, "errors": errors})
    return {"ok": bool(files) and all(r["valid"] for r in results), "count": len(files),
            "files": results, **({} if files else {"error": f"no *{SUFFIX} files under {target}"})}


# --------------------------------------------------------------------------
# Export to Playwright Test
# --------------------------------------------------------------------------

def ts_str(text: str) -> str:
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"


def ts_value(text: str, data: dict) -> str:
    parts, last, out = [], 0, []
    for m in TOKEN_RE.finditer(text):
        parts.append(("lit", text[last:m.start()]))
        parts.append(("tok", m.group(1)))
        last = m.end()
    parts.append(("lit", text[last:]))
    parts = [p for p in parts if p[1] != "" or p[0] == "tok"]
    exprs = []
    for kind, val in parts:
        if kind == "lit":
            exprs.append(("lit", val))
        elif val.startswith("env:"):
            exprs.append(("expr", f"env({ts_str(val[4:])})"))
        else:
            exprs.append(("expr", "data." + val.split(".", 1)[1]))
    if not exprs:
        return "''"
    if len(exprs) == 1:
        kind, val = exprs[0]
        if kind == "lit":
            return ts_str(val)
        return val if val.startswith("env(") else f"String({val})"
    for kind, val in exprs:
        out.append(val.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${") if kind == "lit" else "${" + val + "}")
    return "`" + "".join(out) + "`"


def ts_locator(loc: dict, data: dict) -> str:
    by, value = loc["by"], ts_value(loc["value"], data)
    exact = ", exact: true" if loc.get("exact") else ""
    if by == "role":
        opts = []
        if loc.get("name"):
            opts.append(f"name: {ts_value(loc['name'], data)}")
        if loc.get("exact"):
            opts.append("exact: true")
        return f"page.getByRole({value}{', { ' + ', '.join(opts) + ' }' if opts else ''})"
    if by == "css":
        return f"page.locator({value})"
    method = {"label": "getByLabel", "placeholder": "getByPlaceholder", "text": "getByText", "testid": "getByTestId"}[by]
    if by == "testid":
        return f"page.getByTestId({value})"
    return f"page.{method}({value}{', {' + exact[1:] + ' }' if exact else ''})"


def ts_step(step: dict, data: dict) -> str:
    action = step["action"]
    loc = ts_locator(step["target"], data) if "target" in step else None
    value = ts_value(step["value"], data) if "value" in step else None
    timeout = f", {{ timeout: {step['timeout_ms']} }}" if "timeout_ms" in step and action != "wait" else ""
    if action == "goto":
        return f"await page.goto({value});"
    if action == "click":
        return f"await {loc}.click({timeout[2:]});"
    if action == "fill":
        return f"await {loc}.fill({value}{timeout});"
    if action == "select":
        return f"await {loc}.selectOption({value}{timeout});"
    if action in ("check", "uncheck", "hover"):
        return f"await {loc}.{action}({timeout[2:]});"
    if action == "upload":
        return f"await {loc}.setInputFiles({value}{timeout});"
    if action == "press":
        key = ts_str(step["key"])
        return f"await {loc}.press({key});" if loc else f"await page.keyboard.press({key});"
    if action == "wait":
        if loc:
            t = f", {{ timeout: {step['timeout_ms']} }}" if "timeout_ms" in step else ""
            return f"await expect({loc}).toBeVisible({t[2:]});"
        if value:
            return f"await page.waitForURL(new RegExp(escapeRegExp({value})));"
        return f"await page.waitForTimeout({step['timeout_ms']});"
    raise ValueError(f"unknown action {action}")


def ts_assertion(assertion: dict, data: dict) -> str:
    kind = assertion["expect"]
    if kind == "url":
        return f"await expect(page).toHaveURL(new RegExp(escapeRegExp({ts_value(str(assertion['value']), data)})));"
    loc = ts_locator(assertion["target"], data)
    simple = {"visible": "toBeVisible", "hidden": "toBeHidden", "enabled": "toBeEnabled",
              "disabled": "toBeDisabled", "checked": "toBeChecked"}
    if kind in simple:
        return f"await expect({loc}).{simple[kind]}();"
    if kind == "count":
        return f"await expect({loc}).toHaveCount({int(assertion['value'])});"
    matcher = "toContainText" if kind == "text" else "toHaveValue"
    return f"await expect({loc}).{matcher}({ts_value(str(assertion['value']), data)});"


def export_playwright(doc: dict, source: str) -> str:
    data = doc.get("data", {})
    pre = doc["preconditions"]
    lines = [
        "// GENERATED by pwdev-feat e2e_scenarios.py — do not edit; change the scenario and re-export.",
        f"// Source: {source}",
        f"// Scenario: {doc['id']} — ACs: {', '.join(doc['ac_refs'])} — requires @playwright/test >= 1.42",
        "import { test, expect } from '@playwright/test';",
        "",
        "function env(name: string): string {",
        "  const value = process.env[name];",
        "  if (!value) throw new Error(`Missing environment variable ${name}`);",
        "  return value;",
        "}",
        "",
        "function escapeRegExp(text: string): string {",
        "  return text.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');",
        "}",
        "",
        f"const data = {json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)};",
        "void data;",
        "",
        f"test.describe({ts_str(doc['id'] + ' ' + doc['title'])}, () => {{",
        f"  test.use({{ baseURL: process.env[{ts_str(pre['base_url_env'])}]"
        + (f", viewport: {{ width: {pre['viewport']['width']}, height: {pre['viewport']['height']} }}" if "viewport" in pre else "")
        + " });",
    ]
    if pre.get("state"):
        lines.append("  // Preconditions (arrange before running):")
        lines += [f"  //   - {s}" for s in pre["state"]]
    tags = [f"@{doc['priority']}"] + [f"@{t}" for t in doc.get("tags", [])]
    for variant in doc["variants"]:
        annotations = [f"{{ type: 'E2E', description: {ts_str(doc['id'])} }}"]
        annotations += [f"{{ type: 'AC', description: {ts_str(ac)} }}" for ac in doc["ac_refs"]]
        if variant.get("as_user"):
            annotations.append(f"{{ type: 'user', description: {ts_str(variant['as_user'])} }}")
        lines += [
            "",
            f"  test({ts_str(variant['name'] + ' — ' + variant['title'])}, {{",
            f"    tag: [{', '.join(ts_str(t) for t in tags)}],",
            f"    annotation: [{', '.join(annotations)}],",
            "  }, async ({ page }) => {",
        ]
        if pre.get("start_path"):
            lines.append(f"    await page.goto({ts_str(pre['start_path'])});")
        for step in doc.get("setup_steps", []) + variant["steps"]:
            if step.get("note"):
                lines.append(f"    // {step['note']}")
            lines.append("    " + ts_step(step, data))
        for assertion in variant["assertions"]:
            if assertion.get("note"):
                lines.append(f"    // {assertion['note']}")
            lines.append("    " + ts_assertion(assertion, data))
        lines.append("  });")
    lines += ["});", ""]
    return "\n".join(lines)


def export(target: Path, out: Path) -> dict:
    report = validate(target, None)
    if not report["ok"]:
        return {"ok": False, "error": "validation failed — nothing exported", "validation": report}
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for entry in report["files"]:
        path = Path(entry["file"])
        doc = json.loads(path.read_text(encoding="utf-8"))
        dest = out / (path.name[: -len(SUFFIX)] + ".spec.ts")
        try:
            source = str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            source = path.name
        dest.write_text(export_playwright(doc, source), encoding="utf-8")
        written.append(str(dest))
    return {"ok": True, "written": written}


def coverage(plan: Path, target: Path) -> dict:
    acs = sorted(plan_acs(plan))
    matrix = {ac: [] for ac in acs}
    unknown = []
    for path in collect(target):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for ac in doc.get("ac_refs", []):
            if ac in matrix:
                matrix[ac].append(doc.get("id"))
            else:
                unknown.append({"scenario": doc.get("id"), "ac": ac})
    return {"ok": not unknown, "matrix": {k: sorted(v) for k, v in matrix.items()},
            "uncovered": [ac for ac, ids in matrix.items() if not ids], "unknown_refs": unknown}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("target", type=Path)
    v.add_argument("--plan", type=Path)
    e = sub.add_parser("export")
    e.add_argument("--to", choices=["playwright"], required=True)
    e.add_argument("target", type=Path)
    e.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("coverage")
    c.add_argument("plan", type=Path)
    c.add_argument("target", type=Path)
    args = parser.parse_args(argv)

    for p in [args.target] + ([args.plan] if getattr(args, "plan", None) else []):
        if not p.exists():
            print(json.dumps({"ok": False, "error": f"not found: {p}"}))
            return 2
    if args.cmd == "validate":
        result = validate(args.target, args.plan)
    elif args.cmd == "export":
        result = export(args.target, args.out)
    else:
        result = coverage(args.plan, args.target)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
