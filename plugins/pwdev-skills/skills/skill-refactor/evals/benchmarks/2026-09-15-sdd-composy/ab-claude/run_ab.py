#!/usr/bin/env python3
"""Minimal Claude-only A/B for the sdd-composy plugin: candidate (working tree) vs baseline copy.

Reuses skill-refactor's runtimes.py (command vector, envelope parsing, usage/cost, protected-path
fingerprints) but exposes the WHOLE plugin as --plugin-dir, because sdd-composy skills call the
plugin's scripts/ and references/. Cases and objective checks live in cases.json (frozen before the
run). Nothing here is evidence of efficiency by itself: read summary.json / benchmark.md.
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, tempfile, unicodedata, hashlib, statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
PLUGIN = REPO / "plugins/sdd-composy"
BASELINE_MD = HERE.parent / "versions/baseline"
SR_SCRIPTS = REPO / "plugins/pwdev-skills/skills/skill-refactor/scripts"
sys.path.insert(0, str(SR_SCRIPTS))
import runtimes as rt  # noqa: E402

IGN = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".git", "benchmarks")

def now(): return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def fold(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def build_plugins(out: Path) -> dict:
    """candidate = working tree; baseline = versions/baseline Markdown + current scripts/ and schemas/."""
    vers = out / "versions"; vers.mkdir(parents=True, exist_ok=True)
    cand = vers / "candidate"
    if not cand.exists(): shutil.copytree(PLUGIN, cand, ignore=IGN)
    base = vers / "baseline"
    if not base.exists():
        shutil.copytree(BASELINE_MD, base, ignore=IGN)
        for sub in ("scripts", "schemas"): shutil.copytree(PLUGIN / sub, base / sub, ignore=IGN)
    return {"candidate": cand, "baseline": base}

def build_fixture(out: Path, spec: dict) -> Path:
    tpl = out / "fixture-template"
    if tpl.exists(): return tpl
    tpl.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(tpl)], check=True)
    g = ["git", "-C", str(tpl), "-c", "user.email=bench@example.invalid", "-c", "user.name=bench"]
    subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "base"], check=True)
    init = PLUGIN / "scripts/sdd_init.py"
    for op in ("plan", "apply", "verify"):
        args = ["python3", str(init), op, str(tpl), "--actor", "agent:bench"] + (["--lang", "pt-BR"] if op != "verify" else [])
        r = subprocess.run(args, capture_output=True, text=True, check=True)
        if op == "verify" and not json.loads(r.stdout).get("ok"): raise SystemExit("fixture verify failed: " + r.stdout)
    for rel, text in spec["fixture"]["files"].items():
        p = tpl / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
    subprocess.run(g + ["add", "-A"], check=True); subprocess.run(g + ["commit", "-q", "-m", "fixture"], check=True)
    return tpl

def snapshot_files(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        if ".git" in p.parts or not p.is_file(): continue
        out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out

def make_prepare(plugin_root: Path):
    def prepare(runtime, request):
        assert runtime == "claude"
        request.run_dir.mkdir(parents=True, exist_ok=True); request.workspace.mkdir(parents=True, exist_ok=True)
        pdir = request.run_dir / "plugin"
        if not pdir.exists(): shutil.copytree(plugin_root, pdir, ignore=IGN)
        return {"runtime": "claude", "plugin_dir": str(pdir), "skill_path": str(pdir / "skills")}
    return prepare

# Language heuristic: lowercase function words only, case-sensitive, so identifiers such as
# TASK-001, INIT or PENDING never count as English; accents folded for the Portuguese side.
LANG_PT = re.compile(r"\b(nao|para|com|uma|acao|proxima|proximo|concluida|concluido|pendente|tarefa|tarefas|fluxo|aprovacao|ainda|ja|esta|estao|falta|faltam)\b")
LANG_EN = re.compile(r"\b(the|and|with|is|are|next|pending|complete|workflow|approval|still|missing|needs|should)\b")

def lang_score(text: str):
    pt = len(LANG_PT.findall(fold(text)))
    en = len(LANG_EN.findall(re.sub(r"[A-Z][A-Z0-9_-]{2,}", " ", text)))  # drop identifiers before counting
    return pt, en

def check(c: dict, *, before: dict, after: dict, ws: Path, answer: str) -> tuple[bool, str]:
    k = c["kind"]
    changed = sorted(set(k2 for k2 in set(before) | set(after) if before.get(k2) != after.get(k2)))
    if k == "no_writes": return (not changed, f"changed files: {changed[:8]}")
    if k == "writes_only_under":
        bad = [f for f in changed if not any(f.startswith(p) for p in c["prefixes"])]
        return (not bad, f"changed: {changed[:8]}; outside allow-list: {bad[:8]}")
    if k == "answer_regex":
        m = re.search(c["pattern"], fold(answer) if c.get("fold", True) else answer, re.I | re.S)
        return (bool(m), f"match: {m.group(0)[:80]!r}" if m else "no match in answer")
    if k == "answer_not_regex":
        m = re.search(c["pattern"], answer, re.I | re.S); return (not m, f"forbidden match: {m.group(0)[:80]!r}" if m else "absent")
    if k == "answer_lang":
        pt, en = lang_score(answer); return (pt > en, f"pt markers {pt} vs en {en}")
    p = ws / c["path"]
    if k == "file_exists": return (p.is_file(), f"{c['path']} exists={p.is_file()}")
    if not p.is_file(): return (False, f"{c['path']} missing")
    text = p.read_text(encoding="utf-8", errors="replace")
    if k == "file_regex":
        m = re.search(c["pattern"], text); return (bool(m), f"match: {m.group(0)[:80]!r}" if m else "no match")
    if k == "file_not_regex":
        m = re.search(c["pattern"], text); return (not m, f"forbidden: {m.group(0)[:80]!r}" if m else "absent")
    if k == "file_lang":
        body = text.split("---", 2)[-1]; pt, en = lang_score(body); return (pt > en, f"pt {pt} vs en {en}")
    raise ValueError(k)

def one_run(*, arm, plugin_root, case, spec, tpl, out, args, protected):
    run_dir = out / f"eval-{case['id']}-{case['name']}" / arm
    if run_dir.exists(): shutil.rmtree(run_dir)
    ws = run_dir / "workspace"; shutil.copytree(tpl, ws, symlinks=False)
    before = snapshot_files(ws)
    req = rt.RunRequest(prompt=case["prompt"], workspace=ws, run_dir=run_dir, skill_dir=plugin_root, skill_name="sdd-composy",
                        model=spec["model"], effort=spec["effort"], timeout=spec["limits_fixed_beforehand"]["timeout_s"],
                        budget_usd=case.get("budget_usd", spec["limits_fixed_beforehand"]["budget_usd_per_execution_run"]),
                        protected_paths=protected)
    rt.prepare = make_prepare(plugin_root)
    if args.dry_run:
        rec = {"status": "NOT_RUN", "reason": "dry-run", "command": rt.build_command("claude", req, rt.prepare("claude", req)), "usage": None, "cost_usd": None, "duration_seconds": None}
        answer = ""
    else:
        rec = rt.run("claude", req)
        answer = ""
        rp = rec.get("result_path")
        if rp and Path(rp).is_file(): answer = Path(rp).read_text(encoding="utf-8", errors="replace")
        elif rec.get("stdout_path"):
            try: answer = json.loads(Path(rec["stdout_path"]).read_text()).get("result", "") or ""
            except Exception: answer = Path(rec["stdout_path"]).read_text(errors="replace")
    after = snapshot_files(ws)
    exps = []
    for c in case["checks"]:
        try: ok, ev = check(c, before=before, after=after, ws=ws, answer=answer)
        except Exception as e: ok, ev = False, f"check error: {e}"
        exps.append({"text": c["text"], "passed": bool(ok) and rec["status"] == "PASS", "evidence": rt.sanitize(ev)})
    grading = {"expectations": exps, "summary": {"pass_rate": (sum(e["passed"] for e in exps) / len(exps)) if exps else 0.0}}
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=1, ensure_ascii=False))
    (run_dir / "record.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=str))
    (run_dir / "answer.txt").write_text(rt.sanitize(answer))
    return {"eval_id": case["id"], "eval_name": case["name"], "arm": arm, "status": rec["status"], "reason": rec.get("reason"),
            "cost_usd": rec.get("cost_usd"), "duration_seconds": rec.get("duration_seconds"), "usage": rec.get("usage"),
            "model_observed": rec.get("model_observed"), "effort": rec.get("effort_effective"), "pass_rate": grading["summary"]["pass_rate"],
            "accepted": grading["summary"]["pass_rate"] == 1.0, "failed": [e["text"] for e in exps if not e["passed"]], "run_dir": str(run_dir.relative_to(out))}

def one_probe(*, arm, plugin_root, probe, i, spec, tpl, out, args, protected):
    run_dir = out / "trigger" / arm / f"probe-{i}"
    if run_dir.exists(): shutil.rmtree(run_dir)
    ws = run_dir / "workspace"; shutil.copytree(tpl, ws, symlinks=False)
    prompt = spec["trigger_evals"]["prompt"].replace("{query}", probe["query"])
    req = rt.RunRequest(prompt=prompt, workspace=ws, run_dir=run_dir, skill_dir=plugin_root, skill_name="sdd-composy",
                        model=spec["model"], effort=spec["effort"], timeout=300,
                        budget_usd=spec["limits_fixed_beforehand"]["budget_usd_per_trigger_probe"], protected_paths=protected)
    rt.prepare = make_prepare(plugin_root)
    if args.dry_run: rec, answer = {"status": "NOT_RUN", "reason": "dry-run", "cost_usd": None}, ""
    else:
        rec = rt.run("claude", req)
        try: answer = json.loads(Path(rec["stdout_path"]).read_text()).get("result", "") or ""
        except Exception: answer = ""
    low = answer.lower()
    m = re.search(r"sdd-composy:([a-z]+)", low) or re.search(r"\bsdd-(?!composy)([a-z]+)\b", low)
    # A skill from another installed plugin (e.g. pwdev-devops:custo) is NONE for this plugin's precision.
    predicted = f"sdd-{m.group(1)}" if m else ("NONE" if ("none" in low or re.search(r"[a-z0-9-]+:[a-z-]+", low)) else "?")
    (run_dir / "record.json").write_text(json.dumps(rec, indent=1, default=str)); (run_dir / "answer.txt").write_text(rt.sanitize(answer))
    return {"arm": arm, "i": i, "query": probe["query"], "expected": probe["expected"], "predicted": predicted, "status": rec["status"], "cost_usd": rec.get("cost_usd")}

def prf(rows):
    tp = sum(1 for r in rows if r["expected"] != "NONE" and r["predicted"] == r["expected"])
    fp = sum(1 for r in rows if r["predicted"] not in ("NONE", "?") and r["predicted"] != r["expected"])
    fn = sum(1 for r in rows if r["expected"] != "NONE" and r["predicted"] != r["expected"])
    tn = sum(1 for r in rows if r["expected"] == "NONE" and r["predicted"] == "NONE")
    prec = tp / (tp + fp) if tp + fp else None; cov = tp / (tp + fn) if tp + fn else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "coverage": cov}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only-case", type=int, default=None); ap.add_argument("--skip-trigger", action="store_true"); ap.add_argument("--skip-exec", action="store_true")
    ap.add_argument("--concurrency", type=int, default=3); ap.add_argument("--arms", default="candidate,baseline")
    args = ap.parse_args(); out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    spec = json.load(open(HERE / "cases.json")); assert spec["approved"]
    plugins = build_plugins(out); tpl = build_fixture(out, spec); protected = [PLUGIN, BASELINE_MD, tpl]
    arms = args.arms.split(","); started = now(); jobs = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        if not args.skip_exec:
            for case in spec["evals"]:
                if args.only_case and case["id"] != args.only_case: continue
                for arm in arms: jobs.append(("exec", ex.submit(one_run, arm=arm, plugin_root=plugins[arm], case=case, spec=spec, tpl=tpl, out=out, args=args, protected=protected)))
        if not args.skip_trigger:
            for i, probe in enumerate(spec["trigger_evals"]["probes"], 1):
                for arm in arms: jobs.append(("trig", ex.submit(one_probe, arm=arm, plugin_root=plugins[arm], probe=probe, i=i, spec=spec, tpl=tpl, out=out, args=args, protected=protected)))
        runs = [j.result() for kind, j in jobs if kind == "exec"]; probes = [j.result() for kind, j in jobs if kind == "trig"]
    eff = []
    for arm in arms:
        rs = [r for r in runs if r["arm"] == arm]; executed = [r for r in rs if r["status"] in ("PASS", "FAIL")]
        acc = [r for r in rs if r["accepted"]]; cost = sum(r["cost_usd"] or 0 for r in rs)
        ctx = [r["usage"]["context_tokens"] for r in executed if r.get("usage") and r["usage"].get("context_tokens")]
        outt = [r["usage"]["output_tokens"] for r in executed if r.get("usage") and r["usage"].get("output_tokens")]
        dur = [r["duration_seconds"] for r in executed if r.get("duration_seconds")]
        eff.append({"arm": arm, "planned": len(rs), "executed": len(executed), "not_run": len(rs) - len(executed), "accepted": len(acc),
                    "acceptance_rate": (len(acc) / len(rs)) if rs else None, "pass_rate_mean": statistics.mean([r["pass_rate"] for r in rs]) if rs else None,
                    "cost_total_usd": round(cost, 4), "cost_per_success_usd": round(cost / len(acc), 4) if acc else None,
                    "context_tokens_mean": round(statistics.mean(ctx)) if ctx else None, "output_tokens_mean": round(statistics.mean(outt)) if outt else None,
                    "duration_p50_s": round(statistics.median(dur), 1) if dur else None,
                    "trigger": prf([p for p in probes if p["arm"] == arm]) if probes else None,
                    "trigger_cost_usd": round(sum(p["cost_usd"] or 0 for p in probes if p["arm"] == arm), 4)})
    summary = {"schema_version": 1, "skill_name": "sdd-composy (plugin)", "runtime": "claude", "model": spec["model"], "effort": spec["effort"],
               "claude_version": rt.runtime_version("claude", None), "started_at": started, "ended_at": now(), "dry_run": args.dry_run,
               "limits_fixed_beforehand": spec["limits_fixed_beforehand"], "cost_total_usd": round(sum((r["cost_usd"] or 0) for r in runs) + sum((p["cost_usd"] or 0) for p in probes), 4),
               "efficiency_by_arm": eff, "runs": runs, "trigger_probes": probes}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    lines = [f"# A/B Claude — sdd-composy ({spec['model']}, effort {spec['effort']}, dry_run={args.dry_run})", "",
             "| arm | planned | executed | accepted | acceptance | US$ total | US$/accepted | context mean | out mean | p50 s | trigger P | trigger C |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for e in eff:
        t = e["trigger"] or {}
        lines.append(f"| {e['arm']} | {e['planned']} | {e['executed']} | {e['accepted']} | {e['acceptance_rate']} | {e['cost_total_usd']} | {e['cost_per_success_usd']} | {e['context_tokens_mean']} | {e['output_tokens_mean']} | {e['duration_p50_s']} | {t.get('precision')} | {t.get('coverage')} |")
    lines += ["", "| case | arm | status | pass_rate | accepted | US$ | context | s | failed checks |", "|---|---|---|---:|---|---:|---:|---:|---|"]
    for r in sorted(runs, key=lambda r: (r["eval_id"], r["arm"])):
        lines.append(f"| {r['eval_id']} {r['eval_name']} | {r['arm']} | {r['status']} | {r['pass_rate']:.2f} | {r['accepted']} | {r['cost_usd']} | {(r['usage'] or {}).get('context_tokens')} | {r['duration_seconds']} | {'; '.join(r['failed'])[:160]} |")
    if probes:
        lines += ["", "| probe | expected | candidate | baseline |", "|---|---|---|---|"]
        for i in range(1, len(spec["trigger_evals"]["probes"]) + 1):
            by = {p["arm"]: p for p in probes if p["i"] == i}
            lines.append(f"| {by[arms[0]]['query'][:60]} | {by[arms[0]]['expected']} | {by.get('candidate', {}).get('predicted')} | {by.get('baseline', {}).get('predicted')} |")
    (out / "benchmark.md").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
    print("\ncost_total_usd:", summary["cost_total_usd"])

if __name__ == "__main__": main()
