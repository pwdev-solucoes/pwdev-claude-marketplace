"""pwdev-prd roadmap-check.py: validation of pwdev-roadmap/1, waves, critical path, DEPENDENCIES.md."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "plugins/pwdev-prd/scripts/roadmap-check.py"
FIXTURE = ROOT / "tests/fixtures/pwdev-roadmap/roadmap"
PRD = ROOT / "plugins/pwdev-prd"


def run(path, *extra):
    proc = subprocess.run([sys.executable, str(CHECK), str(path), *extra], capture_output=True, text=True)
    return proc.returncode, proc.stdout


class FixtureCase(unittest.TestCase):
    """A writable copy of the shared roadmap fixture."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.dir = self.tmp / "roadmap"
        shutil.copytree(FIXTURE, self.dir)
        self.path = self.dir / "roadmap.json"
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def node(self, nid):
        return next(n for n in self.data["nodes"] if n["id"] == nid)


class RoadmapCheckTest(FixtureCase):
    def test_valid_roadmap_passes_and_renders_dependencies(self):
        code, out = run(self.path, "--json")
        self.assertEqual(code, 0, out)
        result = json.loads(out)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"], {"phase": 1, "epic": 2, "feature": 3, "task": 2})
        self.assertEqual(result["waves"], [["F01-E01-FT01"], ["F01-E02-FT01"], ["F01-E02-FT02"]])
        self.assertEqual(result["critical_path"], ["F01-E01-FT01", "F01-E02-FT01", "F01-E02-FT02"])
        self.assertEqual(result["critical_weight"], 6)  # M + L + S
        deps = (self.dir / "DEPENDENCIES.md").read_text(encoding="utf-8")
        self.assertIn("```mermaid", deps)
        self.assertIn("F01_E01_FT01 --> F01_E02_FT01", deps)
        self.assertIn("## Ondas", deps)  # meta.language pt-BR
        self.assertIn("**Onda 3:** F01-E02-FT02", deps)

    def test_no_write_leaves_dependencies_untouched(self):
        code, _ = run(self.path, "--no-write")
        self.assertEqual(code, 0)
        self.assertFalse((self.dir / "DEPENDENCIES.md").exists())

    def test_independent_features_share_a_wave(self):
        self.data["edges"] = [e for e in self.data["edges"] if e["from"] != "F01-E01-FT01"]
        self.write()
        code, out = run(self.path, "--json")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads(out)["waves"][0], ["F01-E01-FT01", "F01-E02-FT01"])

    def test_cycle_is_reported_with_its_path(self):
        self.data["edges"].append({"from": "F01-E02-FT02", "to": "F01-E01-FT01", "kind": "technical"})
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("dependency cycle: ", out)
        self.assertIn("F01-E02-FT02", out)
        self.assertFalse((self.dir / "DEPENDENCIES.md").exists())

    def test_dangling_edge_and_bad_kind(self):
        self.data["edges"].append({"from": "F01-E09-FT01", "to": "F01-E02-FT02", "kind": "technical"})
        self.data["edges"][0]["kind"] = "preference"
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("endpoint not found", out)
        self.assertIn("kind must be one of", out)

    def test_task_cannot_depend_on_its_own_feature(self):
        self.data["edges"].append({"from": "F01-E01-FT01", "to": "F01-E01-FT01-T02", "kind": "technical"})
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("own feature", out)

    def test_traceability_both_directions(self):
        self.node("F01-E02-FT02")["requirements"] = ["FR-09"]
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("FR-03: functional requirement with no feature", out)
        self.assertIn("requirement FR-09 is not in the PRD requirement list", out)

    def test_feature_needs_acceptance_priority_and_estimate(self):
        feature = self.node("F01-E02-FT01")
        feature["acceptance"] = []
        feature["priority"] = "high"
        feature["estimate"] = "XL"
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        for text in ("without acceptance criteria", "priority must be one of", "estimate must be one of"):
            self.assertIn(text, out)

    def test_hierarchy_ids_and_files(self):
        self.node("F01-E02-FT02")["parent"] = "F01-E01"  # id does not extend parent
        self.data["nodes"].append(dict(self.node("F01-E02"), title="dup"))
        (self.dir / "F01-fundacao/PHASE.md").unlink()
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("must extend its parent id", out)
        self.assertIn("F01-E02: duplicate id", out)
        self.assertIn("path not found: F01-fundacao/PHASE.md", out)

    def test_split_limit_on_tasks(self):
        for i in range(3, 10):
            self.data["nodes"].append({"id": f"F01-E01-FT01-T{i:02d}", "type": "task", "title": f"t{i}",
                                       "parent": "F01-E01-FT01",
                                       "path": "F01-fundacao/F01-E01-acesso/F01-E01-FT01-login.md"})
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1)
        self.assertIn("9 tasks, split the feature", out)

    def test_wrong_schema_is_rejected(self):
        self.data["schema"] = "pwdev-roadmap/0"
        self.write()
        self.assertEqual(run(self.path)[0], 1)


