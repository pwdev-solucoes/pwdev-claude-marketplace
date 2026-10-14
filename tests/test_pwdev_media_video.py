"""pwdev-media video pipeline: audio analysis, phrases/takes, cut by the waveform, captions, gate,
projeto.json, transcription wrapper and ffmpeg installer.

Run from the repository root:

    python3 -m unittest tests.test_pwdev_media_video

Tests that render need ffmpeg (`pwdev-media video ffmpeg --instalar`); without it they are skipped.
No network and no speech model are used: transcription is exercised with a stubbed backend.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "pwdev-media" / "engine" / "src"))

from pwdev_media import cli  # noqa: E402
from pwdev_media.video import audio, captions, check, cut, phrases, project, tools, transcribe, workflow  # noqa: E402

HAS_FFMPEG = bool(tools.find("ffmpeg") and tools.find("ffprobe"))
needs_ffmpeg = unittest.skipUnless(HAS_FFMPEG, "ffmpeg não instalado (pwdev-media video ffmpeg --instalar)")

# "Speech" windows of the synthetic recording: tones with known gaps between them.
TONES = [(0.5, 1.5), (2.1, 3.0), (3.3, 4.2), (5.4, 6.0)]
DURATION = 7.0


def make_video(path: Path, tones=TONES, duration=DURATION, video=True) -> Path:
    expr = "+".join(f"between(t,{a},{b})" for a, b in tones)
    args = [tools.need("ffmpeg"), "-v", "error", "-y",
            "-f", "lavfi", "-i", f"aevalsrc='0.3*sin(2*PI*220*t)*({expr})':s=48000:d={duration}",
            "-f", "lavfi", "-i", f"anoisesrc=a=0.002:d={duration}:r=48000"]
    if video:
        args += ["-f", "lavfi", "-i", f"color=c=blue:s=180x320:d={duration}:r=30"]
    args += ["-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0[a]"]
    args += (["-map", "2:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p"] if video else ["-map", "[a]"])
    args += ["-c:a", "aac", "-shortest", str(path)]
    subprocess.run(args, check=True, capture_output=True)
    return path


def words_for(tones=TONES) -> list[dict]:
    texts = [["Hoje", "eu", "vou"], ["mostrar", "três", "dicas."], ["Primeira"], ["dica:"]]
    out = []
    for (a, b), ws in zip(tones, texts):
        step = (b - a) / len(ws)
        for i, w in enumerate(ws):
            out.append({"w": w, "inicio": round(a + i * step, 3), "fim": round(a + (i + 1) * step - 0.02, 3), "p": 0.9})
    return out


def run_cli(*argv) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class TempDir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.env = mock.patch.dict(os.environ, {"PWDEV_MEDIA_HOME": str(self.tmp / "home")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self._tmp.cleanup()


# ---------------------------------------------------------------------------- audio

class EnvelopeMathTest(unittest.TestCase):
    """Pure-Python envelope logic on hand-made samples (no ffmpeg)."""

    def samples(self, pattern):
        import array
        data = array.array("h")
        for loud, seconds in pattern:
            n = int(seconds * audio.RATE)
            amp = 9000 if loud else 20
            data.extend((amp if i % 2 else -amp) for i in range(n))
        return data

    def test_silences_and_regions_from_known_pattern(self):
        env = audio.envelope_from_samples(self.samples([(True, 1.0), (False, 0.5), (True, 0.6), (False, 0.2), (True, 0.4)]))
        self.assertLess(env.floor, env.threshold)
        self.assertLess(env.threshold, env.speech)
        self.assertEqual(audio.silences(env, 0.25), [(1.0, 1.5)], "0.2 s pause is not a breath")
        self.assertEqual(audio.speech_regions(env, 0.25), [(0.0, 1.0), (1.5, 2.7)])
        self.assertEqual(audio.onset(env, 1.2, 2.0), 1.5)
        self.assertTrue(1.0 <= audio.quietest(env, 0.9, 1.6) < 1.5)

    def test_recording_without_pauses_is_not_silence(self):
        env = audio.envelope_from_samples(self.samples([(True, 2.0)]))
        self.assertEqual(audio.silences(env, 0.25), [])
        self.assertEqual(audio.speech_regions(env), [(0.0, 2.0)])

    def test_mute_recording_is_all_silence(self):
        import array
        env = audio.envelope_from_samples(array.array("h", [0] * audio.RATE))
        self.assertEqual(audio.silences(env, 0.25), [(0.0, 1.0)])

    def test_empty_audio(self):
        import array
        env = audio.envelope_from_samples(array.array("h"))
        self.assertEqual((env.db, audio.silences(env)), ([], []))


@needs_ffmpeg
class AudioTest(TempDir):
    def test_envelope_finds_the_known_gaps(self):
        env = audio.envelope(make_video(self.tmp / "v.mp4"))
        gaps = audio.silences(env, 0.25)
        expected = [(0.0, 0.5), (1.5, 2.1), (3.0, 3.3), (4.2, 5.4), (6.0, 7.0)]
        self.assertEqual(len(gaps), len(expected))
        for (a, b), (ea, eb) in zip(gaps, expected):
            self.assertAlmostEqual(a, ea, delta=0.04)
            self.assertAlmostEqual(b, eb, delta=0.04)

    def test_probe(self):
        info = tools.probe(make_video(self.tmp / "v.mp4"))
        self.assertAlmostEqual(info["duracao"], DURATION, delta=0.1)
        self.assertEqual((info["video"]["largura"], info["video"]["altura"]), (180, 320))
        self.assertEqual(info["audio"]["taxa"], 48000)


# ---------------------------------------------------------------------------- phrases

class PhrasesTest(unittest.TestCase):
    def w(self, text, a, b):
        return {"w": text, "inicio": a, "fim": b, "p": 0.9}

    def test_split_on_pause_and_final_punctuation(self):
        words = [self.w("Oi", 0, 0.3), self.w("gente.", 0.35, 0.7), self.w("Hoje", 0.9, 1.1),
                 self.w("tem", 1.15, 1.3), self.w("dica", 2.0, 2.3)]
        found = phrases.split(words)
        self.assertEqual([p["texto"] for p in found], ["Oi gente.", "Hoje tem", "dica"])
        self.assertEqual([p["id"] for p in found], ["F001", "F002", "F003"])
        self.assertEqual((found[1]["inicio"], found[1]["fim"]), (0.9, 1.3))

    def test_last_take_wins(self):
        texts = ["Hoje eu vou", "Hoje eu vou mostrar três dicas", "A primeira é simples",
                 "A primeira é bem simples", "Obrigado"]
        found = [{"id": f"F{n:03d}", "texto": t, "inicio": n, "fim": n + 0.5, "palavras": []}
                 for n, t in enumerate(texts, 1)]
        phrases.mark_takes(found)
        self.assertEqual(found[0]["refeita_em"], "F002", "abandoned start")
        self.assertEqual(found[2]["refeita_em"], "F004", "near-identical retake")
        self.assertNotIn("refeita_em", found[4])
        self.assertEqual(phrases.auto_ids(found), ["F002", "F004", "F005"])

    def test_different_sentences_are_not_takes(self):
        found = [{"id": "F001", "texto": "Compre agora", "inicio": 0, "fim": 1, "palavras": []},
                 {"id": "F002", "texto": "O frete é grátis para todo o Brasil", "inicio": 2, "fim": 3, "palavras": []}]
        self.assertEqual(phrases.auto_ids(phrases.mark_takes(found)), ["F001", "F002"])

    def test_normalize_ignores_accents_case_and_punctuation(self):
        self.assertEqual(phrases.normalize("Três DICAS, já!"), "tres dicas ja")

    def test_edl_from_ids_and_validation(self):
        found = [{"id": "F001", "texto": "a", "inicio": 1.0, "fim": 2.0, "palavras": []}]
        edl = phrases.from_phrase_ids(found, ["F001"], "/v.mp4")
        self.assertEqual(phrases.validate_edl(edl), [])
        self.assertEqual(edl["intervalos"], [{"inicio": 1.0, "fim": 2.0, "frases": ["F001"]}])
        with self.assertRaisesRegex(KeyError, "F009"):
            phrases.from_phrase_ids(found, ["F009"], "/v.mp4")
        bad = {"schema": "x", "intervalos": [{"inicio": 2, "fim": 1}]}
        errors = " ".join(phrases.validate_edl(bad))
        for expected in ("schema", "fonte", "fim antes"):
            self.assertIn(expected, errors)

    def test_markdown_marks_takes_and_doubtful_words(self):
        found = [{"id": "F001", "texto": "Oi", "inicio": 0, "fim": 1, "refeita_em": "F002",
                  "palavras": [{"w": "Oi", "p": 0.3}]},
                 {"id": "F002", "texto": "Oi gente", "inicio": 2, "fim": 3, "palavras": []}]
        md = phrases.markdown(found, "/x/bruto.mp4")
        self.assertIn("**F001** [00:00.00–00:01.00] ↺ F002 Oi  (dúvida: Oi)", md)


# ---------------------------------------------------------------------------- cut

@needs_ffmpeg
class CutTest(TempDir):
    def setUp(self):
        super().setUp()
        self.src = make_video(self.tmp / "bruto.mp4")
        self.env_ = audio.envelope(self.src)
        self.edl = {"schema": phrases.EDL_SCHEMA, "fonte": str(self.src),
                    "intervalos": [{"inicio": 0.5, "fim": 4.2, "frases": ["F001"]},
                                   {"inicio": 5.4, "fim": 6.0, "frases": ["F002"]}]}

    def test_plan_keeps_every_word_and_drops_inner_breaths(self):
        segs = cut.plan(self.edl, self.env_)
        self.assertEqual(len(segs), 4, "the 0.6 s and 0.3 s pauses inside the first interval go away")
        for (a, b), (ta, tb) in zip(segs, TONES):
            self.assertLessEqual(a, ta + 0.02, "never cuts the start of a word")
            self.assertGreaterEqual(b, tb, "never eats the end of a word")
            self.assertLess(b - tb, 0.25)
            self.assertLess(ta - a, 0.2)

    def test_edl_whisper_offsets_are_corrected_by_the_wave(self):
        early = {**self.edl, "intervalos": [{"inicio": 0.25, "fim": 1.2, "frases": ["F001"]}]}
        (a, b), = cut.plan(early, self.env_)
        self.assertAlmostEqual(a, 0.5 - cut.PAD, delta=0.03, msg="start moved to the real onset")
        self.assertGreaterEqual(b, 1.5, "end follows the sound, not the transcript")

    def test_render_cut_passes_the_gate_and_the_raw_video_fails(self):
        words = words_for()
        result = cut.render(self.edl, self.tmp / "edit", words, "rascunho")
        kept = sum(b - a for a, b in TONES)
        self.assertGreater(result["duracao"], kept)
        self.assertLess(result["duracao"], kept + 4 * 0.25)
        out = Path(result["arquivo"])
        self.assertAlmostEqual(tools.probe(out)["duracao"], result["duracao"], delta=0.1)
        self.assertEqual(check.gate(out)["veredito"], "PASSOU")
        raw = check.gate(self.src)
        self.assertEqual(raw["veredito"], "REPROVOU")
        self.assertIn("respiro", raw["problemas"][0])
        timeline = json.loads((self.tmp / "edit" / "cut_timeline.json").read_text(encoding="utf-8"))
        self.assertEqual(timeline["schema"], cut.TIMELINE_SCHEMA)
        self.assertEqual([w["w"] for w in timeline["palavras"]], [w["w"] for w in words])
        starts = [w["inicio"] for w in timeline["palavras"]]
        self.assertEqual(starts, sorted(starts))
        self.assertLessEqual(timeline["palavras"][-1]["fim"], timeline["duracao"])

    def test_empty_cut_is_refused(self):
        with self.assertRaisesRegex(ValueError, "vazio"):
            cut.render({**self.edl, "intervalos": [{"inicio": 6.5, "fim": 6.9, "frases": []}]}, self.tmp / "e")

    def test_audio_only_source(self):
        src = make_video(self.tmp / "voz.m4a", video=False)
        result = cut.render({**self.edl, "fonte": str(src)}, self.tmp / "edit-audio")
        info = tools.probe(result["arquivo"])
        self.assertIsNone(info["video"])
        self.assertIsNotNone(info["audio"])

    def test_remap_words_drops_words_outside_kept_segments(self):
        segs = [{"src_inicio": 1.0, "src_fim": 2.0, "dst_inicio": 0.0, "dst_fim": 1.0},
                {"src_inicio": 3.0, "src_fim": 4.0, "dst_inicio": 1.0, "dst_fim": 2.0}]
        ws = [{"w": "a", "inicio": 1.1, "fim": 1.4}, {"w": "fora", "inicio": 2.3, "fim": 2.6},
              {"w": "b", "inicio": 3.2, "fim": 3.5}]
        out = cut.remap_words(ws, segs)
        self.assertEqual([(w["w"], w["inicio"], w["fim"]) for w in out], [("a", 0.1, 0.4), ("b", 1.2, 1.5)])


# ---------------------------------------------------------------------------- captions and gate

class CaptionsTest(unittest.TestCase):
    WORDS = [{"w": "Hoje", "inicio": 0.0, "fim": 0.2}, {"w": "eu", "inicio": 0.25, "fim": 0.35},
             {"w": "vou", "inicio": 0.4, "fim": 0.55}, {"w": "mostrar", "inicio": 0.6, "fim": 0.9},
             {"w": "três", "inicio": 0.95, "fim": 1.1}, {"w": "dicas.", "inicio": 1.15, "fim": 1.5},
             {"w": "Primeira", "inicio": 2.4, "fim": 2.8}]

    def test_max_words_punctuation_and_pause_breaks(self):
        doc = captions.build(self.WORDS, 3)
        self.assertEqual([c["texto"] for c in doc["cues"]], ["Hoje eu vou", "mostrar três dicas.", "Primeira"])
        self.assertTrue(all(len(c["palavras"]) <= 3 for c in doc["cues"]))
        self.assertEqual(doc["cues"][0]["fim"], doc["cues"][1]["inicio"], "short gaps are bridged")
        self.assertEqual(doc["cues"][1]["fim"], 1.5, "a long pause is not bridged")
        doc1 = captions.build(self.WORDS, 1)
        self.assertEqual(len(doc1["cues"]), len(self.WORDS))

    def test_every_word_is_covered(self):
        doc = captions.build(self.WORDS, 2)
        timeline = {"palavras": self.WORDS}
        self.assertEqual(check.caption_gaps(timeline, doc["cues"]), [])
        self.assertEqual(len(check.caption_gaps(timeline, doc["cues"][1:])), 2)

    def test_corrections_keep_punctuation(self):
        fixed = captions.apply_corrections([{"w": "chip,"}, {"w": "Editor"}, {"w": "nada"}],
                                           {"chip": "Chip", "editor": "Editor IA"})
        self.assertEqual([w["w"] for w in fixed], ["Chip,", "Editor IA", "nada"])

    def test_srt(self):
        text = captions.srt(captions.build(self.WORDS[:3], 3))
        self.assertIn("1\n00:00:00,000 --> 00:00:00,550\nHoje eu vou\n", text)


@needs_ffmpeg
class GateTest(TempDir):
    def test_loudness_and_clipping(self):
        loud = self.tmp / "alto.wav"
        subprocess.run([tools.need("ffmpeg"), "-v", "error", "-y", "-f", "lavfi", "-i",
                        "sine=f=440:d=2,volume=24dB", "-c:a", "pcm_s16le", str(loud)], check=True)
        result = check.gate(loud)
        self.assertEqual(result["veredito"], "REPROVOU")
        self.assertTrue(any("estourando" in p for p in result["problemas"]))

    def test_gate_reports_caption_gaps(self):
        src = make_video(self.tmp / "v.mp4", tones=[(0.0, 2.0)], duration=2.0)
        timeline = {"palavras": [{"w": "ok", "inicio": 0.2, "fim": 0.5}, {"w": "sem", "inicio": 1.0, "fim": 1.3}]}
        cues = [{"inicio": 0.1, "fim": 0.6, "texto": "ok"}]
        result = check.gate(src, timeline, cues)
        self.assertEqual(result["veredito"], "REPROVOU")
        self.assertIn("sem (1.00s)", result["problemas"][0])


# ---------------------------------------------------------------------------- projeto.json

class ProjectTest(unittest.TestCase):
    def proj(self, **over):
        p = project.new("teste", "/tmp/edit", "reels-9x16")
        p.update(over)
        return p

    def test_new_project_is_valid(self):
        self.assertEqual(project.validate(self.proj(), 10.0), [])
        with self.assertRaises(KeyError):
            project.new("x", "/tmp/edit", "formato-inexistente")

    def test_one_idea_at_a_time(self):
        p = self.proj(textos=[{"inicio": 1, "fim": 3, "texto": "A", "tipo": "rotulo"}],
                      cenas=[{"inicio": 2.5, "fim": 4, "src": "compositions/c.html"}])
        self.assertIn("uma ideia por vez", " ".join(project.validate(p, 10.0)))
        p["cenas"][0]["inicio"] = 3.0
        self.assertEqual(project.validate(p, 10.0), [])

    def test_ranges_types_and_paths(self):
        p = self.proj(blocos=[{"inicio": 0, "fim": 20, "tipo": "tela_cheia", "zoom": 3}],
                      textos=[{"inicio": 2, "fim": 1, "texto": " ", "tipo": "banner", "posicao": "lado"}],
                      cenas=[{"inicio": 0, "fim": 1, "src": "../fora.html"}],
                      legenda={"estilo": "neon", "max_palavras": 9}, schema="x", formato="nada")
        errors = " | ".join(project.validate(p, 10.0))
        for expected in ("schema", "formato", "legenda.estilo", "max_palavras", "fora do corte", "zoom",
                         "fim (1) antes", "texto vazio", "tipo deve ser", "posicao", "compositions/"):
            self.assertIn(expected, errors)


# ---------------------------------------------------------------------------- workflow and CLI

@needs_ffmpeg
class WorkflowCliTest(TempDir):
    def prepare(self) -> Path:
        src = make_video(self.tmp / "bruto.mp4")
        edit = self.tmp / "edit"
        edit.mkdir()
        doc = {"schema": transcribe.SCHEMA, "fonte": str(src), "idioma": "pt", "motor": "teste", "modelo": "-",
               "duracao": DURATION, "palavras": words_for()}
        (edit / "transcricao.json").write_text(json.dumps(doc), encoding="utf-8")
        return edit

    def test_full_pipeline_through_the_cli(self):
        edit = self.prepare()
        self.assertEqual(run_cli("video", "frases", str(edit))[0], 0)
        self.assertTrue((edit / "frases.md").is_file())
        code, out, _ = run_cli("--json", "video", "montar", str(edit))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["descartadas"], 0)
        code, out, err = run_cli("--json", "video", "cortar", str(edit), "--qualidade", "rascunho")
        self.assertEqual(code, 0, err)
        self.assertGreater(json.loads(out)["legendas"], 0)
        (edit / "correcoes.json").write_text(json.dumps({"dicas": "DICAS"}), encoding="utf-8")
        run_cli("video", "legendas", str(edit))
        self.assertIn("DICAS.", (edit / "legendas.srt").read_text(encoding="utf-8"))
        self.assertEqual(run_cli("video", "portao", str(edit / "cut.mp4"), "--edit", str(edit))[0], 0)
        code, out, _ = run_cli("video", "fala", str(edit))
        self.assertIn("Hoje eu vou mostrar", out)
        proj = self.tmp / "proj" / "projeto.json"
        code, out, _ = run_cli("--json", "video", "projeto", str(proj), "--novo", "--edit", str(edit))
        self.assertEqual(code, 0)
        self.assertGreater(json.loads(out)["duracao_corte"], 3.0)

    def test_choose_phrases_by_id(self):
        edit = self.prepare()
        workflow.do_phrases(str(edit))
        result = workflow.do_assemble(str(edit), ["F002"])
        self.assertEqual(result["frases"], 1)
        edl = json.loads((edit / "edl.json").read_text(encoding="utf-8"))
        self.assertEqual([iv["frases"] for iv in edl["intervalos"]], [["F002"]])

    def test_join_recordings(self):
        a, b = make_video(self.tmp / "a.mp4", duration=2.0, tones=[(0.2, 1.0)]), \
            make_video(self.tmp / "b.mp4", duration=3.0, tones=[(0.5, 2.0)])
        result = workflow.join(self.tmp / "fonte.mp4", [str(a), str(b)])
        self.assertAlmostEqual(tools.probe(result["arquivo"])["duracao"], 5.0, delta=0.15)

    def test_respiros_and_sondar(self):
        src = make_video(self.tmp / "v.mp4")
        code, out, _ = run_cli("--json", "video", "respiros", str(src))
        self.assertEqual(len(json.loads(out)), 5)
        code, out, _ = run_cli("video", "sondar", str(src))
        self.assertIn("180x320", out)


class CliUsageTest(TempDir):
    def test_usage_errors(self):
        self.assertEqual(run_cli("video", "cortar")[0], 2)
        self.assertEqual(run_cli("video", "transcrever", "/x.mp4")[0], 2, "--edit is required")
        self.assertEqual(run_cli("video", "juntar", "/out.mp4", "/a.mp4")[0], 2)
        self.assertEqual(run_cli("video", "montar", str(self.tmp / "nada"))[0], 2, "missing transcription")

    def test_missing_ffmpeg_is_exit_6(self):
        with mock.patch.object(tools, "find", return_value=None):
            code, _, err = run_cli("video", "sondar", "/x.mp4")
        self.assertEqual(code, 6)
        self.assertIn("--instalar", err)


# ---------------------------------------------------------------------------- transcription and installer

@needs_ffmpeg
class TranscribeWrapperTest(TempDir):
    def test_backend_runs_isolated_and_output_is_normalized(self):
        src = make_video(self.tmp / "v.mp4")
        real_run = subprocess.run
        seen = {}

        def fake_run(cmd, *args, **kwargs):
            if cmd and str(cmd[0]).endswith("uv"):
                seen["cmd"] = cmd
                out = Path(cmd[-1])
                out.write_text(json.dumps({"idioma": "pt", "palavras": [{"w": "oi", "inicio": 0.5, "fim": 0.8, "p": 1}]}))
                return subprocess.CompletedProcess(cmd, 0, "", "")
            return real_run(cmd, *args, **kwargs)

        with mock.patch.object(transcribe.subprocess, "run", side_effect=fake_run):
            doc = transcribe.transcribe(src, self.tmp / "edit" / "t.json", "pt", "Marca X", backend="faster")
        self.assertEqual(doc["schema"], transcribe.SCHEMA)
        self.assertEqual(doc["motor"], "faster")
        self.assertEqual(doc["palavras"][0]["w"], "oi")
        cmd = seen["cmd"]
        self.assertEqual(cmd[1:5], ["run", "--no-project", "--with", "faster-whisper>=1.1"])
        self.assertIn("Marca X", cmd)
        self.assertTrue(str(cmd[cmd.index("faster") + 2]).endswith("audio.wav"), "decoded to wav first")
        self.assertTrue((self.tmp / "edit" / "t.json").is_file())

    def test_failure_is_reported(self):
        src = make_video(self.tmp / "v.mp4")
        real_run = subprocess.run

        def fake_run(cmd, *args, **kwargs):
            if cmd and str(cmd[0]).endswith("uv"):
                return subprocess.CompletedProcess(cmd, 1, "", "modelo indisponível")
            return real_run(cmd, *args, **kwargs)

        with mock.patch.object(transcribe.subprocess, "run", side_effect=fake_run):
            with self.assertRaisesRegex(RuntimeError, "modelo indisponível"):
                transcribe.transcribe(src, self.tmp / "t.json", backend="mlx")


class TranscribeBackendTest(unittest.TestCase):
    def test_default_backend(self):
        with mock.patch.object(transcribe.platform, "system", return_value="Darwin"), \
                mock.patch.object(transcribe.platform, "machine", return_value="arm64"), \
                mock.patch.object(transcribe.platform, "mac_ver", return_value=("14.5", ("", "", ""), "")):
            self.assertEqual(transcribe.default_backend(), "mlx")
        with mock.patch.object(transcribe.platform, "system", return_value="Darwin"), \
                mock.patch.object(transcribe.platform, "machine", return_value="arm64"), \
                mock.patch.object(transcribe.platform, "mac_ver", return_value=("13.6", ("", "", ""), "")):
            self.assertEqual(transcribe.default_backend(), "faster")
        with mock.patch.object(transcribe.platform, "system", return_value="Windows"):
            self.assertEqual(transcribe.default_backend(), "faster")

    def test_missing_video(self):
        with self.assertRaises(FileNotFoundError):
            transcribe.transcribe("/nao/existe.mp4", "/tmp/x.json")


class FfmpegInstallerTest(TempDir):
    def test_binaries_are_copied_not_linked(self):
        cache = self.tmp / "cache"
        cache.mkdir()
        for name in ("ffmpeg", "ffprobe"):
            (cache / name).write_text("#!/bin/sh\n")
        fake = subprocess.CompletedProcess([], 0, json.dumps([str(cache / "ffmpeg"), str(cache / "ffprobe")]) + "\n", "")
        with mock.patch.dict(os.environ, {"PWDEV_BIN": str(self.tmp / "bin")}), \
                mock.patch.object(tools.subprocess, "run", return_value=fake) as run, \
                mock.patch.object(tools.shutil, "which", return_value="/usr/bin/uv"):
            info = tools.install()
            self.assertEqual(run.call_args.args[0][1:5], ["run", "--no-project", "--with", "static-ffmpeg"])
        for name in ("ffmpeg", "ffprobe"):
            dest = self.tmp / "bin" / name
            self.assertTrue(dest.is_file() and not dest.is_symlink())
            self.assertTrue(os.access(dest, os.X_OK))
        self.assertEqual(info["pasta"], str(self.tmp / "bin"))

    def test_download_failure(self):
        fake = subprocess.CompletedProcess([], 1, "", "sem rede")
        with mock.patch.object(tools.subprocess, "run", return_value=fake), \
                mock.patch.object(tools.shutil, "which", return_value="/usr/bin/uv"):
            with self.assertRaisesRegex(tools.MissingTool, "sem rede"):
                tools.install()


if __name__ == "__main__":
    unittest.main()
