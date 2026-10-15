# Changelog — pwdev-video-tutorial

## 0.1.0 — 2026-10-14

First release.

- Explainer, tutorial, onboarding and "what's new" videos of software systems, built from the real
  system: nothing on screen that the system does not do.
- `vtut-explorar`: code scan (`tutorial.py codigo`: Laravel, Next.js, SvelteKit, React Router, Vue
  Router, Django, Rails and Express routes; menu links; forms and personal-data fields;
  permissions) crossed with live navigation through playwright-cli (login done by the person, saved
  session, snapshots and screenshots), route coverage and a sourced system map.
- `vtut-roadmap`: series of videos by audience and module with objective, prerequisites, routes,
  target duration, format and priority, validated into a production order
  (`pwdev-roadmap-videos/1`).
- `vtut-roteiro`: storytelling structure (hook → context → demonstration → result → next step),
  narration and screen actions with verified locators (`pwdev-roteiro-tutorial/1`), personal-data
  fields refused unless fictitious or masked.
- `vtut-narrar`: free local pt-BR narration with Kokoro through the HyperFrames CLI (`pf_dora`,
  `pm_alex`, `pm_santa`), the person's own recordings, or ElevenLabs through pwdev-media.
- `vtut-gravar`: playwright-cli `run-code` recording with `page.screencast`: chapter cards, orange
  outline and note on each target, human typing, CSS blur on masked fields across navigations,
  each scene held for its narration; per-action timings and target boxes (`cenas.json`) and one
  screenshot per scene.
- `vtut-montar`: recording + narration into a video-plugin edit folder (normalized loudness,
  captions from the narration transcript or, as a fallback, from the script text), click-zoom
  blocks and readable `caixa` captions for pwdev-video-hyperframes; text tutorial with screenshots.
- `vtut-revisar`: sync, masking and chapter checks, render with the tutorial gate profile
  (`--max-silencio 5`).
- Portable skills for Claude Code, Codex and Hermes Agent; commands are thin wrappers.
