# Changelog — pwdev-media

## 0.5.0 — 2026-10-14

- Caption style `caixa`: text on a dark band, readable over light interfaces (tutorials).
- `video portao --max-silencio`: longest pause allowed (0.25 s for talking videos; tutorials use 5 s).
- Cut fixes found on a real recording (35.1 s → 24.3 s, gate PASSOU):
  - a soft first syllable no longer moves the start past the transcript's word start (a word was
    being dropped from the captions);
  - word ends follow the last loud frame, not Whisper's late end (pauses survived at joints);
  - pauses are cut from 0.20 s (`SPLIT_AT`), so the 0.25 s rule holds after measurement slack;
  - captions keep a word by its overlap with the kept audio, not by its middle;
  - every cut goes through a limiter (true peak was +0.3 dBTP after AAC);
  - the gate judges a cut with its source's silence threshold, and the threshold stays at least
    30 dB under speech (an edited video's own threshold turned soft sounds into "pauses").
- Cut fixes found on a WhatsApp recording (28.1 s → 20.0 s, gate PASSOU):
  - a retake wrapped in new words ("ou seja, …") is detected: a phrase mostly contained in a
    later one is dropped (`CONTAINED` 0.7, at least 4 words);
  - consecutive segments never overlap (a phrase could start before the previous one's real end,
    repeating 0.3 s of audio);
  - clicks shorter than 50 ms inside a pause no longer split it (`BLIP_FRAMES`);
  - `tighten()` simulates the cut and squeezes joints still too long, judged 2 dB stricter than
    the gate (`GATE_MARGIN_DB`);
  - segments continuous in the source are merged (no fades in the middle of speech).

## 0.4.0 — 2026-10-14

Direct providers ported from pwdev-social-media 2.x scripts, so that plugin can drop its bash
wrappers (pwdev-social-media 3.0 requires this version).

- New adapters: BFL/FLUX (`bfl:flux-pro-1.1`, `bfl:flux-2-pro`), Ideogram 3.0 over the v2 API with
  multipart (`ideogram:ideogram-3`), Leonardo REST v1 legacy (`leonardo:conta`), Runway
  image-to-video that now waits and downloads the video (`runway:gen4_turbo`), Magnific upscale
  that now polls and saves the image (`magnific:upscale`).
- `gerar`: `--arquivo`/`--escala` (upscale), `--largura`/`--altura`, `--velocidade`; a local
  `--imagem-inicial` becomes a data URI; local inputs are part of the cache key; subscription items
  are refused with a pointer to the provider's API item.
- Keys: `MAGNIFIC_API_KEY` (and legacy `FREEPIK_API_KEY`), `RUNWAYML_API_SECRET` (and legacy
  `RUNWAY_API_KEY`).
- Catalog: plugin-owned structural fields (category, provider, via, operation, model) and
  deprecations now reach existing working catalogs on load; curation is kept. Old ids `bfl:flux`,
  `ideogram:v3`, `leonardo:phoenix` are deprecated in favor of the new ones.

## 0.3.0 — 2026-10-14

- `video plano-render`: engine-neutral render plan (`pwdev-plano-render/1`) resolved once for both
  video plugins — sample window, clipped and shifted times, caption corrections, safe-zone layout
  scaled to the format, dB volumes as linear gain.
- `projeto.json` scenes may be `.html` (HyperFrames) or `.tsx` (Remotion) under `compositions/`;
  paths with `..` are refused.

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
