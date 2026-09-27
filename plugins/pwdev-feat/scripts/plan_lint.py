#!/usr/bin/env python3
"""pwdev-feat plan linter — structure and traceability of an action plan.

Usage: plan_lint.py <plan.md>

Prints JSON {ok, schema_version, plan_type, stats, errors, warnings}. Exit 0
when there are no errors, 1 otherwise, 2 on I/O error.

Plans created by pwdev-feat 3.x (frontmatter ``schema_version: 3``) get the
full traceability checks as errors; 2.x plans (no frontmatter) get the
structural checks as errors and the traceability checks as warnings.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLAN_TYPES = {"feature", "backend", "frontend", "test", "review"}
ACTIONS = {"create", "modify", "delete"}
SECTIONS = [
    (1, "Persona & Scope"), (2, "Direct Objective"), (3, "Minimum Inputs"), (4, "Output Format"),
    (5, "Quality Criteria"), (6, "Ambiguity Handling"), (7, "Prohibitions"),
]
MAX_STEPS = 10
CONVENTIONAL = re.compile(r"`(feat|fix|refactor|test|docs|chore|perf|style|build|ci|revert)(\([^)]+\))?!?: .+`")
PLACEHOLDER = re.compile(r"\{[a-z][a-z_ |/.-]*\}")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    return {k.strip(): v.strip() for k, v in re.findall(r"^([A-Za-z_]+):\s*(.*)$", match.group(1), re.M)}


def section(text: str, heading_re: str) -> str | None:
    match = re.search(rf"^##\s+{heading_re}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|$", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows[1:] if rows else []


def strip_code(cell: str) -> str:
    return cell.strip().strip("`").strip()


def lint(text: str) -> dict:
    fm = frontmatter(text)
    v3 = fm.get("schema_version") == "3"
    errors: list[str] = []
    warnings: list[str] = []
    trace = errors if v3 else warnings

    plan_type = fm.get("plan_type")
    if not plan_type:
        m = re.search(r"^>\s*\*\*Type:\*\*\s*([a-z]+)", text, re.M)
        plan_type = m.group(1) if m else None
    if plan_type not in PLAN_TYPES:
        errors.append(f"plan type missing or invalid ({plan_type!r}); expected one of {sorted(PLAN_TYPES)}")
    if v3:
        for key in ("type", "slug", "plan_type", "status", "created"):
            if not fm.get(key):
                errors.append(f"frontmatter: missing '{key}'")
        if fm.get("slug") and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fm["slug"]):
            errors.append(f"frontmatter: slug '{fm['slug']}' is not kebab-case")

    for number, title in SECTIONS:
        if section(text, rf"{number}\.\s*{re.escape(title)}") is None:
            errors.append(f"missing section '## {number}. {title}'")

    # Output Format
    outputs: list[tuple[str, str]] = []
    block = section(text, r"4\.\s*Output Format")
    if block is not None:
        for row in table_rows(block):
            if len(row) < 2:
                continue
            path, action = strip_code(row[0]), row[1].strip().lower()
            if not path or PLACEHOLDER.fullmatch(path):
                continue
            if action not in ACTIONS:
                errors.append(f"Output Format: '{path}' has action '{row[1]}' (expected create/modify/delete)")
            outputs.append((path, action))
        if not outputs:
            errors.append("Output Format: no files listed")
    if plan_type == "review":
        code = [p for p, _ in outputs if not p.startswith(".planning/")]
        if code:
            errors.append(f"review plan lists project files in Output Format (must be report-only): {code}")

    # Quality criteria
    acs: dict[str, str] = {}
    block = section(text, r"5\.\s*Quality Criteria")
    if block is not None:
        for row in table_rows(block):
            if row and re.fullmatch(r"AC-\d{3,}", row[0]):
                if row[0] in acs:
                    errors.append(f"Quality Criteria: duplicate {row[0]}")
                acs[row[0]] = row[2] if len(row) > 2 else ""
        if not acs:
            criteria = re.findall(r"^\s*-\s*\[[ x]\]\s*\S", block, re.M)
            (errors if v3 else warnings).append(
                "Quality Criteria: no AC-nnn table" + ("" if v3 else f" (legacy checklist with {len(criteria)} items)"))
        for ac, verification in acs.items():
            if not verification or PLACEHOLDER.fullmatch(verification.strip("` ")):
                trace.append(f"{ac}: no verification")

    # Steps
    steps_block = section(text, r"Execution Steps")
    steps: list[str] = []
    if steps_block is None:
        errors.append("missing section '## Execution Steps'")
    else:
        steps = re.findall(r"^\s*\d+\.\s+(.*)$", steps_block, re.M)
        if not steps:
            errors.append("Execution Steps: no numbered steps")
        if len(steps) > MAX_STEPS:
            errors.append(f"Execution Steps: {len(steps)} steps (max {MAX_STEPS}) — split the plan")
    steps_text = "\n".join(steps)
    for path, action in outputs:
        if path not in steps_text and Path(path).name not in steps_text:
            trace.append(f"Output Format file '{path}' is not referenced by any step")
    covered = set(re.findall(r"AC-\d{3,}", steps_text))
    for ac in acs:
        if ac not in covered:
            trace.append(f"{ac} is not covered by any step ('covers: {ac}')")
    for ac in sorted(covered - set(acs)):
        errors.append(f"steps reference {ac}, which is not in Quality Criteria")

    # Verification / Commit / Done
    verification = section(text, r"Verification")
    if verification is None:
        trace.append("missing section '## Verification'")
    elif v3 and plan_type != "review" and not any(strip_code(r[0]) for r in table_rows(verification) if r and not PLACEHOLDER.fullmatch(strip_code(r[0]))):
        errors.append("Verification: no commands")
    commit = section(text, r"Commit")
    if commit is None:
        errors.append("missing section '## Commit'")
    elif plan_type != "review" and not CONVENTIONAL.search(commit):
        warnings.append("Commit: message is not a backticked Conventional Commit")
    if section(text, r"Done") is None:
        warnings.append("missing section '## Done'")
    if v3 and section(text, r"Risks") is None:
        warnings.append("missing section '## Risks'")

    leftovers = sorted(set(PLACEHOLDER.findall(re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S))))
    if leftovers:
        warnings.append(f"unfilled template placeholders: {leftovers[:8]}")

    e2e = [p for p, _ in outputs if p.endswith(".scenario.json")]
    if e2e:
        specs = {Path(p).name for p, _ in outputs if p.endswith(".spec.ts")}
        for scenario in e2e:
            spec = Path(scenario).name[: -len(".scenario.json")] + ".spec.ts"
            if spec not in specs:
                trace.append(f"E2E: '{scenario}' has no generated spec '{spec}' in Output Format")
        verification_text = verification or ""
        for sub in ("validate", "export"):
            if not re.search(rf"e2e_scenarios\.py[\"'`]?\s+{sub}\b", verification_text):
                trace.append(f"Verification: E2E scenarios need the 'e2e_scenarios.py {sub}' command")
    ui = re.search(r"^\*\*UI:\*\*\s*yes", text, re.M | re.I)
    if ui and plan_type in ("feature", "frontend", "test") and not e2e:
        warnings.append("UI: yes but no E2E scenario (*.scenario.json) in Output Format")

    return {
        "ok": not errors,
        "schema_version": 3 if v3 else 2,
        "plan_type": plan_type,
        "stats": {"outputs": len(outputs), "criteria": len(acs), "steps": len(steps), "e2e_scenarios": len(e2e)},
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        text = Path(args[0]).read_text(encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"ok": False, "errors": [f"cannot read plan: {exc}"], "warnings": []}))
        return 2
    result = lint(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
