#!/usr/bin/env python3
"""Derive benchmark cases from the skill under refactoring, so the A/B measures that skill's own
behavior instead of one fixed fixture.

Three stages, each leaving a file the next one reads:

  --extract <skill_dir>   script only: invariants (identity, literals, labels, prohibitions,
                          conditional blocks, language), the defects it can detect by category,
                          three template requests and eight generic trigger queries
                          -> <out>/cases.draft.json
  --propose <out> --runtime R --model M
                          one headless call that proposes realistic requests and near-miss
                          trigger queries in the skill's own domain -> <out>/cases.proposed.json.
                          The reply is schema-validated; nothing the model writes becomes an
                          objective check unless a person moves it into `invariants`.
  --approve <out>         prints the set, asks for confirmation, writes <out>/cases.json with
                          approved=true and the source SKILL.md hash, so bench.py can refuse a
                          set that no longer matches the skill it was derived from.

bench.py --cases <out> reads cases.json and refuses an unapproved set. The workspace of the
proposal call lives in a temporary directory: it holds a copy of the skill, which must never
land inside the skill's own tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtimes as rt  # noqa: E402
from tokens import description_of, split_frontmatter  # noqa: E402

SCHEMA_VERSION = 1
MAX_FIXTURE_FILE_BYTES = 200_000
SECRET_NAME = re.compile(r"(?i)(^|[./_-])(env|secret|secrets|token|credential|credentials|password)([./_-]|$)|\.(pem|key|p12)$")
SKIP_DIRS = {"evals", "__pycache__", ".git", "node_modules", ".venv"}
# Frontmatter keys a refactoring is expected to change; they are identity for nobody.
VOLATILE_METADATA = {"version", "updated", "generated_at", "generated_by", "updated_at", "revision"}

EN_STOPWORDS = {"the", "and", "with", "for", "that", "this", "from", "when", "only", "into", "each", "every",
                "before", "after", "not", "are", "use", "any", "all", "your", "its", "will", "must", "does"}
PT_STOPWORDS = {"que", "para", "com", "uma", "não", "nao", "por", "como", "mais", "dos", "das", "seu", "sua",
                "quando", "antes", "depois", "cada", "toda", "todo", "sem", "sobre", "apenas"}
GENERIC_NOUNS = re.compile(r"(?i)\b(text|document|message|task|file|information|request|content|data|work|"
                           r"texto|documento|mensagem|tarefa|arquivo|informa[cç][aã]o|pedido|conte[uú]do)\b")
BROAD_QUANTIFIER = re.compile(r"(?i)\b(any|all|every|everything|qualquer|todo|toda|todos|todas)\b")
PROHIBITION = re.compile(r"(?i)\b(never|do not|don't|nunca|n[aã]o)\s+([a-zà-ÿ]+)")
LITERAL = re.compile(r"\b[A-Z][A-Z0-9_]{2,}=[^\s,.;)]+")
IDENTIFIER = re.compile(r"\b[a-z]+_[a-z_]+\b")
TRIPLE = re.compile(r"\b(\w+), (\w+), (?:and |or )?(\w+)\b")  # three-item lists, with or without a conjunction
CONDITIONAL_HEADING = re.compile(r"(?i)\b(optional|if the user|when |on request|only when|only if|opcional|se o usu[aá]rio)")
CONDITIONAL_LINE = re.compile(r"(?i)^(if|when|only when|only if|se|quando)\b")
UNCONDITIONAL = re.compile(r"(?i)\balways (?:read|reread|load|open)\b|\bsempre (?:ler|leia|carreg)|"
                           r"loaded (?:on|for) every|for every task|before doing any work|toda tarefa|todas as tarefas")
LINK = re.compile(r"\[([^\]]+)\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
CONDITION_WORDS = re.compile(r"(?i)\b(if|when|only|any|for|unless|before|after|se|quando|apenas|somente|qualquer|para)\b")
IMPERATIVE_RULE = re.compile(r"(?i)^(always|must|you must|sempre|deve)\b")
PURPOSE = re.compile(r"(?i)\b(because|so that|in order to|since|which|otherwise|porque|para que|pois|caso contr)\b|\bto\s+[a-z]+")
HEADING_STOP = {"optional", "details", "currently", "loaded", "for", "every", "task", "the", "if", "user", "requests",
                "when", "on", "request", "only", "section", "and", "of", "to", "a", "an", "opcional", "detalhes"}

REFACTOR_EXPECTATIONS = [
    "Edits the target instead of only presenting recommendations.",
    "Preserves the target's identity, literals, output labels and prohibitions listed in its invariants.",
    "Moves conditional detail behind an explicit condition or into a reference without losing its requirements.",
    "Modifies no file outside the target folder and the authorized artifact area.",
    "Delivers a report that labels the outcome refactored and statically validated, and does not label it "
    "behaviorally evaluated because no benchmark ran.",
]
REVIEW_EXPECTATIONS = [
    "The hash and inventory of the run's files are identical before and after the execution.",
    "Applies no refactoring, creates no baseline or report, and runs no benchmark.",
    "Names the defects by inspection category: duplication, unconditional reading, and over-broad description at minimum.",
    "Proposes an A/B comparison of the previous version against the candidate on the same cases.",
    "Separates static diagnosis from measured efficiency and states that a review is not evidence of a gain.",
    "Uses the protocol's own measures (cost per accepted task, acceptance rate, accumulated input tokens, "
    "triggering precision/coverage) instead of inventing a metric such as lines per execution or a readability score.",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --- extraction ----------------------------------------------------------------------

def frontmatter_fields(frontmatter: str) -> Dict[str, Any]:
    """name, paths and metadata from the frontmatter, without a YAML dependency."""
    out: Dict[str, Any] = {"name": None, "paths": [], "metadata": {}}
    match = re.search(r"^name:\s*(.+?)\s*$", frontmatter, re.M)
    if match:
        out["name"] = match.group(1).strip("'\"")
    match = re.search(r"^paths:\s*\[(.*)\]\s*$", frontmatter, re.M)
    if match:
        out["paths"] = [p.strip().strip("'\"") for p in match.group(1).split(",") if p.strip()]
    else:
        block = re.search(r"^paths:\s*\n((?:[ \t]+-.*\n?)+)", frontmatter, re.M)
        if block:
            out["paths"] = [line.strip()[1:].strip().strip("'\"") for line in block.group(1).splitlines() if line.strip()]
    block = re.search(r"^metadata:\s*\n((?:[ \t]+\S.*\n?)+)", frontmatter, re.M)
    if block:
        for line in block.group(1).splitlines():
            kv = re.match(r"^[ \t]+([A-Za-z0-9_.-]+):\s*(.*?)\s*$", line)
            if kv and kv.group(2) and kv.group(1) not in VOLATILE_METADATA:
                out["metadata"][kv.group(1)] = kv.group(2).strip("'\"")
    return out


def detect_language(text: str) -> str:
    words = re.findall(r"[a-záàâãéêíóôõúç]+", text.lower())
    en = sum(1 for w in words if w in EN_STOPWORDS)
    pt = sum(1 for w in words if w in PT_STOPWORDS)
    return "pt" if pt > en else "en"


def _sentence_start(text: str, index: int) -> bool:
    before = text[:index].rstrip(" \t#*-")
    return not before or before.endswith(("\n", ".", "!", "?", ":"))


def output_labels(body: str, limit: int = 8) -> List[str]:
    """Capitalized phrases that recur mid-sentence: the names a skill gives its output sections."""
    counts: Counter[str] = Counter()
    order: List[str] = []
    for match in re.finditer(r"\b([A-Z][a-z]+(?: [a-z]{3,})?)\b", body):
        if _sentence_start(body, match.start()):
            continue
        phrase = match.group(1)
        if phrase not in counts:
            order.append(phrase)
        counts[phrase] += 1
    return [p for p in order if counts[p] >= 2][:limit]


def prohibitions(body: str, limit: int = 6) -> List[str]:
    verbs: List[str] = []
    for match in PROHIBITION.finditer(body):
        verb = match.group(2).lower()
        if verb not in verbs and len(verb) > 2:
            verbs.append(verb)
    return [rf"(?i)(never|do not|don't|nunca|n[aã]o)\s+{re.escape(v)}" for v in verbs[:limit]]


def sections(body: str) -> List[Tuple[str, str]]:
    parts = re.split(r"^(#{1,6}[ \t]+.*)$", body, flags=re.M)
    out: List[Tuple[str, str]] = [("", parts[0])]
    for i in range(1, len(parts), 2):
        out.append((parts[i].lstrip("# ").strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return out


def conditional_blocks(body: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for heading, text in sections(body):
        first = text.strip().splitlines()[0] if text.strip() else ""
        if not (heading and CONDITIONAL_HEADING.search(heading)) and not CONDITIONAL_LINE.match(first):
            continue
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9-]+", heading or first) if w.lower() not in HEADING_STOP]
        topic = (words[0] if words else "block").lower()
        terms: List[str] = []
        for triple in TRIPLE.findall(text):
            for term in triple:
                if term.islower() and term not in terms:
                    terms.append(term)
        for ident in IDENTIFIER.findall(text):
            if ident not in terms:
                terms.append(ident)
        guard = None
        g = re.search(r"(?i)\b(do not|don't|never|n[aã]o|nunca)\s+([a-zà-ÿ]+)\s+([a-zà-ÿ]+)", text)
        if g:
            guard = rf"(?i)(do not|don't|never|n[aã]o|nunca) {re.escape(g.group(2).lower())} {re.escape(g.group(3).lower())}"
        marker = next((t for t in terms if "_" in t), terms[-1] if terms else None)
        block = {"topic": topic, "heading": heading, "must_keep_terms": terms[:8]}
        if guard:
            block["guard"] = guard
        if marker:
            block["marker"] = marker
        out.append(block)
    return out


def language_markers(description: str, body: str, language: str) -> List[str]:
    stop = EN_STOPWORDS | PT_STOPWORDS
    words = [w for w in re.findall(r"[a-záàâãéêíóôõúç]{5,}", (description + "\n" + body).lower()) if w not in stop]
    common = [w for w, _ in Counter(words).most_common(2)]
    if not common:
        return []
    return [r"(?i)\b(" + "|".join(re.escape(w[:6]) for w in common) + ")"]


def _repeated_lines(body: str) -> List[str]:
    seen: Counter[str] = Counter()
    for line in body.splitlines():
        stripped = line.strip()
        if len(stripped.split()) >= 6 and not stripped.startswith(("#", "|", "-", "*", "```")):
            seen[stripped] += 1
    return [line for line, count in seen.items() if count > 1]


def blocks(body: str) -> List[str]:
    """Paragraphs and list items: the unit a wrapped markdown sentence lives in."""
    out: List[str] = []
    current: List[str] = []
    for line in body.splitlines():
        item = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)
        if not line.strip() or item:
            if current:
                out.append("\n".join(current))
            current = [line] if line.strip() else []
        else:
            current.append(line)
    if current:
        out.append("\n".join(current))
    return out


def findings(description: str, body: str) -> List[Dict[str, Any]]:
    """Defects detectable by script, one entry per category found. A draft for the reviewer, not a verdict."""
    out: List[Dict[str, Any]] = []
    repeated = _repeated_lines(body)
    if repeated:
        out.append({"category": "duplication", "evidence": repeated[:6]})
    always = {m.group(1).lower() for m in re.finditer(r"(?i)\balways\s+([a-z]+)", body)}
    never = {m.group(2).lower() for m in PROHIBITION.finditer(body)}
    if always & never:
        out.append({"category": "contradiction", "evidence": sorted(f"always/never {v}" for v in always & never)})
    # A sentence that names the defect ("unconditional reading — references loaded on every run")
    # describes it; it is not an instance of it.
    unconditional = [line.strip() for line in body.splitlines()
                     if UNCONDITIONAL.search(line) and not re.search(r"(?i)uncondition|incondicion", line)]
    for block in blocks(body):
        for match in LINK.finditer(block):
            if not CONDITION_WORDS.search(block):
                unconditional.append(f"reference linked without a condition: {match.group(2)}")
    if unconditional:
        out.append({"category": "unconditional reading", "evidence": unconditional[:6]})
    if BROAD_QUANTIFIER.search(description) and GENERIC_NOUNS.search(description):
        out.append({"category": "over-broad description", "evidence": [description]})
    rules = [line.strip() for line in body.splitlines() if IMPERATIVE_RULE.match(line.strip()) and not PURPOSE.search(line)]
    if len(rules) >= 2:
        out.append({"category": "procedure without purpose", "evidence": rules[:6]})
    return out


def fixture_files(skill_dir: Path) -> Dict[str, str]:
    """Text files of the skill, relative to its root, excluding evals, secrets-by-name and symlinks."""
    out: Dict[str, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if path.is_symlink() or not path.is_file() or SECRET_NAME.search(path.name):
            continue
        if path.stat().st_size > MAX_FIXTURE_FILE_BYTES:
            continue
        try:
            out[rel.as_posix()] = rt.sanitize(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return out


def template_requests(name: str, language: str) -> List[Dict[str, Any]]:
    note = "The target is written in Portuguese; keep it so." if language == "pt" else ""
    return [
        {"id": 1, "name": "mixed_consumers_edit", "mode": "refactor", "origin": "template",
         "prompt": (f"Refactor {{target}} (the `{name}` skill) and create only the resources needed inside that skill's "
                    "folder. Report and baseline go in {run_dir}/artifacts. Consumers: two models in lean, every other "
                    "model in guided. Do not run model benchmarks. Preserve the skill's name, frontmatter, requirements "
                    f"and exact output labels. {note} Local editing is authorized; deliver the candidate and the checks performed.").strip(),
         "expected_output": "A real diff in the target with a smaller core and conditional support, requirements preserved, "
                            "valid local links, and a report labelled refactored and statically validated.",
         "files": [], "expectations": REFACTOR_EXPECTATIONS},
        {"id": 2, "name": "unknown_model_explicit_override", "mode": "refactor", "origin": "template",
         "prompt": (f"Refactor {{target}} (the `{name}` skill); baseline and report in {{run_dir}}/artifacts. The executor "
                    "model was not stated and the only consumer model is unknown. Apply the skill's default profile rule "
                    "and state that choice. Do not switch models and do not run provider CLIs. Preserve the target's "
                    f"extensions and requirements. {note} Edit the authorized files and deliver the result.").strip(),
         "expected_output": "Executor and consumer profiles resolved by the default rule and stated; a material change "
                            "with explicit guided support, no invented model identity, and no efficiency claims.",
         "files": [], "expectations": REFACTOR_EXPECTATIONS + [
             "Records the executor and consumer profiles separately, both guided in the absence of an identity or an explicit selection.",
             "Invokes no external provider and invents no model ID."]},
        {"id": 3, "name": "review_only", "mode": "review", "origin": "template",
         "prompt": (f"Review {{target}} (the `{name}` skill) for consumers in the lean profile; describe how to simplify it "
                    "and how to measure the effect. Do not edit files and do not create a report on disk. Do not run benchmarks."),
         "expected_output": "A review in chat against the five inspection categories, a measurement protocol, and no writes at all.",
         "files": [], "expectations": REVIEW_EXPECTATIONS},
    ]


def template_triggers(name: str, description: str) -> List[Dict[str, Any]]:
    job = re.sub(r"(?i)^(use (?:this )?(?:when|for|to)\s*)", "", description.split(".")[0]).strip() or "its own task"
    return [
        {"query": f"Refactor the {name} skill so that lean consumers stop loading redundant instructions.", "should_trigger": True},
        {"query": f"Reorganize the description and references of {name} while keeping support for other models.", "should_trigger": True},
        {"query": f"Compare the previous version of {name} with the candidate on cost per accepted task.", "should_trigger": True},
        {"query": f"Review the {name} SKILL.md without editing it and explain how to measure its efficiency.", "should_trigger": True},
        {"query": f"Use the {name} skill: {job}.", "should_trigger": False},
        {"query": "Refactor this Python function to remove duplication.", "should_trigger": False},
        {"query": f"Translate the text of {name} literally, without changing its behavior.", "should_trigger": False},
        {"query": "Create a new skill for preparing presentations, not based on an existing one.", "should_trigger": False},
    ]


def extract(skill_dir: Path) -> Dict[str, Any]:
    skill_dir = Path(skill_dir).resolve()
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(skill_md)
    fields = frontmatter_fields(frontmatter)
    description = description_of(frontmatter)
    name = fields["name"] or skill_dir.name
    language = detect_language(body)
    invariants: Dict[str, Any] = {"name": name}
    if fields["paths"]:
        invariants["paths"] = fields["paths"]
    if fields["metadata"]:
        invariants["metadata"] = fields["metadata"]
    literals = sorted(set(LITERAL.findall(body)))
    if literals:
        invariants["must_keep_literals"] = literals
    labels = output_labels(body)
    if labels:
        invariants["labels"] = labels
    rules = prohibitions(body)
    if rules:
        invariants["prohibitions"] = rules
    blocks = conditional_blocks(body)
    if blocks:
        invariants["conditional_blocks"] = blocks
    markers = language_markers(description, body, language)
    if markers:
        invariants["language_markers"] = markers
        invariants["foreign_markers"] = []
    references = sorted({m.group(2) for m in LINK.finditer(body)})
    evals = template_requests(name, language)
    for case in evals:
        case["invariants"] = invariants
    return {
        "schema_version": SCHEMA_VERSION, "stage": "draft", "approved": False,
        "skill_name": name,
        "source": {"skill_dir": rt.sanitize(str(skill_dir)), "skill_md_sha256": sha256_text(skill_md),
                   "extracted_at": utc_now(), "language": language, "references": references},
        "fixture": {"skill_md": rt.sanitize(skill_md), "files": {k: v for k, v in fixture_files(skill_dir).items() if k != "SKILL.md"}},
        "fixture_protocol": "The harness writes fixture.skill_md to target/SKILL.md and every fixture.files entry under "
                            "target/ in a fresh workspace, then substitutes {target} and {run_dir} in the prompt.",
        "invariants": invariants,
        "findings": findings(description, body),
        "evals": evals,
        "trigger_evals": template_triggers(name, description),
    }


# --- proposal by one headless call --------------------------------------------------------

PROPOSAL_FILE = "proposal.json"
MODES = ("review", "refactor")


def proposal_prompt(draft: Dict[str, Any]) -> str:
    return (
        "You are designing benchmark cases for a refactoring of the Agent Skill in ./target. Read ./target/SKILL.md "
        "and the files it references. ./draft.json holds invariants and defects extracted by script, three template "
        f"requests and eight trigger queries. Write ./{PROPOSAL_FILE} containing only JSON with this shape:\n"
        '{"requests": [2 to 3 objects {"name": snake_case, "mode": "review" or "refactor", "prompt": a realistic '
        "request a user of this skill would make, in the skill's own domain, naming the skill as {target} and the "
        "artifact area as {run_dir}; a refactor prompt authorizes local edits and forbids benchmarks, a review prompt "
        'forbids edits and files on disk; "expected_output": one sentence}], '
        '"trigger_evals": [8 to 10 objects {"query": string, "should_trigger": boolean}: positives phrased the way this '
        "skill's users speak, and near-miss negatives that mention the skill's domain but do not ask to review, "
        'refactor or measure a skill], "invariant_suggestions": {optional, same keys as draft.invariants, only additions}}\n'
        "Do not modify anything under ./target, do not run benchmarks or provider CLIs, and put no prose outside the JSON."
    )


def validate_proposal(obj: Any) -> Dict[str, Any]:
    """Raise ValueError on anything that is not the shape asked for; return the cleaned proposal."""
    if not isinstance(obj, dict):
        raise ValueError("proposal is not a JSON object")
    requests = obj.get("requests")
    if not isinstance(requests, list) or not 2 <= len(requests) <= 3:
        raise ValueError("requests must hold 2 to 3 items")
    names: List[str] = []
    for i, req in enumerate(requests):
        if not isinstance(req, dict):
            raise ValueError(f"requests[{i}] is not an object")
        for key in ("name", "mode", "prompt", "expected_output"):
            if not isinstance(req.get(key), str) or not req[key].strip():
                raise ValueError(f"requests[{i}].{key} missing or empty")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", req["name"]):
            raise ValueError(f"requests[{i}].name must be snake_case")
        if req["name"] in names:
            raise ValueError(f"requests[{i}].name duplicated")
        names.append(req["name"])
        if req["mode"] not in MODES:
            raise ValueError(f"requests[{i}].mode must be one of {MODES}")
        if "{target}" not in req["prompt"]:
            raise ValueError(f"requests[{i}].prompt must reference {{target}}")
    triggers = obj.get("trigger_evals")
    if not isinstance(triggers, list) or not 8 <= len(triggers) <= 10:
        raise ValueError("trigger_evals must hold 8 to 10 items")
    for i, trig in enumerate(triggers):
        if not isinstance(trig, dict) or not isinstance(trig.get("query"), str) or not trig["query"].strip():
            raise ValueError(f"trigger_evals[{i}].query missing")
        if not isinstance(trig.get("should_trigger"), bool):
            raise ValueError(f"trigger_evals[{i}].should_trigger must be a boolean")
    polarity = {t["should_trigger"] for t in triggers}
    if polarity != {True, False}:
        raise ValueError("trigger_evals must contain both positives and negatives")
    suggestions = obj.get("invariant_suggestions") or {}
    if not isinstance(suggestions, dict):
        raise ValueError("invariant_suggestions must be an object")
    return {"requests": [{k: req[k] for k in ("name", "mode", "prompt", "expected_output")} for req in requests],
            "trigger_evals": [{"query": t["query"], "should_trigger": t["should_trigger"]} for t in triggers],
            "invariant_suggestions": suggestions}


def _json_from_text(text: str) -> Any:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(candidate)


def propose(out_dir: Path, *, runtime: str, model: Optional[str], effort: Optional[str], budget_usd: Optional[float],
            timeout: float, hermes_ack: bool, work_dir: Optional[Path] = None, provider: Optional[str] = None,
            env_passthrough: Optional[Tuple[str, ...]] = None) -> Dict[str, Any]:
    draft = json.loads((out_dir / "cases.draft.json").read_text(encoding="utf-8"))
    work = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="skill-refactor-cases-"))
    run_dir, workspace = work / "run", work / "workspace"
    target = workspace / "target"
    target.mkdir(parents=True, exist_ok=True)
    (target / "SKILL.md").write_text(draft["fixture"]["skill_md"], encoding="utf-8")
    for rel, text in draft["fixture"].get("files", {}).items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    slim = {k: draft[k] for k in ("skill_name", "invariants", "findings", "evals", "trigger_evals")}
    write_json(workspace / "draft.json", slim)
    request = rt.RunRequest(prompt=proposal_prompt(draft), workspace=workspace, run_dir=run_dir, skill_dir=None,
                            model=model, provider=provider, effort=effort, budget_usd=budget_usd, timeout=timeout,
                            hermes_automation_acknowledged=hermes_ack, protected_paths=[target])
    if env_passthrough:
        request.env_passthrough = tuple(request.env_passthrough) + tuple(env_passthrough)
    record = rt.run(runtime, request)
    proposal_path = workspace / PROPOSAL_FILE
    raw: Any = None
    if proposal_path.is_file():
        raw = json.loads(proposal_path.read_text(encoding="utf-8"))
    elif record.get("result_path") and Path(record["result_path"]).is_file():
        raw = _json_from_text(Path(record["result_path"]).read_text(encoding="utf-8"))
    if record.get("status") != "PASS" or raw is None:
        raise SystemExit(f"proposal call did not complete: status={record.get('status')} reason={record.get('reason')}")
    proposal = validate_proposal(raw)  # raises ValueError with the schema violation
    proposed = json.loads(json.dumps(draft))
    next_id = max(c["id"] for c in proposed["evals"]) + 1
    for req in proposal["requests"]:
        proposed["evals"].append({
            "id": next_id, "name": req["name"], "mode": req["mode"], "origin": f"llm:{runtime}:{record.get('model_observed') or model or 'default'}",
            "prompt": req["prompt"], "expected_output": req["expected_output"], "files": [],
            "expectations": REVIEW_EXPECTATIONS if req["mode"] == "review" else REFACTOR_EXPECTATIONS,
            "invariants": draft["invariants"],
        })
        next_id += 1
    for trig in proposal["trigger_evals"]:
        proposed["trigger_evals"].append({**trig, "origin": "llm"})
    proposed["llm_suggested_invariants"] = proposal["invariant_suggestions"]
    proposed["proposal_run"] = {k: record.get(k) for k in ("runtime", "model_requested", "model_observed", "effort_requested",
                                                            "effort_observed", "status", "cost_usd", "cost_source", "usage")}
    proposed["proposal_run"]["protected_changed"] = record.get("protected_changed")
    proposed["stage"] = "proposed"
    write_json(out_dir / "cases.proposed.json", proposed)
    return proposed


# --- approval ----------------------------------------------------------------------------

def render_summary(spec: Dict[str, Any]) -> str:
    lines = [f"Cases for `{spec['skill_name']}` (source SKILL.md sha256 {spec['source']['skill_md_sha256'][:12]}…)", ""]
    lines.append("Invariants:")
    for key, value in spec["invariants"].items():
        lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("")
    lines.append("Findings by category:")
    for f in spec.get("findings", []):
        lines.append(f"  {f['category']}: {f['evidence'][0][:100]}" + (f" (+{len(f['evidence']) - 1})" if len(f["evidence"]) > 1 else ""))
    lines.append("")
    lines.append("Requests:")
    for case in spec["evals"]:
        lines.append(f"  [{case['id']}] {case['name']} ({case.get('mode', '?')}, {case.get('origin', '?')})")
        lines.append(f"      {case['prompt'][:160]}{'…' if len(case['prompt']) > 160 else ''}")
    lines.append("")
    lines.append("Trigger queries:")
    for trig in spec["trigger_evals"]:
        lines.append(f"  {'+' if trig['should_trigger'] else '-'} {trig['query']}" + (" (llm)" if trig.get("origin") == "llm" else ""))
    if spec.get("llm_suggested_invariants"):
        lines += ["", "Invariants the model suggested (NOT applied; move them into `invariants` by hand if they hold):",
                  "  " + json.dumps(spec["llm_suggested_invariants"], ensure_ascii=False)[:400]]
    return "\n".join(lines)


def approve(out_dir: Path, *, skill_dir: Optional[Path], yes: bool, stdin=None, stdout=None) -> Optional[Path]:
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    source = out_dir / "cases.proposed.json"
    if not source.is_file():
        source = out_dir / "cases.draft.json"
    spec = json.loads(source.read_text(encoding="utf-8"))
    if skill_dir is not None:
        current = sha256_text((Path(skill_dir) / "SKILL.md").read_text(encoding="utf-8"))
        if current != spec["source"]["skill_md_sha256"]:
            raise SystemExit("the skill's SKILL.md changed since extraction; run --extract again before approving")
    print(render_summary(spec), file=stdout)
    if not yes:
        print("\nApprove this set for benchmarking? [y/N] ", end="", file=stdout, flush=True)
        answer = stdin.readline().strip().lower() if stdin else ""
        if answer not in ("y", "yes"):
            print("not approved; nothing written", file=stdout)
            return None
    approved = {**spec, "approved": True, "stage": "approved", "approved_at": utc_now(), "approved_from": source.name}
    write_json(out_dir / "cases.json", approved)
    print(f"wrote {out_dir / 'cases.json'}", file=stdout)
    return out_dir / "cases.json"


def check(out_dir: Path, skill_dir: Path) -> bool:
    spec = json.loads((out_dir / "cases.json").read_text(encoding="utf-8"))
    current = sha256_text((Path(skill_dir) / "SKILL.md").read_text(encoding="utf-8"))
    return current == spec["source"]["skill_md_sha256"]


# --- cli ---------------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    stage = parser.add_mutually_exclusive_group(required=True)
    stage.add_argument("--extract", type=Path, metavar="SKILL_DIR")
    stage.add_argument("--propose", type=Path, metavar="OUT_DIR")
    stage.add_argument("--approve", type=Path, metavar="OUT_DIR")
    stage.add_argument("--check", type=Path, metavar="OUT_DIR", help="exit 1 if the skill's SKILL.md drifted from cases.json")
    parser.add_argument("--out", type=Path, help="where --extract writes cases.draft.json (default: <skill>/evals/cases/<name>)")
    parser.add_argument("--skill", type=Path, help="skill dir for --approve/--check drift detection")
    parser.add_argument("--runtime", choices=list(rt.RUNTIMES), default="claude")
    parser.add_argument("--model", default=None)
    parser.add_argument("--provider", default=None, help="hermes provider")
    parser.add_argument("--effort", default=None)
    parser.add_argument("--budget-usd", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--work", type=Path, default=None, help="workspace for the proposal call (default: a temp dir)")
    parser.add_argument("--acknowledge-hermes-automation", action="store_true")
    parser.add_argument("--yes", action="store_true", help="approve without the interactive confirmation")
    args = parser.parse_args(argv)

    if args.extract:
        draft = extract(args.extract)
        out = args.out or (args.extract.resolve() / "evals" / "cases" / draft["skill_name"])
        write_json(out / "cases.draft.json", draft)
        print(f"wrote {out / 'cases.draft.json'}: {len(draft['evals'])} requests, {len(draft['trigger_evals'])} trigger "
              f"queries, findings: {[f['category'] for f in draft['findings']] or 'none'}")
        return 0
    if args.propose:
        proposed = propose(args.propose, runtime=args.runtime, model=args.model, effort=args.effort, budget_usd=args.budget_usd,
                           timeout=args.timeout, hermes_ack=args.acknowledge_hermes_automation, work_dir=args.work,
                           provider=args.provider)
        run = proposed["proposal_run"]
        print(f"wrote {args.propose / 'cases.proposed.json'}: {len(proposed['evals'])} requests, "
              f"{len(proposed['trigger_evals'])} trigger queries; call {run['status']} cost={run.get('cost_usd')}")
        return 0
    if args.approve:
        return 0 if approve(args.approve, skill_dir=args.skill, yes=args.yes) else 1
    if args.check:
        if not args.skill:
            parser.error("--check needs --skill")
        ok = check(args.check, args.skill)
        print("cases.json matches the skill" if ok else "DRIFT: SKILL.md changed since the cases were approved")
        return 0 if ok else 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