class StoriesCheckTest(FixtureCase):
    """User stories (US), acceptance criteria (CA) and business rules (RN) in roadmap.json."""

    def story(self, sid):
        return next(s for s in self.data["stories"] if s["id"] == sid)

    def assertFails(self, *texts):
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 1, out)
        for text in texts:
            self.assertIn(text, out)
        return out

    def test_fixture_stories_pass_and_render(self):
        code, out = run(self.path, "--json")
        self.assertEqual(code, 0, out)
        result = json.loads(out)
        self.assertEqual(result["stories"], {"total": 3, "ready": 2, "draft": 1, "rules": 2})
        files = sorted(p.name for p in (self.dir / "stories").iterdir())
        self.assertEqual(files, ["US-01-entrar-como-administrador.md", "US-02-cadastrar-produto.md",
                                 "US-03-buscar-produto-pelo-nome.md"])
        us01 = (self.dir / "stories" / files[0]).read_text(encoding="utf-8")
        self.assertIn("Como **administrador da loja**, quero **entrar com e-mail e senha**", us01)
        self.assertIn("**CA-03 (error, RN-01)**", us01)
        self.assertIn("RN-01 — Bloqueio após tentativas inválidas", us01)
        stories = (self.dir / "STORIES.md").read_text(encoding="utf-8")
        self.assertIn("2/3 ready.", stories)
        self.assertIn("| RN-02 SKU único |", stories)

    def test_roadmap_without_stories_still_passes_with_a_warning(self):
        del self.data["stories"], self.data["rules"]
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 0, out)
        self.assertIn("no stories: run prd-stories", out)
        self.assertFalse((self.dir / "STORIES.md").exists())

    def test_persona_value_and_priority(self):
        s = self.story("US-01")
        s["persona"] = "o sistema"
        s["value"] = s["action"]
        s["priority"] = "high"
        self.assertFails("US-01: persona 'o sistema' is a system", "US-01: value clause repeats the action",
                         "US-01: priority must be one of")

    def test_ready_needs_three_ca_with_happy_and_error_paths(self):
        s = self.story("US-02")
        s["acceptance"] = [ca for ca in s["acceptance"] if ca["path"] == "happy"]
        self.assertFails("US-02: ready needs at least 3 CA (has 1)", "US-02: ready needs an error or edge CA",
                         "US-02: RN-02 is listed but no CA verifies it")

    def test_draft_is_lenient_but_not_empty(self):
        self.story("US-03")["acceptance"] = []
        self.assertFails("US-03: a draft needs at least one CA")

    def test_rules_must_exist_and_ca_rules_must_be_listed(self):
        self.story("US-01")["rules"] = ["RN-09"]
        self.assertFails("US-01: rule RN-09 is not in rules[]", "US-01/CA-03: cites RN-01 but the story does not list it")

    def test_gherkin_structure_and_ids(self):
        s = self.story("US-01")
        s["acceptance"][0]["text"] = "Dado que sou administrador\nEntão entro"
        s["acceptance"][1]["id"] = "CA-01"
        s["acceptance"][2]["path"] = "sad"
        self.assertFails("US-01/CA-01: Gherkin needs when", "US-01/CA-01: duplicate CA id",
                         "US-01/CA-03: path must be one of")

    def test_every_feature_needs_a_story_and_at_most_five(self):
        self.data["stories"] = [s for s in self.data["stories"] if s["id"] != "US-03"]
        self.story("US-02")["depends_on"] = []
        self.assertFails("F01-E02-FT02: feature without user stories")
        base = self.story("US-01")
        for i in range(4, 10):
            self.data["stories"].append(dict(base, id=f"US-{i:02d}", title=f"t{i}", status="draft"))
        self.assertFails("F01-E01-FT01: 7 stories, split the feature")

    def test_unknown_story_dependency(self):
        self.story("US-03")["depends_on"] = ["US-42"]
        self.assertFails("US-03: depends on unknown story US-42")

    def test_warnings_for_vague_terms_generic_persona_and_unused_rules(self):
        s = self.story("US-03")
        s["acceptance"][0]["text"] = "Dado produtos\nQuando busco\nEntão a busca é rápida"
        s["persona"] = "usuário"
        self.data["rules"].append({"id": "RN-03", "title": "x", "rule": "y", "example": "z"})
        self.write()
        code, out = run(self.path)
        self.assertEqual(code, 0, out)
        self.assertIn("vague term 'rápida'", out)
        self.assertIn("generic persona 'usuário'", out)
        self.assertIn("RN-03: business rule not applied by any story", out)

    def test_stale_generated_story_files_are_removed_but_user_files_kept(self):
        self.assertEqual(run(self.path)[0], 0)
        (self.dir / "stories" / "notes.md").write_text("mine", encoding="utf-8")
        self.story("US-03")["title"] = "Buscar por nome ou SKU"
        self.write()
        self.assertEqual(run(self.path)[0], 0)
        names = sorted(p.name for p in (self.dir / "stories").iterdir())
        self.assertIn("US-03-buscar-por-nome-ou-sku.md", names)
        self.assertNotIn("US-03-buscar-produto-pelo-nome.md", names)
        self.assertIn("notes.md", names)


