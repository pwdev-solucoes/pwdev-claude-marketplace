#!/usr/bin/env python3
"""Grade one benchmark run of skill-refactor against objective expectations.

The fixture (``evals/evals.json`` → ``fixture.skill_md``) carries invariants that any
correct refactoring must keep: the skill name, ``paths``, a user metadata extension,
an editorial note, three output labels, a prohibition, and the CSV requirements. A
run passes an expectation only when the artifacts on disk prove it; the executor's
own claims are never evidence. Output follows skill-creator's ``grading.json`` shape
(``expectations[{text, passed, evidence}]``, ``summary``), so its aggregator and
viewer read it unchanged. Subjective quality is left to human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tokens import Tokenizer, split_frontmatter  # noqa: E402

DELIVERY_LABELS = ("refactored", "statically validated")

# Invariants of the built-in fixture, as data. A context-derived case brings its own block with
# the same keys, so the objective checks are the same code for every target skill.
FIXTURE_INVARIANTS = {
    "name": "meeting-summary",
    "paths": ["**/minutes.txt"],
    "metadata": {"user_extension": "keep-me"},
    "must_keep_literals": ["REVIEW_WINDOW=14"],
    "labels": ["Key points", "Decisions", "Actions"],
    "prohibitions": [r"(?i)(never|do not|don't)\s+(invent|fabricate|make up)"],
    "conditional_blocks": [{"topic": "csv", "must_keep_terms": ["action", "assignee", "due_date"],
                            "guard": r"(?i)(do not|don't|never) export without", "marker": "due_date"}],
    "language_markers": [r"(?i)\b(summar|meeting)\b"],
    "foreign_markers": [r"(?i)\bresum[oa]\b|reuni[aã]o"],
}
BEHAVIORAL_LABEL = "behaviorally evaluated"
# A review may legitimately be written in the target's language or the user's. Matching is done on
# accent-stripped text with stems that hold in English and Portuguese, so "estatico" and "static"
# are the same observation — a grader that only speaks English measures language, not compliance.
INSPECTION_TERMS = {
    "duplication": re.compile(r"(?i)duplicat|duplicad|repeat|repetic|redundan"),
    "unconditional reading": re.compile(r"(?i)uncondition|incondicion|always (?:read|load)|sempre (?:ler|carrega)|"
                                        r"loaded (?:on|for) every|every task|toda tarefa|todas as tarefas"),
    "over-broad description": re.compile(r"(?i)descri(?:ption|cao).{0,80}(broad|ampl|vag|generic|general|any text|qualquer|too wide|over)|"
                                         r"(broad|ampl|vag|generic|abrangente).{0,80}descri(?:ption|cao)"),
}
# The skill's own measurement vocabulary. A review that describes how to measure should reach for
# these, not invent a metric; "lines per execution" is the failure the protocol names explicitly.
MEASUREMENT_TERMS = re.compile(r"(?i)cost per (?:accepted |success)|custo por (?:tarefa aceita|sucesso)|cost_per_success|"
                               r"acceptance rate|taxa de aceit|tokens\.py|bench\.py|trigger_evals|precision|coverage|precisao|cobertura|"
                               r"input_tokens|context_tokens|usage")
COMPARISON_TERMS = re.compile(r"(?i)\bA/B\b|baseline|previous version|versao anterior|versao previa|"
                              r"compar(?:e|ing|ison|ar|acao) .{0,40}(version|versao|candidat)")
STATIC_VS_MEASURED = re.compile(r"(?i)(static|estatic).{0,160}(measur|medi|efficien|eficien|bench|a/b|gain|ganho)|"
                                r"(measur|medi|efficien|eficien|bench|a/b|gain|ganho).{0,160}(static|estatic)|"
                                r"(size|tamanho).{0,40}(only|just|apenas|so|somente).{0,20}(as )?(a )?diagnos|"
                                r"(single run|um unico run|uma unica execucao).{0,80}(not|nao)|"
                                r"(not|nao).{0,80}(evidence|evidencia).{0,80}(efficien|eficien)")
INVENTED_METRIC = re.compile(r"(?i)lines? per (?:execution|invocation|task)|linhas por (?:execucao|tarefa)|"
                             r"clarity index|indice de clareza|time.to.comprehension|readability score")


# Naming a banned metric to reject it is compliance, not use: "a metric invented for the occasion
# (readability score, lines per execution) cannot be compared" repeats the protocol's own rule.
REJECTION_CONTEXT = re.compile(r"(?i)\b(invent|cannot|can't|not|never|avoid|instead of|reject|rather than|nao|nunca|evite|em vez de)\b")


def _cited_as_rejected(text: str, position: int) -> bool:
    sentence_start = max(text.rfind(".", 0, position), text.rfind("\n", 0, position)) + 1
    sentence_end = min((i for i in (text.find(".", position), text.find("\n", position)) if i != -1), default=len(text))
    return bool(REJECTION_CONTEXT.search(text[sentence_start:sentence_end]))


def fold(text: str) -> str:
    """Accent-free text, so a check measures the observation and not the writer's language."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def skill_corpus(skill_root: Path) -> Dict[str, str]:
    """Every text file under the refactored target, keyed by relative path."""
    corpus = {}
    for path in sorted(skill_root.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.suffix in {".md", ".txt", ".json", ".yaml", ".yml"}:
            corpus[path.relative_to(skill_root).as_posix()] = read(path)
    return corpus


def _expect(text: str, passed: bool, evidence: str) -> Dict[str, Any]:
    return {"text": text, "passed": bool(passed), "evidence": evidence}


def grade_run(*, case: Dict[str, Any], fixture_skill_md: str, target_dir: Path, result_text: str,
              record: Dict[str, Any], snapshot_before: Optional[Dict[str, Any]] = None,
              snapshot_after: Optional[Dict[str, Any]] = None, tokenizer: Optional[Tokenizer] = None) -> Dict[str, Any]:
    tokenizer = tokenizer or Tokenizer()
    invariants = case.get("invariants") or FIXTURE_INVARIANTS
    name = case.get("name", f"eval-{case.get('id')}")
    review_only = name == "review_only" or case.get("mode") == "review"
    expectations: List[Dict[str, Any]] = []
    target_md = read(target_dir / "SKILL.md")
    corpus = skill_corpus(target_dir) if target_dir.is_dir() else {}
    everything = "\n".join(corpus.values())
    frontmatter, body = split_frontmatter(target_md)
    original_fm, _ = split_frontmatter(fixture_skill_md)

    # --- the run itself ---------------------------------------------------------------
    expectations.append(_expect("The runtime completed the task without error",
                                record.get("status") == "PASS",
                                f"status={record.get('status')} reason={record.get('reason')}"))
    expectations.append(_expect("No file outside the isolated workspace changed",
                                not record.get("protected_changed"),
                                f"protected_changed={record.get('protected_changed')}"))

    # --- invariants of the fixture ------------------------------------------------------
    if review_only:
        before, after = snapshot_before or {}, snapshot_after or {}
        same = snapshot_before is not None and before == after
        changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        expectations.append(_expect("Review-only: the run's files are byte-identical before and after",
                                    same, "identical" if same else f"changed entries: {changed[:8]}"))
        folded = fold(result_text)
        hits = [term for term, pattern in INSPECTION_TERMS.items() if pattern.search(folded)]
        expectations.append(_expect("Review names the defects by inspection category (duplication, unconditional reading, over-broad description)",
                                    len(hits) >= 2, f"found: {hits}"))
        comparison = COMPARISON_TERMS.search(folded)
        expectations.append(_expect("Review proposes a comparison against the previous version on the same cases",
                                    bool(comparison), f"matched: {comparison.group(0)[:80]!r}" if comparison else "no comparison proposed"))
        separation = STATIC_VS_MEASURED.search(folded)
        expectations.append(_expect("Review separates static validation from measured efficiency",
                                    bool(separation), f"matched: {separation.group(0)[:100]!r}" if separation else "static and measured not distinguished"))
        measurement = sorted({m.group(0).lower() for m in MEASUREMENT_TERMS.finditer(folded)})
        invented = sorted({m.group(0).lower() for m in INVENTED_METRIC.finditer(folded) if not _cited_as_rejected(folded, m.start())})
        expectations.append(_expect("Review measures with the protocol's own metrics instead of inventing one",
                                    bool(measurement) and not invented,
                                    f"protocol metrics: {measurement[:5]}; invented: {invented}" if (measurement or invented)
                                    else "no measurement vocabulary at all"))
    else:
        expectations.append(_expect("Target SKILL.md still exists", bool(target_md), f"{len(target_md)} chars"))
        expectations.append(_expect("Target was edited (not only recommended)",
                                    bool(target_md) and sha(target_md) != sha(fixture_skill_md),
                                    "sha differs from fixture" if sha(target_md) != sha(fixture_skill_md) else "unchanged"))
    if not review_only:
        expectations.extend(expectations_from_spec(invariants, frontmatter=frontmatter, body=body,
                                                   everything=everything, corpus=corpus, target_md=target_md))
        repeated = _repeated_lines(body)
        expectations.append(_expect("Removes verbatim repetition from the core",
                                    not repeated, f"repeated lines: {repeated[:3]}" if repeated else "no repeated non-trivial lines"))
        # The skill sends the report to the artifact area beside the target, not into the target:
        # read what was written there too (observed 2026-09-14: labels present only in artifacts/).
        artifacts = target_dir.parent / "artifacts"
        artifact_texts = [p.read_text(encoding="utf-8", errors="replace") for p in sorted(artifacts.rglob("*"))
                          if p.is_file() and p.suffix.lower() in (".md", ".txt") and "baseline" not in p.parts] if artifacts.is_dir() else []
        report = result_text + "\n" + "\n".join(text for rel, text in corpus.items() if "report" in rel.lower()) + "\n" + "\n".join(artifact_texts)
        labels_ok = all(label in report for label in DELIVERY_LABELS)
        behavioral_claim = BEHAVIORAL_LABEL in report and not re.search(r"(?i)not\s+behaviorally evaluated|no benchmark", report)
        expectations.append(_expect("Delivery labels the outcome refactored and statically validated, and does not claim behaviorally evaluated without a benchmark",
                                    labels_ok and not behavioral_claim,
                                    f"labels present: {labels_ok}; behavioral claim: {behavioral_claim}"))
        if name == "unknown_model_explicit_override":
            expectations.append(_expect("States the executor and consumer profiles separately, both guided by default",
                                        len(re.findall(r"(?i)\bguided\b", report)) >= 2 and bool(re.search(r"(?i)executor", report)),
                                        "guided named for executor and consumer" if "guided" in report else "no profile statement"))
            expectations.append(_expect("Does not claim guided is empirically necessary or better for every model",
                                        not re.search(r"(?i)guided is (necessary|better|required) for (all|every)", report), "no universal claim"))

    passed = sum(1 for e in expectations if e["passed"])
    before_tokens = tokenizer.count(fixture_skill_md)
    after_tokens = tokenizer.count(target_md) if target_md else None
    grading = {
        "expectations": expectations,
        "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations),
                    "pass_rate": round(passed / len(expectations), 4) if expectations else 0.0},
        "execution_metrics": {
            "output_chars": len(result_text),
            "target_tokens_before": before_tokens, "target_tokens_after": after_tokens,
            "target_tokens_source": tokenizer.source,
            "target_files_after": sorted(corpus),
            "runtime_usage": record.get("usage"), "cost_usd": record.get("cost_usd"),
            "cost_source": record.get("cost_source"), "model_observed": record.get("model_observed"),
        },
        "timing": {"total_duration_seconds": record.get("duration_seconds") or 0},
        "user_notes_summary": {"uncertainties": [], "needs_review": ["Subjective quality of the refactored text is not graded here."],
                               "workarounds": []},
    }
    return grading


