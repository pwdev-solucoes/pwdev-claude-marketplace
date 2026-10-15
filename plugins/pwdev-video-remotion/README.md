# PWDEV Video Remotion

Talking-video editing by conversation with [Remotion](https://www.remotion.dev) (React). The flow and
the `projeto.json` are the same as `pwdev-video-hyperframes`; only the rendering engine changes. Works
on Claude Code, Codex and Hermes Agent. Conversation is in Brazilian Portuguese by default.

## When to use it

- Your team works in React and wants scenes as typed components.
- Data-driven batches (many versions from a spreadsheet) or distributed rendering (Remotion Lambda).
- The Remotion license covers you: individuals and companies of up to 3 people are free; larger
  companies need the Company License (see [`references/licenca.md`](./references/licenca.md)).

Otherwise use `pwdev-video-hyperframes` (Apache-2.0), the suite default.

## What it does

- **Cut by the waveform:** no breaths, last good take, word endings kept (shared `pwdev-media` core).
- **On screen:**
  - captions of up to 3 words with the spoken word highlighted;
  - eased zooms;
  - labels and titles inside the safe zone;
  - custom scenes as React components in `compositions/*.tsx`.
- **Sound:** music with fades and effects on the motion frame.
- **Review and render:**
  - Remotion Studio in the background;
  - PNG frames for review;
  - a render quality gate that must print **PASSOU**.

## Installation

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-remotion@pwdev-claude-marketplace
```

In a new conversation: `/pwdev-video-remotion:init` (Codex: `$vrm-setup`). It checks, without sudo:
- the license;
- the `pwdev-media` CLI;
- ffmpeg;
- Node 20+;
- the official Remotion skills.

Each project runs `npm install` once.

## Commands

| Claude Code | Codex / Hermes | Purpose |
|---|---|---|
| `/pwdev-video-remotion:init` · `:status` | `$vrm-setup` | license and tools |
| `:editar` | `$vrm-editar` | full edit (start here) |
| `:corte` | `$vrm-corte` | cut only, or adjust the cut |
| `:plano` | `$vrm-plano` | what appears on screen and when |
| `:cenas` | `$vrm-cenas` | custom React scene |
| `:som` | `$vrm-som` | music and sound effects |
| `:revisar` | `$vrm-revisar` | full video, render and delivery |
| `:versoes` | `$vrm-variacoes` | hooks, formats, versions, data-driven batches |

Pinned versions: Remotion 4.0.535, React 19.3.1, TypeScript 5.9.3.

## Security

- Raw recordings are never modified, moved or deleted; media is copied into the project's `public/`.
- Everything runs locally. Paid AI generation happens only through `pwdev-media`, after an estimate
  and an explicit yes.
- Renders are deterministic: scenes use no clock, randomness or network (enforced by tests).
- The Remotion license is checked before the first project.

## Development

```bash
python3 -m unittest tests.test_pwdev_video_remotion tests.test_pwdev_media_video
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_remotion
claude plugin validate plugins/pwdev-video-remotion
hermes plugins doctor --ci plugins/pwdev-video-remotion
```

## License

The plugin and template are Apache-2.0. The `remotion` and `@remotion/*` packages installed in a
project follow the Remotion license. Montserrat is under the SIL Open Font License.