class PrdPluginContractTest(unittest.TestCase):
    def test_manifest_and_commands(self):
        manifest = json.loads((PRD / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.0.0")
        commands = {p.stem for p in (PRD / "commands").glob("*.md")}
        self.assertTrue({"roadmap", "stories", "publish", "create", "refine", "export", "list"} <= commands)
        self.assertEqual({p.stem for p in (PRD / "agents").glob("*.md")}, {"roadmap"})

    def test_roadmap_command_dispatches_the_agent_and_runs_the_checker(self):
        text = (PRD / "skills/prd-roadmap/SKILL.md").read_text(encoding="utf-8")
        self.assertIn('subagent_type: "pwdev-prd:roadmap"', text)
        self.assertIn("scripts/roadmap-check.py", text)
        self.assertIn("Roadmap: APPROVED", text)

    def test_priority_vocabulary_is_moscow_everywhere(self):
        template = (PRD / "templates/PRD.template.md").read_text(encoding="utf-8")
        method = (PRD / "references/interview-method.md").read_text(encoding="utf-8")
        self.assertIn("[must|should|could|wont]", template)
        self.assertNotIn("high|medium|low", template)
        self.assertIn('"priority": "must|should|could|wont"', method)
        self.assertIn("Status: [DRAFT|APPROVED]", template)
        self.assertIn("### Business Rules", template)
        self.assertIn("#### [RN-01]", template)
        self.assertIn('"business_rules"', method)

    def test_publish_delegates_to_pwdev_github(self):
        text = (PRD / "skills/prd-publish/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("github-publish", text)
        self.assertNotIn("gh issue create", text)


if __name__ == "__main__":
    unittest.main()
