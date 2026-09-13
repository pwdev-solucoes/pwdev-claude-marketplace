# Runtime smoke evidence

Observed on 2026-09-13 in an authorized isolated test. Plugin source was always the repository-local
`plugins/pwdev-qa` directory; report outputs used a newly created isolated temporary directory.
No runtime was installed, enabled, trusted, or copied into personal configuration. A runtime is
VERIFIED only after successful `qa-tooling discovery`, real invocation producing the
`missing-tool response`, and the `fixture report` generation/inspection in that same runtime.

## Result summary

| runtime | exact version | status | discovery | missing-tool response | fixture report | limitations |
|---|---|---|---|---|---|---|
| Claude Code | `2.1.269 (Claude Code)` | UNVERIFIED | session-only plugin inventory found `qa-tooling` | NOT_RUN | NOT_RUN | non-interactive invocation stopped before a model turn because OAuth refresh failed |
| Codex | `codex-cli 0.153.4` | UNVERIFIED | effective ephemeral skill catalog did not expose `qa-tooling` | probe ran, but the skill response was BLOCKED | successful export, parse and inspection | report succeeded, but required skill discovery/invocation did not |
| Hermes Agent | `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29` | UNVERIFIED | doctor passed manifest/import/registration only | NOT_RUN | NOT_RUN | installed help exposes no session-local plugin-path load; safe isolation disables plugins and the remaining mode may load an existing `.env`, which this task must not read |

No row is VERIFIED. `successful` below describes an individual probe only and never upgrades a
runtime whose complete three-step smoke did not pass.

## Claude Code

- Version command/probe: `claude --version` → `2.1.269 (Claude Code)`.
- Local help used: `claude --help`, `claude plugin --help`, and
  `claude plugin details --help`. Help documents `--plugin-dir`, `-p/--print`,
  `--no-session-persistence`, `--permission-mode dontAsk`, and session-only plugins.
- Discovery command/probe: `claude --plugin-dir plugins/pwdev-qa plugin details pwdev-qa` was
  successful. It reported PWDEV QA 0.1.0, `qa-tooling`, `qa-report`, zero agents, zero hooks and zero
  MCP servers. The same output also exposed the 10 command wrappers as invocable components, so its
  39-item UI inventory is 29 skills plus 10 wrappers, not 39 shipped skill files.
- Invocation command/probe: a `claude --plugin-dir <absolute-plugin-path> ... -p <bounded-smoke>`
  run used `dontAsk`, no session persistence, strict MCP configuration and only the required local
  paths. Result: `Failed to authenticate: OAuth session expired and could not be refreshed`.
- Evidence/result: discovery succeeded; no model turn invoked `qa-tooling`, no missing-tool table
  was produced, and no fixture report was created. Status is UNVERIFIED.

## Codex

- Version command/probe: `codex --version` → `codex-cli 0.153.4`.
- Local help used: `codex --help`, `codex exec --help`, `codex plugin --help`,
  `codex plugin marketplace add --help`, and `codex plugin add --help`. The installed executable
  documents marketplace installation but no session-only local plugin path for `codex exec`; this
  smoke did not mutate configuration to manufacture discovery.
- Invocation command/probe: `codex exec --ephemeral --ignore-user-config --ignore-rules
  --skip-git-repo-check --sandbox workspace-write --add-dir <absolute-plugin-path> <bounded-smoke>`
  ran from `/tmp/pwdev-qa-codex.xV0pUf`. The effective catalog explicitly lacked an invocable
  `qa-tooling`; reading `SKILL.md` was correctly refused as proof of discovery.
- Missing tool command/probe: `command -v playwright-cli-does-not-exist` → exit `1`, empty output.
  Observed result: `NOT_RUN`/`BLOCKED`, with no installation and no fabricated execution.
- Fixture report command/probe: the declared Python 3.12 executable ran repository-local
  `qa_demo.py --output-dir ./codex-fixture` once. It returned exit `0`,
  `export_status=complete`, `verdict=FAIL`, and a publication digest. Codex inspected
  `manifest.json` and `report.html`, parsed the 171-page `report.pdf` with pypdf, and observed
  `BUG-OPEN-UNMAPPED` plus both withholding diagnostics.
- Evidence/result: report production is successful, but discovery and skill invocation are not;
  status remains UNVERIFIED.

## Hermes Agent

- Version command/probe: `hermes --version` →
  `Hermes Agent v0.21.1 (2026.9.7) · upstream 564aef29` (Python 3.11.16, OpenAI SDK 2.24.0).
- Local help used: `hermes --help`, `hermes chat --help`, `hermes plugins --help`,
  `hermes plugins doctor --help`, and `hermes skills --help`.
- Discovery command/probe: `hermes plugins doctor plugins/pwdev-qa --ci` was successful for
  runtime discovery, manifest parsing, adapter import and registration. This is packaging evidence,
  not `skill_view`/chat invocation evidence.
- Isolation decision: help states `--safe-mode` disables plugins, while `--ignore-user-config`
  still permits credentials from `.env`; plugin/skill help offers installation or project trust,
  not a session-local path. Repository governance forbids reading existing `.env` content and this
  task forbids changing installation/trust/configuration. No unsafe or stateful workaround ran.
- Evidence/result: missing-tool response and fixture report are NOT_RUN; status is UNVERIFIED.

## playwright-cli probes

The official/local contract requires both paths to be distinguished; `npx` presence alone is not
Playwright evidence.

| command/probe | observed result | evidence and limitations |
|---|---|---|
| `playwright-cli --version` | `0.1.14` | installed global CLI is available |
| `npx --no-install playwright --version` | `Version 1.61.1` | positive local package probe in this checkout; `--no-install` prevented fallback download |
| `npx playwright cli --help` | successful `playwright-cli` help | documented local `npx playwright cli` entry was resolved only after the positive no-install probe |
| `playwright-cli -s=qa-f05-24-report open http://127.0.0.1:18765/report.html` followed by `snapshot`, `screenshot --filename=/tmp/pwdev-qa-f05-24-report.png`, and `close` | successful task-owned session | localhost served the generated static report because the CLI blocks `file:` URLs; screenshot was visually reviewed and not attached as fixture evidence |

An exploratory probe from `/tmp` invoked `npx playwright cli --version` before a local-package
preflight and emitted `The following package was not found and will be installed: playwright@1.63.0`.
That probe is non-compliant with the no-install contract, is excluded from availability evidence,
and may have populated the npm cache. No deletion or further modification of that personal cache
was attempted. The authoritative results are the later checkout-local no-install probe and entry
help above.
