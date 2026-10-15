"""pwdev-video-remotion: portable layout on three runtimes, the project builder (build.py) and
parity with pwdev-video-hyperframes (same projeto.json, same decisions).

Run from the repository root:

    python3 -m unittest tests.test_pwdev_video_remotion

The builder is tested offline with the real pwdev_media package standing in for the CLI. Set
PWDEV_E2E=1 to also install the pinned Remotion packages in a temporary project and run
`build.py checar` (needs network and Node).
"""
from __future__ import annotations

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
PLUGIN = ROOT / "plugins" / "pwdev-video-remotion"
TEMPLATE = PLUGIN / "templates" / "projeto-remotion"
HF_TEMPLATE = ROOT / "plugins" / "pwdev-video-hyperframes" / "templates" / "projeto-hf"
sys.path.insert(0, str(ROOT / "plugins" / "pwdev-media" / "engine" / "src"))

from pwdev_media import formats as media_formats  # noqa: E402
from pwdev_media.video import captions, project as media_project, render_plan  # noqa: E402

SKILLS = {"vrm-setup", "vrm-editar", "vrm-corte", "vrm-plano", "vrm-cenas", "vrm-som", "vrm-revisar", "vrm-variacoes"}
COMMANDS = {"init": "vrm-setup", "status": "vrm-setup", "editar": "vrm-editar", "corte": "vrm-corte",
            "plano": "vrm-plano", "cenas": "vrm-cenas", "som": "vrm-som", "revisar": "vrm-revisar",
            "versoes": "vrm-variacoes"}
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
                self.assertNotIn("vhf-", text, "no leftover HyperFrames skill names")
                self.assertNotRegex(text, r"\bhf (check|snapshot|lint)\b")
                yaml = (PLUGIN / "skills" / skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn(f"${skill}", yaml)

    def test_license_is_checked_before_the_first_project(self):
        for skill in ("vrm-setup", "vrm-editar"):
            self.assertIn("references/licenca.md", (PLUGIN / "skills" / skill / "SKILL.md").read_text(encoding="utf-8"))
        text = (PLUGIN / "references" / "licenca.md").read_text(encoding="utf-8")
        self.assertIn("https://www.remotion.dev/license", text)
        self.assertIn("pwdev-video-hyperframes", text)

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
        self.assertEqual((claude["name"], codex["name"], hermes["name"]), ("pwdev-video-remotion",) * 3)
        self.assertEqual({codex["version"], hermes["version"]}, {claude["version"]})
        self.assertEqual(codex["skills"], "./skills/")
        for field in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
            self.assertTrue(codex["interface"].get(field), field)
        self.assertIn(f"## {claude['version']} ", (PLUGIN / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertTrue((PLUGIN / "LICENSE").is_file())

    def test_marketplaces_list_the_plugin_once(self):
        claude = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual([p["name"] for p in claude["plugins"]].count("pwdev-video-remotion"), 1)
        entries = [p for p in codex["plugins"] if p["name"] == "pwdev-video-remotion"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/pwdev-video-remotion"})

    def test_versions_are_pinned_exactly(self):
        pkg = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))
        deps = {**pkg["dependencies"], **pkg["devDependencies"]}
        for name, version in deps.items():
            with self.subTest(dep=name):
                self.assertRegex(version, r"^\d+\.\d+\.\d+$", "exact version, no ranges")
        pin = re.search(r'^REMOTION = "([\d.]+)"', (TEMPLATE / "build.py").read_text(encoding="utf-8"), re.M).group(1)
        remotion_deps = {k: v for k, v in deps.items() if k == "remotion" or k.startswith("@remotion/")}
        self.assertEqual(set(remotion_deps.values()), {pin})
        self.assertIn(pin, (PLUGIN / "references" / "projeto.md").read_text(encoding="utf-8"))

    def test_template_is_self_contained(self):
        for rel in ("src/index.ts", "src/Root.tsx", "src/Video.tsx", "src/tipos.ts", "src/cenas.generated.ts",
                    "src/dados.json", "public/fonts/Montserrat.ttf", "public/fonts/OFL-Montserrat.txt",
                    "compositions/exemplo-contador.tsx", "compositions/LEIA.md", "tsconfig.json", "remotion.config.ts"):
            self.assertTrue((TEMPLATE / rel).is_file(), rel)
        self.assertFalse({p.name for p in TEMPLATE.rglob("*")} & {"CLAUDE" + ".md", "AGENTS" + ".md", "node_modules"})
        source = "\n".join(p.read_text(encoding="utf-8") for p in [*(TEMPLATE / "src").glob("*.ts*"),
                                                                   *(TEMPLATE / "compositions").glob("*.tsx")])
        code = re.sub(r"//[^\n]*|/\*.*?\*/", "", source, flags=re.S)  # rules in comments do not count
        for banned in ("Math.random", "Date.now", "fetch(", "setTimeout"):
            self.assertNotIn(banned, code, "renders must be deterministic")
        seed = json.loads((TEMPLATE / "src" / "dados.json").read_text(encoding="utf-8"))
        self.assertEqual(seed["schema"], render_plan.SCHEMA)


class HermesAdapterTest(unittest.TestCase):
    def test_registers_every_skill_with_a_bounded_first_turn_bootstrap(self):
        ctx = FakeHermes()
        load_module(PLUGIN / ".hermes-plugin/__init__.py", "pwdev_vrm_hermes").register(ctx)
        self.assertEqual({name for name, _ in ctx.skills}, SKILLS)
        first = ctx.hooks["pre_llm_call"](is_first_turn=True)
        self.assertLess(len(first["context"]), 4000)
        self.assertIn('skill_view("pwdev-video-remotion:vrm-<name>")', first["context"])
        self.assertNotIn("HyperFrames", first["context"])
        self.assertIsNone(ctx.hooks["pre_llm_call"](is_first_turn=False))


# ---------------------------------------------------------------------------- builder

def fake_media():
    def media(*args):
        if args[:2] == ("video", "plano-render"):
            return render_plan.from_files(args[2])
        if args[:2] == ("video", "portao"):
            return {"veredito": "PASSOU", "problemas": [], "avisos": []}
        raise AssertionError(f"chamada inesperada ao pwdev-media: {args}")
    return media


WORDS = [("Hoje", 0.1, 0.3), ("eu", 0.35, 0.45), ("vou", 0.5, 0.7), ("mostrar", 0.8, 1.1),
         ("três", 1.15, 1.35), ("chip,", 1.4, 1.7), ("Primeira", 2.6, 3.0), ("dica.", 3.05, 3.4)]


class ProjectFixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.edit = self.tmp / "edit"
        self.edit.mkdir()
        (self.edit / "cut.mp4").write_bytes(b"fake-mp4")
        words = [{"w": w, "inicio": a, "fim": b} for w, a, b in WORDS]
        (self.edit / "cut_timeline.json").write_text(json.dumps(
            {"schema": "pwdev-corte/1", "duracao": 4.0, "segmentos": [], "palavras": words}), encoding="utf-8")
        (self.edit / "legendas.json").write_text(json.dumps(captions.build(words, 3)), encoding="utf-8")
        self.proj = media_project.new("dicas", str(self.edit), "reels-9x16")

    def tearDown(self):
        self._tmp.cleanup()


class BuilderTest(ProjectFixture):
    def setUp(self):
        super().setUp()
        self.proj_dir = self.tmp / "proj"
        shutil.copytree(TEMPLATE, self.proj_dir)
        self.build = load_module(self.proj_dir / "build.py", f"vrm_build_{id(self)}")
        self.build.HERE = self.proj_dir
        self.build.media = fake_media()

    def run_build(self) -> dict:
        media_project.save(self.proj, self.proj_dir / "projeto.json")
        self.build.build(json.loads((self.proj_dir / "projeto.json").read_text(encoding="utf-8")))
        return json.loads((self.proj_dir / "src" / "dados.json").read_text(encoding="utf-8"))

    def test_data_points_to_public_media(self):
        data = self.run_build()
        self.assertEqual(data["video"]["arquivo"], "cut.mp4")
        self.assertEqual((self.proj_dir / "public" / "cut.mp4").read_bytes(), b"fake-mp4")
        self.assertEqual(data["duracao"], 4.0)
        self.assertGreater(len(data["cues"]), 0)
        generated = (self.proj_dir / "src" / "cenas.generated.ts").read_text(encoding="utf-8")
        self.assertIn("export const CENAS: Record<string, CenaComponent> = {", generated)

    def test_scenes_are_imported_and_html_scenes_refused(self):
        self.proj["cenas"] = [{"inicio": 0, "fim": 1.2, "src": "compositions/exemplo-contador.tsx", "sobre_a_pessoa": True}]
        self.run_build()
        generated = (self.proj_dir / "src" / "cenas.generated.ts").read_text(encoding="utf-8")
        self.assertIn("import Cena0 from '../compositions/exemplo-contador';", generated)
        self.assertIn('"compositions/exemplo-contador.tsx": Cena0,', generated)
        self.proj["cenas"] = [{"inicio": 0, "fim": 1.2, "src": "compositions/cena.html"}]
        (self.proj_dir / "compositions" / "cena.html").write_text("<div></div>")
        with self.assertRaises(SystemExit) as ctx:
            self.run_build()
        self.assertEqual(ctx.exception.code, 1)
        self.proj["cenas"] = [{"inicio": 0, "fim": 1.2, "src": "compositions/falta.tsx"}]
        with self.assertRaises(SystemExit):
            self.run_build()

    def test_audio_is_copied_with_safe_names(self):
        music = self.tmp / "Minha Trilha (final).MP3"
        music.write_bytes(b"music")
        self.proj["audio"]["trilha"] = {"arquivo": str(music), "volume_db": -23}
        data = self.run_build()
        self.assertEqual(data["audio"]["trilha"]["arquivo"], "audio/minha-trilha-final.mp3")
        self.assertTrue((self.proj_dir / "public" / "audio" / "minha-trilha-final.mp3").is_file())
        self.proj["audio"]["efeitos"] = [{"t": 1.0, "arquivo": str(self.tmp / "nao-existe.mp3")}]
        with self.assertRaises(SystemExit):
            self.run_build()

    def test_render_runs_pinned_remotion_then_the_gate(self):
        media_project.save(self.proj, self.proj_dir / "projeto.json")
        (self.proj_dir / "node_modules" / "remotion").mkdir(parents=True)
        calls = []
        with mock.patch.object(self.build.shutil, "which", return_value="/usr/bin/npx"), \
                mock.patch.object(self.build.subprocess, "run",
                                  side_effect=lambda cmd, **kw: calls.append((cmd, kw)) or subprocess.CompletedProcess(cmd, 0)):
            with self.assertRaises(SystemExit) as ctx:
                self.build.main(["render", "--qualidade", "alta"])
        self.assertEqual(ctx.exception.code, 0)
        cmd, kwargs = calls[0]
        self.assertEqual(cmd[:4], ["/usr/bin/npx", "--no-install", "remotion", "render"])
        self.assertIn("Principal", cmd)
        self.assertIn("--crf=14", cmd)
        self.assertTrue(cmd[6].endswith("renders/dicas.mp4"))
        self.assertEqual(kwargs["cwd"], self.proj_dir)

    def test_remotion_requires_installed_dependencies(self):
        with self.assertRaises(SystemExit) as ctx:
            self.build.remotion(["compositions"])
        self.assertEqual(ctx.exception.code, 6)

    def test_still_frame_is_clamped_to_the_video(self):
        self.run_build()
        (self.proj_dir / "node_modules" / "remotion").mkdir(parents=True)
        with mock.patch.object(self.build.shutil, "which", return_value="/usr/bin/npx"), \
                mock.patch.object(self.build.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            self.build.cmd_quadro(["99"])
        self.assertIn("--frame=119", run.call_args.args[0])

    def test_studio_runs_detached_and_stops(self):
        media_project.save(self.proj, self.proj_dir / "projeto.json")
        (self.proj_dir / "node_modules" / "remotion").mkdir(parents=True)
        proc = mock.Mock(pid=4242)
        with mock.patch.object(self.build.shutil, "which", return_value="/usr/bin/npx"), \
                mock.patch.object(self.build.subprocess, "Popen", return_value=proc) as popen:
            self.build.cmd_estudio([])
        args, kwargs = popen.call_args
        self.assertEqual(args[0][:4], ["/usr/bin/npx", "--no-install", "remotion", "studio"])
        self.assertIn("--no-open", args[0])
        self.assertTrue(kwargs["start_new_session"])
        self.assertEqual((self.proj_dir / ".pwdev" / "estudio.pid").read_text(), "4242")
        with mock.patch.object(self.build.os, "kill", side_effect=OSError):
            self.build.cmd_estudio(["--parar"])
        self.assertFalse((self.proj_dir / ".pwdev" / "estudio.pid").exists())

    def test_amostra_limits_length(self):
        with self.assertRaises(SystemExit):
            self.build.main(["amostra", "1", "45"])


class NovoTest(ProjectFixture):
    def test_creates_project_without_node_modules_and_refuses_inside_edit(self):
        build = load_module(TEMPLATE / "build.py", "vrm_build_novo")

        def fake_run(cmd, **kwargs):
            media_project.save(media_project.new("x", str(self.edit)), Path(cmd[cmd.index("projeto") + 1]))
            return subprocess.CompletedProcess(cmd, 0, "{}", "")

        with mock.patch.object(build, "media_cli", return_value="/bin/pwdev-media"), \
                mock.patch.object(build.subprocess, "run", side_effect=fake_run):
            build.cmd_novo([str(self.tmp / "dicas"), "--edit", str(self.edit)])
            with self.assertRaises(SystemExit):
                build.cmd_novo([str(self.edit / "dentro"), "--edit", str(self.edit)])
        proj = self.tmp / "dicas"
        for rel in ("build.py", "package.json", "tsconfig.json", "remotion.config.ts", "src/Video.tsx",
                    "public/fonts/Montserrat.ttf", "compositions/exemplo-contador.tsx", "renders", "projeto.json"):
            self.assertTrue((proj / rel).exists(), rel)
        self.assertFalse((proj / "node_modules").exists())


# ---------------------------------------------------------------------------- parity

class ParityTest(ProjectFixture):
    """The same projeto.json gives the same decisions on both engines."""

    def test_same_cues_texts_and_window_as_hyperframes(self):
        self.proj["legenda"]["estilo"] = "destaque"
        self.proj["amostra"] = {"inicio": 0.5, "fim": 3.5}
        self.proj["textos"] = [{"inicio": 2.6, "fim": 3.4, "texto": "Dica 1", "tipo": "rotulo", "posicao": "topo"}]
        self.proj["blocos"] = [{"inicio": 0, "fim": 4.0, "tipo": "tela_cheia", "zoom": 1.15}]

        hf_dir, rm_dir = self.tmp / "hf", self.tmp / "rm"
        shutil.copytree(HF_TEMPLATE, hf_dir)
        shutil.copytree(TEMPLATE, rm_dir)
        for d in (hf_dir, rm_dir):
            media_project.save(self.proj, d / "projeto.json")

        hf = load_module(hf_dir / "build.py", "parity_hf")
        hf.HERE = hf_dir

        def hf_media(*args):
            if args[:2] == ("formatos", "mostrar"):
                return media_formats.get(args[2])
            if args[:2] == ("video", "projeto"):
                return {"erros": media_project.validate(media_project.load(args[2]), 4.0)}
            raise AssertionError(args)

        hf.media = hf_media
        hf.build(self.proj)
        page = (hf_dir / "index.html").read_text(encoding="utf-8")

        rm = load_module(rm_dir / "build.py", "parity_rm")
        rm.HERE = rm_dir
        rm.media = fake_media()
        rm.build(self.proj)
        data = json.loads((rm_dir / "src" / "dados.json").read_text(encoding="utf-8"))

        hf_cues = re.findall(r'class="clip cue" data-start="([\d.]+)" data-duration="([\d.]+)"', page)
        self.assertEqual([(float(a), float(b)) for a, b in hf_cues],
                         [(c["inicio"], c["duracao"]) for c in data["cues"]])
        hf_text = re.search(r'class="clip texto rotulo topo" data-start="([\d.]+)" data-duration="([\d.]+)"', page)
        self.assertEqual((float(hf_text.group(1)), float(hf_text.group(2))),
                         (data["textos"][0]["inicio"], data["textos"][0]["duracao"]))
        root = re.search(r'id="root"[^>]*data-duration="([\d.]+)"', page).group(1)
        self.assertEqual(float(root), data["duracao"])
        self.assertIn(f'data-media-start="{data["video"]["inicio_midia"]:g}"', page)
        cap_top = int(re.search(r"\.cue \{[^}]*top: (\d+)px", page).group(1))
        self.assertEqual(cap_top, data["legenda"]["topo"])


@unittest.skipUnless(os.environ.get("PWDEV_E2E") == "1" and shutil.which("npm"), "PWDEV_E2E=1 para instalar e checar")
class RemotionCheckE2E(ProjectFixture):
    def test_install_and_check(self):
        proj_dir = self.tmp / "proj"
        shutil.copytree(TEMPLATE, proj_dir)
        media_project.save(self.proj, proj_dir / "projeto.json")
        install = subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=proj_dir, capture_output=True, text=True)
        self.assertEqual(install.returncode, 0, install.stderr[-2000:])
        build = load_module(proj_dir / "build.py", "vrm_e2e")
        build.HERE = proj_dir
        build.media = fake_media()
        build.build(self.proj)
        tsc = subprocess.run(["npx", "--no-install", "tsc", "--noEmit"], cwd=proj_dir, capture_output=True, text=True)
        self.assertEqual(tsc.returncode, 0, tsc.stdout[-2000:])


if __name__ == "__main__":
    unittest.main()
