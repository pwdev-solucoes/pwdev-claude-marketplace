"""pwdev-video-hyperframes: portable layout on three runtimes and the project builder (build.py).

Run from the repository root:

    python3 -m unittest tests.test_pwdev_video_hyperframes

The builder is tested offline: the `pwdev-media` CLI it calls is replaced by an in-process fake
backed by the real pwdev_media package. Set PWDEV_E2E=1 to also run the pinned HyperFrames
`check` on a generated project (needs network the first time, Node and ffmpeg).
"""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "pwdev-video-hyperframes"
TEMPLATE = PLUGIN / "templates" / "projeto-hf"
sys.path.insert(0, str(ROOT / "plugins" / "pwdev-media" / "engine" / "src"))

from pwdev_media import formats as media_formats  # noqa: E402
from pwdev_media.video import project as media_project  # noqa: E402

SKILLS = {"vhf-setup", "vhf-editar", "vhf-corte", "vhf-plano", "vhf-cenas", "vhf-som", "vhf-revisar", "vhf-variacoes"}
COMMANDS = {"init": "vhf-setup", "status": "vhf-setup", "editar": "vhf-editar", "corte": "vhf-corte",
            "plano": "vhf-plano", "cenas": "vhf-cenas", "som": "vhf-som", "revisar": "vhf-revisar",
            "versoes": "vhf-variacoes"}
FORBIDDEN_IN_SKILLS = ("CLAUDE" + ".md", "AGENTS" + ".md", "${CLAUDE_PLUGIN_ROOT}", "$ARGUMENTS")


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
        self.skills.append((name, path))

    def register_hook(self, name, callback):
        self.hooks[name] = callback


# ---------------------------------------------------------------------------- layout

