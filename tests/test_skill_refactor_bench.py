"""skill-refactor measurement and benchmark scripts, exercised without paid calls.

Every runtime is a fake executable on a closed PATH, so the tests assert the exact
command vectors, the parsing of each runtime's usage report, the safety checks and
the on-disk layout that skill-creator's aggregator consumes.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import re
import shutil
import sys
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "pwdev-skills" / "skills" / "skill-refactor"
SCRIPTS = SKILL / "scripts"


def load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"skill_refactor_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module  # dataclasses resolve the defining module through sys.modules
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_skill(root: Path, body: str = "# Demo\n\nDo the thing.\n", description: str = "Use when demoing.") -> Path:
    write(root / "SKILL.md", f"---\nname: demo\ndescription: >\n  {description}\n---\n\n{body}")
    write(root / "references" / "refactoring.md", "# Ref A\n\nalpha beta gamma\n")
    write(root / "references" / "evaluation.md", "# Ref B\n\ndelta epsilon\n")
    write(root / "README.md", "# Readme\n")
    write(root / "evals" / "evals.json", json.dumps({"skill_name": "demo", "evals": []}))
    return root


class TokensTest(unittest.TestCase):
    def setUp(self):
        self.tokens = load("tokens")

    def test_generated_cases_and_benchmark_results_are_not_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._check_not_context(make_skill(Path(tmp) / "sk"))

    def _check_not_context(self, skill: Path):
        write(skill / "evals" / "cases" / "sk" / "cases.json", json.dumps({"fixture": {"skill_md": "x" * 5000}}))
        write(skill / "evals" / "benchmarks" / "2026-09-14" / "summary.json", "{}")
        files = {p.relative_to(skill).as_posix() for p in self.tokens.skill_files(skill)}
        self.assertIn("evals/evals.json", files)
        self.assertFalse(any(f.startswith(("evals/cases/", "evals/benchmarks/")) for f in files), files)

    def test_counts_every_layer_and_scenario(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(Path(tmp) / "demo")
            report = self.tokens.measure_skill(skill, self.tokens.Tokenizer(allow_tiktoken=False))
        self.assertEqual(report["tokens_source"], "estimate:chars/4")
        self.assertEqual(set(report["files"]), {"SKILL.md", "references/refactoring.md",
                                                 "references/evaluation.md", "README.md", "evals/evals.json"})
        self.assertEqual(report["layers"]["SKILL.md#description"]["words"], 3)
        self.assertEqual(report["layers"]["SKILL.md#body"]["words"], 5)
        core = report["layers"]["SKILL.md#body"]["tokens"]
        ref_a = report["layers"]["references/refactoring.md"]["tokens"]
        ref_b = report["layers"]["references/evaluation.md"]["tokens"]
        self.assertEqual(report["scenarios"]["review-only (core)"]["tokens"], core)
        self.assertEqual(report["scenarios"]["refactor (core + refactoring)"]["tokens"], core + ref_a)
        self.assertEqual(report["scenarios"]["refactor + evaluation (core + both references)"]["tokens"],
                         core + ref_a + ref_b)
        self.assertEqual(report["scenarios"]["everything (worst case)"]["members"],
                         ["SKILL.md#body", "references/evaluation.md", "references/refactoring.md",
                          "README.md", "evals/evals.json"])

    def test_block_scalar_description_is_read_whole_and_scripts_are_not_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = make_skill(Path(tmp) / "demo")
            write(skill / "SKILL.md", "---\nname: demo\ndescription: >\n  First line of the\n"
                                      "  description continues here.\n  Do NOT use for x.\nmetadata:\n"
                                      "  version: 1\n---\n\n# Demo\n\nbody\n")
            write(skill / "scripts" / "tool.py", "print('never loaded')\n" * 50)
            report = self.tokens.measure_skill(skill, self.tokens.Tokenizer(allow_tiktoken=False))
        self.assertEqual(report["layers"]["SKILL.md#description"]["words"], 12)
        self.assertNotIn("scripts/tool.py", report["files"])
        self.assertNotIn("scripts/tool.py", report["layers"])

    def test_estimate_is_labelled_and_tiktoken_is_used_when_present(self):
        text = "Refactor a skill: a small shared core."
        estimate = self.tokens.Tokenizer(allow_tiktoken=False)
        self.assertEqual(estimate.source, "estimate:chars/4")
        self.assertEqual(estimate.count(text), round(len(text) / 4))
        measured = self.tokens.Tokenizer()
        if measured.source.startswith("tiktoken"):
            self.assertNotEqual(measured.count(text), 0)
            self.assertNotEqual(measured.source, estimate.source)
        else:
            self.assertEqual(measured.source, "estimate:chars/4")

    def test_markdown_carries_deltas_against_a_baseline(self):
        tokenizer = self.tokens.Tokenizer(allow_tiktoken=False)
        with tempfile.TemporaryDirectory() as tmp:
            before = make_skill(Path(tmp) / "before")
            after = make_skill(Path(tmp) / "after", body="# Demo\n\nDo the thing, but shorter.\n" * 3)
            current = self.tokens.measure_skill(after, tokenizer)
            baseline = self.tokens.measure_skill(before, tokenizer)
        text = self.tokens.render_markdown(current, baseline)
        self.assertIn("Token source: `estimate:chars/4`", text)
        self.assertIn("tokens (estimate)", text)
        self.assertRegex(text, r"\| `SKILL\.md#body` \| .* \| \+\d+ \(\+\d+%\) \|")
        self.assertIn("| **total** |", text)

    def test_cli_refuses_a_directory_without_skill_md(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            self.tokens.main([tmp])


GOOD_REFACTOR = """---
name: meeting-summary
description: Summarize supplied meeting notes into Key points, Decisions and Actions. Use when the user shares minutes, a transcript or notes from a meeting and wants a summary; not for general text tasks.
paths: ["**/minutes.txt"]
metadata:
  user_extension: "keep-me"
---

# Summarize a meeting

Use only supplied content. Never invent decisions, assignees, or dates.
Output Key points, Decisions, and Actions. Label missing assignees and dates.
Preserve the editorial note: REVIEW_WINDOW=14.

If the user requests CSV export, read references/csv-export.md before exporting.
"""

CSV_REFERENCE = """# CSV export

