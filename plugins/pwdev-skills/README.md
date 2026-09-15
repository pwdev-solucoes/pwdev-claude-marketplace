# PWDEV Skills — Skill Engineering (Claude Code, Codex, Hermes, OpenCode)

Review, refactor and benchmark Agent Skills in Claude Code, Codex, Hermes Agent and OpenCode.
The plugin ships one skill, `skill-refactor`, and the scripts it uses to measure a skill on the
models that are actually available on this machine. The same four runtimes are the ones the
benchmark drives.

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
| `scripts/bench.py` + `runtimes.py` + `grade.py` | Headless A/B benchmark across runtimes and models — arms `candidate`, `baseline` and `no_skill` — in two modes: `refactor` (skill-refactor on a fixture skill, graded from invariants) and `task` (**any skill doing its own job**, graded by the checks each case declares), under a budget |
| `scripts/cases.py` | Cases for a skill: `refactor` kind (invariants and defects by script, requests proposed by one headless call) or `task` kind (tasks with synthetic input files and objective checks proposed by one call, schema-validated); human approval pinned to the source hash |
| [`.opencode-plugin/install.py`](./.opencode-plugin/install.py) | OpenCode adapter: links or copies the skills into `~/.config/opencode/skills/` or `<project>/.opencode/skills/`, and uninstalls only what it installed |

Ships 1 skill. No commands, subagents, hooks or MCP server.

## Requirements

- Python 3.10 or later for the scripts; `pip install tiktoken` for measured token counts (without it, sizes are labelled `estimate`).
- For benchmarks: the runtimes you want to measure on `PATH` and already signed in (`claude`, `codex`, `hermes`, `opencode`). Run `scripts/discover.py` to see what is usable.

## Setup

Clone this marketplace and work from its root. Nothing installs itself; the only step that writes outside the checkout is the OpenCode installer below, and only into OpenCode's skills folder, when you run it.

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

**OpenCode** — OpenCode has no plugin mechanism for skills; it discovers `SKILL.md` folders
([opencode.ai/docs/skills](https://opencode.ai/docs/skills)). The plugin ships an installer that
links (or copies) its skills where OpenCode looks, and removes only what it installed:

```bash
python3 plugins/pwdev-skills/.opencode-plugin/install.py               # ~/.config/opencode/skills (symlink)
python3 plugins/pwdev-skills/.opencode-plugin/install.py --project .   # ./.opencode/skills of a project
python3 plugins/pwdev-skills/.opencode-plugin/install.py --uninstall
```

The agent lists the skill and loads it on demand through its native `skill` tool; the scripts run
from the installed folder. A Claude Code *plugin* install lives in Claude's plugin cache, not in
`~/.claude/skills/`, so it does not make the skill visible to OpenCode — the installer does. See
[`.opencode-plugin/README.md`](./.opencode-plugin/README.md).

## Using the skill

Ask in natural language, in the runtime that loaded the plugin (Codex: `$skill-refactor`; Hermes:
`skill_view("pwdev-skills:skill-refactor")`; OpenCode loads it through its `skill` tool). Say whether
you want a **review** (read-only) or a **refactor** (edits authorized), and where artifacts may go.

**Review a skill without touching it**

```text
Review plugins/my-plugin/skills/reports/SKILL.md without editing any file.
Consumers: small models in the lean profile. Tell me how to measure the effect.
```

You get three parts: findings named by category (duplication, contradiction, unconditional
reading, over-broad or under-specific description, procedure without purpose) with the lines they
come from; proposed changes tied to the requirement each one preserves; and how to verify the
effect — static size first, then an A/B by cost per accepted task. Nothing is written to disk.

**Refactor with edits authorized**

```text
Refactor plugins/my-plugin/skills/reports/SKILL.md and its resources.
Consumers: Sonnet in lean, every other model in guided.
Preserve the name, paths, metadata and exact output labels. Do not run benchmarks.
Baseline and report in .planning/refactor/reports/.
```

The skill keeps a baseline of the original files, applies the change, checks frontmatter, links and
mandatory behavior, and closes with every label it earned: `refactored`, `statically validated`
and — only after paired runs on real models — `behaviorally evaluated`.

**Measure a skill on real models**

```text
Compare the previous version of plugins/my-plugin/skills/reports with the candidate on the
same cases, on Sonnet 5 and gpt-5.6-terra at medium effort, two repetitions, budget US$ 5.
```

The skill plans the A/B from what `discover.py` finds on this machine and runs it with `bench.py`
only under an explicit budget. The result is a paired table per case and model — previous ×
candidate × no skill — decided by cost per accepted task, never by file size. Any skill can be
measured on its own tasks (`task` mode); the [usage guide](./docs/guia-de-uso.md) walks through
each scenario and the [manual](./docs/manual-de-uso.md) documents every script option.

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
- In task mode only the declared checks are graded; quality beyond them needs a human reading of `outputs/`.