def expectations_from_spec(spec: Dict[str, Any], *, frontmatter: str, body: str, everything: str,
                           corpus: Dict[str, str], target_md: str) -> List[Dict[str, Any]]:
    """Objective checks built from a target's invariants, not from code that knows one fixture.

    Every key is optional; an absent key produces no expectation. The keys are the things any
    correct refactoring must keep: identity (name, paths, metadata), literals, output labels,
    prohibitions, blocks that must become conditional, and the target's language.
    """
    out: List[Dict[str, Any]] = []
    name = spec.get("name")
    if name:
        out.append(_expect(f"Preserves name: {name}",
                           bool(re.search(rf"^name:\s*{re.escape(name)}\s*$", frontmatter, re.M)), _line(frontmatter, "name:")))
    for path in spec.get("paths") or []:
        out.append(_expect(f"Preserves paths: {path}", path in frontmatter, _line(frontmatter, path.split("/")[-1])))
    for key, value in (spec.get("metadata") or {}).items():
        pattern = rf"{re.escape(key)}:\s*['\"]?{re.escape(str(value))}"
        out.append(_expect(f"Preserves metadata.{key}: {value}", bool(re.search(pattern, frontmatter)), _line(frontmatter, key)))
    for literal in spec.get("must_keep_literals") or []:
        out.append(_expect(f"Preserves the literal {literal}", literal in everything, _where(corpus, literal)))
    labels = spec.get("labels") or []
    if labels:
        missing = [label for label in labels if label not in everything]
        out.append(_expect("Preserves the output labels " + " / ".join(labels),
                           not missing, f"missing: {missing}" if missing else "all present"))
    for pattern in spec.get("prohibitions") or []:
        out.append(_expect(f"Preserves the prohibition /{pattern}/", bool(re.search(pattern, everything)),
                           "prohibition present" if re.search(pattern, everything) else "prohibition not found"))
    for block in spec.get("conditional_blocks") or []:
        topic, terms = block.get("topic", "block"), block.get("must_keep_terms") or []
        missing = [term for term in terms if term not in everything]
        guard = block.get("guard")
        guard_ok = bool(re.search(guard, everything)) if guard else True
        out.append(_expect(f"Keeps the {topic} requirements ({', '.join(terms)}" + (" and its guard rule" if guard else "") + ")",
                           not missing and guard_ok, f"missing terms: {missing}; guard present: {guard_ok}"))
        marker = block.get("marker") or (terms[0] if terms else None)
        if marker:
            in_core = marker in body
            refs = [rel for rel, text in corpus.items() if rel != "SKILL.md" and marker in text]
            conditional = bool(re.search(rf"(?i)(if|when|only).{{0,60}}{re.escape(topic)}", body))
            out.append(_expect(f"{topic} detail is conditional: inline behind an explicit condition, or in a reference the core loads only on request",
                               (in_core and conditional) or (bool(refs) and conditional),
                               f"in core: {in_core}; references: {refs}; condition in core: {conditional}"))
    markers, foreign = spec.get("language_markers") or [], spec.get("foreign_markers") or []
    if markers:
        native = all(re.search(m, target_md) for m in markers)
        translated = any(re.search(f, target_md) for f in foreign)
        out.append(_expect("Target stays in its original language (no translation)", native and not translated,
                           f"native markers: {native}; foreign markers: {translated}"))
    return out


