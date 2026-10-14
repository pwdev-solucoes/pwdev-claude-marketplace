"""pwdev-media: portable layout on three runtimes and the `pwdev-media` engine (no network).

Run from the repository root:

    python3 -m unittest tests.test_pwdev_media
"""
from __future__ import annotations

import base64
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-media"
sys.path.insert(0, str(PLUGIN / "engine" / "src"))

from pwdev_media import catalog, cli, discovery, formats, generate, http, keys, spend  # noqa: E402
from pwdev_media.providers import elevenlabs, fal, openrouter  # noqa: E402

SKILLS = {"media-setup", "media-catalogo", "media-atualizar", "media-gerar", "media-custo", "media-formatos"}
COMMANDS = {"init": "media-setup", "status": "media-setup", "catalogo": "media-catalogo",
            "atualizar": "media-atualizar", "gerar": "media-gerar", "custo": "media-custo",
            "formatos": "media-formatos"}
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")
KEY_ENV = [v for v in keys.ENV.values()]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeHermes:
    def __init__(self):
        self.skills, self.hooks = [], {}

    def register_skill(self, name, path):
        if not isinstance(path, Path):
            raise TypeError(f"Hermes skill path must be a Path, got {type(path)!r}")
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


# ---------------------------------------------------------------------------- layout

