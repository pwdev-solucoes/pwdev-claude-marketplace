import json
import tempfile
import unittest
from pathlib import Path
import sys
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/sdd-composy/scripts"))
import sdd_language
import sdd_localization

INIT = ROOT / "plugins/sdd-composy/scripts/sdd_init.py"


def load_init():
    spec = importlib.util.spec_from_file_location("sdd_init_language_test", INIT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LanguageContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_without_choice_returns_choices_without_writing(self):
        self.assertEqual(sdd_language.resolve_language(self.root, init=True),
                         {"choices": ["pt-BR", "en-US"]})
        self.assertFalse((self.root / ".planning").exists())

    def test_valid_selection_persists_and_is_reused(self):
        self.assertEqual(sdd_language.persist_language(self.root, "pt-BR")["language"], "pt-BR")
        self.assertEqual(sdd_language.resolve_language(self.root), {"language": "pt-BR", "source": "persisted"})

    def test_invalid_selection_does_not_mutate(self):
        sdd_language.persist_language(self.root, "en-US")
        before = (self.root / ".planning/sdd-composy/config.json").read_bytes()
        result = sdd_language.resolve_language(self.root, "fr-FR", init=True)
        self.assertEqual(result["status"], "invalid_language")
        self.assertEqual(before, (self.root / ".planning/sdd-composy/config.json").read_bytes())

    def test_downstream_never_prompts_before_init(self):
        self.assertEqual(sdd_language.resolve_language(self.root), sdd_language.NOT_INITIALIZED)

    def test_explicit_override_is_read_only_for_consumers(self):
        sdd_language.persist_language(self.root, "pt-BR")
        result = sdd_language.resolve_language(self.root, "en-US")
        self.assertEqual(result["language"], "pt-BR")
        config = json.loads((self.root / ".planning/sdd-composy/config.json").read_text())
        self.assertEqual(config["language"], "pt-BR")

    def test_malformed_config_is_rejected_without_overwrite(self):
        target = sdd_language.preference_path(self.root)
        target.parent.mkdir(parents=True)
        target.write_text('{broken')
        with self.assertRaises(ValueError):
            sdd_language.persist_language(self.root, "pt-BR")
        self.assertEqual(target.read_text(), '{broken')

    def test_symlink_parent_is_rejected_on_read(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / '.planning').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                sdd_language.resolve_language(self.root)


class InitLanguageIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.init = load_init()
        self.templates = ROOT / "plugins/sdd-composy/templates"

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_without_language_returns_prompt_and_writes_no_artifacts(self):
        result = self.init.run_plan(self.root, "agent:test", self.templates, None)
        self.assertEqual(result, {"choices": ["pt-BR", "en-US"]})
        self.assertFalse((self.root / ".planning").exists())
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_explicit_language_persists_and_plan_records_it(self):
        result = self.init.run_plan(self.root, "agent:test", self.templates, "pt-BR")
        self.assertEqual(result["language"], "pt-BR")
        self.assertEqual(result["language_source"], "explicit")
        self.assertFalse((self.root / ".planning").exists())
        self.init.apply(self.root, result, self.templates)
        self.assertEqual(json.loads((self.root / ".planning/sdd-composy/config.json").read_text())["language"], "pt-BR")
        self.assertIn('Documentos do projeto', (self.root / 'tasks/index.md').read_text())

    def test_invalid_language_does_not_write_or_generate(self):
        result = self.init.run_plan(self.root, "agent:test", self.templates, "fr-FR")
        self.assertEqual(result["status"], "invalid_language")
        self.assertFalse((self.root / ".planning").exists())
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_persisted_language_is_reused_without_prompt(self):
        plan = self.init.run_plan(self.root, "agent:test", self.templates, "en-US")
        self.init.apply(self.root, plan, self.templates)
        result = self.init.run_plan(self.root, "agent:test", self.templates, None)
        self.assertEqual(result["language"], "en-US")
        self.assertEqual(result["language_source"], "persisted")

    def test_governance_renderer_localizes_static_blocks_only(self):
        dynamic = "Projeto do Usuário / TASK-777 / Não traduza esta evidência"
        source = {
            "AGENTS.md": "# " + dynamic + " — SDD Composy Governance\n\n## Context\n\n"
                         "- Stack summary: " + dynamic + "\n",
            "CLAUDE.md": "# Claude Code compatibility\n\nThe generated contract was produced for `"
                         + dynamic + "` at `2026-09-09T00:00:00+00:00`.\n",
            ".agents/rules/testing.md": "# Testing rule\n\n## Responsibility\n",
        }
        rendered = sdd_localization.render_governance(source, "pt-BR")
        self.assertIn(dynamic, rendered["AGENTS.md"])
        self.assertIn(dynamic, rendered["CLAUDE.md"])
        self.assertIn("## Contexto", rendered["AGENTS.md"])
        self.assertIn("# Compatibilidade com Claude Code", rendered["CLAUDE.md"])
        self.assertIn("# Regra de testes", rendered[".agents/rules/testing.md"])
        self.assertEqual(sdd_localization.render_governance(source, "en-US"), source)

    def test_template_localization_happens_before_dynamic_values_are_inserted(self):
        dynamic = "Never read .env / TASK-777 / ## Context"
        rendered = self.init._template_contents(
            self.templates,
            {
                "PROJECT_NAME": dynamic,
                "SOURCE_COMMIT": "TASK-777",
                "GENERATED_AT": "2026-09-09T00:00:00+00:00",
                "ACTOR_ID": "human:test",
                "STACK_SUMMARY": dynamic,
                "COMMANDS": dynamic,
            },
            "pt-BR",
        )
        self.assertIn(dynamic, rendered["AGENTS.md"])
        self.assertIn("Resumo da stack: " + dynamic, rendered["AGENTS.md"])

    def test_pt_br_init_localizes_all_governance_documents(self):
        plan = self.init.run_plan(self.root, "agent:test", self.templates, "pt-BR")
        self.init.apply(self.root, plan, self.templates)
        expected = {
            "AGENTS.md": "## Contexto",
            "CLAUDE.md": "# Compatibilidade com Claude Code",
            ".agents/rules/00-sdd-composy.md": "## Descoberta e precedência",
            ".agents/rules/architecture.md": "# Regra de arquitetura",
            ".agents/rules/testing.md": "# Regra de testes",
            ".agents/rules/workflow.md": "# Regra de fluxo de trabalho",
        }
        for relative, marker in expected.items():
            self.assertIn(marker, (self.root / relative).read_text(), relative)


class LanguageRoutingDocumentationTests(unittest.TestCase):
    def setUp(self):
        self.plugin = ROOT / "plugins/sdd-composy"
        self.workflow = (self.plugin / "references/workflow.md").read_text()
        self.readme = (self.plugin / "README.md").read_text()
        self.readme_pt = (self.plugin / "README.pt-BR.md").read_text()

    def test_workflow_documents_init_only_prompt_and_downstream_routing(self):
        for text in (self.workflow, self.readme, self.readme_pt):
            self.assertIn("pt-BR", text)
            self.assertIn("en-US", text)
            self.assertIn("init", text.lower())
            self.assertIn("not_initialized", text)
            self.assertIn("run_init", text)
            self.assertTrue("language" in text.lower() or "idioma" in text.lower())

    def test_workflow_documents_localized_human_artifacts_and_english_machine_contract(self):
        for text in (self.workflow, self.readme, self.readme_pt):
            self.assertTrue("human" in text.lower() or "humano" in text.lower())
            self.assertTrue("machine" in text.lower() or "máquina" in text.lower())
            self.assertTrue("IDs" in text or "ids" in text.lower())
            self.assertIn("schemas", text)
            self.assertTrue("filenames" in text or "nomes de arquivos" in text)

    def test_bilingual_readmes_describe_same_language_contract(self):
        for text in (self.readme, self.readme_pt):
            self.assertIn("references", text)
            self.assertIn("OKF", text)
            self.assertIn("Claude Code", text)
            self.assertIn("Codex", text)
            self.assertIn("QUICK", text)
            self.assertIn("LOOP", text)
            self.assertIn("FLEET", text)

class GeneratedLanguageTests(unittest.TestCase):
    def test_map_requires_init_and_renders_persisted_language(self):
        import sdd_map
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = sdd_map.build_map(root)
            self.assertEqual(sdd_map.write_map(root, data), sdd_language.NOT_INITIALIZED)
            self.assertFalse((root / '.planning').exists())
            for language, heading in [('pt-BR', 'Contexto do projeto'), ('en-US', 'Project context')]:
                sdd_language.persist_language(root, language)
                sdd_map.write_map(root, data)
                self.assertIn(heading, (root / '.planning/sdd-composy/context/project.md').read_text())

    def test_qa_report_uses_workspace_language(self):
        import sdd_qa
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(sdd_qa.assess({}, allowed_root=root), sdd_language.NOT_INITIALIZED)
            sdd_language.persist_language(root, 'pt-BR')
            result = sdd_qa.assess({}, allowed_root=root, report_path='qa.md')
            self.assertIn('qualidade', result['report']['title'])
            self.assertEqual(result['reason'], 'invalid_state')


if __name__ == "__main__":
    unittest.main()
