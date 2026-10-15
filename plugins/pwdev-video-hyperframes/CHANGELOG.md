# Changelog — pwdev-video-hyperframes

## 0.2.0 — 2026-10-14

- Caption style `caixa` (dark band, for screen recordings and light backgrounds); words wrapped in a
  `.faixa` span.
- `build.py render --max-silencio <s>` passes the pause limit to the gate (tutorial profile).
- Requires pwdev-media ≥ 0.5.0.

## 0.1.0 — 2026-10-14

First release.

- Talking-video editing by conversation with HyperFrames 0.8.158 (pinned): `vhf-editar` drives the
  whole flow — cut, block plan, 8–15 s studio sample, full video, render and delivery.
- `vhf-corte` on top of the `pwdev-media` video pipeline: local word-level transcription, phrases
  and abandoned takes, EDL, cut by the waveform (no silence of 0.25 s or more, ~0.12 s joints, word
  ends never clipped), captions and gate.
- Project template `templates/projeto-hf/` with its own `build.py` (standard library): builds the
  official HyperFrames `index.html` from `projeto.json` (schema `pwdev-projeto-video/1`, shared with
  pwdev-video-remotion) — word-timed captions (`discreta`, `destaque` with a readable highlight
  pill), zoom blocks, labels and titles inside the platform safe zone, custom scene
  sub-compositions, music bed and sound effects; sample windows; pinned HyperFrames commands with
  telemetry off; verified local GSAP copy for offline renders; render followed by the quality gate.
- Custom scenes are written with the official HyperFrames skills (`vhf-cenas`), installed by
  `vhf-setup` together with ffmpeg (no sudo) and the core CLI.
- Portable skills `vhf-setup`, `vhf-editar`, `vhf-corte`, `vhf-plano`, `vhf-cenas`, `vhf-som`,
  `vhf-revisar`, `vhf-variacoes`; Claude commands are thin wrappers; Codex manifest and
  `openai.yaml` per skill; Hermes adapter with a first-turn bootstrap.
