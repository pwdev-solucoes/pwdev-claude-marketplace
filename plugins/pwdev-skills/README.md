# PWDEV Skills — Skill Engineering (Claude Code, Codex, Hermes)

Review, refactor and benchmark Agent Skills in Claude Code, Codex and Hermes Agent. The
benchmark also drives OpenCode. The plugin ships one skill, `skill-refactor`, and the scripts it
uses to measure a skill on the models that are actually available on this machine.

> [Versão em Português](./README.pt-BR.md) · [Guia de uso (PT-BR)](./docs/guia-de-uso.md) · [Manual de uso (PT-BR)](./docs/manual-de-uso.md) · [Metodologia de refatoração (PT-BR)](./docs/metodologia-de-refatoracao.md)

## What's inside

| Part | Purpose |
| --- | --- |
| [`skills/skill-refactor/SKILL.md`](./skills/skill-refactor/SKILL.md) | Review or refactor a skill: a smaller always-loaded core, conditional references, preserved behavior, lean/guided profiles |
| `references/refactoring.md` | The refactoring protocol, the ten optimization rules, and profile selection by measurement |
| `references/evaluation.md` | A/B evaluation: acceptance, cost per accepted task, context, triggering precision/coverage |
| `references/runtimes.md` | The headless contract per runtime: command vectors, usage and cost sources, safety rules |
| `scripts/discover.py` | Which runtimes are installed and signed in, their default model and effort, and the models each one can run |
| `scripts/tokens.py` | Size per file, context layer and load scenario with a generic tokenizer (`tiktoken`) |
| `scripts/bench.py` + `runtimes.py` + `grade.py` | Headless A/B benchmark across runtimes and models — arms `candidate`, `baseline` and `no_skill` — graded from each case's invariants, under a budget |
| `scripts/cases.py` | Cases derived from the skill under refactoring: invariants and defects by script, requests and trigger queries proposed by one headless call, human approval pinned to the source hash |
| `evals/evals.json` | Fixture, cases, trigger and routing checks, default matrix and dated pricing |

Ships 1 skill. No commands, subagents, hooks or MCP server.

## Requirements

- Python 3.10 or later for the scripts; `pip install tiktoken` for measured token counts (without it, sizes are labelled `estimate`).
- For benchmarks: the runtimes you want to measure on `PATH` and already signed in (`claude`, `codex`, `hermes`, `opencode`). Run `scripts/discover.py` to see what is usable.

## Setup

Clone this marketplace and work from its root. Nothing installs itself or changes personal configuration.

**Claude Code** — install from the marketplace, or load the checkout for one session:

```bash
claude plugin install pwdev-skills@pwdev-claude-marketplace
claude --plugin-dir ./plugins/pwdev-skills
```

The skill is available as `pwdev-skills:skill-refactor` and triggers from requests such as "review this SKILL.md".

**Codex** — open this checkout and load `plugins/pwdev-skills` through the Codex local-plugin
mechanism. `.codex-plugin/plugin.json` declares `"skills": "./skills/"`; invoke `$skill-refactor`.

**Hermes Agent** — inspect the package before enabling anything:

```bash
hermes plugins doctor plugins/pwdev-skills
```

The adapter registers `skill-refactor` as a `pathlib.Path` with no hook. The skill is larger than
Hermes' inline bootstrap limit, so it is listed and loaded on demand with
`skill_view("pwdev-skills:skill-refactor")`.

## Measuring a skill

```bash
cd plugins/pwdev-skills/skills/skill-refactor
python3 scripts/discover.py                          # runtimes, defaults, models available here
python3 scripts/tokens.py <skill-dir> --baseline <previous-version>
python3 scripts/bench.py --skill <skill-dir> --baseline git:<sha> --runtimes auto \
  --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F) --budget-usd 5
```

Use a temporary `--out`: a round writes workspaces and version copies that contain `SKILL.md`
files. `--publish` copies only `summary.json`, `benchmark.md` and `tokens.json` into the skill.

## Security

- **Benchmarks make paid calls.** Every case, version, runtime, model and repetition is one call. Runs are ordered cheapest first and stop at `--budget-usd`; Claude runs also carry `--max-budget-usd`.
- **Bypass flags stay in a throw-away workspace.** Each call runs with the runtime's approval bypass inside a fresh temporary directory. Every protected path is fingerprinted before and after, and any change outside the workspace fails the run.
- **Hermes** headless mode bypasses approvals, so it runs only with `--acknowledge-hermes-automation`.
- **Free OpenCode Zen models may retain or train on prompts** ([opencode.ai/docs/zen](https://opencode.ai/docs/zen/)). Do not benchmark unpublished or confidential skills on them.
- **Secret handling.** Stored records pass through a sanitizer that redacts tokens, API keys, bearer headers and home-directory paths. Discovery never records e-mail addresses, organization ids or key fragments.

## Limits

- One benchmark repetition characterizes nothing. Treat single runs as direction, not as a claim of efficiency.
- Codex on a ChatGPT plan is not billed per token. Its costs are API-price equivalents.
- Claude Code has no model-listing command: discovery reports the documented aliases and cached options.
- Runtimes expose the skill differently: Claude Code through a generated plugin, Codex and Hermes through `AGENTS.md`, OpenCode natively. Token comparisons across runtimes are approximate.
