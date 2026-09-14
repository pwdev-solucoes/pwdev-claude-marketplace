"""skill-refactor measurement and benchmark scripts, exercised without paid calls.

Every runtime is a fake executable on a closed PATH, so the tests assert the exact
command vectors, the parsing of each runtime's usage report, the safety checks and
the on-disk layout that skill-creator's aggregator consumes.
"""
from __future__ import annotations

import importlib.util
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
if prompt.startswith("Review"):
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
open(last, "w").write("done: statically validated")
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
        self.assertIn("Preserves the editorial note REVIEW_WINDOW=14", failed)
        self.assertIn("Preserves metadata.user_extension: keep-me", failed)
        self.assertTrue(any("behaviorally evaluated" in text for text in failed))
        self.assertLess(grading["summary"]["pass_rate"], 1.0)

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
        self.assertEqual({p.parent.name for p in run_dirs}, {"with_skill", "without_skill"})
        rows = {(r["runtime"], r["model"], r["config"]) for r in summary["efficiency_by_model"]}
        self.assertIn(("claude", "claude-haiku-4-5-20251001", "with_skill"), rows)
        self.assertIn(("codex", "gpt-5.6-luna", "without_skill"), rows)
        codex_row = next(r for r in summary["efficiency_by_model"] if r["runtime"] == "codex" and r["config"] == "with_skill")
        self.assertEqual(codex_row["executed"], 3)
        self.assertIsNotNone(codex_row["cost_total_usd"])  # from the pricing table in evals.json
        self.assertGreater(summary["cost_total_usd"], 0)
        # the claude edit cases pass every objective expectation with the fake's good refactor
        claude_edit = [r for r in summary["runs"] if r["runtime"] == "claude" and r["eval_name"] == "mixed_consumers_edit"]
        self.assertTrue(all(r["pass_rate"] == 1.0 for r in claude_edit), claude_edit)
        self.assertIn("with_skill", summary["static_tokens"])
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

    def test_hermes_model_must_be_chosen_by_the_user_outside_dry_run(self):
        with self.assertRaises(SystemExit):
            self.bench.main(["--skill", str(self.candidate), "--out", str(self.root / "o"), "--runtimes", "hermes"])

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
