# Changelog — pwdev-media

## 0.2.0 — 2026-10-14

Talking-video pipeline shared by the video plugins (`pwdev-media video ...`).

- `ffmpeg --instalar`: static ffmpeg/ffprobe in `~/.pwdev/bin`, no sudo (public `static-ffmpeg`).
- `transcrever`: local word-level transcription (mlx-whisper on Apple Silicon with macOS 14+,
  faster-whisper elsewhere) in an isolated `uv run --with` environment; phrases and abandoned
  takes in `frases.md`.
- `juntar`, `montar` (EDL from phrase ids or automatic: last take wins), `cortar` (cut by the
  waveform: real onsets/offsets, every silence of 0.25 s or more removed, ~0.12 s joints, click-free
  fades), `legendas` (cues of up to N words, every spoken word covered, corrections), `fala`,
  `respiros`, `sondar`.
- `portao`: quality gate (no breaths, no clipping, captions cover every word; loudness warning).
- `projeto`: engine-neutral `projeto.json` (`pwdev-projeto-video/1`) creation and validation,
  including "one idea at a time" overlap checks.
- Fix: keys are written to the Keychain through stdin; output file names from provider responses
  are sanitized.

## 0.1.0 — 2026-10-14

First release: the core of the pwdev media suite.

- `pwdev-media` CLI (Python, standard library only, installed with `uv tool install`).
- Catalog of AI media models and apps in 14 categories (image, video, audio, transcription,
  LLM/vision, render engines), curated seed with sourced prices, validation and recommendation by
  goal (`barato`, `equilibrado`, `maximo`), commercial license and configured keys.
- Update routine: OpenRouter video and image models and npm versions of HyperFrames and Remotion,
  merged without touching curation; removed models are flagged, never deleted; pt-BR diff report;
  optional monthly schedule (macOS LaunchAgent, cron or Task Scheduler line elsewhere).
- Providers: OpenRouter (images, async video jobs), fal (queue API, any model) and ElevenLabs
  (music, sound effects, text to speech); contract changes fail loudly.
- Keys from environment or the macOS Keychain (`pwdev-media-<provider>`), typed by the person,
  never printed.
- Spend guard: estimate first, `--confirmar` required for paid calls, monthly budget, ledger and
  generation cache.
- Creative formats with safe zones (Reels, Stories, TikTok, Shorts, feed, link ads, YouTube,
  Pinterest, Google display).
- Portable skills `media-setup`, `media-catalogo`, `media-atualizar`, `media-gerar`,
  `media-custo`, `media-formatos`; Claude commands are thin wrappers; Codex manifest and
  `openai.yaml` per skill; Hermes adapter with a first-turn bootstrap.
