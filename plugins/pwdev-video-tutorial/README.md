# PWDEV Video Tutorial

Explainer, tutorial, onboarding and "what's new" videos of **software systems**, built from the real
system. The agent reads the codebase and navigates the system with `playwright-cli`, understands
screens, flows and permissions, plans the video series, writes storytelling scripts, narrates,
records the screen and assembles the final video with captions and click zoom, plus a text tutorial
with screenshots. Works on Claude Code, Codex and Hermes Agent. Conversation and narration default
to Brazilian Portuguese.

```
code + navigation ─▶ system map ─▶ video roadmap ─▶ script ─▶ narration ─▶ recording
                  ─▶ assembly (captions, zoom) ─▶ review + render ─▶ video + tutorial.md
```

## Installation

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace
claude plugin install pwdev-video-tutorial@pwdev-claude-marketplace
```

Then `/pwdev-video-tutorial:init` (Codex: `$vtut-setup`).

## Commands

| Claude Code | Codex / Hermes | What it does |
|---|---|---|
| `/pwdev-video-tutorial:init` · `:status` | `$vtut-setup` | playwright-cli, local voice, assembly tools |
| `:explorar` | `$vtut-explorar` | code scan + live navigation → system map |
| `:roadmap` | `$vtut-roadmap` | video series: objective, audience, order, priority |
| `:roteiro` | `$vtut-roteiro` | storytelling script with verified screen actions |
| `:narrar` | `$vtut-narrar` | narration per scene: free local voice, own voice or ElevenLabs |
| `:gravar` | `$vtut-gravar` | records the screen by running the script |
| `:montar` | `$vtut-montar` | final video (captions, click zoom) + text tutorial |
| `:revisar` | `$vtut-revisar` | checks, renders with the gate and delivers |

## Security and privacy

- **Passwords:** the person logs in by themselves in a visible browser; only the session is saved
  (`sessao.json`, never committed).
- **Personal-data fields:** e-mail, tax id, phone, password, card and address fields accept only
  fictitious values or selectors listed in `mascarar`, which blurs them for the whole recording.
- **Environment:** recording targets a staging environment; production only with an explicit yes
  and without submitting forms.
- **Local by default:** nothing leaves the machine unless the paid ElevenLabs voice is chosen
  (estimate and yes first).

## Development

```bash
python3 -m unittest tests.test_pwdev_video_tutorial
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_tutorial
claude plugin validate plugins/pwdev-video-tutorial
hermes plugins doctor --ci plugins/pwdev-video-tutorial
```

## License

Apache-2.0.
