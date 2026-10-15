"""pwdev-video-tutorial: portable layout and scripts/tutorial.py (code scan, coverage, validators,
recording script, narration, recording, assembly, checks, text tutorial).

Run from the repository root:

    python3 -m unittest tests.test_pwdev_video_tutorial

Assembly tests need ffmpeg (`pwdev-media video ffmpeg --instalar`). No browser, network or voice
model is used unless PWDEV_E2E=1 (then a real recording of a local page runs through playwright-cli).
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-video-tutorial"
ENGINE_SRC = ROOT / "plugins" / "pwdev-media" / "engine" / "src"
SKILLS = {"vtut-setup", "vtut-explorar", "vtut-roadmap", "vtut-roteiro", "vtut-narrar", "vtut-gravar",
          "vtut-montar", "vtut-revisar"}
COMMANDS = {"init": "vtut-setup", "status": "vtut-setup", "explorar": "vtut-explorar", "roadmap": "vtut-roadmap",
            "roteiro": "vtut-roteiro", "narrar": "vtut-narrar", "gravar": "vtut-gravar", "montar": "vtut-montar",
            "revisar": "vtut-revisar"}
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tut = load_module(PLUGIN / "scripts" / "tutorial.py", "pwdev_tutorial_script")
FFMPEG = Path.home() / ".pwdev" / "bin" / "ffmpeg"
HAS_FFMPEG = FFMPEG.is_file() or bool(shutil.which("ffmpeg"))
needs_ffmpeg = unittest.skipUnless(HAS_FFMPEG, "ffmpeg não instalado")


def write(root: Path, files: dict) -> Path:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    return root


class FakeHermes:
    def __init__(self):
        self.skills, self.hooks = [], {}

    def register_skill(self, name, path):
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


def script(**over) -> dict:
    base = {"schema": tut.ROTEIRO_SCHEMA, "video_id": "V01", "titulo": "Cadastrar cliente",
            "url_base": "https://homolog.exemplo.com", "viewport": {"largura": 1280, "altura": 720},
            "mascarar": ["#email"],
            "cenas": [
                {"id": "C01", "capitulo": {"titulo": "Cadastro", "descricao": "Passo a passo"},
                 "narracao": "Vamos cadastrar um cliente.", "acoes": [{"tipo": "ir", "valor": "/clientes"}]},
                {"id": "C02", "narracao": "Clique em Novo cliente.",
                 "acoes": [{"tipo": "clicar", "alvo": "getByRole('button', { name: 'Novo cliente' })", "nota": "Aqui"}]},
                {"id": "C03", "narracao": "Preencha o e-mail.",
                 "acoes": [{"tipo": "preencher", "alvo": "#email", "valor": "maria@exemplo.com"}]}]}
    base.update(over)
    return base


# ---------------------------------------------------------------------------- layout

class PortableLayoutTest(unittest.TestCase):
    def test_skills_commands_and_bodies(self):
        self.assertEqual({p.parent.name for p in (PLUGIN / "skills").glob("*/SKILL.md")}, SKILLS)
        self.assertEqual({p.stem for p in (PLUGIN / "commands").glob("*.md")}, set(COMMANDS))
        for command, skill in COMMANDS.items():
            text = (PLUGIN / "commands" / f"{command}.md").read_text(encoding="utf-8")
            self.assertIn(f"skills/{skill}/SKILL.md", text)
            self.assertIn("Do not add workflow steps here.", text)
            self.assertLess(len(text.splitlines()), 20)
        version = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())["version"]
        for skill in SKILLS:
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1)
                self.assertIn(f"name: {skill}\n", front)
                self.assertIn("Use quando", front)
                self.assertIn("Não use", front)
                self.assertIn(f"version: {version}", front)
                for token in FORBIDDEN_IN_SKILLS:
                    self.assertNotIn(token, text)
                self.assertIn("<plugin-root>/references/", text)
                self.assertTrue((PLUGIN / "skills" / skill / "agents" / "openai.yaml").is_file())
                for rel in set(re.findall(r"<plugin-root>/(\w[\w./-]*?)[`'\"\s)]", text)):
                    self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_safety_rules_are_in_the_skills(self):
        explore = (PLUGIN / "skills" / "vtut-explorar" / "SKILL.md").read_text(encoding="utf-8")
        guide = (PLUGIN / "references" / "exploracao.md").read_text(encoding="utf-8")
        self.assertIn("state-save", guide)
        self.assertIn("senha nunca passa", guide)
        self.assertIn(".gitignore", explore)
        self.assertIn("borrar depois não é aceitável", (PLUGIN / "skills" / "vtut-revisar" / "SKILL.md").read_text())

    def test_manifests_marketplaces_and_templates(self):
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        hermes = dict(re.findall(r"^(\w+):\s*(.+)$", (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(), re.M))
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-video-tutorial",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field))
        self.assertIn(f"## {claude['version']} ", (PLUGIN / "CHANGELOG.md").read_text())
        mk = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual([p["name"] for p in mk["plugins"]].count("pwdev-video-tutorial"), 1)
        cx = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual([p["source"] for p in cx["plugins"] if p["name"] == "pwdev-video-tutorial"],
                         [{"source": "local", "path": "./plugins/pwdev-video-tutorial"}])
        self.assertEqual(tut.validate_roadmap(json.loads((PLUGIN / "templates/roadmap.exemplo.json").read_text()))[0], [])
        self.assertEqual(tut.validate_script(json.loads((PLUGIN / "templates/roteiro.exemplo.json").read_text())), [])

    def test_hermes_adapter(self):
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_vtut_hermes").register(ctx)
        self.assertEqual({n for n, _ in ctx.skills}, SKILLS)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)["context"]
        self.assertLess(len(first), 4000)
        self.assertIn('skill_view("pwdev-video-tutorial:vtut-<name>")', first)
        self.assertIn("password", first)


# ---------------------------------------------------------------------------- code scan and coverage

class CodeScanTest(unittest.TestCase):
    def test_laravel_next_react_django_and_ignored_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write(Path(tmp), {
                "routes/web.php": """
                    Route::get('/clientes', [ClienteController::class, 'index'])->name('clientes.index');
                    Route::post('/clientes', [ClienteController::class, 'store'])->middleware('can:clientes.criar');
                    Route::resource('pedidos', PedidoController::class);
                """,
                "resources/views/clientes/form.blade.php": """
                    @can('clientes.criar')
                    <a href="{{ route('clientes.index') }}">Clientes</a>
                    <label>Nome completo</label><input name="nome"><input name="email"><input name="cpf">
                    <button type="submit">Salvar cliente</button>
                    @endcan
                """,
                "app/(painel)/relatorios/[id]/page.tsx": "export default function P() { return null }\n",
                "app/page.tsx": "export default function Home() { return null }\n",
                "src/components/Menu.tsx": '<Link href="/relatorios">Relatórios</Link>\n',
                "src/App.tsx": '<Route path="/pedidos/:id" element={<Pedido />} />\n',
                "loja/urls.py": "urlpatterns = [path('produtos/<int:pk>/', views.produto)]\n",
                "node_modules/lib/routes/web.php": "Route::get('/nao-deve-aparecer', fn() => 1);\n",
            })
            doc = tut.scan_code(root)
        paths = {(r["framework"], r["caminho"]) for r in doc["rotas"]}
        for expected in [("laravel", "/clientes"), ("laravel", "pedidos"), ("nextjs-app", "/relatorios/[id]"),
                         ("nextjs-app", "/"), ("react-router", "/pedidos/:id"), ("django", "/produtos/<int:pk>/")]:
            self.assertIn(expected, paths)
        self.assertNotIn("/nao-deve-aparecer", {p for _, p in paths})
        named = next(r for r in doc["rotas"] if r["caminho"] == "/clientes" and r["metodo"] == "GET")
        self.assertEqual((named["nome"], named["arquivo"], named["linha"]), ("clientes.index", "routes/web.php", 1))
        self.assertIn({"texto": "Relatórios", "destino": "/relatorios", "arquivo": "src/components/Menu.tsx"}, doc["links_menu"])
        self.assertIn("Clientes", {l["texto"] for l in doc["links_menu"]})
        form = next(f for f in doc["formularios"] if f["arquivo"].endswith("form.blade.php"))
        self.assertEqual(form["campos"], ["cpf", "email", "nome"])
        self.assertEqual(form["dados_pessoais"], ["cpf", "email"])
        self.assertIn("Salvar cliente", form["botoes"])
        self.assertTrue({"clientes.criar"} <= set(doc["permissoes"]))
        self.assertEqual(doc["schema"], tut.CODIGO_SCHEMA)

    def test_coverage_matches_parameters(self):
        code = {"rotas": [{"metodo": "GET", "caminho": "/clientes"}, {"metodo": "GET", "caminho": "/clientes/{id}"},
                          {"metodo": "GET", "caminho": "/relatorios/[id]"}, {"metodo": "POST", "caminho": "/clientes"},
                          {"metodo": "GET", "caminho": "/api/clientes"}]}
        result = tut.coverage(code, ["https://app.x/clientes?page=2", "https://app.x/clientes/42", "/ajuda"])
        self.assertEqual(result["alcancadas"], ["/clientes", "/clientes/{id}"])
        self.assertEqual(result["nao_alcancadas"], ["/relatorios/[id]"])
        self.assertEqual(result["visitadas_fora_do_codigo"], ["/ajuda"])


# ---------------------------------------------------------------------------- validators

class ValidatorTest(unittest.TestCase):
    def roadmap(self, videos):
        return {"schema": tut.ROADMAP_SCHEMA, "series": [{"id": "s"}], "videos": videos}

    def video(self, vid, prio="P1", deps=()):
        return {"id": vid, "titulo": vid, "serie": "s", "objetivo": "o", "publico": "p", "prioridade": prio,
                "tipo": "tutorial", "duracao_alvo_s": 60, "formato": "youtube-16x9", "prerequisitos": list(deps)}

    def test_roadmap_order_by_prerequisites_then_priority(self):
        errors, order = tut.validate_roadmap(self.roadmap([
            self.video("V03", "P1", ["V02"]), self.video("V02", "P2"), self.video("V01", "P3"), self.video("V04", "P1")]))
        self.assertEqual(errors, [])
        self.assertEqual(order, ["V04", "V02", "V03", "V01"])

    def test_roadmap_errors_and_cycles(self):
        errors, _ = tut.validate_roadmap(self.roadmap([self.video("A", deps=["B"]), self.video("B", deps=["A"]),
                                                       {**self.video("C", "P9"), "serie": "x", "tipo": "filme"},
                                                       self.video("D", deps=["Z"])]))
        text = " | ".join(errors)
        for expected in ("ciclo", "P1, P2 ou P3", "série 'x'", "tipo tutorial", "'Z' não existe"):
            self.assertIn(expected, text)

    def test_script_rules(self):
        self.assertEqual(tut.validate_script(script()), [])
        bad = script(url_base="javascript:alert(1)", mascarar=["#a { color: red }"])
        bad["cenas"][1]["acoes"][0]["alvo"] = "getByRole('button'); process.exit()"
        bad["cenas"][2]["acoes"].append({"tipo": "preencher", "alvo": "getByLabel('CPF')", "valor": "123"})
        bad["cenas"][0]["narracao"] = " "
        bad["cenas"][0]["acoes"].append({"tipo": "voar"})
        errors = " | ".join(tut.validate_script(bad))
        for expected in ("url_base", "mascarar", "localizador inválido", "dado pessoal", "narração vazia", "tipo deve ser"):
            self.assertIn(expected, errors)

    def test_masked_or_fictitious_personal_data_is_accepted(self):
        ok = script()
        ok["cenas"][2]["acoes"].append({"tipo": "preencher", "alvo": "getByLabel('CPF')", "valor": "000", "ficticio": True})
        self.assertEqual(tut.validate_script(ok), [])

    def test_locators(self):
        for alvo, valid in (("getByLabel('Nome')", True), ("getByTestId(\"salvar\")", True), ("#salvar", True),
                            ("getByRole('a'); x", False), ("getByRole(`x`)", False), ("evaluate('x')", True),
                            ("", False)):
            with self.subTest(alvo=alvo):
                self.assertEqual(tut.validate_locator(alvo) is None, valid)


# ---------------------------------------------------------------------------- recording script

class RecordingScriptTest(unittest.TestCase):
    def build(self, narration=None):
        with tempfile.TemporaryDirectory() as tmp:
            return tut.build_js(script(), Path(tmp), narration), tmp

    def test_actions_masks_chapters_and_narration_timing(self):
        narration = {"cenas": [{"id": "C01", "duracao": 2.0}, {"id": "C02", "duracao": 1.5}, {"id": "C03", "duracao": 3.0}]}
        js, tmp = self.build(narration)
        self.assertTrue(js.startswith("async page => {"))
        self.assertIn('page.goto("https://homolog.exemplo.com/clientes")', js)
        self.assertIn("page.getByRole('button', { name: 'Novo cliente' })", js)
        self.assertIn('page.locator("#email")', js)
        self.assertIn('pressSequentially("maria@exemplo.com"', js)
        self.assertIn('#email { filter: blur(8px) !important; }', js)
        self.assertIn("addInitScript", js, "mask survives navigation")
        self.assertIn('showChapter("Cadastro"', js)
        self.assertIn("cena.narracao_inicio + 2.400 - now()", js)
        self.assertIn("cena.narracao_inicio + 3.400 - now()", js)
        self.assertIn(str(Path(tmp).resolve() / "gravacao.webm"), js)
        self.assertIn("page.screencast.stop()", js)

    def test_text_is_escaped(self):
        s = script()
        s["cenas"][2]["acoes"][0]["valor"] = 'a"); await page.close(); ("'
        with tempfile.TemporaryDirectory() as tmp:
            js = tut.build_js(s, Path(tmp), None)
        self.assertIn(json.dumps('a"); await page.close(); ("'), js)
        self.assertNotIn('pressSequentially("a"); await', js)

    @unittest.skipUnless(shutil.which("node"), "node não instalado")
    def test_generated_code_is_valid_javascript(self):
        js, _ = self.build({"cenas": [{"id": "C01", "duracao": 1.0}]})
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "check.js"
            f.write_text(f"const fn = ({js});\n", encoding="utf-8")
            result = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


# ---------------------------------------------------------------------------- narration, recording, assembly

def fake_cli(tmp: Path) -> str:
    """A `pwdev-media` that runs the engine from the repository (no installed tool needed)."""
    shim = tmp / "pwdev-media"
    shim.write_text(f"#!/bin/sh\nPYTHONPATH='{ENGINE_SRC}' exec '{sys.executable}' -m pwdev_media.cli \"$@\"\n")
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
    return str(shim)


class NarrationTest(unittest.TestCase):
    def test_local_voice_calls_pinned_hyperframes_tts_without_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            calls = []

            def run(cmd, **kw):
                calls.append((cmd, kw))
                Path(cmd[cmd.index("-o") + 1]).write_bytes(b"RIFF")
                return subprocess.CompletedProcess(cmd, 0, "{}", "")

            with mock.patch.object(tut, "tts_python", return_value="/venv/python"), \
                    mock.patch.object(tut.shutil, "which", return_value="/usr/bin/npx"), \
                    mock.patch.object(tut.subprocess, "run", side_effect=run), \
                    mock.patch.object(tut, "duration", return_value=2.5):
                result = tut.narrate(script(), folder, "pm_alex", 1.1, None)
            cmd, kw = calls[0]
            self.assertEqual(cmd[:4], ["/usr/bin/npx", "--yes", f"hyperframes@{tut.HYPERFRAMES}", "tts"])
            self.assertIn("pt-br", cmd)
            self.assertEqual(cmd[cmd.index("--voice") + 1], "pm_alex")
            self.assertEqual(kw["env"]["HYPERFRAMES_PYTHON"], "/venv/python")
            self.assertEqual(kw["env"]["HYPERFRAMES_NO_TELEMETRY"], "1")
            self.assertEqual((folder / "narracao" / "C01.txt").read_text(), "Vamos cadastrar um cliente.")
            self.assertEqual([c["duracao"] for c in result["cenas"]], [2.5, 2.5, 2.5])
            self.assertTrue((folder / "narracao.json").is_file())

    @needs_ffmpeg
    def test_imports_the_persons_recordings(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "audios"
            src.mkdir()
            ff = str(FFMPEG if FFMPEG.is_file() else shutil.which("ffmpeg"))
            for n, cid in enumerate(("C01", "C02", "C03"), 1):
                subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=d={n}", str(src / f"{cid}.m4a")], check=True)
            result = tut.narrate(script(), Path(tmp) / "v", "pf_dora", 1.0, str(src))
            self.assertEqual([round(c["duracao"]) for c in result["cenas"]], [1, 2, 3])
            with self.assertRaises(SystemExit):
                (src / "C03.m4a").unlink()
                tut.narrate(script(), Path(tmp) / "v2", "pf_dora", 1.0, str(src))


class RecordTest(unittest.TestCase):
    def test_record_runs_playwright_cli_and_saves_timings(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = {"cenas": [{"id": "C01", "inicio": 0, "narracao_inicio": 1.6, "fim": 4, "acoes": []}], "duracao": 4.0}
            calls = []

            def cli(args, session):
                calls.append(args)
                return "### Result\n" + json.dumps(json.dumps(payload)) if args[0] == "--raw" else "ok"

            with mock.patch.object(tut, "run_cli", side_effect=cli), \
                    mock.patch.object(tut.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
                result = tut.record(script(), folder, "s1", str(folder / "sessao.json"), keep=False)
            self.assertEqual([c[0] for c in calls], ["open", "state-load", "--raw"])
            self.assertTrue(calls[2][2].endswith("gravar.js"))
            doc = json.loads((folder / "cenas.json").read_text())
            self.assertEqual((doc["schema"], doc["duracao"], result["cenas"]), (tut.CENAS_SCHEMA, 4.0, 1))


@needs_ffmpeg
class AssembleTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        ff = str(FFMPEG if FFMPEG.is_file() else shutil.which("ffmpeg"))
        self.folder = self.tmp / "v"
        (self.folder / "narracao").mkdir(parents=True)
        (self.folder / "capturas").mkdir()
        subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1280x720:d=8:r=25", "-c:v", "libvpx",
                        "-b:v", "1M", str(self.folder / "gravacao.webm")], check=True)
        for cid, d in (("C01", 1.5), ("C02", 1.2), ("C03", 1.0)):
            subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", f"sine=f=300:d={d}", "-ar", "24000",
                            str(self.folder / "narracao" / f"{cid}.wav")], check=True)
            (self.folder / "capturas" / f"{cid}.png").write_bytes(b"png")
        narr = {"voz": "pf_dora", "cenas": [{"id": c, "arquivo": str(self.folder / "narracao" / f"{c}.wav"), "duracao": d}
                                            for c, d in (("C01", 1.5), ("C02", 1.2), ("C03", 1.0))]}
        (self.folder / "narracao.json").write_text(json.dumps(narr))
        cenas = {"schema": tut.CENAS_SCHEMA, "video": str(self.folder / "gravacao.webm"), "duracao": 8.0,
                 "viewport": {"largura": 1280, "altura": 720}, "narracao": True, "cenas": [
                     {"id": "C01", "inicio": 0.0, "narracao_inicio": 1.6, "fim": 3.5, "acoes": [{"tipo": "ir", "t": 0.1}]},
                     {"id": "C02", "inicio": 3.5, "narracao_inicio": 3.5, "fim": 5.2,
                      "acoes": [{"tipo": "clicar", "t": 3.9, "box": {"x": 1100, "y": 600, "width": 100, "height": 40}}]},
                     {"id": "C03", "inicio": 5.2, "narracao_inicio": 5.2, "fim": 8.0, "acoes": []}]}
        (self.folder / "cenas.json").write_text(json.dumps(cenas))
        self.shim = fake_cli(self.tmp)
        real_tool = tut.tool
        self.patch = mock.patch.object(tut, "tool", side_effect=lambda n: self.shim if n == "pwdev-media" else real_tool(n))
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self._tmp.cleanup()

    def test_assembly_gives_the_video_plugins_an_edit_folder(self):
        edit = self.tmp / "edit"
        result = tut.assemble(self.folder, edit, "youtube-16x9", script(), transcribe=False)
        probe = subprocess.run([tut.tool("ffprobe"), "-v", "error", "-show_entries", "stream=codec_type,width,height",
                                "-of", "json", str(edit / "cut.mp4")], capture_output=True, text=True)
        streams = json.loads(probe.stdout)["streams"]
        self.assertEqual({s["codec_type"] for s in streams}, {"video", "audio"})
        video = next(s for s in streams if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (1920, 1080))
        self.assertAlmostEqual(result["duracao"], 8.0, delta=0.15)
        timeline = json.loads((edit / "cut_timeline.json").read_text())
        self.assertEqual(timeline["origem_palavras"], "texto")
        first = timeline["palavras"][0]
        self.assertEqual(first["w"], "Vamos")
        self.assertAlmostEqual(first["inicio"], 1.6, delta=0.01, msg="words start with the scene narration")
        self.assertTrue((edit / "legendas.json").is_file(), "captions built by pwdev-media")
        sug = json.loads((self.folder / "sugestoes-projeto.json").read_text())
        zoom = next(b for b in sug["blocos"] if b["zoom"] > 1)
        self.assertEqual(zoom["origem"], "90% 86%", "origin clamped inside the frame")
        self.assertEqual(sug["legenda"]["estilo"], "caixa")
        audio = subprocess.run([tut.tool("ffmpeg"), "-hide_banner", "-i", str(edit / "cut.mp4"), "-t", "1.4", "-af",
                                "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        mean = float(re.search(r"mean_volume: (-?[\d.]+) dB", audio).group(1))
        self.assertLess(mean, -60, "silence before the narration of the first scene")

    def test_checks_and_text_tutorial(self):
        result = tut.check_tutorial(self.folder, script(mascarar=[]))
        self.assertEqual(result["veredito"], "REPROVOU", "e-mail typed without mask or fictitious flag is refused")
        ok = script()
        ok["cenas"][2]["acoes"][0]["ficticio"] = True
        result = tut.check_tutorial(self.folder, ok)
        self.assertEqual((result["veredito"], result["avisos"]), ("PASSOU", []))
        cenas = json.loads((self.folder / "cenas.json").read_text())
        cenas["cenas"][2]["fim"] = 9.5  # 3.3 s of screen after the last words
        (self.folder / "cenas.json").write_text(json.dumps(cenas))
        warnings = tut.check_tutorial(self.folder, ok)["avisos"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("C03: 3.3s de tela sem fala", warnings[0])
        cenas["cenas"][1]["fim"] = 4.0
        (self.folder / "cenas.json").write_text(json.dumps(cenas))
        self.assertTrue(any("passa do fim" in p for p in tut.check_tutorial(self.folder, ok)["problemas"]))
        md = tut.markdown_tutorial(self.folder, ok)
        self.assertIn("# Cadastrar cliente", md)
        self.assertIn("## Cadastro", md)
        self.assertIn("**2.** Clique em Novo cliente.", md)
        self.assertIn("![C03](capturas/C03.png)", md)


# ---------------------------------------------------------------------------- CLI

class CliTest(unittest.TestCase):
    def test_validate_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "r.json", Path(tmp) / "b.json"
            good.write_text(json.dumps(script()))
            bad.write_text(json.dumps(script(url_base="ftp://x")))
            run = lambda f: subprocess.run([sys.executable, str(PLUGIN / "scripts" / "tutorial.py"), "validar", str(f)],
                                           capture_output=True, text=True).returncode
            self.assertEqual((run(good), run(bad)), (0, 1))

    def test_unknown_local_voice(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "r.json"
            f.write_text(json.dumps(script()))
            with self.assertRaises(SystemExit):
                tut.main(["narrar", str(f), "--pasta", tmp, "--voz", "af_heart"])


@unittest.skipUnless(os.environ.get("PWDEV_E2E") == "1" and shutil.which("playwright-cli"), "PWDEV_E2E=1 para gravar de verdade")
class RecordingE2E(unittest.TestCase):
    def test_records_a_local_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "app.html").write_text(
                '<!doctype html><button id="novo" onclick="f.hidden=false">Novo cliente</button>'
                '<form id="f" hidden><label>E-mail <input id="email"></label></form>', encoding="utf-8")
            s = script(url_base=f"file://{tmp}")
            s["cenas"][0]["acoes"] = [{"tipo": "ir", "valor": "app.html"}]
            s["cenas"][2]["acoes"][0]["ficticio"] = True
            result = tut.record(s, tmp / "v", "pwdev-tutorial-e2e", None, keep=False)
            self.assertEqual(result["cenas"], 3)
            self.assertTrue((tmp / "v" / "gravacao.webm").stat().st_size > 1000)
            cenas = json.loads((tmp / "v" / "cenas.json").read_text())
            self.assertIsNotNone(cenas["cenas"][1]["acoes"][0]["box"])


if __name__ == "__main__":
    unittest.main()