class PortableLayoutTest(unittest.TestCase):
    def test_skills_are_the_single_source_and_commands_wrap_them(self):
        self.assertEqual({p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}, SKILLS)
        self.assertEqual({p.stem for p in (PLUGIN / "commands").glob("*.md")}, set(COMMANDS))
        for command, skill in COMMANDS.items():
            text = (PLUGIN / "commands" / f"{command}.md").read_text(encoding="utf-8")
            with self.subTest(command=command):
                self.assertIn(f"skills/{skill}/SKILL.md", text)
                self.assertIn("Do not add workflow steps here.", text)
                self.assertLess(len(text.splitlines()), 20)

    def test_skill_frontmatter_and_runtime_neutral_bodies(self):
        for skill in SKILLS:
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(front)
                self.assertIn(f"name: {skill}\n", front.group(1))
                self.assertIn("Use quando", front.group(1))
                version = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
                self.assertIn(f"version: {version}", front.group(1))
                for token in FORBIDDEN_IN_SKILLS:
                    self.assertNotIn(token, text)
                self.assertIn("references/runtime.md", text)
                self.assertIn("pwdev-media", text)
                yaml = (PLUGIN / "skills" / skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn(f"${skill}", yaml)

    def test_referenced_plugin_files_exist(self):
        for md in [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "references").glob("*.md")]:
            text = md.read_text(encoding="utf-8")
            for rel in set(re.findall(r"<plugin-root>/(\w[\w./-]*?)[`\"\s)]", text)):
                with self.subTest(file=md.name, path=rel):
                    self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_manifests_agree(self):
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        hermes = dict(re.findall(r"^(\w+):\s*(.+)$",
                                 (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"), re.M))
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-media",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        pyproject = (PLUGIN / "engine" / "pyproject.toml").read_text(encoding="utf-8")
        import pwdev_media
        self.assertEqual(pwdev_media.__version__, claude["version"])
        self.assertIn(f'version = "{claude["version"]}"', pyproject)
        self.assertEqual(codex["skills"], "./skills/")
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        self.assertIn(f"## {claude['version']} ", (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_marketplaces_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in claude["plugins"]].count("pwdev-media"), 1)
        entries = [p for p in codex["plugins"] if p["name"] == "pwdev-media"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-media"})

    def test_exit_codes_are_documented(self):
        doc = (PLUGIN / "references" / "provedores.md").read_text(encoding="utf-8")
        for code in (0, 1, 2, cli.EXIT_CONFIRM, cli.EXIT_BUDGET, cli.EXIT_PROVIDER, cli.EXIT_KEY,
                     cli.EXIT_UNSUPPORTED):
            self.assertIn(f"| {code} |", doc)


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_with_a_bounded_first_turn_bootstrap(self):
        manifest = (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8")
        self.assertIn("provides_hooks:\n  - pre_llm_call", manifest)
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_media_hermes").register(ctx)
        self.assertEqual({name for name, _ in ctx.skills}, SKILLS)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-media:media-<name>")', first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_missing_skills_fail_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "__init__.py").write_text(
                (PLUGIN / ".hermes-plugin/__init__.py").read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load_module(Path(tmp) / "__init__.py", "pwdev_media_hermes_broken").register(FakeHermes())


# ---------------------------------------------------------------------------- engine

class Isolated(unittest.TestCase):
    """Each test gets its own ~/.pwdev/media, no API keys and no Keychain."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        env = {k: v for k, v in os.environ.items() if k not in KEY_ENV}
        env["PWDEV_MEDIA_HOME"] = self.tmp.name
        self.env = mock.patch.dict(os.environ, env, clear=True)
        self.env.start()
        self.keychain = mock.patch.object(keys, "_from_keychain", return_value=None)
        self.keychain.start()

    def tearDown(self):
        self.keychain.stop()
        self.env.stop()
        self.tmp.cleanup()

    def run_cli(self, *argv) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()


class FakeHttp:
    """Replaces http.request: routes (METHOD, url prefix) to canned responses and records calls."""

    def __init__(self, routes: dict):
        self.routes = routes
        self.calls = []

    def __call__(self, method, url, headers=None, payload=None, timeout=120.0):
        self.calls.append((method, url, headers or {}, payload))
        for (m, prefix), value in self.routes.items():
            if m == method and url.startswith(prefix):
                value = value(url, payload) if callable(value) else value
                if isinstance(value, Exception):
                    raise value
                if isinstance(value, bytes):
                    return http.Response(200, {"Content-Type": "application/octet-stream"}, value)
                return http.Response(200, {"Content-Type": "application/json"}, json.dumps(value).encode())
        raise AssertionError(f"chamada inesperada: {method} {url}")


def item(**over) -> dict:
    base = {"id": "x:y", "categoria": "video-gerar", "nome": "Y", "provedor": "x", "via": "agregador",
            "operacao": "video", "modelo": "y",
            "preco": {"valor": 0.1, "unidade": "segundo", "moeda": "USD", "fonte": "https://a", "verificado_em": "2026-10-01"},
            "qualidade": 4, "limites": {}, "audio_nativo": None, "licenca_comercial": "sim",
            "exige_rotulo_ia": True, "status": "ativo", "origem": "curado", "url": "", "notas": ""}
    base.update(over)
    return base


class CatalogTest(Isolated):
    def test_seed_is_valid_and_covers_every_category(self):
        seed = catalog.load_seed()
        self.assertEqual(catalog.validate(seed), [])
        used = {i["categoria"] for i in seed["itens"]}
        self.assertEqual(used, set(seed["categorias"]))
        for i in seed["itens"]:
            if i["preco"]["valor"] is not None and i["via"] != "local":
                self.assertTrue(i["preco"]["fonte"].startswith("https://"), i["id"])

    def test_validate_reports_bad_items(self):
        bad = catalog.load_seed()
        bad["itens"].append(item(id=bad["itens"][0]["id"], via="pirata", qualidade=9,
                                 preco={"valor": 1, "unidade": "segundo", "moeda": "USD", "fonte": "", "verificado_em": None}))
        errors = "\n".join(catalog.validate(bad))
        for expected in ("id repetido", "via deve ser", "qualidade deve ser", "precisa de fonte", "verificado_em"):
            self.assertIn(expected, errors)

    def test_working_copy_is_created_and_topped_up_with_new_seed_items(self):
        first = catalog.load()
        self.assertTrue(Path(self.tmp.name, "catalogo.json").is_file())
        first["itens"] = first["itens"][:3]
        first["itens"][0]["qualidade"] = 1  # curated by the person
        catalog.save(first)
        again = catalog.load()
        self.assertEqual(len(again["itens"]), len(catalog.load_seed()["itens"]))
        self.assertEqual(again["itens"][0]["qualidade"], 1, "a user's curation survives a plugin update")

    def test_merge_keeps_curation_marks_removed_and_reports_price_changes(self):
        base = {"schema": catalog.SCHEMA, "atualizado_em": "2026-09-01",
                "categorias": {"video-gerar": {"nome": "Vídeo"}},
                "itens": [item(id="openrouter:a", qualidade=5, notas="testado", licenca_comercial="sim",
                               fonte_descoberta="openrouter-videos"),
                          item(id="openrouter:b", fonte_descoberta="openrouter-videos"),
                          item(id="curado:c")]}
        found = [
            {**item(id="openrouter:a", qualidade=None, notas="", licenca_comercial="a_verificar"),
             "preco": {"valor": 0.2, "unidade": "segundo", "moeda": "USD", "fonte": "api", "verificado_em": "2026-10-14"}},
            {k: v for k, v in item(id="openrouter:novo").items() if k not in ("qualidade", "licenca_comercial", "notas")},
        ]
        merged, diff = catalog.merge(base, found, "openrouter-videos", "2026-10-14")
        a = catalog.find(merged, "openrouter:a")
        self.assertEqual((a["qualidade"], a["notas"], a["licenca_comercial"]), (5, "testado", "sim"))
        self.assertEqual(a["preco"]["valor"], 0.2)
        self.assertEqual(catalog.find(merged, "openrouter:b")["status"], "removido")
        self.assertEqual(catalog.find(merged, "curado:c")["status"], "ativo", "other sources untouched")
        novo = catalog.find(merged, "openrouter:novo")
        self.assertIsNone(novo["qualidade"])
        self.assertEqual((novo["licenca_comercial"], novo["origem"]), ("a_verificar", "descoberto"))
        self.assertEqual(diff["novos"], ["openrouter:novo"])
        self.assertEqual(diff["removidos"], ["openrouter:b"])
        self.assertEqual(diff["preco"][0]["id"], "openrouter:a")
        self.assertEqual(merged["atualizado_em"], "2026-10-14")
        self.assertEqual(catalog.validate(merged), [])
        back, diff2 = catalog.merge(merged, [item(id="openrouter:b")], "openrouter-videos", "2026-10-15")
        self.assertEqual(catalog.find(back, "openrouter:b")["status"], "ativo")
        self.assertEqual(diff2["voltaram"], ["openrouter:b"])
        md = catalog.diff_markdown([diff], [{"nome": "Runway", "url": "https://r", "verificado_em": None}])
        self.assertIn("Novos (1)", md)
        self.assertIn("+100%", md)
        self.assertIn("Runway: https://r", md)

    def test_recommend_by_goal_license_and_keys(self):
        cat = {"schema": catalog.SCHEMA, "atualizado_em": "2026-10-14", "categorias": {"video-gerar": {"nome": "V"}},
               "itens": [item(id="barato", qualidade=3, preco={**item()["preco"], "valor": 0.02}),
                         item(id="top", qualidade=5, preco={**item()["preco"], "valor": 0.5}),
                         item(id="bom", qualidade=4, preco={**item()["preco"], "valor": 0.08}),
                         item(id="assinatura", qualidade=5, via="assinatura", provedor="runway",
                              preco={**item()["preco"], "valor": 15, "unidade": "mes"}),
                         item(id="sem-licenca", qualidade=5, licenca_comercial="a_verificar",
                              preco={**item()["preco"], "valor": 0.01}),
                         item(id="sem-nota", qualidade=None),
                         item(id="removido", qualidade=5, status="removido")]}
        ids = lambda rows: [r["id"] for r in rows]
        self.assertEqual(ids(catalog.recommend(cat, "video-gerar", "barato"))[:3], ["barato", "bom", "top"])
        self.assertEqual(ids(catalog.recommend(cat, "video-gerar", "maximo"))[:2], ["top", "assinatura"])
        self.assertEqual(ids(catalog.recommend(cat, "video-gerar", "equilibrado"))[0], "bom")
        self.assertNotIn("sem-licenca", ids(catalog.recommend(cat, "video-gerar")))
        self.assertIn("sem-licenca", ids(catalog.recommend(cat, "video-gerar", apenas_comercial=False)))
        self.assertNotIn("sem-nota", ids(catalog.recommend(cat, "video-gerar", apenas_comercial=False)))
        self.assertEqual(ids(catalog.recommend(cat, "video-gerar", provedores={"runway"})), ["assinatura"])
        self.assertEqual(catalog.recommend(cat, "video-gerar", "barato")[-1]["id"], "assinatura",
                         "a subscription price is not comparable with a per-use price")

    def test_age_and_staleness(self):
        cat = {"atualizado_em": "2026-09-01"}
        self.assertEqual(catalog.age_days(cat, "2026-10-14"), 43)
        self.assertTrue(catalog.is_stale(cat, "2026-10-14"))
        self.assertFalse(catalog.is_stale(cat, "2026-09-20"))


class DiscoveryTest(Isolated):
    ROUTES = {
        ("GET", "https://openrouter.ai/api/v1/videos/models"): {"data": [
            {"id": "google/veo-3.1", "name": "Google: Veo 3.1", "supported_durations": [4, 8],
             "supported_resolutions": ["720p"], "supported_aspect_ratios": ["16:9", "9:16"],
             "pricing_skus": {"per-video-second": "0.40"}},
            {"id": "acme/novo-video", "name": "Acme Video", "pricing_skus": {"per-video-second-1080p": "0.30"}}]},
        ("GET", "https://openrouter.ai/api/v1/images/models"): {"data": [
            {"id": "bytedance-seed/seedream-4.5", "name": "Seedream 4.5", "pricing": {"image": "0.04"}}]},
        ("GET", "https://registry.npmjs.org/hyperframes/latest"): {"version": "0.9.0"},
        ("GET", "https://registry.npmjs.org/remotion/latest"): {"version": "4.1.0"},
    }

    def test_update_merges_sources_reports_and_never_overwrites_curation(self):
        fake = FakeHttp(self.ROUTES)
        with mock.patch.object(http, "request", fake):
            result = discovery.update(on="2026-10-14")
        working = catalog.load()
        veo = catalog.find(working, "openrouter:google/veo-3.1")
        self.assertEqual(veo["preco"]["valor"], 0.40)
        self.assertEqual(veo["preco"]["unidade"], "segundo")
        self.assertEqual(veo["qualidade"], 5, "curated quality kept")
        self.assertEqual(veo["nome"], "Veo 3.1 (OpenRouter)", "curated name kept")
        self.assertEqual(veo["limites"]["proporcoes"], ["16:9", "9:16"])
        novo = catalog.find(working, "openrouter:acme/novo-video")
        self.assertEqual((novo["preco"]["valor"], novo["qualidade"]), (0.30, None))
        self.assertEqual(catalog.find(working, "local:hyperframes")["versao_mais_nova"], "0.9.0")
        self.assertEqual(result["falhas"], [])
        report = Path(result["relatorio"]).read_text(encoding="utf-8")
        self.assertIn("openrouter:acme/novo-video", report)
        self.assertIn("hyperframes", report)
        self.assertIn("Conferir à mão", report)
        self.assertTrue(all(c[0] == "GET" for c in fake.calls), "discovery never posts")
        self.assertTrue(all("Authorization" not in c[2] for c in fake.calls), "discovery needs no key")

    def test_second_price_handles_documented_and_live_sku_names(self):
        self.assertEqual(discovery._second_price({"per-video-second": "0.5", "per-video-second-1080p": "0.75"}), 0.5)
        live = {"duration_seconds_with_audio_4k": "0.60", "duration_seconds_without_audio": "0.20",
                "duration_seconds_with_audio": "0.40", "duration_seconds_without_audio_4k": "0.40"}
        self.assertEqual(discovery._second_price(live), 0.40)
        self.assertEqual(discovery._second_price({"seconds_1080p": "0.9", "seconds_720p": "0.3"}), 0.3)
        self.assertIsNone(discovery._second_price({"per-image": "0.04"}))
        self.assertIsNone(discovery._second_price(None))

    def test_a_failing_or_empty_source_removes_nothing(self):
        routes = dict(self.ROUTES)
        routes[("GET", "https://openrouter.ai/api/v1/videos/models")] = http.HttpError(503, "u", "fora do ar")
        routes[("GET", "https://openrouter.ai/api/v1/images/models")] = {"data": []}
        before = {i["id"]: i["status"] for i in catalog.load()["itens"]}
        with mock.patch.object(http, "request", FakeHttp(routes)):
            result = discovery.update(on="2026-10-14")
        after = {i["id"]: i["status"] for i in catalog.load()["itens"]}
        self.assertEqual(before, after)
        self.assertEqual(len(result["falhas"]), 2)

    def test_contract_change_fails_loudly(self):
        routes = dict(self.ROUTES)
        routes[("GET", "https://openrouter.ai/api/v1/videos/models")] = {"models": []}
        with mock.patch.object(http, "request", FakeHttp(routes)):
            result = discovery.update(on="2026-10-14", sources=("openrouter-videos",))
        self.assertIn("campo 'data' ausente", result["falhas"][0])


class SpendAndGenerateTest(Isolated):
    def setUp(self):
        super().setUp()
        working = catalog.load()
        working["itens"].append(item(id="openrouter:teste/video", provedor="openrouter", modelo="teste/video"))
        working["itens"].append(item(id="openrouter:teste/img", provedor="openrouter", categoria="imagem-gerar",
                                     operacao="imagem", modelo="teste/img",
                                     preco={"valor": 0.04, "unidade": "imagem", "moeda": "USD",
                                            "fonte": "https://a", "verificado_em": "2026-10-14"}))
        catalog.save(working)
        os.environ["OPENROUTER_API_KEY"] = "sk-or-teste-segredo"

    def video_routes(self):
        return {
            ("POST", "https://openrouter.ai/api/v1/videos"): {"id": "job1", "status": "pending",
                                                              "polling_url": "https://openrouter.ai/api/v1/videos/job1"},
            ("GET", "https://openrouter.ai/api/v1/videos/job1/content"): b"MP4DATA",
            ("GET", "https://openrouter.ai/api/v1/videos/job1"): {
                "id": "job1", "status": "completed", "usage": {"cost": 0.5},
                "unsigned_urls": ["https://openrouter.ai/api/v1/videos/job1/content?index=0"]},
        }

    def test_paid_call_without_confirmation_estimates_and_calls_nothing(self):
        fake = FakeHttp({})
        with mock.patch.object(http, "request", fake):
            code, out, _ = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--duration", "5")
        self.assertEqual(code, cli.EXIT_CONFIRM)
        self.assertIn("US$ 0.5", out)
        self.assertEqual(fake.calls, [])
        self.assertEqual(spend.entries(), [])

    def test_confirmed_video_is_generated_logged_and_then_reused_from_cache(self):
        fake = FakeHttp(self.video_routes())
        with mock.patch.object(http, "request", fake), mock.patch("time.sleep"):
            code, out, err = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--duration", "5",
                                          "--aspect-ratio", "9:16", "--confirmar")
        self.assertEqual(code, 0, err)
        body = fake.calls[0][3]
        self.assertEqual(body, {"model": "teste/video", "prompt": "x", "duration": 5, "aspect_ratio": "9:16"})
        self.assertEqual(fake.calls[0][2]["Authorization"], "Bearer sk-or-teste-segredo")
        self.assertNotIn("sk-or-teste-segredo", out + err, "a key is never printed")
        ledger = spend.entries()
        self.assertEqual(len(ledger), 1)
        self.assertEqual((ledger[0]["estimativa_usd"], ledger[0]["custo_real_usd"]), (0.5, 0.5))
        self.assertEqual(Path(ledger[0]["arquivos"][0]).read_bytes(), b"MP4DATA")
        self.assertIn("gerado por IA", out)
        again = FakeHttp({})
        with mock.patch.object(http, "request", again):
            code, out, _ = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--duration", "5",
                                        "--aspect-ratio", "9:16", "--confirmar")
        self.assertEqual((code, again.calls), (0, []))
        self.assertIn("cache", out)

    def test_failed_video_job_is_a_provider_error(self):
        routes = self.video_routes()
        routes[("GET", "https://openrouter.ai/api/v1/videos/job1")] = {"id": "job1", "status": "failed", "error": "nsfw"}
        with mock.patch.object(http, "request", FakeHttp(routes)), mock.patch("time.sleep"):
            code, _, err = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--confirmar")
        self.assertEqual(code, cli.EXIT_PROVIDER)
        self.assertIn("nsfw", err)
        self.assertEqual(spend.entries(), [])

    def test_image_contract_and_contract_change(self):
        png = base64.b64encode(b"PNG").decode()
        ok = {("POST", "https://openrouter.ai/api/v1/images"):
              {"data": [{"b64_json": png, "media_type": "image/png"}], "usage": {"cost": 0.04}}}
        with mock.patch.object(http, "request", FakeHttp(ok)):
            result = generate.run("openrouter:teste/img", {"prompt": "p", "aspect_ratio": "1:1"}, confirmar=True)
        self.assertTrue(result["arquivos"][0].endswith(".png"))
        self.assertEqual(Path(result["arquivos"][0]).read_bytes(), b"PNG")
        changed = {("POST", "https://openrouter.ai/api/v1/images"): {"images": []}}
        with mock.patch.object(http, "request", FakeHttp(changed)):
            code, _, err = self.run_cli("gerar", "openrouter:teste/img", "--prompt", "outra", "--confirmar")
        self.assertEqual(code, cli.EXIT_PROVIDER)
        self.assertIn("contrato da API pode ter mudado", err)

    def test_budget_blocks_unless_explicitly_allowed(self):
        self.run_cli("custo", "orcamento", "0.3")
        with mock.patch.object(http, "request", FakeHttp(self.video_routes())), mock.patch("time.sleep"):
            code, _, err = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--duration", "5", "--confirmar")
            self.assertEqual(code, cli.EXIT_BUDGET)
            self.assertIn("orçamento", err)
            code, _, _ = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--duration", "5",
                                      "--confirmar", "--acima-do-orcamento")
        self.assertEqual(code, 0)
        code, out, _ = self.run_cli("custo")
        self.assertIn("Total: US$ 0.5", out)

    def test_missing_key_and_unsupported_items(self):
        del os.environ["OPENROUTER_API_KEY"]
        code, _, err = self.run_cli("gerar", "openrouter:teste/video", "--prompt", "x", "--confirmar")
        self.assertEqual(code, cli.EXIT_KEY)
        self.assertIn("pwdev-media chaves guardar openrouter", err)
        code, _, err = self.run_cli("gerar", "runway:assinatura", "--prompt", "x", "--confirmar")
        self.assertEqual(code, cli.EXIT_UNSUPPORTED)
        code, _, err = self.run_cli("gerar", "local:whisper", "--prompt", "x")
        self.assertEqual(code, cli.EXIT_UNSUPPORTED)
        os.environ["FAL_KEY"] = "k"
        code, _, err = self.run_cli("gerar", "fal:kling", "--prompt", "x", "--confirmar")
        self.assertEqual(code, cli.EXIT_UNSUPPORTED)
        self.assertIn("slug", err)

    def test_estimate_units(self):
        it = catalog.find(catalog.load(), "openrouter:teste/img")
        self.assertEqual(spend.estimate(it, generate.quantity(it, {"n": 3}))["total_usd"], 0.12)
        local = catalog.find(catalog.load(), "local:whisper")
        self.assertEqual(spend.estimate(local, 1), {**spend.estimate(local, 1), "pago": False, "total_usd": 0.0})
        sub = catalog.find(catalog.load(), "runway:assinatura")
        self.assertIsNone(spend.estimate(sub, 1)["total_usd"])


class ProvidersTest(Isolated):
    def test_fal_queue_collects_every_output_url(self):
        os.environ["FAL_KEY"] = "fal-segredo"
        routes = {
            ("POST", "https://queue.fal.run/fal-ai/teste"): {"request_id": "r1",
                                                            "status_url": "https://queue.fal.run/fal-ai/teste/requests/r1/status",
                                                            "response_url": "https://queue.fal.run/fal-ai/teste/requests/r1"},
            ("GET", "https://queue.fal.run/fal-ai/teste/requests/r1/status"): {"status": "COMPLETED"},
            ("GET", "https://queue.fal.run/fal-ai/teste/requests/r1"): {"video": {"url": "https://cdn.fal/v.mp4"}},
            ("GET", "https://cdn.fal/v.mp4"): b"VIDEO",
        }
        fake = FakeHttp(routes)
        it = item(provedor="fal", modelo="fal-ai/teste")
        with tempfile.TemporaryDirectory() as out, mock.patch.object(http, "request", fake):
            result = fal.Fal().generate(it, {"prompt": "p", "entrada": {"duration": "5"}}, Path(out))
            self.assertEqual(Path(result.arquivos[0]).read_bytes(), b"VIDEO")
            self.assertTrue(result.arquivos[0].endswith(".mp4"))
        self.assertEqual(fake.calls[0][3], {"prompt": "p", "duration": "5"})
        self.assertEqual(fake.calls[0][2]["Authorization"], "Key fal-segredo")

    def test_fal_output_names_from_the_response_cannot_escape_the_output_folder(self):
        os.environ["FAL_KEY"] = "k"
        routes = {
            ("POST", "https://queue.fal.run/m"): {"request_id": "r"},
            ("GET", "https://queue.fal.run/m/requests/r/status"): {"status": "COMPLETED"},
            ("GET", "https://queue.fal.run/m/requests/r"): {"../../../fora": {"url": "https://cdn/x"},
                                                            "/etc/passwd": {"url": "https://cdn/y"}},
            ("GET", "https://cdn/"): b"DATA",
        }
        with tempfile.TemporaryDirectory() as parent, mock.patch.object(http, "request", FakeHttp(routes)):
            out = Path(parent) / "saida"
            result = fal.Fal().generate(item(provedor="fal", modelo="m"), {"prompt": "p"}, out)
            for path in result.arquivos:
                self.assertEqual(Path(path).resolve().parent, out.resolve())
            self.assertEqual(sorted(p.name for p in Path(parent).iterdir()), ["saida"])

    def test_fal_error_and_empty_result(self):
        os.environ["FAL_KEY"] = "k"
        base = {("POST", "https://queue.fal.run/m"): {"request_id": "r"}}
        failing = {**base, ("GET", "https://queue.fal.run/m/requests/r/status"):
                   {"status": "COMPLETED", "error": "bad prompt", "error_type": "validation"}}
        with tempfile.TemporaryDirectory() as out, mock.patch.object(http, "request", FakeHttp(failing)):
            with self.assertRaisesRegex(RuntimeError, "bad prompt"):
                fal.Fal().generate(item(provedor="fal", modelo="m"), {"prompt": "p"}, Path(out))
        empty = {**base, ("GET", "https://queue.fal.run/m/requests/r/status"): {"status": "COMPLETED"},
                 ("GET", "https://queue.fal.run/m/requests/r"): {"seed": 1}}
        with tempfile.TemporaryDirectory() as out, mock.patch.object(http, "request", FakeHttp(empty)):
            with self.assertRaises(http.ContractError):
                fal.Fal().generate(item(provedor="fal", modelo="m"), {"prompt": "p"}, Path(out))

    def test_elevenlabs_music_sfx_and_tts(self):
        os.environ["ELEVENLABS_API_KEY"] = "el-segredo"
        fake = FakeHttp({("POST", "https://api.elevenlabs.io/v1/"): b"ID3audio"})
        p = elevenlabs.ElevenLabs()
        with tempfile.TemporaryDirectory() as out, mock.patch.object(http, "request", fake):
            music = p.generate(item(provedor="elevenlabs", operacao="musica", modelo="music_v1"),
                               {"prompt": "upbeat", "duracao": 30}, Path(out))
            p.generate(item(provedor="elevenlabs", operacao="sfx", modelo="eleven_text_to_sound_v2"),
                       {"prompt": "whoosh", "duracao": 1.5}, Path(out))
            p.generate(item(provedor="elevenlabs", operacao="tts", modelo="eleven_multilingual_v2"),
                       {"prompt": "Olá", "voz": "V1"}, Path(out))
            self.assertEqual(Path(music.arquivos[0]).read_bytes(), b"ID3audio")
            with self.assertRaisesRegex(Exception, "--voz"):
                p.generate(item(provedor="elevenlabs", operacao="tts", modelo="m"), {"prompt": "x"}, Path(out))
        urls = [c[1] for c in fake.calls]
        self.assertEqual(urls, ["https://api.elevenlabs.io/v1/music", "https://api.elevenlabs.io/v1/sound-generation",
                                "https://api.elevenlabs.io/v1/text-to-speech/V1"])
        self.assertEqual(fake.calls[0][3]["music_length_ms"], 30000)
        self.assertEqual(fake.calls[1][3]["duration_seconds"], 1.5)
        self.assertEqual(fake.calls[0][2]["xi-api-key"], "el-segredo")

    def test_unsupported_operation(self):
        os.environ["OPENROUTER_API_KEY"] = "k"
        with tempfile.TemporaryDirectory() as out:
            with self.assertRaisesRegex(Exception, "não faz 'musica'"):
                openrouter.OpenRouter().generate(item(operacao="musica"), {"prompt": "x"}, Path(out))


class KeysTest(Isolated):
    def test_env_wins_over_keychain_and_status_never_shows_values(self):
        with mock.patch.object(keys, "_from_keychain", return_value="do-keychain"):
            self.assertEqual(keys.lookup("fal"), ("do-keychain", "keychain"))
            os.environ["FAL_KEY"] = "da-env"
            self.assertEqual(keys.lookup("fal"), ("da-env", "env"))
            code, out, _ = self.run_cli("--json", "status")
        self.assertEqual(code, 0)
        self.assertNotIn("da-env", out)
        self.assertNotIn("do-keychain", out)
        rows = {r["provedor"]: r["origem"] for r in json.loads(out)["chaves"]}
        self.assertEqual(rows["fal"], "env")

    def test_store_never_puts_the_secret_in_process_arguments(self):
        with mock.patch.object(keys, "_keychain_available", return_value=True), \
                mock.patch.object(keys.subprocess, "run") as run:
            keys.store("openrouter", "sk-segredo")
        argv = run.call_args.args[0]
        self.assertNotIn("sk-segredo", " ".join(argv))
        self.assertEqual(argv[-1], "-w")
        self.assertEqual(run.call_args.kwargs["input"], "sk-segredo\nsk-segredo\n")

    def test_unknown_provider_is_refused(self):
        with self.assertRaises(ValueError):
            keys.store("inexistente", "x")


class FormatsTest(Isolated):
    def test_every_format_has_a_sane_safe_zone(self):
        for fmt in formats.load():
            with self.subTest(fmt=fmt["id"]):
                x, y, w, h = formats.safe_box(fmt)
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                self.assertLessEqual(x + w, fmt["largura"])
                self.assertLessEqual(y + h, fmt["altura"])
                self.assertTrue(fmt["fonte"] and fmt["verificado_em"])

    def test_check_box_reports_sides_and_cli_exit_codes(self):
        fmt = formats.get("reels-9x16")
        x, y, w, h = formats.safe_box(fmt)
        self.assertEqual(formats.check_box(fmt, (x, y, w, h)), [])
        problems = formats.check_box(fmt, (x - 10, y, w, h + 50))
        self.assertTrue(any("esquerda" in p for p in problems))
        self.assertTrue(any("base" in p for p in problems))
        self.assertEqual(self.run_cli("formatos", "conferir", "reels-9x16", "--caixa", f"{x},{y},{w},{h}")[0], 0)
        self.assertEqual(self.run_cli("formatos", "conferir", "reels-9x16", "--caixa", "0,0,10,10")[0], 1)
        self.assertEqual(self.run_cli("formatos", "mostrar", "nao-existe")[0], 2)

    def test_main_social_formats_exist(self):
        ids = {f["id"] for f in formats.load()}
        self.assertTrue({"reels-9x16", "tiktok-9x16", "feed-4x5", "feed-1x1", "youtube-16x9", "link-1.91x1"} <= ids)


class CliTest(Isolated):
    def test_usage_errors_and_catalog_commands(self):
        self.assertEqual(self.run_cli("catalogo", "recomendar")[0], 2)
        self.assertEqual(self.run_cli("catalogo", "mostrar")[0], 2)
        self.assertEqual(self.run_cli("catalogo", "mostrar", "nao:existe")[0], 2)
        code, out, _ = self.run_cli("catalogo", "recomendar", "--categoria", "audio-trilha")
        self.assertEqual(code, 0)
        self.assertIn("ElevenLabs Music", out)
        self.assertNotIn("MusicGen", out, "non-commercial license is not recommended")
        self.assertEqual(self.run_cli("catalogo", "validar")[0], 0)
        code, out, _ = self.run_cli("--json", "catalogo", "listar", "--categoria", "motor-render")
        self.assertEqual({i["id"] for i in json.loads(out)},
                         {"local:hyperframes", "local:remotion", "local:ffmpeg"})

    def test_schedule_plan_is_printed_not_installed(self):
        code, out, _ = self.run_cli("catalogo", "agendar")
        self.assertEqual(code, 0)
        self.assertIn("<string>catalogo</string><string>atualizar</string>", out)
        self.assertIn("--instalar", out)


if __name__ == "__main__":
    unittest.main()