def _line(text: str, needle: str) -> str:
    for line in text.splitlines():
        if needle in line:
            return line.strip()
    return f"'{needle}' not found"


def _where(corpus: Dict[str, str], needle: str) -> str:
    hits = [rel for rel, text in corpus.items() if needle.lower() in text.lower()]
    return f"found in {hits}" if hits else f"'{needle}' not found in any file"


def _repeated_lines(body: str) -> List[str]:
    seen: Dict[str, int] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if len(stripped.split()) >= 6 and not stripped.startswith(("#", "|", "-", "*", "```")):
            seen[stripped] = seen.get(stripped, 0) + 1
    return [line for line, count in seen.items() if count > 1]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Grade one benchmark run.")
    parser.add_argument("run_dir", type=Path, help="run directory holding record.json, result.txt, workspace/")
    parser.add_argument("--case", type=Path, required=True, help="JSON file with the eval case (id, name, prompt, ...)")
    parser.add_argument("--fixture", type=Path, required=True, help="the original fixture SKILL.md")
    args = parser.parse_args(argv)
    run_dir = args.run_dir
    case = json.loads(args.case.read_text(encoding="utf-8"))
    record = json.loads(read(run_dir / "record.json") or "{}")
    before = json.loads(read(run_dir / "snapshot-before.json") or "null")
    after = json.loads(read(run_dir / "snapshot-after.json") or "null")
    grading = grade_run(case=case, fixture_skill_md=read(args.fixture), target_dir=run_dir / "workspace" / "target",
                        result_text=read(run_dir / "result.txt"), record=record,
                        snapshot_before=before, snapshot_after=after)
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(grading["summary"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
