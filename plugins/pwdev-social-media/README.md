# PWDEV Social Media — AI Creatives

AI-first creative production for social media on Claude Code, Codex and Hermes Agent. From approved
copy to a delivered piece:
- concept, cost triage and prompts;
- generation with an estimate and an explicit yes;
- curation and optional Figma composition;
- every format, an accessibility gate and a delivery package.

Conversation and skills are in Brazilian Portuguese ([README.pt-BR.md](./README.pt-BR.md) has the
full manual). Every paid call goes through the [`pwdev-media`](../pwdev-media/README.md) core.

## Installation

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-social-media@pwdev-claude-marketplace
```

In a new conversation: `/pwdev-social-media:init` (Codex: `$social-contexto`; Hermes:
`skill_view("pwdev-social-media:social-contexto")`). It does three things:
- creates the brand context;
- checks `pwdev-media` (0.4.0+);
- stores API keys in the Keychain with `pwdev-media chaves guardar <provider>`, typed by the person.

Without keys the plugin runs in prompt mode.

## Commands

| Claude Code | Codex | Purpose |
|---|---|---|
| `/pwdev-social-media:init` · `:status` | `$social-contexto` | brand context, keys, current mode |
| `:criar` | `$social-criar` | end-to-end production |
| `:gerar` | `$social-imagem` | one AI-generated asset |
| `:carrossel` | `$social-carrossel` | full carousel |
| `:video` | `$social-video` | script, storyboard and AI clip |
| `:revisar` | `$social-revisao` | quality gate |
| `:exportar` | `$social-entrega` | delivery package |
| `:custo` | `$social-custo` | estimate, budget, spend |
| `:formatos` | `$social-formatos` | sizes, safe zones, every format |
| `:lote` | `$social-lote` | hook × visual × format test batch |

Hermes: `skill_view("pwdev-social-media:social-<name>")`.

The four Claude Code subagents (`art-director`, `asset-generator`, `figma-builder`, `creative-reviewer`)
run inline on Codex and Hermes.

## Security

- **Money:**
  - no generation without `pwdev-media gerar --estimar` and the person's explicit yes;
  - `--confirmar` and the monthly budget are enforced by the core;
  - identical requests are reused for free.
- **Keys:** in the Keychain or the environment, never in project files, the context file or the
  conversation.
- **No simulated results:** without a key or Figma, the skill says "NÃO GERADO" / "not composed" and
  delivers the prompt or a spec.
- **Accessibility is a gate:** contrast, safe zone and alt text can fail a piece.
- **Never publishes.**

## Migrating from v2

Install `pwdev-media`, run `/pwdev-social-media:init` to store the keys, and see
[`CHANGELOG.md`](./CHANGELOG.md):
- the bash scripts are gone;
- skills were renamed with the `social-` prefix (Claude command names are unchanged);
- generations are now recorded in the `pwdev-media` ledger.

## Development

```bash
python3 -m unittest tests.test_pwdev_social_media
claude plugin validate plugins/pwdev-social-media
hermes plugins doctor --ci plugins/pwdev-social-media
```

## Credits

Derived from [social-media-skills](https://github.com/blacktwist/social-media-skills) (MIT). See
`NOTICE.md`. Apache-2.0.
