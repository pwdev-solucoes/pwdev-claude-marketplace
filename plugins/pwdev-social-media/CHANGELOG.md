# Changelog — pwdev-social-media

## 3.0.0 — 2026-10-14

Portable major release: the same creative workflow on Claude Code, Codex and Hermes Agent, with every
paid call going through the `pwdev-media` core.

### Breaking changes

- **Requires `pwdev-media` ≥ 0.4.0** (`claude plugin install pwdev-media@pwdev-claude-marketplace`).
  Without it the plugin runs in prompt mode only.
- **`scripts/` removed** (`gen-ideogram.sh`, `gen-leonardo.sh`, `gen-flux.sh`, `gen-runway.sh`,
  `upscale-freepik.sh`, `check-keys.sh`, `lib.sh`). Generation is `pwdev-media gerar <item> --estimar`,
  then `--confirmar` after an explicit yes.
- **Keys via `pwdev-media`:** `pwdev-media chaves guardar <provedor>` stores them in the Keychain; the
  environment still works. Runway now reads `RUNWAYML_API_SECRET` (legacy `RUNWAY_API_KEY` accepted);
  Magnific reads `MAGNIFIC_API_KEY` (legacy `FREEPIK_API_KEY` accepted).
- **Skills renamed** with the `social-` prefix (table below). Claude Code commands keep their names.
- **Ledger:** generations are recorded in the `pwdev-media` ledger (`pwdev-media custo extrato`) instead
  of `.pwdev-social/gerados/manifest.jsonl`; files of each campaign go to
  `.pwdev-social/gerados/<AAAA-MM-DD>-<slug>/`.
- **Safe zones:** dimensions and safe zones come from `pwdev-media formatos`; the pixel tables were
  removed from `references/formatos.md` (typography, slide counts and contrast stay).

### Migration — skills

| v2 | v3 |
|---|---|
| `image-gen` | `social-imagem` |
| `video-gen` | `social-video` |
| `prompt-craft` | `social-prompt` |
| `cost-control` | `social-custo` |
| `creative-concept` | `social-conceito` |
| `creative-review` | `social-revisao` |
| `carousel-builder` | `social-carrossel` |
| `story-reels` | `social-reels` |
| `post-visual` | `social-post` |
| `brand-kit` | `social-marca` |
| `visual-consistency` | `social-consistencia` |
| `asset-curation` | `social-curadoria` |
| `asset-upscale` | `social-upscale` |
| `alt-text` | `social-alt-text` |
| `format-specs` | `social-formatos` |
| `export-handoff` | `social-entrega` |
| `figma-pipeline` | `social-figma` |
| `social-context` | `social-contexto` (also owns init and status) |
| `vault-sync` | `social-vault` |
| — | `social-criar` (end-to-end flow that lived in `/criar`) |
| — | `social-lote` (hook × visual × format batches) |
| — | `social-video-curto` (routes to the HyperFrames/Remotion video plugins) |

### Migration — scripts

| v2 script | v3 |
|---|---|
| `gen-ideogram.sh --ratio 4x5 --n 2 --seed S --confirm` | `pwdev-media gerar ideogram:ideogram-3 --aspect-ratio 4x5 --n 2 --seed S` |
| `gen-flux.sh --w 1080 --h 1350 --seed S --confirm` | `pwdev-media gerar bfl:flux-2-pro --largura 1080 --altura 1350 --seed S` (or `bfl:flux-pro-1.1`) |
| `gen-leonardo.sh --w 1080 --h 1350 --n 2 --confirm` | `pwdev-media gerar leonardo:conta --largura 1080 --altura 1350 --n 2` |
| `gen-runway.sh --image I --dur 5 --ratio 720:1280 --confirm` | `pwdev-media gerar runway:gen4_turbo --imagem-inicial I --duration 5 --aspect-ratio 720:1280` |
| `upscale-freepik.sh --file F --scale 2 --confirm` | `pwdev-media gerar magnific:upscale --arquivo F --escala 2x` |
| `check-keys.sh` | `pwdev-media chaves listar` / `pwdev-media status --ao-vivo` |

Every `pwdev-media gerar` runs first with `--estimar` and only then with `--confirmar`. Runway now waits
for the task and downloads the clip, and the upscale saves the enlarged image (v2 returned only the task
id / raw JSON).

### New

- Portable layout: thin Claude commands, Codex manifest and `openai.yaml` per skill, Hermes adapter with
  a first-turn bootstrap, `references/runtime.md` (subagents inline on Codex/Hermes, Figma/Notion MCP per
  runtime, curation grid as Artifact or local HTML).
- New commands `/pwdev-social-media:formatos` and `/pwdev-social-media:lote`.
- `social-formatos` derives one approved piece into every format and checks text boxes against each safe
  zone with `pwdev-media formatos conferir`.
- Cost estimates in dollars from the `pwdev-media` catalog (with source and date), monthly budget, cache
  of identical requests.
