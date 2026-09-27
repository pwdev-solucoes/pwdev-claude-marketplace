"""pwdev-hermes-orca: Hermes adapter, coordinator skill contract, preflight and catalog entry.

Run from the repository root:

    python3 -m unittest tests.test_hermes_orca
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-hermes-orca"
HERMES_INIT = PLUGIN / ".hermes-plugin" / "__init__.py"
SKILL = PLUGIN / "skills" / "hermes-orca" / "SKILL.md"
# Hermes silently drops a skill whose body names either instructions file.
FORBIDDEN_IN_SKILLS = ("CLAUDE.md", "AGENTS.md")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Ctx:
    """Stand-in for the Hermes plugin context; register_skill rejects str like the real one."""

    def __init__(self):
        self.skills = {}
        self.hooks = {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise AttributeError("register_skill needs a pathlib.Path")
        self.skills[name] = path

    def register_hook(self, event, handler):
        self.hooks[event] = handler


class HermesAdapterTest(unittest.TestCase):
    def register(self, init=HERMES_INIT):
        ctx = Ctx()
        load(init, f"hermes_orca_{id(ctx)}").register(ctx)
        return ctx

    def test_registers_the_coordinator_skill_as_path(self):
        ctx = self.register()
        self.assertEqual(set(ctx.skills), {"hermes-orca"})
        self.assertEqual(ctx.skills["hermes-orca"].resolve(), SKILL.resolve())
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})

    def test_bootstrap_only_on_first_turn_inside_orca(self):
        hook = self.register().hooks["pre_llm_call"]
        with mock.patch.dict(os.environ, {"ORCA_TERMINAL_HANDLE": "term_x"}):
            first = hook(is_first_turn=True, session_id="s")
            self.assertIsNone(hook(is_first_turn=False))
        self.assertEqual(set(first), {"context"})
        text = first["context"]
        self.assertIn("pwdev-hermes-orca bootstrap", text)
        self.assertIn('skill_view("pwdev-hermes-orca:hermes-orca")', text)
        self.assertIn("delegate_task", text)
        self.assertLess(len(text), 10_000)
        env = {k: v for k, v in os.environ.items() if k != "ORCA_TERMINAL_HANDLE"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertIsNone(hook(is_first_turn=True))

    def test_flat_install_layout_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            flat = Path(tmp) / "pwdev-hermes-orca"
            shutil.copytree(PLUGIN / "skills", flat / "skills")
            shutil.copy(HERMES_INIT, flat / "__init__.py")
            self.assertEqual(set(self.register(flat / "__init__.py").skills), {"hermes-orca"})

    def test_missing_skills_raise_before_registration(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken"
            broken.mkdir()
            shutil.copy(HERMES_INIT, broken / "__init__.py")
            ctx = Ctx()
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load(broken / "__init__.py", "hermes_orca_broken").register(ctx)
            self.assertEqual(ctx.skills, {})
            self.assertEqual(ctx.hooks, {})


class ManifestTest(unittest.TestCase):
    def test_versions_agree(self):
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        hermes = (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8")
        self.assertEqual(claude["name"], "pwdev-hermes-orca")
        self.assertIn("name: pwdev-hermes-orca", hermes)
        self.assertIn(f"version: {claude['version']}", hermes)
        self.assertIn("provides_hooks:\n  - pre_llm_call", hermes)
        self.assertIn(f"version: {claude['version']}", SKILL.read_text(encoding="utf-8"))
        self.assertIn(f"## {claude['version']}", (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8"))
        for readme in ("README.md", "README.pt-BR.md"):
            self.assertIn(f"v{claude['version']}", (PLUGIN / readme).read_text(encoding="utf-8"))

    def test_listed_once_in_the_claude_catalog(self):
        catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        entries = [p for p in catalog["plugins"] if p["name"] == "pwdev-hermes-orca"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], "./plugins/pwdev-hermes-orca")
        self.assertTrue(entries[0]["strict"])
        for tag in ("hermes", "orca", "github-issues"):
            self.assertIn(tag, entries[0]["tags"])


class SkillContractTest(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text(encoding="utf-8")

    def test_frontmatter_triggers_and_exclusions(self):
        match = re.match(r"^---\n(.*?)\n---\n", self.text, re.S)
        self.assertTrue(match)
        self.assertIn("name: hermes-orca", match.group(1))
        description = match.group(1).split("description:", 1)[1].split("metadata:", 1)[0]
        self.assertIn("Use when", description)
        self.assertIn("Do NOT use", description)
        self.assertLessEqual(len(" ".join(description.split())), 1024)

    def test_portable_for_hermes(self):
        for needle in FORBIDDEN_IN_SKILLS:
            self.assertNotIn(needle, self.text)

    def test_loads_orca_contract_at_runtime_instead_of_copying_it(self):
        self.assertIn("orca skills get orchestration", self.text)
        # Distinctive sentences of Orca's bundled skill must not be vendored here.
        for vendored in ("Classify the role", "Canonical supervised loop", "Completion accounting"):
            for path in PLUGIN.rglob("*.md"):
                self.assertNotIn(vendored, path.read_text(encoding="utf-8"), f"{path} copies Orca's skill")

    def test_user_gate_before_dispatch_and_never_merges(self):
        self.assertIn("esperar aprovação explícita", self.text)
        self.assertLess(self.text.index("Gate do plano"), self.text.index("run-create"))
        self.assertIn("Nunca fazer merge", self.text)
        self.assertIn("nunca troque um worker do\nOrca por `delegate_task`", self.text)

    def test_every_cited_reference_exists(self):
        cited = set(re.findall(r"`((?:references|templates|scripts)/[A-Za-z0-9_./-]+\.(?:md|json|py))`", self.text))
        self.assertTrue(cited)
        for rel in cited:
            self.assertTrue((PLUGIN / rel).is_file(), rel)
        for path in (PLUGIN / "references").glob("*.md"):
            for link in re.findall(r"\]\(([a-z-]+\.md)\)", path.read_text(encoding="utf-8")):
                self.assertTrue((PLUGIN / "references" / link).is_file(), f"{path.name} → {link}")

    def test_workers_run_feat_loop_per_agent(self):
        prompt = (PLUGIN / "references/worker-prompt.md").read_text(encoding="utf-8")
        for line in ("/pwdev-feat:loop #<N>", "$feat-loop #<N>", "/feat-loop #<N>"):
            self.assertIn(line, prompt)
        config = json.loads((PLUGIN / "templates/hermes-orca.config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["worker_skill"], "feat-loop")
        self.assertIn(config["routing"]["default"], ("claude", "codex", "opencode"))
        self.assertLess(config["wait_timeout_ms"], 600_000)
        # The gate kinds Hermes answers are the ones feat-loop raises.
        mode = (ROOT / "plugins/pwdev-feat/references/orchestrated-mode.md").read_text(encoding="utf-8")
        answers = (PLUGIN / "references/answering-asks.md").read_text(encoding="utf-8")
        raised = set(re.findall(r"^\| `([a-z]+)` \|", mode, re.M))
        self.assertEqual(raised, {"interview", "plan", "quick", "exec", "branch", "advice", "stopped", "pr"})
        for kind in raised:
            self.assertIn(f"`{kind}`", answers, kind)


class PreflightTest(unittest.TestCase):
    def setUp(self):
        self.pre = load(PLUGIN / "scripts/preflight.py", "hermes_orca_preflight")

    def test_detects_feat_versions_per_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, project = Path(tmp) / "home", Path(tmp) / "proj"
            for ver in ("2.1.1", "3.2.0"):
                manifest = home / f".claude/plugins/cache/m/pwdev-feat/{ver}/.claude-plugin/plugin.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text(json.dumps({"version": ver}))
            skill = project / ".opencode/skills/feat-loop/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: feat-loop\nmetadata:\n  version: 3.1.9\n---\n")
            self.assertEqual(self.pre.feat_version("claude", home, project), (3, 2, 0))
            self.assertEqual(self.pre.feat_version("opencode", home, project), (3, 1, 9))
            self.assertIsNone(self.pre.feat_version("codex", home, project))

    def test_blocks_outside_orca_and_on_old_feat(self):
        def fake_run(*cmd, timeout=20):
            return 1, "unavailable"
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.pre, "run", fake_run):
            env = {k: v for k, v in os.environ.items() if k != "ORCA_TERMINAL_HANDLE"}
            with mock.patch.dict(os.environ, env, clear=True):
                report = self.pre.check(["codex"], Path(tmp), Path(tmp))
        self.assertFalse(report["ok"])
        joined = "\n".join(report["blockers"])
        for needle in ("ORCA_TERMINAL_HANDLE", "runtime do Orca", "gh auth login", "codex: pwdev-feat"):
            self.assertIn(needle, joined)

    def test_ready_environment_has_no_blocker(self):
        answers = {
            ("orca", "status", "--json"): {"result": {"runtime": {"state": "ready", "reachable": True, "appVersion": "1.4.215"}}},
            ("orca", "worktree", "current", "--json"): {"result": {"worktree": {"id": "r::/p", "projectId": "github:o/r"}}},
            ("gh", "repo", "view", "--json", "nameWithOwner,defaultBranchRef"): {"nameWithOwner": "o/r", "defaultBranchRef": {"name": "main"}},
        }

        def fake_run(*cmd, timeout=20):
            return 0, json.dumps(answers.get(cmd, {}))
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(self.pre, "run", fake_run):
            home = Path(tmp)
            manifest = home / ".claude/plugins/cache/m/pwdev-feat/3.2.0/.claude-plugin/plugin.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"version": "3.2.0"}))
            with mock.patch.dict(os.environ, {"ORCA_TERMINAL_HANDLE": "term_x"}):
                report = self.pre.check(["claude"], home, home)
        self.assertEqual(report["blockers"], [])
        self.assertTrue(report["ok"])
        self.assertEqual(report["facts"]["default_branch"], "main")


if __name__ == "__main__":
    unittest.main()
