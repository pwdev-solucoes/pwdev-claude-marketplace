"""pwdev-feat feat_map.py: deterministic, read-only evidence scan with staleness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "pwdev-feat" / "scripts" / "feat_map.py"


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def run(repo: Path, *args: str) -> dict:
    proc = subprocess.run([sys.executable, str(SCRIPT), "--repo-root", str(repo), *args],
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


class FeatMapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "app"
        files = {
            "package.json": json.dumps({"scripts": {"test": "vitest run", "lint": "eslint .", "danger": "touch PWNED"},
                                        "dependencies": {"vue": "^3.4.0"},
                                        "devDependencies": {"@playwright/test": "^1.45.0", "vitest": "^1.0.0"}}),
            "composer.json": json.dumps({"require": {"laravel/framework": "^11.0"}, "scripts": {"test": "pest"}}),
            "artisan": "#!/usr/bin/env php\n",
            "playwright.config.ts": "export default {}\n",
            ".eslintrc.json": "{}\n",
            "app/Http/Controllers/AuthController.php": "<?php\n",
            "app/Services/PaymentService.php": "<?php\n",
            "resources/js/components/UserForm.vue": "<template/>\n",
            "tests/Feature/LoginTest.php": "<?php\n",
            "tests/e2e/scenarios/E2E-001-login.scenario.json": "{}\n",
            "database/migrations/2024_01_01_create_users.php": "<?php\n",
            ".github/workflows/ci.yml": "on: push\n",
            "docker-compose.yml": "services: {}\n",
            "AGENTS.md": "# rules\n",
            ".env": "APP_KEY=secret-value\n",
            ".env.example": "APP_KEY=\n",
            "config/secrets/prod.json": "{\"token\": \"x\"}\n",
            "certs/server.pem": "-----BEGIN PRIVATE KEY-----\n",
            "node_modules/pkg/index.js": "x\n",
        }
        for rel, content in files.items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        git(self.repo, "init", "-q")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "feat: initial")

    def tearDown(self):
        self.tmp.cleanup()

    def test_scan_reports_evidence_without_executing_or_reading_secrets(self):
        data = run(self.repo)
        self.assertEqual(data["schema"], "pwdev-feat.codebase")
        self.assertTrue(data["observation_only"])
        self.assertIn("Laravel", data["frameworks"])
        self.assertIn("Vue", data["frameworks"])
        self.assertIn("playwright", data["testing"]["e2e"])
        self.assertIn("tests", data["testing"]["test_dirs"])
        self.assertEqual(data["testing"]["e2e_scenarios"], ["tests/e2e/scenarios/E2E-001-login.scenario.json"])
        commands = {c["command"] for c in data["commands"]}
        self.assertIn("npm run test", commands)
        self.assertIn("php artisan test", commands)
        self.assertFalse((self.repo / "PWNED").exists(), "a declared command was executed")
        self.assertEqual(data["ci"], [".github/workflows/ci.yml"])
        self.assertIn("database/migrations", data["migrations"])
        self.assertEqual(data["instructions_files"], ["AGENTS.md"])
        self.assertTrue(any("Payment" in a or "Controllers" in a for a in data["sensitive_areas"]))
        self.assertGreaterEqual(data["excluded_sensitive"], 3)
        dump = json.dumps(data)
        for leaked in ("secret-value", "server.pem", "prod.json", "node_modules", '".env"'):
            self.assertNotIn(leaked, dump)
        self.assertEqual(data["git"]["conventional_commits"], 1)

    def test_output_is_deterministic_and_read_only_without_write(self):
        first, second = run(self.repo), run(self.repo)
        self.assertEqual(first, second)
        self.assertFalse((self.repo / ".planning").exists())

    def test_write_publishes_only_codebase_json_and_tracks_staleness(self):
        self.assertTrue(run(self.repo, "--staleness")["stale"])
        data = run(self.repo, "--write")
        self.assertEqual(data["published"], ".planning/feat/context/codebase.json")
        written = sorted(p.relative_to(self.repo).as_posix() for p in (self.repo / ".planning").rglob("*") if p.is_file())
        self.assertEqual(written, [".planning/feat/context/codebase.json"])
        self.assertFalse(run(self.repo, "--staleness")["stale"])
        (self.repo / "app/Services/NewService.php").write_text("<?php\n", encoding="utf-8")
        git(self.repo, "add", "app/Services/NewService.php")
        git(self.repo, "commit", "-qm", "feat: more")
        stale = run(self.repo, "--staleness")
        self.assertTrue(stale["stale"])
        self.assertEqual(stale["changed_files"], 1)


if __name__ == "__main__":
    unittest.main()