class PortableLayoutTest(unittest.TestCase):
    def manifest(self) -> dict:
        return json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))

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
        version = self.manifest()["version"]
        for skill in SKILLS:
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                front = re.match(r"^---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(front)
                self.assertIn(f"name: {skill}\n", front.group(1))
                self.assertIn("Use quando", front.group(1))
                self.assertIn("Não use", front.group(1))
                self.assertIn(f"version: {version}", front.group(1))
                for token in FORBIDDEN_IN_SKILLS:
                    self.assertNotIn(token, text)
                self.assertIn("<plugin-root>/references/", text)
                yaml = (PLUGIN / "skills" / skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn(f"${skill}", yaml)

    def test_every_skill_that_edits_follows_the_rules(self):
        for skill in SKILLS - {"vhf-setup"}:
            text = (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("references/regras.md", text)

    def test_referenced_plugin_files_exist(self):
        docs = [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "references").glob("*.md")]
        for md in docs:
            text = md.read_text(encoding="utf-8")
            for rel in set(re.findall(r"<plugin-root>/(\w[\w./-]*?)[`'\"\s)]", text)):
                with self.subTest(file=md.name, path=rel):
                    self.assertTrue((PLUGIN / rel).exists(), rel)

    def test_manifests_agree(self):
        claude = self.manifest()
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        hermes = dict(re.findall(r"^(\w+):\s*(.+)$",
                                 (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"), re.M))
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-video-hyperframes",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        self.assertEqual(codex["skills"], "./skills/")
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        self.assertIn(f"## {claude['version']} ", (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertTrue((PLUGIN / "LICENSE").is_file())

    def test_marketplaces_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in claude["plugins"]].count("pwdev-video-hyperframes"), 1)
        entries = [p for p in codex["plugins"] if p["name"] == "pwdev-video-hyperframes"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-video-hyperframes"})

    def test_hyperframes_version_is_pinned_the_same_everywhere(self):
        build = (TEMPLATE / "build.py").read_text(encoding="utf-8")
        pin = re.search(r'^HYPERFRAMES = "([\d.]+)"', build, re.M).group(1)
        scripts = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertTrue(all(f"hyperframes@{pin} " in cmd for cmd in scripts.values()), scripts)
        for md in [*(PLUGIN / "skills").glob("*/SKILL.md"), *(PLUGIN / "references").glob("*.md")]:
            for found in re.findall(r"hyperframes@([\d.]+)", md.read_text(encoding="utf-8")):
                with self.subTest(file=md.name):
                    self.assertEqual(found, pin)
        self.assertNotRegex(build, r"npx hyperframes(?!@)", "never an unpinned HyperFrames")

    def test_template_ships_licensed_font_and_no_project_instructions(self):
        fonts = TEMPLATE / "assets" / "fonts"
        self.assertTrue((fonts / "Montserrat.ttf").is_file())
        self.assertIn("SIL Open Font License", (fonts / "OFL-Montserrat.txt").read_text(encoding="utf-8"))
        names = {p.name for p in TEMPLATE.rglob("*")}
        self.assertFalse(names & {"CLAUDE" + ".md", "AGENTS" + ".md"})


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_with_a_bounded_first_turn_bootstrap(self):
        self.assertIn("provides_hooks:\n  - pre_llm_call",
                      (PLUGIN / ".hermes-plugin/plugin.yaml").read_text(encoding="utf-8"))
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_vhf_hermes").register(ctx)
        self.assertEqual({name for name, _ in ctx.skills}, SKILLS)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-video-hyperframes:vhf-<name>")', first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))

    def test_missing_skills_fail_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "__init__.py").write_text(
                (PLUGIN / ".hermes-plugin/__init__.py").read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "cannot find the skills"):
                load_module(Path(tmp) / "__init__.py", "pwdev_vhf_hermes_broken").register(FakeHermes())


# ---------------------------------------------------------------------------- builder

def fake_media(proj_dir: Path, durations: dict | None = None):
    """In-process stand-in for `pwdev-media --json ...`, backed by the real package."""

    def media(*args):
        if args[:2] == ("formatos", "mostrar"):
            return media_formats.get(args[2])
        if args[:2] == ("video", "projeto"):
            proj = media_project.load(args[2])
            timeline = Path(proj["edit"]) / "cut_timeline.json"
            duration = json.loads(timeline.read_text(encoding="utf-8"))["duracao"]
            return {"erros": media_project.validate(proj, duration), "duracao_corte": duration}
        if args[:2] == ("video", "sondar"):
            return {"duracao": (durations or {}).get(args[2], 0.6)}
        raise AssertionError(f"chamada inesperada ao pwdev-media: {args}")

    return media


class BuilderBase(unittest.TestCase):
    WORDS = [("Hoje", 0.1, 0.3), ("eu", 0.35, 0.45), ("vou", 0.5, 0.7), ("mostrar", 0.8, 1.1),
             ("três", 1.15, 1.35), ("chip,", 1.4, 1.7), ("Primeira", 2.6, 3.0), ("dica.", 3.05, 3.4)]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.edit = self.tmp / "edit"
        self.edit.mkdir()
        (self.edit / "cut.mp4").write_bytes(b"fake-mp4")
        words = [{"w": w, "inicio": a, "fim": b} for w, a, b in self.WORDS]
        (self.edit / "cut_timeline.json").write_text(json.dumps(
            {"schema": "pwdev-corte/1", "duracao": 4.0, "segmentos": [], "palavras": words}), encoding="utf-8")
        from pwdev_media.video import captions
        (self.edit / "legendas.json").write_text(json.dumps(captions.build(words, 3)), encoding="utf-8")
        self.proj_dir = self.tmp / "proj"
        shutil.copytree(TEMPLATE, self.proj_dir)
        self.build = load_module(self.proj_dir / "build.py", f"vhf_build_{id(self)}")
        self.build.HERE = self.proj_dir
        self.build.media = fake_media(self.proj_dir)
        self.proj = media_project.new("dicas", str(self.edit), "reels-9x16")
        self.save()

    def tearDown(self):
        self._tmp.cleanup()

    def save(self):
        media_project.save(self.proj, self.proj_dir / "projeto.json")

    def run_build(self) -> str:
        self.save()
        self.build.build(json.loads((self.proj_dir / "projeto.json").read_text(encoding="utf-8")))
        return (self.proj_dir / "index.html").read_text(encoding="utf-8")

    def attr(self, page: str, element_id: str, name: str) -> str:
        tag = re.search(rf'<[^>]*\bid="{element_id}"[^>]*>', page).group(0)
        return re.search(rf'\b{name}="([^"]*)"', tag).group(1)


class BuilderTest(BuilderBase):

    def test_whole_video_has_root_video_and_word_timed_captions(self):
        page = self.run_build()
        self.assertIn('data-composition-id="main"', page)
        self.assertIn('data-width="1080" data-height="1920"', page)
        self.assertEqual(self.attr(page, "root", "data-duration"), "4")
        self.assertEqual(self.attr(page, "fala", "src"), "assets/cut.mp4")
        self.assertEqual(self.attr(page, "fala", "data-media-start"), "0")
        self.assertEqual(self.attr(page, "fala", "data-has-audio"), "true")
        self.assertEqual((self.proj_dir / "assets" / "cut.mp4").read_bytes(), b"fake-mp4")
        cues = re.findall(r'class="clip cue"', page)
        self.assertEqual(len(cues), len(json.loads((self.edit / "legendas.json").read_text())["cues"]))
        self.assertEqual(self.attr(page, "c0", "data-start"), "0.1")
        self.assertIn('window.__timelines["main"] = tl;', page)
        self.assertIn("gsap.timeline({ paused: true })", page)
        for banned in ("Math.random", "Date.now", "fetch("):
            self.assertNotIn(banned, page)

    def test_destaque_lights_each_word_at_its_measured_time(self):
        self.proj["legenda"]["estilo"] = "destaque"
        page = self.run_build()
        on = re.findall(r'tl\.set\("#c0w(\d)", \{ backgroundColor: "#FF6A00", color: "#0A0A0A" \}, ([\d.]+)\);', page)
        self.assertEqual(on, [("0", "0.1"), ("1", "0.35"), ("2", "0.5")])
        self.assertIn("text-transform: uppercase", page)

    def test_captions_and_texts_stay_inside_the_safe_zone(self):
        self.proj["textos"] = [{"inicio": 2.6, "fim": 3.4, "texto": "Dica 1", "tipo": "rotulo", "posicao": "topo"}]
        self.proj["legenda"]["y"] = 0.95  # asks for a spot below the safe zone
        page = self.run_build()
        fmt = media_formats.get("reels-9x16")
        sx, sy, sw, sh = media_formats.safe_box(fmt)
        cue_top = int(re.search(r"\.cue \{[^}]*top: (\d+)px", page).group(1))
        self.assertGreaterEqual(cue_top, sy)
        self.assertLess(cue_top, sy + sh)
        self.assertIn(f"left: {sx}px; width: {sw}px", page)
        top = int(re.search(r"\.texto\.topo \{ top: (\d+)px", page).group(1))
        self.assertGreaterEqual(top, sy)
        self.assertIn('class="clip texto rotulo topo"', page)
        self.assertIn("<span>Dica 1</span>", page)

    def test_sample_window_shifts_every_time(self):
        self.proj["amostra"] = {"inicio": 2.5, "fim": 3.5}
        self.proj["textos"] = [{"inicio": 2.6, "fim": 3.4, "texto": "Dica", "tipo": "titulo", "posicao": "centro"},
                               {"inicio": 0.0, "fim": 1.0, "texto": "Fora", "tipo": "titulo", "posicao": "centro"}]
        self.proj["blocos"] = [{"inicio": 0, "fim": 4.0, "tipo": "tela_cheia", "zoom": 1.2}]
        page = self.run_build()
        self.assertEqual(self.attr(page, "root", "data-duration"), "1")
        self.assertEqual(self.attr(page, "fala", "data-media-start"), "2.5")
        self.assertEqual(self.attr(page, "t0", "data-start"), "0.1")
        self.assertNotIn(">Fora<", page, "texts outside the sample are left out")
        self.assertNotIn("Hoje", page, "captions outside the sample are left out")
        self.assertIn('tl.to("#fala", { scale: 1.2', page)

    def test_corrections_keep_punctuation_and_text_is_escaped(self):
        self.proj["correcoes"] = {"chip": "Chip IA"}
        self.proj["textos"] = [{"inicio": 2.6, "fim": 3.4, "texto": "<b>R$97</b> & mais", "tipo": "titulo"}]
        page = self.run_build()
        self.assertIn(">Chip IA,<", page)
        self.assertIn("&lt;b&gt;R$97&lt;/b&gt; &amp; mais", page)

    def test_scenes_and_audio(self):
        (self.proj_dir / "compositions" / "contador.html").write_text("<div></div>", encoding="utf-8")
        sfx, music = self.tmp / "whoosh.mp3", self.tmp / "trilha.mp3"
        sfx.write_bytes(b"sfx")
        music.write_bytes(b"music")
        self.build.media = fake_media(self.proj_dir, {str(sfx): 0.4})
        self.proj["cenas"] = [{"inicio": 1.0, "fim": 2.5, "src": "compositions/contador.html", "sobre_a_pessoa": True}]
        self.proj["audio"] = {"trilha": {"arquivo": str(music), "volume_db": -23},
                              "efeitos": [{"t": 1.0, "arquivo": str(sfx), "volume_db": -12}]}
        page = self.run_build()
        self.assertEqual(self.attr(page, "cena0", "data-composition-src"), "compositions/contador.html")
        self.assertEqual(self.attr(page, "trilha", "data-volume"), f"{10 ** (-23 / 20):.4f}")
        self.assertEqual(self.attr(page, "sfx0", "data-start"), "1")
        self.assertEqual(self.attr(page, "sfx0", "data-duration"), "0.4")
        self.assertTrue((self.proj_dir / "assets" / "audio" / "whoosh.mp3").is_file())

    def test_missing_scene_and_invalid_project_stop_the_build(self):
        self.proj["cenas"] = [{"inicio": 1.0, "fim": 2.0, "src": "compositions/nao-existe.html"}]
        with self.assertRaises(SystemExit) as ctx:
            self.run_build()
        self.assertEqual(ctx.exception.code, 1)
        self.proj["cenas"] = []
        self.proj["textos"] = [{"inicio": 1, "fim": 3, "texto": "A", "tipo": "rotulo"},
                               {"inicio": 2, "fim": 4, "texto": "B", "tipo": "rotulo"}]
        with self.assertRaises(SystemExit):
            self.run_build()
        self.assertFalse((self.proj_dir / "index.html").exists(), "nothing is written for a broken plan")

    def test_gsap_is_local_when_vendored_and_cdn_with_integrity_otherwise(self):
        page = self.run_build()
        self.assertIn(f'integrity="{self.build.GSAP_SRI}" crossorigin="anonymous"', page)
        (self.proj_dir / self.build.GSAP_LOCAL).parent.mkdir(parents=True)
        (self.proj_dir / self.build.GSAP_LOCAL).write_text("// gsap")
        page = self.run_build()
        self.assertIn('<script src="assets/vendor/gsap.min.js"></script>', page)
        self.assertNotIn("cdn.jsdelivr.net", page)

    def test_vendor_gsap_verifies_integrity(self):
        payload = b"window.gsap = {};"

        class Resp:
            def __init__(self, data):
                self.data = data

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return self.data

        sri = "sha384-" + base64.b64encode(hashlib.sha384(payload).digest()).decode()
        with mock.patch("urllib.request.urlopen", return_value=Resp(payload)), \
                mock.patch.object(self.build, "GSAP_SRI", sri):
            self.assertTrue(self.build.vendor_gsap(self.proj_dir))
        self.assertEqual((self.proj_dir / self.build.GSAP_LOCAL).read_bytes(), payload)
        (self.proj_dir / self.build.GSAP_LOCAL).unlink()
        with mock.patch("urllib.request.urlopen", return_value=Resp(b"tampered")):
            with self.assertRaises(SystemExit) as ctx:
                self.build.vendor_gsap(self.proj_dir)
        self.assertEqual(ctx.exception.code, 5)
        self.assertFalse((self.proj_dir / self.build.GSAP_LOCAL).exists())
        with mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
            self.assertFalse(self.build.vendor_gsap(self.proj_dir))

    def test_hf_runs_pinned_with_tools_on_path_and_telemetry_off(self):
        with mock.patch.object(self.build.shutil, "which", return_value="/usr/bin/npx"), \
                mock.patch.object(self.build.subprocess, "run",
                                  return_value=subprocess.CompletedProcess([], 0)) as run:
            self.build.hf(["lint"])
        cmd, kwargs = run.call_args.args[0], run.call_args.kwargs
        self.assertEqual(cmd, ["/usr/bin/npx", "--yes", f"hyperframes@{self.build.HYPERFRAMES}", "lint"])
        self.assertEqual(kwargs["cwd"], self.proj_dir)
        self.assertEqual(kwargs["env"]["HYPERFRAMES_NO_TELEMETRY"], "1")
        self.assertTrue(kwargs["env"]["PATH"].startswith(str(Path.home() / ".pwdev" / "bin")))

    def test_amostra_command_limits_length(self):
        with self.assertRaises(SystemExit):
            self.build.main(["amostra", "1", "45"])


class NovoTest(unittest.TestCase):
    def test_creates_project_next_to_edit_and_refuses_inside_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            edit = tmp / "edit"
            edit.mkdir()
            build = load_module(TEMPLATE / "build.py", "vhf_build_novo")
            calls = []

            def fake_run(cmd, **kwargs):
                calls.append(cmd)
                media_project.save(media_project.new("x", str(edit)), Path(cmd[cmd.index("projeto") + 1]))
                return subprocess.CompletedProcess(cmd, 0, "{}", "")

            with mock.patch.object(build, "media_cli", return_value="/bin/pwdev-media"), \
                    mock.patch.object(build.subprocess, "run", side_effect=fake_run), \
                    mock.patch.object(build, "vendor_gsap", return_value=False):
                build.cmd_novo([str(tmp / "dicas"), "--edit", str(edit), "--formato", "feed-4x5"])
                with self.assertRaises(SystemExit):
                    build.cmd_novo([str(edit / "dentro"), "--edit", str(edit)])
                with self.assertRaises(SystemExit):
                    build.cmd_novo([str(tmp / "dicas"), "--edit", str(edit)])
            proj = tmp / "dicas"
            for rel in ("build.py", "package.json", "hyperframes.json", "assets/fonts/Montserrat.ttf",
                        "compositions/LEIA.md", "renders", "meta.json", "projeto.json"):
                self.assertTrue((proj / rel).exists(), rel)
            self.assertEqual(json.loads((proj / "meta.json").read_text())["id"], "dicas")
            self.assertIn("feed-4x5", calls[0])
            self.assertFalse((edit / "dentro").exists())


@unittest.skipUnless(os.environ.get("PWDEV_E2E") == "1" and shutil.which("npx"), "PWDEV_E2E=1 para rodar o check oficial")
class HyperFramesCheckE2E(BuilderBase):
    def test_official_check_passes(self):
        self.proj["textos"] = [{"inicio": 2.6, "fim": 3.4, "texto": "Dica 1", "tipo": "rotulo"}]
        self.run_build()
        result = subprocess.run(["npx", "--yes", f"hyperframes@{self.build.HYPERFRAMES}", "lint"],
                                cwd=self.proj_dir, capture_output=True, text=True,
                                env={**os.environ, "HYPERFRAMES_NO_TELEMETRY": "1"})
        self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
