"""pwdev-feat scripts: plan_lint, feat_state, audit, review_package and guard-secrets."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "pwdev-feat" / "scripts"
GIT_ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

PLAN_V3 = """---
type: feat-plan
schema_version: 3
slug: user-crud
plan_type: feature
status: pending
created: 2026-09-27T10:00:00Z
---

# Action Plan — User CRUD

> **Type:** feature
> **Created:** 2026-09-27
> **Status:** pending

## 1. Persona & Scope
**Persona:** Senior Laravel engineer
**Scope:** users module
**Stack:** PHP 8.3, Laravel 11, Vue 3
**UI:** yes

## 2. Direct Objective
Users can be listed and created.

## 3. Minimum Inputs
### Entities / Data
User(name, email)
### Business Rules
BR-001 email unique
### Existing Files to Read
- `app/Models/User.php` — model

## 4. Output Format
| File | Action | Description |
|------|--------|-------------|
| `app/Http/Controllers/UserController.php` | create | controller |
| `tests/Feature/UserTest.php` | create | tests |
| `tests/e2e/scenarios/E2E-001-create-user.scenario.json` | create | e2e |

## 5. Quality Criteria
| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-001 | creating a user persists it | `php artisan test --filter=UserTest` |
| AC-002 | duplicate email is rejected with 422 | `php artisan test --filter=UserTest` |

## 6. Ambiguity Handling
**Assumptions made:**
- none

## 7. Prohibitions
- no raw SQL

---

## Risks
- none — n/a

## Execution Steps
1. Create the controller — files: `app/Http/Controllers/UserController.php` — covers: AC-001, AC-002
2. Write feature tests — files: `tests/Feature/UserTest.php` — covers: AC-001, AC-002
3. Write the E2E scenario — files: `tests/e2e/scenarios/E2E-001-create-user.scenario.json` — covers: AC-001

## Verification
| Command | Purpose |
|---------|---------|
| `php artisan test` | unit + feature |

## Done
Users can be created through the API and UI.

## Commit
`feat(users): add user CRUD`
"""

# A plan exactly as pwdev-feat 2.1 wrote it (no frontmatter, checklist criteria).
PLAN_V2 = """# Action Plan — Login page

> **Type:** frontend
> **Created:** 2026-01-10
> **Status:** pending

---

## 1. Persona & Scope
**Persona:** Vue dev
**Scope:** login
**Stack:** Vue 3

## 2. Direct Objective
A login page.

## 3. Minimum Inputs
### Existing Files to Read
- src/router.ts

## 4. Output Format
| File | Action | Description |
|------|--------|-------------|
| src/pages/Login.vue | create | page |

## 5. Quality Criteria
- [ ] form validates email
- [ ] Playwright E2E: happy path

## 6. Ambiguity Handling
- ask

## 7. Prohibitions
- no new libs

---

## Execution Steps
1. Create the page component
2. Add the route

## Done
Login works.

