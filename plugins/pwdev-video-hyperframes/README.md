# PWDEV Video HyperFrames

Talking-video editing by conversation: ads, Reels, TikTok, VSLs, lessons and answers. Hand over the
folder with the recordings and talk; the agent cuts, builds and renders with
[HyperFrames](https://github.com/heygen-com/hyperframes) (HTML → MP4, Apache-2.0), showing everything
in the studio before rendering. Works on Claude Code, Codex and Hermes Agent. Conversation is in
Brazilian Portuguese by default.

## What it does

- **Cut by the waveform:**
  - transcribes locally and splits the speech into phrases;
  - keeps the last good take;
  - removes every silence of 0.25 s or more without clipping word endings.
- **Block plan:** one idea at a time, something changes every 2–4 s.
- **On screen:**
  - captions of up to 3 words with the spoken word highlighted;
  - camera zooms;
  - labels and titles inside each platform's safe zone;
  - custom animated scenes written with the official HyperFrames skills.
- **Sound:** effects synced to motion, music 22–24 dB under the voice.
- **Review:** an 8–15 s studio sample first.
- **Render:** the pinned HyperFrames version, with a quality gate that must print **PASSOU**.
- **Versions:** hook batches, other formats, short cuts.

## Installation

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace
```

In a new conversation: `/pwdev-video-hyperframes:init` (Codex: `$vhf-setup`). It checks and
installs, without sudo:
- the `pwdev-media` CLI;
- ffmpeg, in `~/.pwdev/bin`;
- Node 22+;
- the official HyperFrames skills.

It also turns HyperFrames telemetry off.

## Commands

| Claude Code | Codex / Hermes | Purpose |
|---|---|---|
| `/pwdev-video-hyperframes:init` · `:status` | `$vhf-setup` | prepare and check tools |
| `:editar` | `$vhf-editar` | full edit (start here) |
| `:corte` | `$vhf-corte` | cut only, or adjust the cut |
| `:plano` | `$vhf-plano` | what appears on screen and when |
| `:cenas` | `$vhf-cenas` | custom animated scene |
| `:som` | `$vhf-som` | music and sound effects |
| `:revisar` | `$vhf-revisar` | full video, render and delivery |
| `:versoes` | `$vhf-variacoes` | hooks, formats, short versions |

`projeto.json` uses the schema `pwdev-projeto-video/1`, shared with `pwdev-video-remotion`.

## Security

- Raw recordings are never modified, moved or deleted.
- Everything runs locally. Paid AI generation happens only through `pwdev-media`, after an estimate
  and an explicit yes.
- The project's GSAP copy is pinned and verified by SHA-384; the CDN fallback carries SRI.
- HyperFrames telemetry is off in every call the plugin makes.

## Development

```bash
python3 -m unittest tests.test_pwdev_video_hyperframes tests.test_pwdev_media_video
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_hyperframes
claude plugin validate plugins/pwdev-video-hyperframes
hermes plugins doctor --ci plugins/pwdev-video-hyperframes
```

## License

Apache-2.0. The template's Montserrat font is under the SIL Open Font License.
