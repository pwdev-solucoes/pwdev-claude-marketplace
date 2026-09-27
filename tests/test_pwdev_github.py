"""pwdev-github ghp.py: roadmap publishing against a fake `gh` on PATH."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GHP = ROOT / "plugins/pwdev-github/scripts/ghp.py"
CHECK = ROOT / "plugins/pwdev-prd/scripts/roadmap-check.py"
FIXTURE = ROOT / "tests/fixtures/pwdev-roadmap/roadmap"
PLUGIN = ROOT / "plugins/pwdev-github"

spec = importlib.util.spec_from_file_location("ghp", GHP)
ghp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ghp)

FAKE_GH = textwrap.dedent(r'''
    #!/usr/bin/env python3
    import json, os, sys
    home = os.environ["FAKE_GH_HOME"]
    args = sys.argv[1:]
    stdin = "" if sys.stdin.isatty() else sys.stdin.read()
    state_path = os.path.join(home, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"issues": 0, "items": 0}
    with open(os.path.join(home, "calls.jsonl"), "a") as log:
        log.write(json.dumps({"args": args, "stdin": stdin}) + "\n")

    def out(value):
        json.dump(state, open(state_path, "w"))
        print(json.dumps(value) if not isinstance(value, str) else value)
        sys.exit(0)

    def fail(message):
        json.dump(state, open(state_path, "w"))
        print(message, file=sys.stderr)
        sys.exit(1)

    method = args[args.index("--method") + 1] if "--method" in args else "GET"
    if args[:2] == ["api", "graphql"]:
        query = json.loads(stdin)["query"]
        if "projectV2(number" in query:
            def select(fid, name, options):
                return {"id": fid, "name": name, "dataType": "SINGLE_SELECT",
                        "options": [{"id": f"{fid}-{o}", "name": o} for o in options]}
            fields = [
                {"id": "F_TITLE", "name": "Title", "dataType": "TITLE"},
                select("F_STATUS", "Status", ["Todo", "In Progress", "Done"]),
                select("F_TIPO", "Tipo", ["Épico", "Feature", "História", "Task"]),
                select("F_PRIO", "Prioridade", ["Must", "Should", "Could", "Won't"]),
                select("F_EST", "Estimativa", ["P", "M", "G"]),
                {"id": "F_FASE", "name": "Fase", "dataType": "TEXT"},
                {"id": "F_ONDA", "name": "Onda", "dataType": "NUMBER"},
                {"id": "F_REQ", "name": "Requisitos", "dataType": "TEXT"},
            ]
            project = {"id": "PVT_1", "url": "https://github.com/users/me/projects/7", "title": "P",
                       "fields": {"nodes": fields}}
            out({"data": {"viewer": {"projectV2": project}, "repositoryOwner": {"projectV2": project}}})
        out({"data": {}})
    if args[:2] == ["label", "list"]:
        out(json.dumps(state.get("labels", [])))
    if args[:2] == ["label", "create"]:
        state.setdefault("labels", []).append(args[2])
        out("")
    if args[:2] in (["project", "item-edit"], ["issue", "comment"]):
        out("")
    if args[:2] == ["project", "item-add"]:
        state["items"] += 1
        out({"id": f"PVTI_{state['items']}"})
    if args[0] == "api":
        path = args[1]
        if path.endswith("/milestones") and method == "POST":
            out({"number": 1})
        if "/milestones" in path:
            out([])
        if path.endswith("/issues") and method == "POST":
            fail_at = int(os.environ.get("FAKE_FAIL_AT_ISSUE", "0"))
            if fail_at and state["issues"] + 1 == fail_at and not os.path.exists(os.path.join(home, "failed")):
                open(os.path.join(home, "failed"), "w").close()
                fail("HTTP 502: Bad Gateway")
            state["issues"] += 1
            n = state["issues"]
            out({"number": n, "id": 1000 + n, "node_id": f"I_{n}", "html_url": f"https://github.com/o/r/issues/{n}"})
        if "/dependencies/blocked_by" in path and os.environ.get("FAKE_NO_DEPS"):
            fail("HTTP 404: Not Found (https://api.github.com/...)")
        out({})
    fail("fake gh: unhandled " + " ".join(args))
''').lstrip()


class FakeGhCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.work = self.tmp / "work"
        shutil.copytree(FIXTURE, self.work / "roadmap")
        self.roadmap = self.work / "roadmap/roadmap.json"
        self.map = self.work / ".planning/github/catalogo-produtos.map.json"
        self.env = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        FAKE_GH_HOME=str(self.home))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def ghp(self, *args, **env):
        proc = subprocess.run([sys.executable, str(GHP), *args], capture_output=True, text=True,
                              cwd=self.work, env=dict(self.env, **env))
        return proc.returncode, proc.stdout, proc.stderr

    def publish(self, *extra, **env):
        return self.ghp("publish", "--roadmap", str(self.roadmap), "--owner", "@me", "--repo", "o/r",
                        "--number", "7", *extra, **env)

    def calls(self):
        path = self.home / "calls.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines()]

    def api_posts(self, suffix):
        return [c for c in self.calls() if c["args"][0] == "api" and c["args"][1].endswith(suffix)
                and "POST" in c["args"]]


class PlanTest(FakeGhCase):
    def load(self):
        return json.loads(self.roadmap.read_text(encoding="utf-8"))

    def test_dry_run_default_mapping_makes_no_gh_calls(self):
        code, out, err = self.publish("--dry-run")
        self.assertEqual(code, 0, err)
        plan = json.loads(out)
        self.assertEqual(plan["create"], ["F01-E01", "F01-E01-FT01", "F01-E02", "F01-E02-FT01", "F01-E02-FT02"])
        self.assertEqual(plan["milestones"], ["F01"])
        self.assertEqual(plan["sub_issues"], ["F01-E01>F01-E01-FT01", "F01-E02>F01-E02-FT01", "F01-E02>F01-E02-FT02"])
        self.assertEqual(plan["blocked_by"], ["F01-E02-FT01>F01-E01-FT01", "F01-E02-FT02>F01-E02-FT01"])
        self.assertIn("prd:catalogo-produtos", plan["labels"])
        self.assertEqual(self.calls(), [])

    def test_flat_and_task_issue_mappings(self):
        flat = ghp.build_plan(self.load(), self.roadmap, "flat")
        self.assertEqual([i["id"] for i in flat["issues"]], ["F01-E01-FT01", "F01-E02-FT01", "F01-E02-FT02"])
        self.assertEqual(flat["sub_issues"], [])
        self.assertEqual(len(flat["blocked_by"]), 2)
        tasks = ghp.build_plan(self.load(), self.roadmap, "task-issues")
        self.assertEqual(len(tasks["issues"]), 7)
        self.assertEqual(len(tasks["sub_issues"]), 5)
        self.assertIn(("F01-E01-FT01-T02", "F01-E01-FT01-T01"), tasks["blocked_by"])

    def test_task_edges_lift_to_features_when_tasks_are_checklists(self):
        data = self.load()
        data["edges"].append({"from": "F01-E01-FT01-T02", "to": "F01-E02-FT02", "kind": "data"})
        plan = ghp.build_plan(data, self.roadmap, "default")
        self.assertIn(("F01-E02-FT02", "F01-E01-FT01"), plan["blocked_by"])
        self.assertNotIn(("F01-E01-FT01", "F01-E01-FT01"), plan["blocked_by"])

    def test_feature_body_and_fields(self):
        plan = ghp.build_plan(self.load(), self.roadmap, "default")
        feature = next(i for i in plan["issues"] if i["id"] == "F01-E01-FT01")
        self.assertEqual(feature["title"], "[F01-E01-FT01] Login de administrador")
        self.assertIn("### Critérios de aceite", feature["body"])
        self.assertIn("- [ ] F01-E01-FT01-T01 Modelo de usuário e senha com hash", feature["body"])
        self.assertIn("<details><summary>Arquivo do roadmap</summary>", feature["body"])
        self.assertEqual(feature["milestone"], "F01 Fundação")
        self.assertEqual(feature["fields"]["wave"], 1)
        self.assertEqual(feature["fields"]["requirements"], "FR-01, NFR-01")
        busca = next(i for i in plan["issues"] if i["id"] == "F01-E02-FT02")
        self.assertIn("**Depende de:** F01-E02-FT01 Cadastro de produto", busca["body"])
        self.assertEqual(busca["fields"]["wave"], 3)

    def test_waves_match_the_prd_checker(self):
        proc = subprocess.run([sys.executable, str(CHECK), str(self.roadmap), "--json", "--no-write"],
                              capture_output=True, text=True)
        checker = json.loads(proc.stdout)
        self.assertEqual(checker["status"], "PASS")
        level = ghp.waves(self.load()["nodes"], self.load()["edges"])
        for index, wave in enumerate(checker["waves"], 1):
            for feature in wave:
                self.assertEqual(level[feature], index)

    def test_stories_go_into_the_feature_body_by_default(self):
        plan = ghp.build_plan(self.load(), self.roadmap, "default")
        self.assertEqual([i["id"] for i in plan["issues"] if i["id"].startswith("US-")], [])
        login = next(i for i in plan["issues"] if i["id"] == "F01-E01-FT01")["body"]
        self.assertIn("### Histórias de usuário", login)
        self.assertIn("#### US-01 — Entrar como administrador", login)
        self.assertIn("Como **administrador da loja**, quero **entrar com e-mail e senha**", login)
        self.assertIn("- [ ] **CA-03 (error, RN-01)**", login)
        self.assertIn("```gherkin", login)
        self.assertIn("**RN-01 — Bloqueio após tentativas inválidas:**", login)
        busca = next(i for i in plan["issues"] if i["id"] == "F01-E02-FT02")["body"]
        self.assertIn("#### US-03 — Buscar produto pelo nome _(rascunho)_", busca)

    def test_stories_as_sub_issues(self):
        plan = ghp.build_plan(self.load(), self.roadmap, "default", stories_mode="issues")
        stories = {i["id"]: i for i in plan["issues"] if i["id"].startswith("US-")}
        self.assertEqual(sorted(stories), ["US-01", "US-02", "US-03"])
        self.assertIn(("F01-E01-FT01", "US-01"), plan["sub_issues"])
        self.assertIn(("US-02", "US-01"), plan["blocked_by"])
        self.assertIn("type:story", stories["US-01"]["labels"])
        self.assertIn("status:draft", stories["US-03"]["labels"])
        self.assertNotIn("status:draft", stories["US-01"]["labels"])
        self.assertEqual(stories["US-02"]["fields"]["type"], "story")
        self.assertEqual(stories["US-02"]["fields"]["wave"], 2)
        self.assertEqual(stories["US-01"]["milestone"], "F01 Fundação")
        self.assertIn("História de usuário da feature F01-E01-FT01", stories["US-01"]["body"])
        feature = next(i for i in plan["issues"] if i["id"] == "F01-E01-FT01")["body"]
        self.assertIn("- US-01 Entrar como administrador", feature)
        self.assertNotIn("```gherkin", feature)

    def test_body_limit(self):
        data = self.load()
        big = self.work / "roadmap" / data["nodes"][2]["path"]
        big.write_text("x" * 70000)
        plan = ghp.build_plan(data, self.roadmap, "default")
        body = next(i for i in plan["issues"] if i["id"] == "F01-E01-FT01")["body"]
        self.assertLess(len(body), ghp.BODY_LIMIT)
        self.assertNotIn("<details>", body)

    def test_field_resolution_uses_aliases_for_a_default_project(self):
        fields = [{"id": "S", "name": "Status", "dataType": "SINGLE_SELECT",
                   "options": [{"id": "a", "name": "Todo"}, {"id": "b", "name": "In Progress"}, {"id": "c", "name": "Done"}]},
                  {"id": "W", "name": "Wave", "dataType": "NUMBER"}]
        setters = ghp.field_setter(fields, None)
        self.assertEqual(setters["status"][1]["backlog"], "a")
        self.assertEqual(setters["status"][1]["done"], "c")
        self.assertIn("wave", setters)
        self.assertNotIn("type", setters)

    def test_iteration_config(self):
        import datetime as dt
        conf = ghp.iteration_config({"start": "next-monday", "duration": 14, "count": 2},
                                    today=dt.date(2026, 9, 27))  # a Sunday
        self.assertEqual(conf["startDate"], "2026-09-28")
        self.assertEqual([i["startDate"] for i in conf["iterations"]], ["2026-09-28", "2026-10-12"])
        self.assertEqual(conf["iterations"][1]["title"], "Sprint 2")


class PublishTest(FakeGhCase):
    def test_publish_creates_links_and_fields_then_is_idempotent(self):
        code, out, err = self.publish()
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["status"], "OK")
        self.assertEqual((result["issues"], result["sub_issues"], result["blocked_by"], result["milestones"]),
                         (5, 3, 2, 1))
        state = json.loads(self.map.read_text())
        self.assertEqual(state["schema"], "pwdev-github-map/1")
        self.assertEqual(state["project_url"], "https://github.com/users/me/projects/7")
        # blocked-by uses the internal id of the blocker, on the blocked issue's number
        prereq = state["issues"]["F01-E01-FT01"]
        dependent = state["issues"]["F01-E02-FT01"]
        deps = self.api_posts("/dependencies/blocked_by")
        self.assertTrue(any(c["args"][1] == f"repos/o/r/issues/{dependent['number']}/dependencies/blocked_by"
                            and json.loads(c["stdin"]) == {"issue_id": prereq["id"]} for c in deps))
        subs = self.api_posts("/sub_issues")
        epic = state["issues"]["F01-E01"]
        self.assertTrue(any(c["args"][1] == f"repos/o/r/issues/{epic['number']}/sub_issues"
                            and json.loads(c["stdin"]) == {"sub_issue_id": prereq["id"]} for c in subs))
        edits = [c["args"] for c in self.calls() if c["args"][:2] == ["project", "item-edit"]]
        self.assertIn("F_STATUS-Todo", sum(edits, []))       # Status = Backlog via the "Todo" alias
        self.assertIn("F_TIPO-Feature", sum(edits, []))
        self.assertIn("F_EST-G", sum(edits, []))              # estimate L -> "G"
        created = json.loads(self.api_posts("/issues")[0]["stdin"])
        self.assertEqual(created["milestone"], 1)
        self.assertIn("type:epic", created["labels"])

        before = len(self.calls())
        code, out, err = self.publish()
        self.assertEqual(code, 0, err)
        new_calls = self.calls()[before:]
        writes = [c for c in new_calls if "POST" in c["args"] or "PATCH" in c["args"]
                  or c["args"][:2] in (["project", "item-add"], ["project", "item-edit"], ["label", "create"])]
        self.assertEqual(writes, [], "second publish must not write")

    def test_changed_roadmap_patches_only_the_changed_issue(self):
        self.assertEqual(self.publish()[0], 0)
        data = json.loads(self.roadmap.read_text())
        next(n for n in data["nodes"] if n["id"] == "F01-E02-FT02")["title"] = "Busca por nome e categoria"
        self.roadmap.write_text(json.dumps(data, ensure_ascii=False))
        code, out, _ = self.publish("--dry-run")
        self.assertEqual(json.loads(out)["update"], ["F01-E02-FT02"])
        before = len(self.calls())
        self.assertEqual(self.publish()[0], 0)
        patches = [c for c in self.calls()[before:] if "PATCH" in c["args"]]
        self.assertEqual(len(patches), 1)
        self.assertEqual(json.loads(patches[0]["stdin"])["title"], "[F01-E02-FT02] Busca por nome e categoria")

    def test_failure_is_resumable_without_duplicates(self):
        code, out, _ = self.publish(FAKE_FAIL_AT_ISSUE="3")
        self.assertEqual(code, 1)
        failed = json.loads(out)
        self.assertEqual(failed["status"], "FAILED")
        self.assertEqual(len(json.loads(self.map.read_text())["issues"]), 2)
        code, out, err = self.publish(FAKE_FAIL_AT_ISSUE="3")
        self.assertEqual(code, 0, err)
        self.assertEqual(len(self.api_posts("/o/r/issues")), 6)  # 5 created + the one that failed
        self.assertEqual(json.loads(out)["issues"], 5)

    def test_publish_stories_as_issues_sets_story_type(self):
        code, out, err = self.publish("--stories", "issues")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual((result["issues"], result["sub_issues"], result["blocked_by"]), (8, 6, 4))
        edits = sum((c["args"] for c in self.calls() if c["args"][:2] == ["project", "item-edit"]), [])
        self.assertIn("F_TIPO-História", edits)

    def test_dependency_fallback_comment(self):
        code, out, err = self.publish(FAKE_NO_DEPS="1")
        self.assertEqual(code, 0, err)
        result = json.loads(out)
        self.assertEqual(result["blocked_by"], 0)
        self.assertEqual(result["fallback_blocked_by"], 2)
        comments = [c["args"] for c in self.calls() if c["args"][:2] == ["issue", "comment"]]
        self.assertEqual(len(comments), 2)
        self.assertTrue(any("Bloqueada por #" in " ".join(a) for a in comments))

    def test_map_for_another_repo_is_refused(self):
        self.assertEqual(self.publish()[0], 0)
        code, _, err = self.ghp("publish", "--roadmap", str(self.roadmap), "--owner", "@me", "--repo", "x/y",
                                "--number", "7", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("belongs to o/r", err)

    def test_orphans_are_listed_not_closed(self):
        self.assertEqual(self.publish()[0], 0)
        data = json.loads(self.roadmap.read_text())
        data["nodes"] = [n for n in data["nodes"] if n["id"] != "F01-E02-FT02"]
        data["requirements"].remove("FR-03")
        data["edges"] = [e for e in data["edges"] if "F01-E02-FT02" not in (e["from"], e["to"])]
        self.roadmap.write_text(json.dumps(data, ensure_ascii=False))
        code, out, _ = self.publish("--dry-run")
        self.assertEqual(json.loads(out)["orphans"], ["F01-E02-FT02"])


class PluginContractTest(unittest.TestCase):
    def test_manifest_commands_skill_and_presets(self):
        manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "pwdev-github")
        self.assertEqual({p.stem for p in (PLUGIN / "commands").glob("*.md")},
                         {"init", "project", "publish", "status"})
        self.assertTrue((PLUGIN / "skills/github-issues/SKILL.md").is_file())
        for preset in ("roadmap-produto", "kanban", "scrum"):
            data = ghp.load_preset(preset)
            roles = [f.get("role") for f in data["fields"]]
            self.assertIn("status", roles)
            for field in data["fields"]:
                for option in field.get("options", []):
                    self.assertIn(option["color"], {"GRAY", "BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE"})

    def test_skill_never_deletes_by_default(self):
        text = (PLUGIN / "skills/github-issues/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Nunca apagar", text)
        self.assertIn("--reason", text)

    def test_marketplace_lists_the_plugin(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        entry = next(p for p in market["plugins"] if p["name"] == "pwdev-github")
        self.assertEqual(entry["source"], "./plugins/pwdev-github")


if __name__ == "__main__":
    unittest.main()
