#!/usr/bin/env python3
"""Run skill-refactor's evaluation cases across runtimes and models, A/B, under a budget.

For every case × version × (runtime, model) × repetition the harness materializes the
fixture in a fresh workspace, exposes the skill version to the runtime the way that
runtime discovers skills, runs one headless call, grades the artifacts objectively and
writes the layout that skill-creator's ``aggregate_benchmark.py`` and
``eval-viewer/generate_review.py`` consume:

    <out>/eval-<id>-<name>/<config>/run-<n>/{workspace/, outputs/, record.json,
                                             grading.json, timing.json, transcript.md}

``with_skill`` is the candidate and ``without_skill`` the baseline (an older version of
the same skill, or none). The names are the aggregator's: it computes deltas as the
alphabetically-first configuration minus the second, so this naming keeps the sign
"candidate minus baseline". ``summary.json`` adds the per-model efficiency table.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtimes as rt  # noqa: E402
from grade import grade_run  # noqa: E402
from tokens import Tokenizer, measure_skill  # noqa: E402

DEFAULT_SKILL_CREATOR = Path.home() / ".claude/plugins/cache/claude-plugins-official/skill-creator"
CLAUDE_COST_RANK = {"haiku": 0.8, "sonnet": 3.0, "opus": 15.0, "fable": 20.0}
CONFIGS = ("with_skill", "without_skill")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def repo_root(start: Path) -> Optional[Path]:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / ".git").exists():
            return parent
    return None


def resolve_version(spec: str, skill: Path, dest: Path) -> Path:
    """A skill version from a directory, ``git:<sha>`` or ``git:<sha>:<path>``.

    ``git:<sha>`` looks for the skill at its current path in that commit and, when it lived
    elsewhere then (a skill moved between plugins), at the single ``*/skills/<name>/SKILL.md``
    that commit holds. ``git:<sha>:<path>`` names the path explicitly.
    """
    dest.mkdir(parents=True, exist_ok=True)
    if spec.startswith("git:"):
        root = repo_root(skill)
        if root is None:
            raise SystemExit("git: baseline needs the skill to live inside a git repository")
        sha, _, explicit = spec[4:].partition(":")
        rel = explicit.strip("/") if explicit else skill.resolve().relative_to(root).as_posix()
        if not explicit:
            listed = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only", sha],
                                    capture_output=True, text=True, check=True).stdout.splitlines()
            if f"{rel}/SKILL.md" not in listed:
                moved = [p[: -len("/SKILL.md")] for p in listed if p.endswith(f"/skills/{skill.name}/SKILL.md")]
                if len(moved) != 1:
                    raise SystemExit(f"{skill.name} is not at {rel} in {sha} and was found at {len(moved)} other paths; "
                                     f"use git:{sha}:<path>")
                rel = moved[0]
        archive = subprocess.run(["git", "-C", str(root), "archive", sha, rel], capture_output=True)
        if archive.returncode != 0:
            raise SystemExit(f"git archive {sha} {rel} failed: {archive.stderr.decode(errors='replace').strip()}")
        subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)
        return dest / rel
    source = Path(spec)
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"{source} has no SKILL.md")
    target = dest / source.name
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "benchmarks"))
    return target


def cost_rank(runtime: str, model: Optional[str], pricing: Dict[str, Dict[str, float]]) -> float:
    if model and model in pricing:
        return pricing[model]["input"]
    if runtime == "opencode" and model and model.endswith("-free"):
        return 0.0
    if runtime == "claude" and model:
        return next((rank for key, rank in CLAUDE_COST_RANK.items() if key in model), 5.0)
    return 2.0


def build_plan(cases: List[Dict[str, Any]], targets: List[Tuple[str, Optional[str]]], reps: int,
               pricing: Dict[str, Dict[str, float]], configs: Tuple[str, ...]) -> List[Dict[str, Any]]:
    plan = []
    for runtime, model in targets:
        for case in cases:
            for config in configs:
                for rep in range(1, reps + 1):
                    plan.append({"runtime": runtime, "model": model, "case": case, "config": config, "rep": rep,
                                 "rank": cost_rank(runtime, model, pricing)})
    plan.sort(key=lambda item: (item["rank"], item["runtime"], item["model"] or "", item["case"]["id"], item["config"], item["rep"]))
    return plan


def materialize(case: Dict[str, Any], fixture_md: str, run_dir: Path) -> Tuple[Path, str]:
    workspace = run_dir / "workspace"
    (workspace / "target").mkdir(parents=True, exist_ok=True)
    (workspace / "artifacts").mkdir(exist_ok=True)
    (workspace / "target" / "SKILL.md").write_text(fixture_md, encoding="utf-8")
    prompt = case["prompt"].replace("{target}", "target/SKILL.md").replace("{run_dir}", "artifacts")
    return workspace, prompt


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def p50(values: List[float]) -> Optional[float]:
    return round(statistics.median(values), 3) if values else None


def summarize(out: Path, runs: List[Dict[str, Any]], static: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for run in runs:
        label = run.get("model_observed") or run.get("model_effective") or run["model"] or "(default)"
        groups.setdefault((run["runtime"], f'{label} @ {run.get("effort_effective") or "default"}', run["config"]), []).append(run)
    table = []
    for (runtime, model, config), items in sorted(groups.items()):
        executed = [r for r in items if r["status"] in ("PASS", "FAIL")]
        accepted = [r for r in executed if r.get("pass_rate") == 1.0]
        costs = [r["cost_usd"] for r in executed if isinstance(r.get("cost_usd"), (int, float))]
        total_cost = round(sum(costs), 6) if costs else None
        table.append({
            "runtime": runtime, "model": model.split(" @ ")[0], "effort": model.split(" @ ")[1], "config": config,
            "effort_source": items[0].get("effort_source"), "model_source": items[0].get("model_source"),
            "planned": len(items), "executed": len(executed), "not_run": len(items) - len(executed),
            "accepted": len(accepted),
            "pass_rate_mean": round(statistics.mean([r["pass_rate"] for r in executed]), 4) if executed else None,
            "acceptance_rate": round(len(accepted) / len(executed), 4) if executed else None,
            "cost_total_usd": total_cost,
            "cost_per_success_usd": round(total_cost / len(accepted), 6) if total_cost is not None and accepted else None,
            "tokens_in_mean": p50([r["usage"].get("context_tokens", r["usage"].get("input_tokens")) for r in executed
                                   if r.get("usage") and r["usage"].get("context_tokens", r["usage"].get("input_tokens")) is not None]),
            "tokens_out_mean": p50([r["usage"]["output_tokens"] for r in executed if r.get("usage") and r["usage"].get("output_tokens") is not None]),
            "duration_p50_s": p50([r["duration_seconds"] for r in executed if r.get("duration_seconds") is not None]),
            "skill_static_tokens": static.get(config, {}).get("scenarios", {}).get("refactor (core + refactoring)", {}).get("tokens"),
            "reasons": sorted({r["reason"] for r in items if r["status"] not in ("PASS",) and r.get("reason")})[:5],
        })
    cost_total = round(sum(r["cost_usd"] for r in runs if isinstance(r.get("cost_usd"), (int, float))), 6)
    executed = [r for r in runs if r["status"] in ("PASS", "FAIL")]
    verdict = "PASS" if executed and all(r["status"] == "PASS" for r in executed) else ("NOT_RUN" if not executed else "FAIL")
    summary = {"schema_version": 1, **meta, "ended_at": utc_now(), "verdict": verdict,
               "runs_planned": len(runs), "runs_executed": len(executed), "cost_total_usd": cost_total,
               "efficiency_by_model": table, "static_tokens": static, "runs": runs}
    # The summary is versioned: no local paths in it, the same rule the records follow.
    summary = json.loads(rt.sanitize(json.dumps(summary, ensure_ascii=False)))
    write_json(out / "summary.json", summary)
    lines = [f"# Benchmark — {meta['skill_name']} ({meta['started_at'][:10]})", "",
             f"Verdict: **{verdict}** · runs executed {len(executed)}/{len(runs)} · cost total US$ {cost_total}",
             f"Budget: US$ {meta['budget_usd']} · baseline: `{meta['baseline']}` · dry-run: {meta['dry_run']}", "",
             "| Runtime | Model | Effort | Config | Exec/Plan | Acceptance | Pass rate | Cost total | Cost/success | Tokens in (p50) | Tokens out (p50) | p50 s | Skill static tok |",
             "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in table:
        fmt = lambda v, f="{}": "—" if v is None else f.format(v)  # noqa: E731
        lines.append(f"| {row['runtime']} | {row['model']} | {row['effort']} | {row['config']} | {row['executed']}/{row['planned']} | "
                     f"{fmt(row['acceptance_rate'], '{:.0%}')} | {fmt(row['pass_rate_mean'], '{:.0%}')} | {fmt(row['cost_total_usd'], '{:.4f}')} | "
                     f"{fmt(row['cost_per_success_usd'], '{:.4f}')} | {fmt(row['tokens_in_mean'], '{:.0f}')} | {fmt(row['tokens_out_mean'], '{:.0f}')} | "
                     f"{fmt(row['duration_p50_s'], '{:.1f}')} | {fmt(row['skill_static_tokens'])} |")
    lines += ["", "Configs: `with_skill` = candidate version, `without_skill` = baseline version.",
              "Cost sources: Claude `total_cost_usd` (runtime), Codex pricing table, Hermes `--usage-file` (estimated).",
              "A run is *accepted* only when every objective expectation passed."]
    (out / "benchmark.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


PUBLISHED_FILES = ("summary.json", "benchmark.md", "tokens.json")


def publish(out: Path, destination: Path) -> List[str]:
    """Copy the round's summaries, never its workspaces.

    A round directory holds version copies and fixture workspaces, each with a SKILL.md. Kept inside
    a plugin, those count as extra skills to every inventory check, so only summaries are published.
    Every copied file passes through the sanitizer again.
    """
    destination.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in PUBLISHED_FILES:
        source = out / name
        if source.is_file():
            (destination / name).write_text(rt.sanitize(source.read_text(encoding="utf-8")), encoding="utf-8")
            copied.append(name)
    return copied


def skill_creator_tools(base: Optional[Path]) -> Optional[Dict[str, Path]]:
    if base is None:
        return None
    candidates = [base] + sorted(base.glob("*/skills/skill-creator"))
    for candidate in candidates:
        agg = candidate / "scripts" / "aggregate_benchmark.py"
        viewer = candidate / "eval-viewer" / "generate_review.py"
        if agg.is_file() and viewer.is_file():
            return {"root": candidate, "aggregate": agg, "viewer": viewer}
    return None


def run_skill_creator(tools: Dict[str, Path], out: Path, skill_name: str, skill_path: Path) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    agg = subprocess.run([sys.executable, "-m", "scripts.aggregate_benchmark", str(out), "--skill-name", skill_name,
                          "--skill-path", str(skill_path)], cwd=str(tools["root"]), capture_output=True, text=True)
    result["aggregate"] = {"exit_code": agg.returncode, "stderr": agg.stderr[-500:]}
    if agg.returncode == 0 and (out / "benchmark.json").is_file():
        view = subprocess.run([sys.executable, str(tools["viewer"]), str(out), "--skill-name", skill_name,
                               "--benchmark", str(out / "benchmark.json"), "--static", str(out / "review.html")],
                              capture_output=True, text=True)
        result["viewer"] = {"exit_code": view.returncode, "stderr": view.stderr[-500:]}
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--skill", type=Path, required=True, help="candidate skill directory")
    parser.add_argument("--baseline", default=None, help="baseline skill: a directory or git:<sha>")
    parser.add_argument("--cases", type=Path, default=None, help="evals.json (default: <skill>/evals/evals.json)")
    parser.add_argument("--runtimes", default="claude,codex,hermes",
                        help="comma-separated runtimes, or 'auto' for every runtime discover.py finds usable")
    parser.add_argument("--claude-models", default="")
    parser.add_argument("--codex-models", default="")
    parser.add_argument("--hermes-model", default=None)
    parser.add_argument("--opencode-models", default="")
    for runtime in ("claude", "codex", "hermes", "opencode"):
        parser.add_argument(f"--{runtime}-effort", default=None,
                            help="reasoning effort passed explicitly; omit to use and record the configured default")
    parser.add_argument("--hermes-provider", default=None)
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--budget-usd", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=rt.DEFAULT_TIMEOUT)
    parser.add_argument("--out", type=Path, required=True,
                        help="working directory for the round; use a temporary one (it holds workspaces and SKILL.md copies)")
    parser.add_argument("--publish", type=Path, default=None,
                        help="copy only summary.json, benchmark.md and tokens.json here (e.g. evals/benchmarks/<date>)")
    parser.add_argument("--only-case", type=int, action="append", default=None)
    parser.add_argument("--dry-run", action="store_true", help="use fake executables from --fake-bin; no paid calls")
    parser.add_argument("--fake-bin", type=Path, default=None)
    parser.add_argument("--acknowledge-hermes-automation", action="store_true")
    parser.add_argument("--skill-creator", type=Path, default=DEFAULT_SKILL_CREATOR)
    parser.add_argument("--no-skill-creator", action="store_true")
    args = parser.parse_args(argv)

    skill = args.skill.resolve()
    cases_path = args.cases or (skill / "evals" / "evals.json")
    spec = json.loads(cases_path.read_text(encoding="utf-8"))
    fixture_md = spec["fixture"]["skill_md"]
    matrix = spec.get("matrix", {})
    pricing = {m: v for m, v in matrix.get("pricing", {}).items() if isinstance(v, dict) and "input" in v}
    cases = [c for c in spec["evals"] if not args.only_case or c["id"] in args.only_case]
    runtimes_wanted = [r.strip() for r in args.runtimes.split(",") if r.strip()]
    if runtimes_wanted == ["auto"]:
        # Only what is installed and signed in here; discovery is read-only and records its sources.
        from discover import discover
        found = discover(list(rt.RUNTIMES), pricing)
        runtimes_wanted = found["usable"]
        print(f"auto: usable runtimes {runtimes_wanted}", file=sys.stderr)
        if "hermes" in runtimes_wanted and args.hermes_model is None:
            runtimes_wanted.remove("hermes")
            print("auto: hermes skipped — its model is chosen by the user (--hermes-model, or 'default')", file=sys.stderr)
    targets: List[Tuple[str, Optional[str]]] = []
    if "claude" in runtimes_wanted:
        targets += [("claude", None if m.strip() in ("", "default") else m) for m in (args.claude_models or "default").split(",")]
    if "codex" in runtimes_wanted:
        targets += [("codex", None if m.strip() in ("", "default") else m) for m in (args.codex_models or "default").split(",")]
    if "opencode" in runtimes_wanted:
        targets += [("opencode", None if m.strip() in ("", "default") else m.strip()) for m in (args.opencode_models or "default").split(",")]
    if "hermes" in runtimes_wanted:
        if args.hermes_model is None and not args.dry_run:
            raise SystemExit("--hermes-model is required: the Hermes model is chosen by the user, never assumed; "
                             "pass 'default' to use the model configured in ~/.hermes/config.yaml")
        # 'default' is an explicit user choice: no -m, the usage file records what Hermes actually used
        targets.append(("hermes", None if args.hermes_model == "default" else args.hermes_model))
    targets = [(r, m.strip() if m else None) for r, m in targets]

    if args.dry_run:
        if not args.fake_bin:
            raise SystemExit("--dry-run needs --fake-bin with fake claude/codex/hermes executables")
        os.environ["PATH"] = f"{args.fake_bin.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    versions_dir = out / "versions"
    versions = {"with_skill": resolve_version(str(skill), skill, versions_dir / "with_skill")}
    configs: Tuple[str, ...] = ("with_skill",)
    if args.baseline:
        versions["without_skill"] = resolve_version(args.baseline, skill, versions_dir / "without_skill")
        configs = CONFIGS
    tokenizer = Tokenizer()
    static = {config: measure_skill(path, tokenizer) for config, path in versions.items()}
    write_json(out / "tokens.json", static)

    plan = build_plan(cases, targets, args.reps, pricing, configs)
    claude_runs = sum(1 for p in plan if p["runtime"] == "claude")
    per_claude_budget = max(0.05, round(args.budget_usd / claude_runs, 4)) if claude_runs else None
    meta = {"skill_name": spec.get("skill_name", skill.name), "skill_path": str(skill), "baseline": args.baseline,
            "started_at": utc_now(), "budget_usd": args.budget_usd, "dry_run": args.dry_run, "reps": args.reps,
            "runtime_versions": {r: rt.runtime_version(r) for r in runtimes_wanted},
            "targets": [{"runtime": r, "model": m} for r, m in targets],
            "pricing": pricing, "per_claude_run_budget_usd": per_claude_budget}
    live_skill_before = rt.snapshot(skill)
    runs: List[Dict[str, Any]] = []
    spent = 0.0
    for item in plan:
        case, config = item["case"], item["config"]
        eval_dir = out / f"eval-{case['id']}-{case['name']}"
        write_json(eval_dir / "eval_metadata.json", {"eval_id": case["id"], "eval_name": case["name"],
                                                     "prompt": case["prompt"], "assertions": case.get("expectations", [])})
        model_slug = (item["model"] or "default").replace("/", "_")
        run_dir = eval_dir / config / f"run-{item['rep']}-{item['runtime']}-{model_slug}"
        run_dir.mkdir(parents=True, exist_ok=True)
        entry = {"eval_id": case["id"], "eval_name": case["name"], "config": config, "runtime": item["runtime"],
                 "model": item["model"], "rep": item["rep"], "run_dir": str(run_dir.relative_to(out))}
        if spent >= args.budget_usd:
            record = {"status": "NOT_RUN", "reason": f"budget of US$ {args.budget_usd} exhausted (spent {spent:.4f})"}
            write_json(run_dir / "record.json", record)
            runs.append({**entry, **record, "pass_rate": None, "cost_usd": None, "usage": None, "duration_seconds": None})
            continue
        workspace, prompt = materialize(case, fixture_md, run_dir)
        # Only the fixture is the run's subject: the adapter itself writes AGENTS.md / skills/
        # into the workspace to expose the skill, and those must not count as the run's edits.
        before = rt.snapshot(workspace / "target")
        write_json(run_dir / "snapshot-before.json", before)
        passthrough = tuple(rt.RunRequest.__dataclass_fields__["env_passthrough"].default)
        if args.dry_run:
            passthrough += tuple(k for k in os.environ if k.startswith("FAKE_"))
        request = rt.RunRequest(prompt=prompt, workspace=workspace, run_dir=run_dir, skill_dir=versions[config],
                               skill_name=skill.name, model=item["model"], provider=args.hermes_provider if item["runtime"] == "hermes" else None,
                               effort=getattr(args, f"{item['runtime']}_effort"),
                               timeout=args.timeout, budget_usd=per_claude_budget if item["runtime"] == "claude" else None,
                               hermes_automation_acknowledged=args.acknowledge_hermes_automation or args.dry_run,
                               # Only the copy handed to the runtime is a run-level verdict. The live
                               # skill is checked once per round instead: editing it mid-round is an
                               # operator mistake, and charging it to the model misreads the result.
                               protected_paths=[versions[config]], pricing=pricing, env_passthrough=passthrough)
        record = rt.run(item["runtime"], request)
        after = rt.snapshot(workspace / "target")
        write_json(run_dir / "snapshot-after.json", after)
        result_text = (run_dir / "result.txt").read_text(encoding="utf-8") if (run_dir / "result.txt").is_file() else ""
        outputs = run_dir / "outputs"
        outputs.mkdir(exist_ok=True)
        if (workspace / "target").is_dir():
            shutil.copytree(workspace / "target", outputs / "target", dirs_exist_ok=True)
        (outputs / "report.md").write_text(result_text, encoding="utf-8")
        (run_dir / "transcript.md").write_text(f"## Eval Prompt\n\n{prompt}\n\n## Runtime stdout\n\n" +
                                               ((run_dir / "stdout.txt").read_text(encoding="utf-8") if (run_dir / "stdout.txt").is_file() else ""),
                                               encoding="utf-8")
        grading = grade_run(case=case, fixture_skill_md=fixture_md, target_dir=workspace / "target", result_text=result_text,
                            record=record, snapshot_before=before, snapshot_after=after, tokenizer=tokenizer)
        write_json(run_dir / "grading.json", grading)
        usage = record.get("usage") or {}
        write_json(run_dir / "timing.json", {"total_tokens": usage.get("total_tokens"),
                                             "duration_ms": round((record.get("duration_seconds") or 0) * 1000),
                                             "total_duration_seconds": record.get("duration_seconds") or 0})
        if isinstance(record.get("cost_usd"), (int, float)):
            spent += record["cost_usd"]
        runs.append({**entry, "status": record["status"], "reason": record.get("reason"), "exit_code": record.get("exit_code"),
                     "duration_seconds": record.get("duration_seconds"), "usage": record.get("usage"),
                     "cost_usd": record.get("cost_usd"), "cost_source": record.get("cost_source"),
                     "model_observed": record.get("model_observed"), "pass_rate": grading["summary"]["pass_rate"],
                     "model_effective": record.get("model_effective"), "model_source": record.get("model_source"),
                     "effort_effective": record.get("effort_effective"), "effort_source": record.get("effort_source"),
                     "expectations_failed": [e["text"] for e in grading["expectations"] if not e["passed"]]})
        print(f"[{record['status']:>7}] {item['runtime']}/{item['model'] or 'default'} {config} eval-{case['id']} "
              f"pass={grading['summary']['pass_rate']:.2f} cost={record.get('cost_usd')} spent={spent:.4f}", file=sys.stderr)

    live_skill_after = rt.snapshot(skill)
    changed_live = sorted(k for k in set(live_skill_before) | set(live_skill_after)
                          if live_skill_before.get(k) != live_skill_after.get(k))
    if changed_live:
        meta["source_skill_changed_during_round"] = [rt.sanitize(p) for p in changed_live[:20]]
        print(f"WARNING: the source skill changed while the round ran ({len(changed_live)} paths). "
              "Results describe a moving target; rerun after the edits settle.", file=sys.stderr)

    summary = summarize(out, runs, static, meta)
    if changed_live and summary["verdict"] == "PASS":
        # Not hidden, but not charged to the models either: their per-run verdicts stand.
        summary["verdict"] = "PASS_WITH_SOURCE_DRIFT"
        write_json(out / "summary.json", summary)
    if not args.no_skill_creator:
        tools = skill_creator_tools(args.skill_creator)
        if tools:
            summary["skill_creator"] = run_skill_creator(tools, out, meta["skill_name"], versions["with_skill"])
            write_json(out / "summary.json", summary)
    if args.publish:
        published = publish(out, args.publish)
        print(f"published {published} to {args.publish}", file=sys.stderr)
    print(json.dumps({"verdict": summary["verdict"], "runs_executed": summary["runs_executed"],
                      "runs_planned": summary["runs_planned"], "cost_total_usd": summary["cost_total_usd"], "out": str(out)}))
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