Columns: action, assignee, due_date. Quote fields containing commas. Preserve dates exactly as
supplied. Missing assignees and dates remain empty cells. Do not export without a request.
Use UTF-8 and include the header row. Preserve accents and source ordering. Check that parsing
the CSV yields the expected columns and row count.
"""

FAKE_CLAUDE = '''#!/usr/bin/env python3
import json, os, sys
GOOD = %r
CSV = %r
log = os.environ["FAKE_LOG"]
open(log, "a").write(json.dumps({"exe": "claude", "argv": sys.argv[1:], "cwd": os.getcwd()}) + "\\n")
if "--version" in sys.argv:
    print("9.9.9 (Claude Code)"); sys.exit(0)
if "--model" in sys.argv and sys.argv[sys.argv.index("--model") + 1] == "claude-nope":
    sys.stderr.write("Error: unknown model claude-nope\\n"); sys.exit(1)
if os.environ.get("FAKE_PARTIAL"):
    print(json.dumps({"stop_reason": "tool_use", "session_id": "s-partial", "total_cost_usd": 1.0524,
                      "usage": {"input_tokens": 2, "cache_creation_input_tokens": 25940,
                                "cache_read_input_tokens": 8033, "output_tokens": 250}}))
    sys.exit(1)
if os.environ.get("FAKE_ESCAPE"):
    open(os.environ["FAKE_ESCAPE"], "w").write("escaped")
prompt = sys.argv[sys.argv.index("-p") + 1]
result = "done: refactored"
target = os.path.join(os.getcwd(), "target", "SKILL.md")
if os.environ.get("FAKE_TASK") and os.path.isfile(os.path.join(os.getcwd(), "notes.txt")):
    # a task-mode run: the skill under test summarizes notes.txt into summary.md
    open(os.path.join(os.getcwd(), "summary.md"), "w").write(os.environ["FAKE_TASK"])
    result = "Wrote summary.md with Key points, Decisions and Actions."
elif os.environ.get("FAKE_PROPOSAL") and "proposal.json" in prompt:
    open(os.path.join(os.getcwd(), "proposal.json"), "w").write(os.environ["FAKE_PROPOSAL"])
    result = "wrote proposal.json"
elif prompt.startswith("Review"):
    result = ("Review: the description is too broad, two paragraphs are duplicated verbatim and the CSV section is "
              "loaded unconditionally on every task. Compare the candidate with the previous version on the same "
              "cases; static validation is not measured efficiency.")
elif os.environ.get("FAKE_EDIT") and os.path.isfile(target):
    open(target, "w").write(GOOD)
    os.makedirs(os.path.join(os.getcwd(), "target", "references"), exist_ok=True)
    open(os.path.join(os.getcwd(), "target", "references", "csv-export.md"), "w").write(CSV)
    result = ("Outcome: refactored and statically validated; not behaviorally evaluated (no benchmark ran). "
              "Executor profile: guided; consumer profile: guided (no identity given).")
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": result,
                  "usage": {"input_tokens": 1200, "output_tokens": 300, "cache_read_input_tokens": 50,
                            "cache_creation_input_tokens": 0}, "total_cost_usd": 0.0123, "duration_ms": 4321,
                  "num_turns": 2, "session_id": "s-1", "modelUsage": {"claude-haiku-4-5-20251001": {}}}))
'''

FAKE_CODEX = '''#!/usr/bin/env python3
import json, os, sys
log = os.environ["FAKE_LOG"]
open(log, "a").write(json.dumps({"exe": "codex", "argv": sys.argv[1:], "cwd": os.getcwd()}) + "\\n")
if "--version" in sys.argv:
    print("codex-cli 0.0.0"); sys.exit(0)
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "gpt-nope":
    sys.stderr.write("error: model `gpt-nope` is not available\\n"); sys.exit(2)
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "gpt-quota":
    print(json.dumps({"type": "error", "message": "You've hit your usage limit. Visit https://chatgpt.com/codex/settings/usage"}))
    sys.exit(1)
last = sys.argv[sys.argv.index("--output-last-message") + 1]
text = "done: statically validated"
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "gpt-quota-quote":
    # a clean run whose agent text quotes documentation about quotas
    text = "The runtime contract says a run that reports 'hit your usage limit' or a rate limit is NOT_RUN. done: statically validated"
open(last, "w").write(text)
for event in ({"type": "thread.started", "thread_id": "t-1", "model": "gpt-5.6-luna"},
              {"type": "item.completed", "item": {"type": "agent_message"}},
              {"type": "turn.completed", "usage": {"input_tokens": 2000, "cached_input_tokens": 500, "output_tokens": 400}}):
    print(json.dumps(event))
'''

FAKE_HERMES = '''#!/usr/bin/env python3
import json, os, sys
log = os.environ["FAKE_LOG"]
open(log, "a").write(json.dumps({"exe": "hermes", "argv": sys.argv[1:], "cwd": os.getcwd(),
                                 "skills_dir": os.environ.get("HERMES_SKILLS_DIR"),
                                 "terminal_cwd": os.environ.get("TERMINAL_CWD")}) + "\\n")
if "--version" in sys.argv:
    print("Hermes Agent v0.0.0"); sys.exit(0)
usage = sys.argv[sys.argv.index("--usage-file") + 1]
open(usage, "w").write(json.dumps({"model": "openrouter/some-model", "api_calls": 3, "estimated_cost": 0.004,
                                   "usage": {"prompt_tokens": 900, "completion_tokens": 200, "total_tokens": 1100}}))
print("final answer text")
'''


FAKE_OPENCODE = '''#!/usr/bin/env python3
import json, os, sys
log = os.environ["FAKE_LOG"]
open(log, "a").write(json.dumps({"exe": "opencode", "argv": sys.argv[1:], "cwd": os.getcwd()}) + "\\n")
if "--version" in sys.argv:
    print("0.0.0"); sys.exit(0)
if sys.argv[1] == "export":
    print("Exporting session: " + sys.argv[2])
    filler = [{"info": {"role": "user"}, "parts": [{"text": "x" * 2000}]} for _ in range(60)]
    print(json.dumps({"info": {"model": {"providerID": "opencode", "variant": "high"}},
                      "messages": filler + [{"info": {"role": "assistant", "providerID": "opencode", "modelID": "big-pickle"}}]}))
    sys.exit(0)
workspace = sys.argv[sys.argv.index("--dir") + 1]
skills = os.path.join(workspace, ".opencode", "skills")
names = sorted(os.listdir(skills)) if os.path.isdir(skills) else []
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "opencode/overloaded-free":
    print(json.dumps({"type": "error", "sessionID": "ses_y", "error": {"name": "UnknownError", "data": {"message": "Streaming response failed: [502] Upstream error from Nvidia: Service temporarily overloaded"}}}))
    sys.exit(1)
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "opencode/disconnected-free":
    # the answer so far quoted the docs; the runtime's own failure is a dropped connection
    print(json.dumps({"type": "text", "sessionID": "ses_z", "part": {"text": "The contract says a rate limit is NOT_RUN."}}))
    print(json.dumps({"type": "error", "sessionID": "ses_z", "error": {"name": "APIError", "data": {"message": "Cannot connect to API: The socket connection was closed unexpectedly", "isRetryable": True}}}))
    sys.exit(1)
if "-m" in sys.argv and sys.argv[sys.argv.index("-m") + 1] == "opencode/rate-limited-free":
    print(json.dumps({"type": "error", "sessionID": "ses_x", "error": {"message": "Rate limit exceeded for free model"}}))
    sys.exit(0)
def ev(kind, **part):
    print(json.dumps({"type": kind, "timestamp": 1, "sessionID": "ses_fake1", "part": part}))
ev("step_start")
if names:
    ev("tool_use", tool="skill", state={"input": {"name": names[0]}})
ev("step_finish", reason="tool-calls", cost=0.001, tokens={"total": 11681, "input": 9802, "output": 87, "reasoning": 5, "cache": {"read": 1792, "write": 0}})
ev("text", text="done: statically validated")
ev("step_finish", reason="stop", cost=0.0005, tokens={"total": 11851, "input": 323, "output": 8, "reasoning": 0, "cache": {"read": 11520, "write": 10}})
'''


def install_fakes(bin_dir: Path) -> None:
    claude = FAKE_CLAUDE % (GOOD_REFACTOR, CSV_REFERENCE)
    for name, body in (("claude", claude), ("codex", FAKE_CODEX), ("hermes", FAKE_HERMES), ("opencode", FAKE_OPENCODE)):
        path = write(bin_dir / name, body)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)


class RuntimesTest(unittest.TestCase):
    def setUp(self):
        self.runtimes = load("runtimes")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        install_fakes(self.bin)
        self.log = self.root / "calls.jsonl"
        self.skill = make_skill(self.root / "skill-src")
        self._env = dict(os.environ)
        os.environ["PATH"] = f"{self.bin}:/usr/bin:/bin"
        os.environ["FAKE_LOG"] = str(self.log)
        os.environ.pop("FAKE_ESCAPE", None)
        os.environ.pop("FAKE_PARTIAL", None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def request(self, **overrides):
        base = dict(prompt="Refactor the skill in ./skills", workspace=self.root / "ws", run_dir=self.root / "run",
                    skill_dir=self.skill, skill_name="demo", protected_paths=[self.skill],
                    env_passthrough=("PATH", "HOME", "FAKE_LOG", "FAKE_ESCAPE", "FAKE_PARTIAL"))
        base.update(overrides)
        return self.runtimes.RunRequest(**base)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_claude_vector_plugin_dir_and_usage(self):
        record = self.runtimes.run("claude", self.request(model="claude-haiku-4-5-20251001", budget_usd=0.25))
        self.assertEqual(record["status"], "PASS", record)
        argv = [c for c in self.calls() if "--version" not in c["argv"]][0]["argv"]
        self.assertEqual(argv[:6], ["-p", "Refactor the skill in ./skills", "--output-format", "json",
                                    "--no-session-persistence", "--dangerously-skip-permissions"])
        self.assertIn("--plugin-dir", argv)
        plugin = Path(argv[argv.index("--plugin-dir") + 1])
        self.assertTrue((plugin / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((plugin / "skills" / "demo" / "SKILL.md").is_file())
        self.assertEqual(argv[argv.index("--model") + 1], "claude-haiku-4-5-20251001")
        self.assertEqual(argv[argv.index("--max-budget-usd") + 1], "0.2500")
        self.assertEqual(record["usage"], {"input_tokens": 1200, "output_tokens": 300, "cache_read_tokens": 50,
                                           "cache_write_tokens": 0, "reasoning_tokens": None, "total_tokens": 1550, "context_tokens": 1250})
        self.assertEqual(record["usage_source"], "claude:result.usage")
        self.assertEqual((record["cost_usd"], record["cost_source"]), (0.0123, "runtime"))
        self.assertEqual(record["model_observed"], "claude-haiku-4-5-20251001")
        self.assertEqual(record["version"], "9.9.9 (Claude Code)")
        self.assertEqual((self.root / "run" / "result.txt").read_text(), "done: refactored")
        self.assertTrue((self.root / "run" / "record.json").is_file())

    def test_codex_vector_agents_md_and_pricing_cost(self):
        pricing = {"gpt-5.6-luna": {"input": 0.20, "output": 1.20, "cached_input": 0.05}}
        record = self.runtimes.run("codex", self.request(model="gpt-5.6-luna", pricing=pricing))
        self.assertEqual(record["status"], "PASS", record)
        argv = [c for c in self.calls() if "--version" not in c["argv"]][0]["argv"]
        self.assertEqual(argv[:6], ["exec", "--json", "--ephemeral", "--skip-git-repo-check",
                                    "--dangerously-bypass-approvals-and-sandbox", "--cd"])
        self.assertEqual(argv[-1], "Refactor the skill in ./skills")
        self.assertEqual(argv[argv.index("-m") + 1], "gpt-5.6-luna")
        agents = (self.root / "ws" / "AGENTS.md").read_text()
        self.assertIn("skills/demo/SKILL.md", agents)
        # OpenAI's input_tokens (2000) already includes the 500 cached: normalized fresh input is 1500,
        # accumulated context stays 2000, and the cached part is billed once, at the cached price.
        self.assertEqual(record["usage"]["cache_read_tokens"], 500)
        self.assertEqual(record["usage"]["input_tokens"], 1500)
        self.assertEqual(record["usage"]["context_tokens"], 2000)
        self.assertEqual(record["usage_source"], "codex:turn.completed.usage")
        expected = round((1500 * 0.20 + 400 * 1.20 + 500 * 0.05) / 1_000_000, 6)
        self.assertEqual((record["cost_usd"], record["cost_source"]), (expected, "pricing_table"))
        self.assertEqual(record["model_observed"], "gpt-5.6-luna")

    def test_hermes_requires_acknowledgement_then_reads_usage_file(self):
        blocked = self.runtimes.run("hermes", self.request())
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertIn("hermes -z bypasses approvals", blocked["reason"])
        record = self.runtimes.run("hermes", self.request(model="some/model", provider="openrouter",
                                                          hermes_automation_acknowledged=True))
        self.assertEqual(record["status"], "PASS", record)
        call = [c for c in self.calls() if "--version" not in c["argv"]][0]
        argv = call["argv"]
        self.assertEqual(argv[:2], ["-z", "Refactor the skill in ./skills"])
        for flag in ("--in", "--no-restore-cwd", "--usage-file", "--yolo", "--accept-hooks", "-m", "--provider"):
            self.assertIn(flag, argv)
        for flag in ("--ignore-rules", "--safe-mode", "--skills"):
            self.assertNotIn(flag, argv)
        self.assertEqual(argv[argv.index("--provider") + 1], "openrouter")
        # the skill is exposed through the workspace, never through the user's profile or trust list
        self.assertIsNone(call["skills_dir"])
        self.assertTrue((self.root / "ws" / "skills" / "demo" / "SKILL.md").is_file())
        self.assertIn("skills/demo/SKILL.md", (self.root / "ws" / "AGENTS.md").read_text())
        # Hermes anchors its tools on $TERMINAL_CWD; without it the run works from the user's home
        self.assertEqual(record["env_overrides"], ["TERMINAL_CWD"])
        self.assertEqual(call["terminal_cwd"], str((self.root / "ws").resolve()))
        self.assertEqual(record["usage"], {"input_tokens": 900, "output_tokens": 200, "cache_read_tokens": None,
                                           "cache_write_tokens": None, "reasoning_tokens": None, "total_tokens": 1100, "context_tokens": 900})
        self.assertEqual((record["cost_usd"], record["cost_source"]), (0.004, "estimated"))
        self.assertEqual(record["model_observed"], "openrouter/some-model")

    def test_unknown_model_is_not_run_never_substituted(self):
        claude = self.runtimes.run("claude", self.request(model="claude-nope"))
        self.assertEqual(claude["status"], "NOT_RUN")
        self.assertIn("rejected the model", claude["reason"])
        codex = self.runtimes.run("codex", self.request(model="gpt-nope", run_dir=self.root / "run2",
                                                        workspace=self.root / "ws2"))
        self.assertEqual(codex["status"], "NOT_RUN")

    def test_effort_is_passed_explicitly_or_recorded_from_the_configured_default(self):
        # A comparison across runtimes was published without effort: Codex ran at "low" from its config
        # and Claude lost CLAUDE_EFFORT to the env allowlist. Every run now says what effort it used.
        home = self.root / "home"
        write(home / ".claude" / "settings.json", json.dumps({"model": "opus"}))
        write(home / ".codex" / "config.toml", 'model = "gpt-5.6-sol"\nmodel_reasoning_effort = "low"\n\n[profiles.x]\nmodel_reasoning_effort = "high"\n')
        write(home / ".hermes" / "config.yaml", "model:\n  default: deepseek/deepseek-v4-flash-0731\n  provider: openrouter\n"
                                                "agent:\n  max_turns: 90\n  reasoning_effort: medium\n")
        os.environ["HOME"] = str(home)
        os.environ["CLAUDE_EFFORT"] = "high"
        passthrough = ("PATH", "HOME", "FAKE_LOG", "CLAUDE_EFFORT")

        claude = self.runtimes.run("claude", self.request(env_passthrough=passthrough))
        self.assertEqual((claude["model_effective"], claude["effort_effective"], claude["effort_source"]),
                         ("opus", "high", "env CLAUDE_EFFORT"))
        codex = self.runtimes.run("codex", self.request(env_passthrough=passthrough, run_dir=self.root / "r2", workspace=self.root / "w2"))
        self.assertEqual((codex["model_effective"], codex["effort_effective"]), ("gpt-5.6-sol", "low"))
        self.assertEqual(codex["effort_source"], "~/.codex/config.toml model_reasoning_effort")
        hermes = self.runtimes.run("hermes", self.request(env_passthrough=passthrough, run_dir=self.root / "r3", workspace=self.root / "w3",
                                                          hermes_automation_acknowledged=True))
        self.assertEqual((hermes["model_effective"], hermes["effort_effective"], hermes["provider_effective"]),
                         ("deepseek/deepseek-v4-flash-0731", "medium", "openrouter"))

        self.log.unlink()
        self.runtimes.run("claude", self.request(effort="medium", env_passthrough=passthrough, run_dir=self.root / "r4", workspace=self.root / "w4"))
        self.runtimes.run("codex", self.request(effort="medium", env_passthrough=passthrough, run_dir=self.root / "r5", workspace=self.root / "w5"))
        self.runtimes.run("hermes", self.request(effort="medium", env_passthrough=passthrough, run_dir=self.root / "r6", workspace=self.root / "w6",
                                                 hermes_automation_acknowledged=True))
        argvs = {c["exe"]: c["argv"] for c in self.calls() if "--version" not in c["argv"]}
        self.assertEqual(argvs["claude"][argvs["claude"].index("--effort") + 1], "medium")
        self.assertIn('model_reasoning_effort="medium"', argvs["codex"])
        self.assertEqual(argvs["hermes"][argvs["hermes"].index("--reasoning") + 1], "medium")

        # a default-model Codex run is priced by the model its config selected, not left at null
        priced = self.runtimes.run("codex", self.request(env_passthrough=passthrough, run_dir=self.root / "r8", workspace=self.root / "w8",
                                                         pricing={"gpt-5.6-sol": {"input": 4.0, "cached_input": 0.4, "output": 20.0}}))
        self.assertEqual(priced["cost_source"], "pricing_table")
        self.assertEqual(priced["cost_usd"], round((1500 * 4.0 + 500 * 0.4 + 400 * 20.0) / 1_000_000, 6))
        # Claude reports thinking under output_tokens_details
        self.assertEqual(self.runtimes.normalize_usage({"input_tokens": 1, "output_tokens": 9,
                                                        "output_tokens_details": {"thinking_tokens": 7}})["reasoning_tokens"], 7)

        os.environ.pop("CLAUDE_EFFORT")
        write(home / ".claude" / "settings.json", "{}")
        bare = self.runtimes.run("claude", self.request(env_passthrough=passthrough, run_dir=self.root / "r7", workspace=self.root / "w7"))
        self.assertIsNone(bare["effort_effective"])
        self.assertEqual(bare["effort_source"], "runtime built-in default (not reported by the runtime)")

    def test_opencode_discovers_the_skill_natively_and_sums_usage_per_step(self):
        record = self.runtimes.run("opencode", self.request(model="opencode/big-pickle", effort="high"))
        self.assertEqual(record["status"], "PASS", record)
        call = [c for c in self.calls() if c["exe"] == "opencode" and c["argv"][0] == "run"][0]
        argv = call["argv"]
        self.assertEqual(argv[:6], ["run", "--format", "json", "--dir", str(self.root / "ws"), "--dangerously-skip-permissions"])
        self.assertEqual(argv[argv.index("-m") + 1], "opencode/big-pickle")
        self.assertEqual(argv[argv.index("--variant") + 1], "high")
        self.assertEqual(argv[-1], "Refactor the skill in ./skills")
        # native skill path, bounded by a git repository at the workspace
        self.assertTrue((self.root / "ws" / ".opencode" / "skills" / "demo" / "SKILL.md").is_file())
        self.assertTrue((self.root / "ws" / ".git").exists())
        self.assertFalse((self.root / "ws" / "AGENTS.md").exists())
        # two steps summed; input excludes cache, so context = input + cache read + cache write
        self.assertEqual(record["usage"]["input_tokens"], 9802 + 323)
        self.assertEqual(record["usage"]["cache_read_tokens"], 1792 + 11520)
        self.assertEqual(record["usage"]["context_tokens"], 9802 + 323 + 1792 + 11520 + 10)
        self.assertEqual(record["usage"]["output_tokens"], 95)
        self.assertEqual(record["usage"]["reasoning_tokens"], 5)
        self.assertEqual((record["cost_usd"], record["cost_source"]), (0.0015, "runtime"))
        # the model and variant come from the stored session, since events do not name them
        self.assertEqual(record["model_observed"], "opencode/big-pickle")
        self.assertEqual(record["effort_observed"], "high")
        self.assertTrue(record["extra"]["skill_loaded"])
        self.assertEqual(record["extra"]["steps"], 2)
        self.assertEqual((self.root / "run" / "result.txt").read_text(), "done: statically validated")

    def test_opencode_dropped_connection_is_not_run_with_the_runtime_s_reason(self):
        record = self.runtimes.run("opencode", self.request(model="opencode/disconnected-free"))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("provider unavailable", record["reason"])
        self.assertIn("Cannot connect to API", record["reason"])
        self.assertNotIn("contract says", record["reason"])

    def test_opencode_provider_overload_is_not_run(self):
        record = self.runtimes.run("opencode", self.request(model="opencode/overloaded-free"))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("provider unavailable", record["reason"])

    def test_opencode_error_event_with_exit_zero_is_not_a_pass(self):
        record = self.runtimes.run("opencode", self.request(model="opencode/rate-limited-free"))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("Rate limit", record["reason"])

    def test_a_failed_run_still_reports_what_it_spent(self):
        # A run stopped by the per-run budget cap emits a non-result envelope that still carries
        # its cost; dropping it would understate cost per success, which the protocol forbids.
        os.environ["FAKE_PARTIAL"] = "1"
        record = self.runtimes.run("claude", self.request(model="claude-haiku-4-5-20251001", budget_usd=0.5))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("per-run budget", record["reason"])
        self.assertEqual(record["cost_usd"], 1.0524)
        self.assertEqual(record["cost_source"], "runtime")
        self.assertEqual(record["usage"]["output_tokens"], 250)
        self.assertEqual(record["extra"]["stop_reason"], "tool_use")

    def make_plugin(self) -> Path:
        root = self.root / "plug"
        write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": "plug", "version": "1.0.0"}))
        write(root / "skills" / "alpha" / "SKILL.md", "---\nname: alpha\ndescription: Use when alpha.\n---\nRead [r](../../references/r.md) before writing.\n")
        write(root / "skills" / "beta" / "SKILL.md", "---\nname: beta\ndescription: Use when beta.\n---\nbeta\n")
        write(root / "references" / "r.md", "# r\n")
        write(root / "scripts" / "tool.sh", "#!/bin/sh\necho ok\n")
        write(root / "agents" / "worker.md", "---\ntools: Read, Bash\n---\nnot an OpenCode agent\n")
        write(root / "commands" / "go.md", "---\ndescription: x\n---\n/go\n")
        write(root / "evals" / "benchmarks" / "x" / "summary.json", "{}")
        return root

    def test_a_plugin_root_is_exposed_whole_so_relative_references_resolve(self):
        plugin = self.make_plugin()
        # Claude: the plugin itself, manifest and all, becomes --plugin-dir
        record = self.runtimes.run("claude", self.request(skill_dir=plugin, skill_name="plug", protected_paths=[plugin]))
        self.assertEqual(record["status"], "PASS")
        plugin_dir = Path(record["command"][record["command"].index("--plugin-dir") + 1].replace("/[USER]", str(Path.home())))
        self.assertEqual(json.loads((plugin_dir / ".claude-plugin" / "plugin.json").read_text())["name"], "plug")
        self.assertTrue((plugin_dir / "skills" / "alpha" / "SKILL.md").is_file())
        self.assertTrue((plugin_dir / "references" / "r.md").is_file())
        self.assertFalse((plugin_dir / "evals").exists())
        # Codex: the plugin is copied into the workspace and AGENTS.md names every skill
        shutil.rmtree(self.root / "ws", ignore_errors=True); shutil.rmtree(self.root / "run", ignore_errors=True)
        record = self.runtimes.run("codex", self.request(skill_dir=plugin, skill_name="plug", protected_paths=[plugin]))
        self.assertEqual(record["status"], "PASS")
        agents = (self.root / "ws" / "AGENTS.md").read_text()
        self.assertIn("`plugin/skills/alpha/SKILL.md`", agents)
        self.assertIn("`plugin/skills/beta/SKILL.md`", agents)
        self.assertTrue((self.root / "ws" / "plugin" / "references" / "r.md").is_file())
        # OpenCode: skills/ and its siblings land under .opencode/ so ../../references resolves
        shutil.rmtree(self.root / "ws", ignore_errors=True); shutil.rmtree(self.root / "run", ignore_errors=True)
        record = self.runtimes.run("opencode", self.request(skill_dir=plugin, skill_name="plug", protected_paths=[plugin],
                                                             model="opencode/big-pickle"))
        self.assertEqual(record["status"], "PASS")
        oc = self.root / "ws" / ".opencode"
        self.assertTrue((oc / "skills" / "alpha" / "SKILL.md").is_file())
        self.assertTrue((oc / "skills" / "alpha" / ".." / ".." / "references" / "r.md").resolve().is_file())
        self.assertFalse((oc / ".claude-plugin").exists())
        self.assertFalse((oc / "evals").exists())
        # agents/ and commands/ are OpenCode's own config namespaces: a plugin's copies break its startup
        self.assertFalse((oc / "agents").exists())
        self.assertFalse((oc / "commands").exists())
        self.assertTrue((oc / "scripts" / "tool.sh").is_file())

    def test_installed_plugins_can_be_switched_off_and_opencode_home_isolated(self):
        record = self.runtimes.run("claude", self.request(disable_claude_plugins=("pwdev-power@pwdev-claude-marketplace",)))
        argv = record["command"]
        self.assertIn("--settings", argv)
        settings = json.loads((self.root / "run" / "settings.json").read_text())
        self.assertEqual(settings, {"enabledPlugins": {"pwdev-power@pwdev-claude-marketplace": False}})
        shutil.rmtree(self.root / "ws", ignore_errors=True); shutil.rmtree(self.root / "run", ignore_errors=True)
        record = self.runtimes.run("opencode", self.request(model="opencode/big-pickle", isolate_user_skills=True))
        self.assertEqual(record["status"], "PASS")
        self.assertIn("HOME", record["env_overrides"])
        self.assertTrue((self.root / "run" / "home" / ".config").is_dir())
        calls = [json.loads(l) for l in self.log.read_text().splitlines()]
        self.assertTrue(any(c["exe"] == "opencode" for c in calls))

    def test_quota_words_inside_a_successful_run_are_not_a_quota(self):
        # Observed 2026-09-14: two Codex runs that read references/runtimes.md and quoted "hit your
        # usage limit" in their answer were recorded NOT_RUN although they exited 0 with a clean envelope.
        record = self.runtimes.run("codex", self.request(model="gpt-quota-quote"))
        self.assertEqual(record["status"], "PASS", record.get("reason"))
        self.assertTrue(record["envelope_ok"])

    def test_quota_exhaustion_is_not_run_not_fail(self):
        record = self.runtimes.run("codex", self.request(model="gpt-quota"))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("usage limit", record["reason"])

    def test_bytecode_caches_never_count_as_protected_changes(self):
        cache = self.skill / "scripts" / "__pycache__"
        write(self.skill / "scripts" / "tool.py", "print('x')\n")
        before = self.runtimes.snapshot(self.skill)
        write(cache / "tool.cpython-312.pyc", "bytes")
        self.assertEqual(before, self.runtimes.snapshot(self.skill))
        record = self.runtimes.run("claude", self.request())
        self.assertFalse(record["protected_changed"], record["protected_diff"])
        self.assertEqual(record["protected_diff"], [])

    def test_escaped_write_into_a_protected_path_fails_the_run(self):
        os.environ["FAKE_ESCAPE"] = str(self.skill / "README.md")
        record = self.runtimes.run("claude", self.request())
        self.assertTrue(record["protected_changed"])
        self.assertEqual(record["status"], "FAIL")
        self.assertIn("protected path changed", record["reason"])

    def test_missing_executable_is_not_run(self):
        record = self.runtimes.run("claude", self.request(executable="claude-does-not-exist"))
        self.assertEqual(record["status"], "NOT_RUN")
        self.assertIn("executable not found", record["reason"])

    def test_commands_and_paths_are_sanitized(self):
        record = self.runtimes.run("claude", self.request())
        self.assertNotIn("/Users/", json.dumps(record))
        self.assertEqual(self.runtimes.sanitize("api_key=abc Authorization: Bearer xyz /Users/me/x"),
                         "api_key=[REDACTED] Authorization: Bearer [REDACTED] /[USER]/x")


DISCOVER_FAKES = {
    "claude": r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
if a == ["--version"]: print("9.9.9 (Claude Code)")
elif a == ["auth", "status"]:
    print(json.dumps({"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty", "email": "someone@example.com",
                      "orgId": "org-secret-id", "orgName": "Private Org", "subscriptionType": "max"}))
elif a == ["--help"]:
    print("  --effort <level>   Effort level for the current session\n                     (low, medium, high, xhigh, max)\n"
          "  --model <model>    Provide an alias for the latest model (e.g. 'sonnet' or 'opus')")
''',
    "codex": r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
if a == ["--version"]: print("codex-cli 0.0.0")
elif a == ["login", "status"]: print("Logged in using ChatGPT")
elif a == ["debug", "models"]:
    print(json.dumps({"models": [
        {"slug": "gpt-5.6-terra", "display_name": "GPT-5.6-Terra", "visibility": "list", "priority": 7, "context_window": 272000,
         "default_reasoning_level": "medium", "supported_in_api": True,
         "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}, {"effort": "high"}]},
        {"slug": "internal-reviewer", "visibility": "hide", "priority": 1, "supported_reasoning_levels": []},
        {"slug": "gpt-5.6-sol", "display_name": "GPT-5.6-Sol", "visibility": "list", "priority": 4, "context_window": 272000,
         "default_reasoning_level": "low", "supported_in_api": True, "supported_reasoning_levels": [{"effort": "low"}]}]}))
''',
    "hermes": r'''#!/usr/bin/env python3
import sys
a = sys.argv[1:]
if a == ["--version"]: print("Hermes Agent v0.0.0")
elif a == ["status"]:
    print("  Model:        deepseek/deepseek-v4-flash-0731\n  Provider:     OpenRouter\n\u25c6 API Keys\n  OpenRouter    \u2713 sk-o...9b90\n"
          "\u25c6 Auth Providers\n  OpenAI Codex  \u2717 not logged in")
elif a == ["--help"]:
    print("  --reasoning LEVEL     Reasoning effort for this invocation: none, minimal,\n                        low, medium, high, xhigh, max, or ultra.")
''',
    "opencode": r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
if a == ["--version"]: print("0.0.0")
elif a[:2] == ["providers", "list"]: print("\x1b[0m\n\u250c  Credentials ~/.local/share/opencode/auth.json\n\u2502\n\u2514  0 credentials")
elif a == ["models", "--verbose"]:
    for name, variants in (("opencode/ling-3.0-flash-fin-free", {"low": {}, "high": {}}), ("opencode/big-pickle", {})):
        print(name)
        print(json.dumps({"name": name, "status": "active", "cost": {"input": 0, "output": 0}, "limit": {"context": 262144, "output": 32768},
                          "capabilities": {"reasoning": True}, "variants": variants, "release_date": "2026-08-27"}, indent=2))
''',
}


class DiscoverTest(unittest.TestCase):
    def setUp(self):
        self.discover = load("discover")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        bin_dir = self.root / "bin"
        for name, body in DISCOVER_FAKES.items():
            path = write(bin_dir / name, body)
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        home = self.root / "home"
        write(home / ".claude" / "settings.json", json.dumps({"model": "opus"}))
        write(home / ".claude.json", json.dumps({"additionalModelOptionsCache": [{"value": "claude-fable-5-1[1m]", "label": "Fable"}],
                                                 "oauthAccount": {"emailAddress": "someone@example.com"}}))
        write(home / ".codex" / "config.toml", 'model = "gpt-5.6-sol"\n')
        write(home / ".hermes" / "config.yaml", "model:\n  default: deepseek/deepseek-v4-flash-0731\n  provider: openrouter\nagent:\n  reasoning_effort: medium\n")
        write(home / ".hermes" / "provider_models_cache.json", json.dumps({
            "openrouter": {"models": ["anthropic/claude-sonnet-5", "openai/gpt-5.6-terra"]},
            "copilot": {"models": ["should-not-appear"]}}))
        self._env = dict(os.environ)
        os.environ.update(PATH=f"{bin_dir}:/usr/bin:/bin", HOME=str(home))
        os.environ.pop("CLAUDE_EFFORT", None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def test_reports_every_runtime_with_sources_and_no_personal_data(self):
        report = self.discover.discover(["claude", "codex", "hermes", "opencode"], {"gpt-5.6-terra": {"input": 2.0, "output": 12.0}})
        rts = report["runtimes"]
        self.assertEqual(report["usable"], ["claude", "codex", "hermes", "opencode"])

        claude = rts["claude"]
        self.assertEqual(claude["auth"], {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty", "subscriptionType": "max"})
        self.assertEqual([m["id"] for m in claude["models"]], ["opus", "sonnet", "claude-fable-5-1[1m]"])
        self.assertEqual(claude["effort_levels"], ["low", "medium", "high", "xhigh", "max"])
        self.assertEqual(claude["default"]["model_effective"], "opus")

        codex = rts["codex"]
        self.assertEqual([m["id"] for m in codex["models"]], ["gpt-5.6-sol", "gpt-5.6-terra"])  # hidden entry dropped, priority order
        terra = codex["models"][1]
        self.assertEqual((terra["default_effort"], terra["efforts"], terra["price_per_mtok"]),
                         ("medium", ["low", "medium", "high"], {"input": 2.0, "output": 12.0}))
        # no effort in config.toml: the default comes from the selected model's own default
        self.assertEqual((codex["default"]["effort_effective"], codex["default"]["effort_source"]),
                         ("low", "model default_reasoning_level (codex debug models)"))

        hermes = rts["hermes"]
        self.assertEqual(hermes["auth"]["providers_ready"], ["OpenRouter"])
        self.assertEqual([m["id"] for m in hermes["models"]], ["anthropic/claude-sonnet-5", "openai/gpt-5.6-terra"])
        self.assertEqual(hermes["default"]["effort_effective"], "medium")

        opencode = rts["opencode"]
        self.assertEqual(opencode["auth"], {"credentials": 0})
        self.assertEqual([m["id"] for m in opencode["models"]], ["opencode/ling-3.0-flash-fin-free", "opencode/big-pickle"])
        self.assertEqual(opencode["models"][0]["efforts"], ["high", "low"])
        self.assertTrue(all(m["free"] for m in opencode["models"]))
        self.assertTrue(any("retain or train" in n for n in opencode["notes"]))

        text = json.dumps(report)
        for secret in ("someone@example.com", "org-secret-id", "Private Org", "9b90"):
            self.assertNotIn(secret, text)

    def test_markdown_view_and_a_missing_runtime(self):
        os.remove(Path(os.environ["PATH"].split(":")[0]) / "hermes")
        report = self.discover.discover(["claude", "hermes", "opencode"], {})
        self.assertFalse(report["runtimes"]["hermes"]["installed"])
        self.assertNotIn("hermes", report["usable"])
        view = self.discover.render_markdown(report, limit=1)
        self.assertIn("| opencode | yes | 0.0.0 | free tier only |", view)
        self.assertIn("| hermes | no |", view)
        self.assertIn("more (use --json)", view)


REAL_EVALS = SKILL / "evals" / "evals.json"


class GradeTest(unittest.TestCase):
    def setUp(self):
        self.grade = load("grade")
        self.tokens = load("tokens")
        self.spec = json.loads(REAL_EVALS.read_text(encoding="utf-8"))
        self.fixture = self.spec["fixture"]["skill_md"]
        self.cases = {c["name"]: c for c in self.spec["evals"]}
        self.tokenizer = self.tokens.Tokenizer(allow_tiktoken=False)

    def grade_edit(self, target_md: str, result: str, name: str = "mixed_consumers_edit", csv: str | None = CSV_REFERENCE):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write(target / "SKILL.md", target_md)
            if csv:
                write(target / "references" / "csv-export.md", csv)
            return self.grade.grade_run(case=self.cases[name], fixture_skill_md=self.fixture, target_dir=target,
                                        result_text=result, record={"status": "PASS", "protected_changed": False,
                                                                    "duration_seconds": 1.5, "usage": {"input_tokens": 10}},
                                        tokenizer=self.tokenizer)

    def test_good_refactor_passes_every_objective_expectation(self):
        grading = self.grade_edit(GOOD_REFACTOR, "Outcome: refactored and statically validated; not behaviorally evaluated.")
        failed = [e for e in grading["expectations"] if not e["passed"]]
        self.assertEqual(failed, [], failed)
        self.assertEqual(grading["summary"]["pass_rate"], 1.0)
        for expectation in grading["expectations"]:
            self.assertEqual(set(expectation), {"text", "passed", "evidence"})
        self.assertLess(grading["execution_metrics"]["target_tokens_after"], grading["execution_metrics"]["target_tokens_before"])
        self.assertEqual(grading["timing"]["total_duration_seconds"], 1.5)

    def test_dropping_invariants_fails_the_matching_expectations(self):
        broken = GOOD_REFACTOR.replace("REVIEW_WINDOW=14", "").replace('user_extension: "keep-me"', "other: 1")
        grading = self.grade_edit(broken, "Outcome: refactored, statically validated and behaviorally evaluated on all models!")
        failed = {e["text"] for e in grading["expectations"] if not e["passed"]}
        self.assertIn("Preserves the literal REVIEW_WINDOW=14", failed)
        self.assertIn("Preserves metadata.user_extension: keep-me", failed)
        self.assertTrue(any("behaviorally evaluated" in text for text in failed))
        self.assertLess(grading["summary"]["pass_rate"], 1.0)

    def test_task_mode_grades_only_the_declared_checks(self):
        case = {"id": 7, "name": "summarize_notes", "prompt": "Summarize notes.txt into summary.md",
                "checks": [{"type": "file_exists", "path": "summary.md"},
                           {"type": "contains", "path": "summary.md", "needle": "Decisões"},
                           {"type": "regex", "path": "summary.md", "pattern": "(?im)^## Key points"},
                           {"type": "not_regex", "path": "summary.md", "pattern": "(?i)lorem ipsum"},
                           {"type": "not_contains", "path": "never-created.md", "needle": "x"},
                           {"type": "json_valid", "path": "out.json"},
                           {"type": "regex", "target": "result", "pattern": "(?i)wrote summary"},
                           {"type": "script", "command": "grep -q 'Key points' summary.md", "text": "summary.md has a Key points heading"},
                           {"type": "file_absent", "path": "notes.txt.bak"}]}
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            write(ws / "summary.md", "## Key points\n- a\n## Decisoes\n- b\n")
            write(ws / "out.json", "{not json")
            write(ws / "skills" / "x" / "SKILL.md", "adapter copy, not an output")
            grading = self.grade.grade_task(case=case, workspace=ws, result_text="Wrote summary.md.",
                                            record={"status": "PASS", "protected_changed": False}, tokenizer=self.tokenizer)
        by = {e["text"]: e for e in grading["expectations"]}
        self.assertTrue(by["Creates summary.md"]["passed"])
        self.assertTrue(by["summary.md contains 'Decisões'"]["passed"])  # accent-folded
        self.assertTrue(by["summary.md matches /(?im)^## Key points/"]["passed"])
        self.assertTrue(by["summary.md does not match /(?i)lorem ipsum/"]["passed"])
        self.assertTrue(by["never-created.md does not contain 'x'"]["passed"])  # absent file passes only negatives
        self.assertFalse(by["out.json is valid JSON"]["passed"])
        self.assertTrue(by["the answer matches /(?i)wrote summary/"]["passed"])
        self.assertTrue(by["summary.md has a Key points heading"]["passed"])
        self.assertTrue(by["Does not create notes.txt.bak"]["passed"])
        self.assertEqual(grading["summary"]["total"], 11)  # 9 checks + run status + protected paths
        self.assertNotIn("skills/x/SKILL.md", grading["execution_metrics"]["workspace_files_after"])

    def test_task_checks_are_validated_before_anything_runs(self):
        v = self.grade.validate_checks
        self.assertEqual(v([{"type": "file_exists", "path": "a.md"}]), [])
        self.assertTrue(v([]))
        self.assertTrue(v([{"type": "file_exists", "path": "/etc/passwd"}]))
        self.assertTrue(v([{"type": "contains", "path": "../x", "needle": "a"}]))
        self.assertTrue(v([{"type": "regex", "path": "a", "pattern": "("}]))
        self.assertTrue(v([{"type": "teleport", "path": "a"}]))
        self.assertTrue(v([{"type": "script"}]))

    def test_delivery_labels_are_read_from_the_artifact_area_too(self):
        # The skill sends the report to {run_dir}/artifacts, beside target/: labels written only there
        # must count (observed 2026-09-14: Claude labelled the report file, not the chat answer).
        case = self.cases["mixed_consumers_edit"]
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            write(ws / "target" / "SKILL.md", GOOD_REFACTOR)
            write(ws / "target" / "references" / "csv-export.md", CSV_REFERENCE)
            write(ws / "artifacts" / "artifacts" / "report-2026-09-14.md",
                  "# Report\n\nOutcome: refactored, statically validated. Not behaviorally evaluated (no benchmark ran).\n"
                  "Executor profile: guided; consumer profile: guided.\n")
            write(ws / "artifacts" / "artifacts" / "baseline" / "SKILL.md", "old text labelled behaviorally evaluated\n")
            grading = self.grade.grade_run(case=case, fixture_skill_md=self.fixture, target_dir=ws / "target",
                                           result_text="Done; see artifacts/artifacts/report-2026-09-14.md.",
                                           record={"status": "PASS", "protected_changed": False}, tokenizer=self.tokenizer)
        labels = next(e for e in grading["expectations"] if e["text"].startswith("Delivery labels"))
        self.assertTrue(labels["passed"], labels["evidence"])

    def test_invariants_from_a_case_replace_the_fixture_rules(self):
        # A context-derived case brings its own invariants; the fixture's rules must not leak in.
        case = dict(self.cases["mixed_consumers_edit"])
        case["invariants"] = {"name": "ticket-triage", "must_keep_literals": ["SLA=4h"], "labels": ["Severity", "Owner"],
                              "prohibitions": [r"(?i)never\s+close"], "language_markers": [r"(?i)\bticket\b"]}
        target_md = ("---\nname: ticket-triage\n---\n\n# Triage a ticket\n\nLabel Severity and Owner. Never close a "
                     "ticket without a reply. Keep SLA=4h.\n")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write(target / "SKILL.md", target_md)
            grading = self.grade.grade_run(case=case, fixture_skill_md="---\nname: ticket-triage\n---\nold old old\n",
                                           target_dir=target, result_text="Outcome: refactored, statically validated.",
                                           record={"status": "PASS", "protected_changed": False}, tokenizer=self.tokenizer)
        texts = [e["text"] for e in grading["expectations"]]
        self.assertIn("Preserves name: ticket-triage", texts)
        self.assertIn("Preserves the literal SLA=4h", texts)
        self.assertIn("Preserves the output labels Severity / Owner", texts)
        self.assertFalse(any("meeting-summary" in x or "REVIEW_WINDOW" in x or "csv" in x.lower() for x in texts))
        failed = [e["text"] for e in grading["expectations"] if not e["passed"]]
        self.assertNotIn("Preserves name: ticket-triage", failed)
        self.assertNotIn("Preserves the literal SLA=4h", failed)

    def test_unchanged_target_fails_edit_but_review_only_requires_no_change(self):
        unchanged = self.grade_edit(self.fixture, "recommendations only", csv=None)
        self.assertIn("Target was edited (not only recommended)", {e["text"] for e in unchanged["expectations"] if not e["passed"]})
        snap = {"target/SKILL.md": ["abc", 420]}
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write(target / "SKILL.md", self.fixture)
            good = ("Duplicated paragraphs; the CSV block is loaded on every task; the description is too "
                    "broad. A/B the previous version against the candidate on the same cases with bench.py, "
                    "decided by cost per accepted task; static diagnosis is not measured efficiency.")
            review = self.grade.grade_run(case=self.cases["review_only"], fixture_skill_md=self.fixture, target_dir=target,
                                          result_text=good, record={"status": "PASS", "protected_changed": False},
                                          snapshot_before=snap, snapshot_after=dict(snap), tokenizer=self.tokenizer)
        self.assertEqual([e for e in review["expectations"] if not e["passed"]], [])
        # A review written in Portuguese must grade the same as one in English: the check reads the
        # observation, not the writer's language (a grader looking for "static" failed "estático").
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write(target / "SKILL.md", self.fixture)
            pt = ("Duplicação de parágrafos; o bloco CSV é carregado em toda tarefa; a descrição é ampla "
                  "demais. Comparar a versão anterior com a candidata (A/B) nos mesmos casos via bench.py, "
                  "por custo por tarefa aceita; diagnóstico estático não é ganho de eficiência medido.")
            review_pt = self.grade.grade_run(case=self.cases["review_only"], fixture_skill_md=self.fixture, target_dir=target,
                                             result_text=pt, record={"status": "PASS", "protected_changed": False},
                                             snapshot_before=snap, snapshot_after=dict(snap), tokenizer=self.tokenizer)
        self.assertEqual([e["text"] for e in review_pt["expectations"] if not e["passed"]], [])

        # Naming the tools instead of the abstraction is still the separation: gpt-5.6-luna wrote
        # "static layer/load diagnostics, but treat size only as a diagnostic. Use bench.py for the A/B"
        # and a check that required the word "benchmark" scored it as a failure.
        separation = self.grade.STATIC_VS_MEASURED
        self.assertTrue(separation.search("use tokens.py for static layer/load diagnostics, but treat size only as a "
                                          "diagnostic. use bench.py for the authorized a/b execution later."))
        self.assertIsNone(separation.search("token efficiency: count tokens in this skill vs. simplified version."))

        # Citing the banned metrics to reject them is the protocol's own rule, not a violation
        # (opencode/ling-3.0-flash-fin-free was scored as inventing them for quoting the prohibition).
        self.assertTrue(self.grade._cited_as_rejected(
            "a metric invented for the occasion (readability score, lines per execution) cannot be compared.", 50))
        self.assertFalse(self.grade._cited_as_rejected("measure with a clarity index and lines per execution.", 20))

        # An invented metric fails even when the review otherwise looks complete.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            write(target / "SKILL.md", self.fixture)
            invented = ("Duplication; the CSV section loads on every task; the description is too broad. "
                        "Measure with a clarity index and lines per execution against the baseline.")
            review_bad = self.grade.grade_run(case=self.cases["review_only"], fixture_skill_md=self.fixture, target_dir=target,
                                              result_text=invented, record={"status": "PASS", "protected_changed": False},
                                              snapshot_before=snap, snapshot_after=dict(snap), tokenizer=self.tokenizer)
        failed = {e["text"] for e in review_bad["expectations"] if not e["passed"]}
        self.assertIn("Review measures with the protocol's own metrics instead of inventing one", failed)
        self.assertIn("Review separates static validation from measured efficiency", failed)

        changed = self.grade.grade_run(case=self.cases["review_only"], fixture_skill_md=self.fixture, target_dir=Path("/nonexistent"),
                                       result_text="", record={"status": "PASS", "protected_changed": False},
                                       snapshot_before=snap, snapshot_after={"target/SKILL.md": ["zzz", 420]},
                                       tokenizer=self.tokenizer)
        self.assertIn("Review-only: the run's files are byte-identical before and after",
                      {e["text"] for e in changed["expectations"] if not e["passed"]})


VALID_PROPOSAL = {
    "requests": [
        {"name": "agenda_focus", "mode": "refactor",
         "prompt": "Refactor {target} so the agenda section loads only when minutes carry an agenda; report in {run_dir}/artifacts. No benchmarks.",
         "expected_output": "Conditional agenda support, requirements preserved."},
        {"name": "csv_review", "mode": "review",
         "prompt": "Review {target}: is the CSV block worth its cost on every summary? Do not edit files.",
         "expected_output": "A review with a measurement plan."},
    ],
    "trigger_evals": [
        {"query": "Slim down the meeting-summary skill for cheap models.", "should_trigger": True},
        {"query": "Split meeting-summary's CSV export into a reference.", "should_trigger": True},
        {"query": "Measure whether the new meeting-summary core costs less per accepted summary.", "should_trigger": True},
        {"query": "Audit meeting-summary for duplicated instructions.", "should_trigger": True},
        {"query": "Summarize yesterday's board meeting from these minutes.", "should_trigger": False},
        {"query": "Export the action items of this meeting to CSV.", "should_trigger": False},
        {"query": "Write minutes for the meeting we just had.", "should_trigger": False},
        {"query": "Which decisions were taken in the Q3 planning meeting?", "should_trigger": False},
    ],
    "invariant_suggestions": {"labels": ["Agenda"]},
}


class CasesTest(unittest.TestCase):
    def setUp(self):
        self.cases = load("cases")
        self.grade = load("grade")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        install_fakes(self.bin)
        spec = json.loads(REAL_EVALS.read_text(encoding="utf-8"))
        self.fixture_md = spec["fixture"]["skill_md"]
        self.skill = self.root / "meeting-summary"
        write(self.skill / "SKILL.md", self.fixture_md)
        write(self.skill / "references" / "style.md", "# Style\n\nShort sentences.\n")
        write(self.skill / "evals" / "evals.json", "{}")
        write(self.skill / "private.pem", "not a real key\n")
        write(self.skill / "credentials.json", "{}\n")
        self.out = self.root / "cases"
        self._env = dict(os.environ)
        os.environ["FAKE_LOG"] = str(self.root / "calls.jsonl")
        os.environ["PATH"] = f"{self.bin}:/usr/bin:/bin"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def test_extract_reproduces_the_fixture_invariants_and_finds_its_defects(self):
        draft = self.cases.extract(self.skill)
        inv = draft["invariants"]
        self.assertEqual(inv["name"], "meeting-summary")
        self.assertEqual(inv["paths"], ["**/minutes.txt"])
        self.assertEqual(inv["metadata"], {"user_extension": "keep-me"})
        self.assertEqual(inv["must_keep_literals"], ["REVIEW_WINDOW=14"])
        self.assertTrue({"Key points", "Decisions", "Actions"} <= set(inv["labels"]), inv["labels"])
        self.assertTrue(any(re.search(p, "Never invent decisions") for p in inv["prohibitions"]), inv["prohibitions"])
        block = next(b for b in inv["conditional_blocks"] if b["topic"] == "csv")
        self.assertEqual(block["must_keep_terms"][:3], ["action", "assignee", "due_date"])
        self.assertTrue(re.search(block["guard"], "Do not export without a request."))
        self.assertEqual(block["marker"], "due_date")
        self.assertEqual(draft["source"]["language"], "en")
        categories = {f["category"] for f in draft["findings"]}
        self.assertTrue({"duplication", "unconditional reading", "over-broad description", "procedure without purpose"} <= categories, categories)
        self.assertFalse(draft["approved"])
        self.assertEqual([c["name"] for c in draft["evals"]], ["mixed_consumers_edit", "unknown_model_explicit_override", "review_only"])
        self.assertTrue(all("{target}" in c["prompt"] and c["invariants"] is inv for c in draft["evals"]))
        self.assertEqual(len(draft["trigger_evals"]), 8)
        self.assertEqual({t["should_trigger"] for t in draft["trigger_evals"]}, {True, False})
        # the fixture carries the skill's own files, never its evals, dotfiles or secrets-by-name
        self.assertEqual(set(draft["fixture"]["files"]), {"references/style.md"})
        self.assertEqual(draft["fixture"]["skill_md"], self.fixture_md)
        self.assertNotIn("/Users/", json.dumps(draft))

    def test_extraction_ignores_volatile_metadata_and_judges_links_by_paragraph(self):
        write(self.skill / "SKILL.md", (
            "---\nname: wrapped\ndescription: Use when wrapping.\nmetadata:\n  version: 0.2.1\n  updated: 2026-09-14\n"
            "  generated_at: 2026-09-12T00:00:00Z\n  author: Someone\n---\n\n# Wrapped\n\n"
            "Inspect the target for these defects: 3. Unconditional reading — references loaded on every run.\n\n"
            "- Any edit to the target, and any review that names findings:\n"
            "  [the protocol](references/protocol.md).\n"
            "- Packaging questions only: [usage](README.md).\n\n"
            "Terms are defined once, in [the glossary](references/glossary.md).\n"))
        draft = self.cases.extract(self.skill)
        self.assertEqual(draft["invariants"]["metadata"], {"author": "Someone"})
        unconditional = [f for f in draft["findings"] if f["category"] == "unconditional reading"]
        evidence = unconditional[0]["evidence"] if unconditional else []
        self.assertEqual(evidence, ["reference linked without a condition: references/glossary.md"])

    def test_extracted_invariants_drive_the_grader_and_hold_on_the_untouched_fixture(self):
        inv = self.cases.extract(self.skill)["invariants"]
        frontmatter, body = self.cases.split_frontmatter(self.fixture_md)
        corpus = {"SKILL.md": self.fixture_md}
        expectations = self.grade.expectations_from_spec(inv, frontmatter=frontmatter, body=body, everything=self.fixture_md,
                                                         corpus=corpus, target_md=self.fixture_md)
        texts = {e["text"]: e["passed"] for e in expectations}
        for needle in ("Preserves name: meeting-summary", "Preserves paths: **/minutes.txt",
                       "Preserves metadata.user_extension: keep-me", "Preserves the literal REVIEW_WINDOW=14",
                       "Target stays in its original language (no translation)"):
            self.assertIn(needle, texts)
            self.assertTrue(texts[needle], needle)
        self.assertTrue(all(v for k, v in texts.items() if k.startswith("Preserves")), texts)

    def test_proposal_schema_rejects_what_the_grader_could_not_trust(self):
        good = json.loads(json.dumps(VALID_PROPOSAL))
        self.assertEqual(len(self.cases.validate_proposal(good)["requests"]), 2)
        bad_cases = {
            "not an object": [],
            "one request": {**good, "requests": good["requests"][:1]},
            "bad mode": {**good, "requests": [{**good["requests"][0], "mode": "benchmark"}, good["requests"][1]]},
            "no target placeholder": {**good, "requests": [{**good["requests"][0], "prompt": "Refactor the skill."}, good["requests"][1]]},
            "name not snake": {**good, "requests": [{**good["requests"][0], "name": "Agenda Focus"}, good["requests"][1]]},
            "too few triggers": {**good, "trigger_evals": good["trigger_evals"][:5]},
            "only positives": {**good, "trigger_evals": [{**t, "should_trigger": True} for t in good["trigger_evals"]]},
            "string polarity": {**good, "trigger_evals": [{**good["trigger_evals"][0], "should_trigger": "yes"}] + good["trigger_evals"][1:]},
        }
        for label, payload in bad_cases.items():
            with self.assertRaises(ValueError, msg=label):
                self.cases.validate_proposal(payload)

    def test_propose_makes_one_headless_call_without_a_skill_and_keeps_suggestions_apart(self):
        draft = self.cases.extract(self.skill)
        write(self.out / "cases.draft.json", json.dumps(draft))
        os.environ["FAKE_PROPOSAL"] = json.dumps(VALID_PROPOSAL)
        work = self.root / "work"
        proposed = self.cases.propose(self.out, runtime="claude", model="claude-haiku-4-5-20251001", effort="medium",
                                      budget_usd=1.0, timeout=60, hermes_ack=False, work_dir=work,
                                      env_passthrough=("FAKE_LOG", "FAKE_PROPOSAL"))
        calls = [json.loads(line) for line in (self.root / "calls.jsonl").read_text().splitlines()]
        runs = [c for c in calls if "-p" in c["argv"]]
        self.assertEqual(len(runs), 1)
        self.assertNotIn("--plugin-dir", runs[0]["argv"])
        self.assertTrue((work / "workspace" / "target" / "references" / "style.md").is_file())
        self.assertTrue((self.out / "cases.proposed.json").is_file())
        self.assertEqual([c["name"] for c in proposed["evals"]][3:], ["agenda_focus", "csv_review"])
        llm = proposed["evals"][3]
        self.assertTrue(llm["origin"].startswith("llm:claude:"))
        self.assertEqual(llm["invariants"], draft["invariants"])  # objective checks come from extraction only
        self.assertEqual(len(proposed["trigger_evals"]), 16)
        self.assertEqual(proposed["llm_suggested_invariants"], {"labels": ["Agenda"]})
        self.assertNotIn("Agenda", proposed["invariants"].get("labels", []))
        self.assertEqual(proposed["proposal_run"]["status"], "PASS")
        self.assertFalse(proposed["proposal_run"]["protected_changed"])
        self.assertFalse(proposed["approved"])
        self.assertFalse((self.skill / "evals" / "cases").exists())  # nothing landed in the skill tree

    def test_task_kind_extracts_a_skeleton_and_accepts_a_valid_task_proposal(self):
        draft = self.cases.extract_task(self.skill)
        self.assertEqual(draft["kind"], "task")
        self.assertEqual(draft["evals"], [])
        self.assertEqual(draft["fixture"], {"files": {}})
        self.assertEqual(draft["checks_allowed"], list(self.grade.CHECK_TYPES))
        self.assertEqual({q["should_trigger"] for q in draft["trigger_evals"]}, {True, False})
        write(self.out / "cases.draft.json", json.dumps(draft))
        proposal = {
            "tasks": [
                {"name": "summarize_short_minutes", "prompt": "Summarize notes/minutes.txt into summary.md.",
                 "expected_output": "Three labelled sections.",
                 "files": {"notes/minutes.txt": "Alice: ship Friday.\nBob: budget approved.\n"},
                 "checks": [{"type": "file_exists", "path": "summary.md"},
                            {"type": "regex", "path": "summary.md", "pattern": "(?im)^## Decisions"},
                            {"type": "script", "command": "test -s summary.md"}]},
                {"name": "no_invented_owner", "prompt": "Summarize notes/minutes.txt; owners missing must be labelled.",
                 "expected_output": "No invented names.", "files": {"notes/minutes.txt": "Someone: fix login.\n"},
                 "checks": [{"type": "not_regex", "path": "summary.md", "pattern": "(?i)\\bCarol\\b"}]},
            ],
            "trigger_evals": [{"query": f"q{i}", "should_trigger": i % 2 == 0} for i in range(8)],
        }
        os.environ["FAKE_PROPOSAL"] = json.dumps(proposal)
        proposed = self.cases.propose(self.out, runtime="claude", model="claude-sonnet-5", effort=None, budget_usd=1.0, timeout=60,
                                      hermes_ack=False, work_dir=self.root / "work", env_passthrough=("FAKE_LOG", "FAKE_PROPOSAL"))
        self.assertEqual([c["name"] for c in proposed["evals"]], ["summarize_short_minutes", "no_invented_owner"])
        self.assertEqual(proposed["evals"][0]["mode"], "task")
        self.assertEqual(proposed["evals"][0]["files"], {"notes/minutes.txt": "Alice: ship Friday.\nBob: budget approved.\n"})
        self.assertEqual(len(proposed["evals"][0]["checks"]), 3)
        self.assertEqual(proposed["needs_review"], ["summarize_short_minutes: script check `test -s summary.md`"])
        self.assertEqual(len(proposed["trigger_evals"]), 4 + 8)
        sink = io.StringIO()
        path = self.cases.approve(self.out, skill_dir=self.skill, yes=True, stdout=sink)
        self.assertIn("Script checks run shell commands", sink.getvalue())
        approved = json.loads(path.read_text())
        self.assertTrue(approved["approved"] and approved["kind"] == "task")

    def test_task_proposal_schema_rejects_unsafe_files_and_bad_checks(self):
        good = {"tasks": [{"name": "a", "prompt": "p", "expected_output": "e", "files": {}, "checks": [{"type": "file_exists", "path": "x"}]},
                          {"name": "b", "prompt": "p", "expected_output": "e", "files": {}, "checks": [{"type": "file_exists", "path": "y"}]}],
                "trigger_evals": [{"query": f"q{i}", "should_trigger": i % 2 == 0} for i in range(8)]}
        self.assertEqual(len(self.cases.validate_task_proposal(good)["tasks"]), 2)
        bad = {
            "absolute file": {**good, "tasks": [{**good["tasks"][0], "files": {"/tmp/x": "y"}}, good["tasks"][1]]},
            "parent file": {**good, "tasks": [{**good["tasks"][0], "files": {"../x": "y"}}, good["tasks"][1]]},
            "huge file": {**good, "tasks": [{**good["tasks"][0], "files": {"x": "y" * 9000}}, good["tasks"][1]]},
            "no checks": {**good, "tasks": [{**good["tasks"][0], "checks": []}, good["tasks"][1]]},
            "unknown check": {**good, "tasks": [{**good["tasks"][0], "checks": [{"type": "vibes"}]}, good["tasks"][1]]},
            "absolute check path": {**good, "tasks": [{**good["tasks"][0], "checks": [{"type": "contains", "path": "/etc/x", "needle": "a"}]}, good["tasks"][1]]},
            "duplicate names": {**good, "tasks": [good["tasks"][0], good["tasks"][0]]},
        }
        for label, payload in bad.items():
            with self.assertRaises(ValueError, msg=label):
                self.cases.validate_task_proposal(payload)

    def test_propose_refuses_an_invalid_reply(self):
        write(self.out / "cases.draft.json", json.dumps(self.cases.extract(self.skill)))
        os.environ["FAKE_PROPOSAL"] = json.dumps({"requests": [], "trigger_evals": []})
        with self.assertRaises(ValueError):
            self.cases.propose(self.out, runtime="claude", model=None, effort=None, budget_usd=1.0, timeout=60,
                               hermes_ack=False, work_dir=self.root / "work", env_passthrough=("FAKE_LOG", "FAKE_PROPOSAL"))
        self.assertFalse((self.out / "cases.proposed.json").exists())

    def test_approve_needs_a_yes_and_pins_the_source_hash(self):
        write(self.out / "cases.draft.json", json.dumps(self.cases.extract(self.skill)))
        sink = io.StringIO()
        self.assertIsNone(self.cases.approve(self.out, skill_dir=self.skill, yes=False, stdin=io.StringIO("n\n"), stdout=sink))
        self.assertFalse((self.out / "cases.json").exists())
        self.assertIn("mixed_consumers_edit", sink.getvalue())
        path = self.cases.approve(self.out, skill_dir=self.skill, yes=False, stdin=io.StringIO("y\n"), stdout=io.StringIO())
        approved = json.loads(path.read_text())
        self.assertTrue(approved["approved"])
        self.assertEqual(approved["source"]["skill_md_sha256"], hashlib.sha256(self.fixture_md.encode()).hexdigest())
        self.assertTrue(self.cases.check(self.out, self.skill))
        # editing the skill after approval is drift: bench must not pair the cases with a different source
        write(self.skill / "SKILL.md", self.fixture_md + "\nOne more rule.\n")
        self.assertFalse(self.cases.check(self.out, self.skill))
        with self.assertRaisesRegex(SystemExit, "changed since extraction"):
            self.cases.approve(self.out, skill_dir=self.skill, yes=True, stdout=io.StringIO())

    def test_bench_materializes_the_whole_context_fixture(self):
        bench = load("bench")
        write(self.out / "cases.draft.json", json.dumps(self.cases.extract(self.skill)))
        self.cases.approve(self.out, skill_dir=self.skill, yes=True, stdout=io.StringIO())
        out = self.root / "bench-out"
        os.environ["FAKE_EDIT"] = "1"
        code = bench.main(["--skill", str(self.skill), "--out", str(out), "--cases", str(self.out), "--only-case", "3",
                           "--runtimes", "claude", "--claude-models", "claude-haiku-4-5-20251001", "--reps", "1",
                           "--dry-run", "--fake-bin", str(self.bin), "--no-skill-creator", "--no-skill-arm"])
        self.assertEqual(code, 0)
        summary = json.loads((out / "summary.json").read_text())
        self.assertTrue(summary["cases_source"].endswith("cases.json"))
        run = next(r for r in summary["runs"] if r["config"] == "no_skill")
        target = out / run["run_dir"] / "workspace" / "target"
        self.assertTrue((target / "references" / "style.md").is_file())
        self.assertFalse((target / "evals").exists())


class BenchTest(unittest.TestCase):
    def setUp(self):
        self.bench = load("bench")
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        install_fakes(self.bin)
        self.candidate = make_skill(self.root / "skill-refactor", body="# Candidate\n\nShort core.\n")
        self.baseline = make_skill(self.root / "old" / "skill-refactor", body="# Baseline\n\nLonger older core text here.\n")
        for skill in (self.candidate, self.baseline):
            write(skill / "evals" / "evals.json", REAL_EVALS.read_text(encoding="utf-8"))
        self._env = dict(os.environ)
        os.environ["FAKE_LOG"] = str(self.root / "calls.jsonl")
        os.environ["FAKE_EDIT"] = "1"
        os.environ["PATH"] = f"/usr/bin:/bin:{os.environ.get('PATH', '')}"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env)
        self.tmp.cleanup()

    def calls(self):
        log = self.root / "calls.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def run_bench(self, *extra: str, budget: str = "5") -> tuple[int, Path]:
        out = self.root / "out"
        code = self.bench.main(["--skill", str(self.candidate), "--baseline", str(self.baseline), "--out", str(out),
                                "--runtimes", "claude,codex,hermes", "--claude-models", "claude-haiku-4-5-20251001",
                                "--codex-models", "gpt-5.6-luna", "--hermes-model", "openrouter/some-model",
                                "--hermes-provider", "openrouter", "--budget-usd", budget, "--dry-run",
                                "--fake-bin", str(self.bin), "--no-skill-creator", *extra])
        return code, out

    def test_dry_run_produces_the_skill_creator_layout_and_a_per_model_summary(self):
        code, out = self.run_bench()
        summary = json.loads((out / "summary.json").read_text())
        self.assertTrue(summary["dry_run"])
        self.assertEqual(summary["runs_planned"], 3 * 2 * 3)  # cases × configs × (runtime, model)
        self.assertEqual(summary["runs_executed"], 18)
        self.assertEqual(code, 0, summary["verdict"])
        run_dirs = sorted(p for p in out.glob("eval-*/*/run-*") if p.is_dir())
        self.assertEqual(len(run_dirs), 18)
        for run_dir in run_dirs:
            for name in ("record.json", "grading.json", "timing.json", "transcript.md", "outputs/report.md", "outputs/target/SKILL.md"):
                self.assertTrue((run_dir / name).exists(), f"{run_dir.name} lacks {name}")
            self.assertTrue((run_dir.parent.parent / "eval_metadata.json").is_file())
        # directories keep skill-creator's names; the summary names the arms by their role
        self.assertEqual({p.parent.name for p in run_dirs}, {"with_skill", "without_skill"})
        self.assertEqual(summary["arms"], ["candidate", "baseline"])
        rows = {(r["runtime"], r["model"], r["config"]) for r in summary["efficiency_by_model"]}
        self.assertIn(("claude", "claude-haiku-4-5-20251001", "candidate"), rows)
        self.assertIn(("codex", "gpt-5.6-luna", "baseline"), rows)
        codex_row = next(r for r in summary["efficiency_by_model"] if r["runtime"] == "codex" and r["config"] == "candidate")
        self.assertEqual(codex_row["executed"], 3)
        self.assertIsNotNone(codex_row["cost_total_usd"])  # from the pricing table in evals.json
        self.assertGreater(summary["cost_total_usd"], 0)
        # the claude edit cases pass every objective expectation with the fake's good refactor
        claude_edit = [r for r in summary["runs"] if r["runtime"] == "claude" and r["eval_name"] == "mixed_consumers_edit"]
        self.assertTrue(all(r["pass_rate"] == 1.0 for r in claude_edit), claude_edit)
        self.assertIn("candidate", summary["static_tokens"])
        paired = summary["paired_by_case"]
        self.assertEqual(len(paired), 3 * 3)  # cases × (runtime, model)
        self.assertEqual(set(paired[0]["arms"]), {"candidate", "baseline"})
        self.assertIn("cost_per_success_usd", paired[0]["arms"]["candidate"])
        self.assertTrue((out / "benchmark.md").is_file())
        self.assertTrue((out / "tokens.json").is_file())
        # summary.json is the versioned artifact: no home-directory paths anywhere in it
        text = (out / "summary.json").read_text()
        self.assertNotIn("/Users/", text)
        self.assertNotIn("/home/", text)
        self.assertEqual(self.bench.rt.sanitize("/Users/someone/skills/x"), "/[USER]/skills/x")

    def test_budget_exhaustion_marks_remaining_runs_not_run(self):
        code, out = self.run_bench(budget="0.02")
        summary = json.loads((out / "summary.json").read_text())
        not_run = [r for r in summary["runs"] if r["status"] == "NOT_RUN"]
        self.assertTrue(not_run)
        self.assertTrue(all("budget" in r["reason"] for r in not_run))
        self.assertLess(summary["runs_executed"], summary["runs_planned"])
        self.assertLessEqual(summary["cost_total_usd"], 0.02 + 0.02)  # one run may overshoot the cap

    def test_editing_the_source_skill_mid_round_is_a_round_warning_not_a_model_failure(self):
        # Twice during real rounds the operator edited the skill while runs were in flight and every
        # run was scored FAIL. The runtime never sees the live skill — only its copy — so that is an
        # operator mistake to report, not evidence about the model.
        out = self.root / "out"
        os.environ["FAKE_ESCAPE"] = str(self.candidate / "references" / "evaluation.md")
        try:
            self.bench.main(["--skill", str(self.candidate), "--out", str(out), "--runtimes", "claude",
                             "--claude-models", "claude-haiku-4-5-20251001", "--only-case", "1",
                             "--dry-run", "--fake-bin", str(self.bin), "--no-skill-creator"])
        finally:
            os.environ.pop("FAKE_ESCAPE", None)
        summary = json.loads((out / "summary.json").read_text())
        # the run keeps its own verdict — the copy it was handed was untouched
        self.assertEqual([r["status"] for r in summary["runs"]], ["PASS"])
        # but the drift is reported, never silent, and the round says so
        self.assertIn("references/evaluation.md", " ".join(summary["source_skill_changed_during_round"]))
        self.assertEqual(summary["verdict"], "PASS_WITH_SOURCE_DRIFT")

    def test_git_baseline_follows_a_skill_that_moved_between_plugins(self):
        # After skill-refactor moved from pwdev-code to pwdev-skills, `--baseline git:<old sha>` looked
        # for the new path in the old commit and git archive failed.
        import subprocess
        repo = self.root / "repo"
        old = make_skill(repo / "plugins" / "old-plugin" / "skills" / "demo", body="# Old\n\nold body\n")
        git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()
        git("init", "-q"); git("add", "-A")
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "old")
        old_sha = git("rev-parse", "HEAD")
        new = repo / "plugins" / "new-plugin" / "skills" / "demo"
        new.parent.mkdir(parents=True)
        git("mv", "plugins/old-plugin/skills/demo", "plugins/new-plugin/skills/demo")
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "moved")

        found = self.bench.resolve_version(f"git:{old_sha}", new, self.root / "v1")
        self.assertEqual(found.relative_to(self.root / "v1").as_posix(), "plugins/old-plugin/skills/demo")
        self.assertIn("old body", (found / "SKILL.md").read_text())
        explicit = self.bench.resolve_version(f"git:{old_sha}:plugins/old-plugin/skills/demo", new, self.root / "v2")
        self.assertTrue((explicit / "SKILL.md").is_file())
        with self.assertRaises(SystemExit):
            self.bench.resolve_version(f"git:{old_sha}:plugins/nowhere", new, self.root / "v3")

    def test_no_skill_arm_exposes_nothing_and_is_paired_with_the_others(self):
        code, out = self.run_bench("--no-skill-arm", "--only-case", "3", "--runtimes", "claude,codex,opencode",
                                   "--opencode-models", "opencode/big-pickle")
        summary = json.loads((out / "summary.json").read_text())
        self.assertEqual(summary["arms"], ["candidate", "baseline", "no_skill"])
        control = [r for r in summary["runs"] if r["config"] == "no_skill"]
        self.assertEqual(len(control), 3)
        for run in control:
            run_dir = out / run["run_dir"]
            self.assertEqual(run_dir.parent.name, "no_skill")
            workspace = run_dir / "workspace"
            # the runtime received the fixture and the prompt, and no skill through any channel
            self.assertTrue((workspace / "target" / "SKILL.md").is_file())
            self.assertFalse((workspace / "skills").exists())
            self.assertFalse((workspace / "AGENTS.md").exists())
            self.assertFalse((workspace / ".opencode").exists())
            self.assertFalse((run_dir / "plugin" / "skills").exists())
        argvs = [c["argv"] for c in self.calls() if c["exe"] == "claude" and "-p" in c["argv"]]
        self.assertTrue(argvs)
        self.assertTrue(any("--plugin-dir" not in a for a in argvs), "the no-skill Claude run must not load a plugin")
        self.assertEqual(summary["static_tokens"].get("no_skill"), None)
        slot = next(s for s in summary["paired_by_case"] if s["runtime"] == "claude")
        self.assertEqual(set(slot["arms"]), {"candidate", "baseline", "no_skill"})
        row = next(r for r in summary["efficiency_by_model"] if r["config"] == "no_skill")
        self.assertEqual(row["skill_static_tokens"], 0)

    def test_unapproved_context_cases_are_refused(self):
        cases_dir = self.root / "cases"
        spec = json.loads(REAL_EVALS.read_text(encoding="utf-8"))
        spec["approved"] = False
        write(cases_dir / "cases.json", json.dumps(spec))
        with self.assertRaisesRegex(SystemExit, "unapproved"):
            self.bench.main(["--skill", str(self.candidate), "--out", str(self.root / "o"), "--cases", str(cases_dir),
                             "--runtimes", "claude", "--dry-run", "--fake-bin", str(self.bin), "--no-skill-creator"])

    def test_task_mode_measures_any_skill_on_its_own_task(self):
        # The measured skill is an arbitrary one (here "demo"), not skill-refactor: arms are its versions,
        # the workspace holds the task's input files, and grading comes from the case's checks.
        spec = {"skill_name": "demo", "kind": "task", "approved": True,
                "fixture": {"files": {"notes.txt": "Alice: ship Friday. Bob: budget ok.\n"}},
                "evals": [{"id": 1, "name": "summarize_notes",
                           "prompt": "Summarize notes.txt into summary.md with Key points, Decisions and Actions. Put nothing in {run_dir}.",
                           "expected_output": "summary.md with three sections",
                           "checks": [{"type": "file_exists", "path": "summary.md"},
                                      {"type": "regex", "path": "summary.md", "pattern": "(?im)^## (Key points|Decisions|Actions)"},
                                      {"type": "not_regex", "path": "summary.md", "pattern": "(?i)Carol"},
                                      {"type": "regex", "target": "result", "pattern": "(?i)summary\\.md"}]}]}
        write(self.root / "task" / "cases.json", json.dumps(spec))
        os.environ["FAKE_TASK"] = "## Key points\n- ship Friday\n## Decisions\n- budget ok\n## Actions\n- none\n"
        out = self.root / "task-out"
        code = self.bench.main(["--skill", str(self.candidate), "--baseline", str(self.baseline), "--no-skill-arm",
                                "--cases", str(self.root / "task"), "--out", str(out), "--runtimes", "claude",
                                "--claude-models", "claude-haiku-4-5-20251001", "--reps", "1", "--dry-run",
                                "--fake-bin", str(self.bin), "--no-skill-creator"])
        self.assertEqual(code, 0)
        summary = json.loads((out / "summary.json").read_text())
        self.assertEqual(summary["kind"], "task")
        self.assertEqual(summary["arms"], ["candidate", "baseline", "no_skill"])
        self.assertEqual(len(summary["runs"]), 3)
        self.assertTrue(all(r["status"] == "PASS" and r["pass_rate"] == 1.0 for r in summary["runs"]), summary["runs"])
        run_dir = out / summary["runs"][0]["run_dir"]
        self.assertTrue((run_dir / "workspace" / "notes.txt").is_file())
        self.assertFalse((run_dir / "workspace" / "target").exists())
        self.assertTrue((run_dir / "outputs" / "workspace" / "summary.md").is_file())
        meta = json.loads((out / "eval-1-summarize_notes" / "eval_metadata.json").read_text())
        self.assertIn("Creates summary.md", meta["assertions"])
        plugin_calls = [c for c in self.calls() if c["exe"] == "claude" and "-p" in c["argv"] and "--plugin-dir" in c["argv"]]
        self.assertEqual(len(plugin_calls), 2)  # candidate and baseline expose "demo"; no_skill exposes nothing
        self.assertTrue(all((Path(c["argv"][c["argv"].index("--plugin-dir") + 1]) / "skills" / "skill-refactor").is_dir() for c in plugin_calls))
        # regrade understands the mode
        self.assertEqual(self.bench.main(["--regrade", str(out), "--fake-bin", str(self.bin), "--no-skill-creator"]), 0)
        self.assertEqual(json.loads((out / "summary.json").read_text())["kind"], "task")

    def test_task_cases_without_usable_checks_are_refused_before_any_call(self):
        spec = {"skill_name": "demo", "kind": "task", "fixture": {"files": {}},
                "evals": [{"id": 1, "name": "bad", "prompt": "x", "checks": [{"type": "file_exists", "path": "/etc/hosts"}]}]}
        write(self.root / "task" / "cases.json", json.dumps(spec))
        with self.assertRaisesRegex(SystemExit, "usable checks"):
            self.bench.main(["--skill", str(self.candidate), "--cases", str(self.root / "task"), "--out", str(self.root / "o"),
                             "--runtimes", "claude", "--dry-run", "--fake-bin", str(self.bin), "--no-skill-creator"])
        self.assertEqual([c for c in self.calls() if "-p" in c["argv"]], [])

    def test_a_second_invocation_starts_each_run_from_a_fresh_workspace(self):
        code, out = self.run_bench("--only-case", "3", "--runtimes", "codex", "--codex-models", "gpt-5.6-luna", "--reps", "1")
        self.assertEqual(code, 0)
        run_dir = next(out.glob("eval-3-*/with_skill/run-1-codex-*"))
        write(run_dir / "workspace" / "stale.txt", "left over")
        code, _ = self.run_bench("--only-case", "3", "--runtimes", "codex", "--codex-models", "gpt-5.6-luna", "--reps", "1")
        self.assertEqual(code, 0)
        self.assertFalse((run_dir / "workspace" / "stale.txt").exists())
        self.assertTrue((run_dir / "workspace" / "target" / "SKILL.md").is_file())

    def test_regrade_reclassifies_and_resummarizes_without_new_calls(self):
        code, out = self.run_bench("--only-case", "3", "--runtimes", "codex", "--codex-models", "gpt-5.6-luna", "--reps", "1")
        self.assertEqual(code, 0)
        summary = json.loads((out / "summary.json").read_text())
        run = next(r for r in summary["runs"] if r["config"] == "candidate")
        record_path = out / run["run_dir"] / "record.json"
        record = json.loads(record_path.read_text())
        # simulate the classifier bug: a clean run recorded as a quota outage
        record.update(status="NOT_RUN", reason="runtime quota or usage limit: rate limit quoted from docs")
        record.pop("envelope_ok", None)
        record_path.write_text(json.dumps(record))
        calls_before = len(self.calls())
        code = self.bench.main(["--regrade", str(out), "--fake-bin", str(self.bin), "--no-skill-creator"])
        self.assertEqual(code, 0)
        self.assertEqual(len(self.calls()), calls_before)  # no runtime was invoked
        regraded = json.loads(record_path.read_text())
        self.assertEqual(regraded["status"], "PASS")
        self.assertTrue(regraded["envelope_ok"])
        grading = json.loads((out / run["run_dir"] / "grading.json").read_text())
        self.assertTrue(next(e["passed"] for e in grading["expectations"] if e["text"].startswith("The runtime completed")))
        summary2 = json.loads((out / "summary.json").read_text())
        self.assertEqual(summary2["runs_executed"], summary["runs_executed"])
        self.assertTrue(all(r["status"] == "PASS" for r in summary2["runs"]))
        self.assertIn("regraded_at", summary2)
        self.assertEqual(summary2["arms"], summary["arms"])
        self.assertEqual(summary2["started_at"], summary["started_at"])
        self.assertTrue((out / "benchmark.md").is_file())

    def test_regrade_summarizes_runs_from_disk_across_invocations(self):
        # Round interrupted (no summary.json), then completed by a second invocation of another
        # runtime into the same --out: the regrade unites both from the run dirs.
        code, out = self.run_bench("--only-case", "3", "--runtimes", "codex", "--codex-models", "gpt-5.6-luna", "--reps", "1")
        self.assertEqual(code, 0)
        (out / "summary.json").unlink()
        code, _ = self.run_bench("--only-case", "3", "--runtimes", "claude", "--reps", "1")
        self.assertEqual(code, 0)
        only_claude = json.loads((out / "summary.json").read_text())
        self.assertEqual({r["runtime"] for r in only_claude["runs"]}, {"claude"})
        code = self.bench.main(["--regrade", str(out), "--fake-bin", str(self.bin), "--no-skill-creator"])
        self.assertEqual(code, 0)
        merged = json.loads((out / "summary.json").read_text())
        self.assertEqual({r["runtime"] for r in merged["runs"]}, {"claude", "codex"})
        self.assertEqual(merged["runs_planned"], 4)
        self.assertEqual({(r["runtime"], r["config"]) for r in merged["runs"]},
                         {("claude", "candidate"), ("claude", "baseline"), ("codex", "candidate"), ("codex", "baseline")})
        self.assertTrue(all(r["status"] == "PASS" for r in merged["runs"]))

    def test_publish_copies_summaries_only_never_skill_copies(self):
        # A round directory holds version copies and fixture workspaces, each with a SKILL.md.
        # Published into a plugin those would count as extra skills, so only summaries are copied.
        code, out = self.run_bench("--only-case", "3")
        published = self.root / "published"
        copied = self.bench.publish(out, published)
        self.assertEqual(sorted(copied), ["benchmark.md", "summary.json", "tokens.json"])
        self.assertEqual(sorted(p.name for p in published.iterdir()), ["benchmark.md", "summary.json", "tokens.json"])
        self.assertEqual(list(published.rglob("SKILL.md")), [])
        self.assertTrue(list(out.rglob("SKILL.md")), "the round itself does contain skill copies")

    def test_hermes_model_accepts_a_list_of_provider_slugs(self):
        code, out = self.run_bench("--only-case", "3", "--runtimes", "hermes", "--hermes-provider", "openrouter",
                                   "--hermes-model", "z-ai/glm-5.3-flash,deepseek/deepseek-v4.1-flash")
        self.assertEqual(code, 0)
        summary = json.loads((out / "summary.json").read_text())
        models = {r["model"] for r in summary["runs"] if r["runtime"] == "hermes"}
        self.assertEqual(models, {"z-ai/glm-5.3-flash", "deepseek/deepseek-v4.1-flash"})
        argvs = [c["argv"] for c in self.calls() if c["exe"] == "hermes" and "-z" in c["argv"]]
        self.assertTrue(all(a[a.index("--provider") + 1] == "openrouter" for a in argvs))
        self.assertEqual({a[a.index("-m") + 1] for a in argvs}, models)

    def test_hermes_model_must_be_chosen_by_the_user_outside_dry_run(self):
        with self.assertRaises(SystemExit):
            self.bench.main(["--skill", str(self.candidate), "--out", str(self.root / "o"), "--runtimes", "hermes"])

    def test_skill_creator_tools_run_on_a_python_that_supports_their_syntax(self):
        # skill-creator's viewer uses PEP 604 annotations (`dict | None`), so it needs Python >= 3.10
        # even when the bench itself runs on an older interpreter.
        fakes = self.root / "pythons"; fakes.mkdir()
        for name, version in (("python3", "3.9.6"), ("python3.12", "3.12.4")):
            exe = fakes / name
            exe.write_text(f"#!/bin/sh\necho {version}\n"); exe.chmod(0o755)
        chosen = self.bench.tool_python(minimum=(3, 10), search_path=str(fakes), current=(3, 9))
        self.assertEqual(Path(chosen).name, "python3.12")
        self.assertEqual(self.bench.tool_python(minimum=(3, 10), search_path=str(fakes), current=(3, 11)), sys.executable)
        empty = self.root / "none"; empty.mkdir()
        self.assertIsNone(self.bench.tool_python(minimum=(3, 10), search_path=str(empty), current=(3, 9)))

    @unittest.skipUnless(load("bench").skill_creator_tools(load("bench").DEFAULT_SKILL_CREATOR), "skill-creator not installed")
    def test_skill_creator_aggregator_and_static_viewer_consume_the_layout(self):
        out = self.root / "out"
        code = self.bench.main(["--skill", str(self.candidate), "--baseline", str(self.baseline), "--out", str(out),
                                "--runtimes", "claude", "--claude-models", "claude-haiku-4-5-20251001", "--dry-run",
                                "--fake-bin", str(self.bin)])
        summary = json.loads((out / "summary.json").read_text())
        self.assertEqual(summary["skill_creator"]["aggregate"]["exit_code"], 0, summary["skill_creator"])
        self.assertTrue((out / "benchmark.json").is_file())
        self.assertEqual(summary["skill_creator"]["viewer"]["exit_code"], 0, summary["skill_creator"])
        self.assertTrue((out / "review.html").is_file())


if __name__ == "__main__":
    unittest.main()
