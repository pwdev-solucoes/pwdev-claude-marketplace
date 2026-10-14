# PWDEV Media

Core of the pwdev media suite. One CLI, `pwdev-media`, and six portable skills (Claude Code,
Codex and Hermes Agent) that answer three questions before any AI generation:

1. **Which model or app?** A catalog by category, with price, quality and commercial license.
2. **How much will it cost?** Estimate, mandatory confirmation, monthly budget and ledger.
3. **Which format?** Sizes and safe zones per platform.

The video plugins (`pwdev-video-hyperframes`, `pwdev-video-remotion`, `pwdev-video-tutorial`) and
`pwdev-social-media` v3 build on this CLI. Conversation and CLI output are in Brazilian Portuguese.

## Installation

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
```

Then, in a new conversation: `/pwdev-media:init` (Codex: `$media-setup`; Hermes:
`skill_view("pwdev-media:media-setup")`). The skill installs the CLI with
`uv tool install <plugin>/engine` (no sudo) and walks through the keys.

Requirements: Python 3.10+ and [uv](https://docs.astral.sh/uv/). The CLI uses the standard
library only.

## Commands

| Claude Code | Codex / Hermes | What it does |
|---|---|---|
| `/pwdev-media:init` | `$media-setup` | install, store keys, test providers |
| `/pwdev-media:status` | `$media-setup` | tools, keys (live check), catalog age, spend |
| `/pwdev-media:catalogo` | `$media-catalogo` | "which model for…", recommendation by goal |
| `/pwdev-media:atualizar` | `$media-atualizar` | refresh the catalog and report changes; optional schedule |
| `/pwdev-media:gerar` | `$media-gerar` | generate image, video, music, sound effect or narration |
| `/pwdev-media:custo` | `$media-custo` | spending report and monthly budget |
| `/pwdev-media:formatos` | `$media-formatos` | creative formats and safe zones |

## Catalog

14 categories: image (generate, upscale, cut-out), video (generate, upscale, lip sync, person
matte), audio (voice cleanup, music, sound effects, TTS), transcription, LLM/vision and render
engines (HyperFrames, Remotion, FFmpeg). Each item is an **aggregator** (OpenRouter, fal), a direct
**API**, a **subscription** (Runway, Higgsfield, Magnific, Topaz, Adobe) or **local** (free).

- Working copy in `~/.pwdev/media/catalogo.json`, created from the plugin seed.
- A price always has a source and a date; otherwise it stays unknown.
- The update reads OpenRouter (video and image models) and npm (HyperFrames, Remotion), **never**
  overwrites curated quality, license or notes, and **never** deletes: a model that disappears is
  flagged `removido`. Subscriptions without a price API become manual reminders in the report.

Details: [`references/catalogo.md`](./references/catalogo.md) (pt-BR).

## Providers in this version

| Provider | Does | Key |
|---|---|---|
| OpenRouter | image and video (Veo, Seedance, Wan, Sora…) | `OPENROUTER_API_KEY` |
| fal | any queue model (Kling, Hailuo, Flux, upscalers…) | `FAL_KEY` |
| ElevenLabs | music, sound effects and narration | `ELEVENLABS_API_KEY` |

Exit codes and contracts: [`references/provedores.md`](./references/provedores.md) (pt-BR).

## Security

- **Keys:** read from the environment or the macOS Keychain (`pwdev-media-<provider>`). The person
  types the key in their own terminal; the agent never sees the value and `status` only says where
  a key was found.
- **Money:** no paid call without `--confirmar`, which the skills only pass after an explicit yes in
  the same session. Optional monthly budget; ledger in `~/.pwdev/media/ledger.jsonl`.
- **Cache:** an identical request already generated is reused for free.
- **API contracts:** when a provider changes its response shape, the CLI stops with a clear error.

## Development

```bash
python3 -m unittest tests.test_pwdev_media      # from the marketplace root, no network
claude plugin validate plugins/pwdev-media
hermes plugins doctor --ci plugins/pwdev-media
```

## License

Apache-2.0.
