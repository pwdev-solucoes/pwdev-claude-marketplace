# Changelog — pwdev-video-remotion

## 0.1.0 — 2026-10-14

First release.

- Talking-video editing by conversation with Remotion 4.0.535 (React 19.3.1, TypeScript 5.9.3,
  pinned): the same flow and the same `projeto.json` (`pwdev-projeto-video/1`) as
  pwdev-video-hyperframes.
- Project template `templates/projeto-remotion/`: `src/Video.tsx` renders the cut with
  `OffthreadVideo`, eased zoom blocks, word-timed captions (`discreta`, `destaque` with a readable
  highlight pill), labels and titles inside the safe zone, custom scenes as React components in
  `compositions/*.tsx`, music with fades and sound effects; local Montserrat via `@remotion/fonts`.
- `build.py` (standard library): `novo`, `instalar`, `montar` (render plan from
  `pwdev-media video plano-render` → `src/dados.json`, generated scene imports, media copied into
  `public/`), `amostra`, `completo`, `checar` (TypeScript + composition), `quadro`, background
  `estudio`, pinned `rm` passthrough and `render` followed by the quality gate.
- Remotion license notice (`references/licenca.md`) checked before the first project, with
  pwdev-video-hyperframes as the Apache-2.0 alternative.
- Portable skills `vrm-setup`, `vrm-editar`, `vrm-corte`, `vrm-plano`, `vrm-cenas`, `vrm-som`,
  `vrm-revisar`, `vrm-variacoes`; Claude commands are thin wrappers; Codex manifest and
  `openai.yaml` per skill; Hermes adapter with a first-turn bootstrap.