## Commit
`feat(auth): login page`
"""


def run(script: str, *args: str, cwd: Path, expect: int | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPTS / script), *args] if script.endswith(".py") else ["sh", str(SCRIPTS / script), *args]
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=GIT_ENV)
    if expect is not None:
        assert proc.returncode == expect, (proc.returncode, proc.stdout, proc.stderr)
    return proc


class PlanLintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def lint(self, text: str) -> dict:
        path = self.dir / "plan.md"
        path.write_text(text, encoding="utf-8")
        return json.loads(run("plan_lint.py", str(path), cwd=self.dir).stdout)

    def test_valid_v3_plan(self):
        result = self.lint(PLAN_V3)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["schema_version"], 3)
        self.assertEqual(result["stats"], {"outputs": 3, "criteria": 2, "steps": 3, "e2e_scenarios": 1})

    def test_v3_traceability_errors(self):
        broken = PLAN_V3.replace(" — covers: AC-001, AC-002\n2.", " — covers: AC-001\n2.") \
                        .replace("2. Write feature tests — files: `tests/Feature/UserTest.php` — covers: AC-001, AC-002",
                                 "2. Write feature tests — covers: AC-001")
        result = self.lint(broken)
        self.assertFalse(result["ok"])
        joined = " ".join(result["errors"])
        self.assertIn("AC-002 is not covered", joined)
        self.assertIn("tests/Feature/UserTest.php", joined)

    def test_structural_errors(self):
        cases = {
            "missing section": PLAN_V3.replace("## 7. Prohibitions", "## Seven"),
            "too many steps": PLAN_V3.replace("## Verification", "".join(f"{i}. step {i}\n" for i in range(4, 12)) + "\n## Verification"),
            "bad action": PLAN_V3.replace("| create | controller |", "| build | controller |"),
            "unknown AC in steps": PLAN_V3.replace("covers: AC-001\n\n", "covers: AC-001, AC-009\n\n"),
            "review with code": PLAN_V3.replace("plan_type: feature", "plan_type: review"),
            "no verification commands": PLAN_V3.replace("| `php artisan test` | unit + feature |\n", ""),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertFalse(self.lint(text)["ok"], label)

    def test_legacy_v2_plan_passes_with_warnings(self):
        result = self.lint(PLAN_V2)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["schema_version"], 2)
        self.assertEqual(result["plan_type"], "frontend")
        self.assertTrue(result["warnings"])


class FeatStateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "README.md").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=self.repo, check=True, env=GIT_ENV)
        self.features = self.repo / ".planning/feat/features"
        for slug, text in (("login-page", PLAN_V2), ("user-crud", PLAN_V3)):
            (self.features / slug).mkdir(parents=True)
            (self.features / slug / "plan.md").write_text(text, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def state(self, *args: str) -> dict:
        return json.loads(run("feat_state.py", *args, cwd=self.repo).stdout)

    def test_list_status_marker_and_legacy_strings(self):
        (self.features / "login-page" / "plan.done.md").write_text("> **Status:** ⚠️ WITH CAVEATS\n", encoding="utf-8")
        result = self.state("list")
        by_slug = {p["slug"]: p for p in result["plans"]}
        self.assertEqual(by_slug["login-page"]["status"], "CAVEATS")
        self.assertEqual(by_slug["user-crud"]["status"], "PENDING")
        (self.features / "user-crud" / "plan.done.md").write_text(
            "<!-- feat-status: FAILED -->\n> **Status:** ✅ COMPLETE\n", encoding="utf-8")
        self.assertEqual({p["slug"]: p["status"] for p in self.state("list")["plans"]}["user-crud"], "FAILED")

    def test_mode_rule(self):
        self.assertEqual(self.state("mode", str(self.features / "user-crud/plan.md"))["mode"], "IMPLEMENT")
        review = self.features / "user-crud/review.md"
        review.write_text(PLAN_V3.replace("plan_type: feature", "plan_type: review"), encoding="utf-8")
        self.assertEqual(self.state("mode", str(review))["mode"], "REPORT")
        audit = self.features / "user-crud/audit.md"
        audit.write_text(PLAN_V2.replace("| src/pages/Login.vue | create | page |",
                                         "| .planning/feat/features/x/report.md | create | report |"), encoding="utf-8")
        self.assertEqual(self.state("mode", str(audit))["mode"], "REPORT")

    def test_resolve_latest_and_resume(self):
        (self.features / "login-page" / "plan.done.md").write_text("<!-- feat-status: COMPLETE -->\n", encoding="utf-8")
        latest = self.state("resolve", "latest")
        self.assertEqual(latest["slug"], "user-crud")
        (self.features / "user-crud" / "progress.md").write_text(
            "> **Base commit:** `abc1234`\n\n| Step | Status | Evidence |\n|---|---|---|\n"
            "| 1 | done | ok |\n| 2 | failed | x |\n| 3 | pending | |\n", encoding="utf-8")
        resolved = self.state("resolve", "user-crud")
        self.assertEqual(resolved["progress"]["resume_step"], 2)
        self.assertEqual(resolved["progress"]["base_commit"], "abc1234")
        missing = run("feat_state.py", "resolve", "nope", cwd=self.repo)
        self.assertEqual(missing.returncode, 1)
        self.assertEqual(json.loads(missing.stdout)["error"], "PLAN_NOT_FOUND")

    def test_precheck_flags_dirty_planned_files(self):
        target = self.repo / "app/Http/Controllers/UserController.php"
        target.parent.mkdir(parents=True)
        target.write_text("<?php\n", encoding="utf-8")
        result = self.state("precheck", "user-crud")
        self.assertEqual(result["dirty_planned_files"], ["app/Http/Controllers/UserController.php"])
        self.assertEqual(result["base_commit"], result["head"])
        self.assertEqual(result["mode"], "IMPLEMENT")


class AuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / ".planning").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_disabled_then_init_and_read_only_queries(self):
        self.assertEqual(run("audit.py", "summary", cwd=self.repo).returncode, 2)
        (self.repo / ".planning/config.json").write_text('{"audit": true}', encoding="utf-8")
        run("audit.py", "init", cwd=self.repo, expect=0)
        run("audit.py", "init", cwd=self.repo, expect=0)  # idempotent
        self.assertIn(".planning/pwdev-audit.db", (self.repo / ".gitignore").read_text(encoding="utf-8"))
        self.assertEqual((self.repo / ".gitignore").read_text(encoding="utf-8").count("pwdev-audit.db\n"), 1)
        summary = run("audit.py", "summary", cwd=self.repo, expect=0).stdout
        self.assertIn("Events by action", summary)
        ok = run("audit.py", "query", "SELECT command, action FROM events;", cwd=self.repo, expect=0).stdout
        self.assertIn("| init | completed |", ok)
        for sql in ("SELECT 1; DELETE FROM events", "DELETE FROM events", "PRAGMA table_info(events)",
                    "ATTACH DATABASE 'x.db' AS x", "SELECT * FROM events; SELECT 1"):
            with self.subTest(sql):
                proc = run("audit.py", "query", sql, cwd=self.repo)
                self.assertEqual(proc.returncode, 1)
                self.assertIn("REJECTED", proc.stdout)
        count = run("audit.py", "query", "SELECT COUNT(*) AS n FROM events", cwd=self.repo, expect=0).stdout
        self.assertIn("| 2 |", count)
        run("audit.py", "export", cwd=self.repo, expect=0)
        self.assertTrue((self.repo / ".planning/audit-report.md").is_file())


class ShellScriptsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        for i in range(2):
            (self.repo / f"f{i}.txt").write_text(f"{i}\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
            subprocess.run(["git", "commit", "-qm", f"c{i}"], cwd=self.repo, check=True, env=GIT_ENV)

    def tearDown(self):
        self.tmp.cleanup()

    def test_review_package(self):
        head_before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True).stdout
        proc = run("review_package.sh", "HEAD~1", "HEAD", "pkg", cwd=self.repo, expect=0)
        summary = json.loads(proc.stdout)
        self.assertEqual(summary["changed_files"], 1)
        for name in ("range.txt", "commits.txt", "changed-files.txt", "diffstat.txt", "diff.patch"):
            self.assertTrue((self.repo / "pkg" / name).is_file(), name)
        self.assertEqual(subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True).stdout, head_before)
        self.assertEqual(run("review_package.sh", "HEAD", "HEAD", "pkg", cwd=self.repo).returncode, 3)
        self.assertEqual(run("review_package.sh", "nope", "HEAD", "pkg", cwd=self.repo).returncode, 2)

    def test_guard_secrets(self):
        def guard(payload: dict) -> int:
            return subprocess.run(["sh", str(SCRIPTS / "guard-secrets.sh")], input=json.dumps(payload),
                                  capture_output=True, text=True).returncode
        self.assertEqual(guard({"tool_input": {"file_path": "/app/.env"}}), 2)
        self.assertEqual(guard({"tool_input": {"command": "cat .env.production"}}), 2)
        self.assertEqual(guard({"tool_input": {"file_path": "/keys/server.pem"}}), 2)
        self.assertEqual(guard({"tool_input": {"file_path": "/app/.env.example"}}), 0)
        self.assertEqual(guard({"tool_input": {"file_path": "/app/src/env.ts"}}), 0)


if __name__ == "__main__":
    unittest.main()
