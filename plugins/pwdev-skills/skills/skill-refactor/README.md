---
okf_version: "0.2"
type: usage-guide
title: "Skill Refactor"
generated:
  by: "agent:codex"
  at: "2026-09-12T23:39:51Z"
lifecycle:
  status: draft
  updated_at: "2026-09-13T20:30:12Z"
sources:
  - resource: "docs/skill-refactoring-guide.md"
  - resource: "https://claude.com/plugins/skill-creator"
verified:
  - event: static_validation
    by: "agent:claude"
    at: "2026-09-13T20:30:12Z"
    scope: "README.md"
    source: "quick_validate.py (skill-creator) on the skill folder: Skill is valid!; relative links resolved from each referencing file; tests.test_marketplace_readmes + tests.test_readme_marketplace: 9 tests OK"
---

# Skill Refactor

[Entry skill](SKILL.md) for refactoring other skills from the guide: preserve their
requirements, shrink the always-loaded core, and measure efficiency only when
comparable runs exist. The references are portable; the source repository is not
required at install time.

## Usage

In the runtime that loaded the skill, invoke `skill-refactor` with the target and the
intent. Example requests:

```text
Use skill-refactor to refactor skills/summary/SKILL.md and its resources.
Consumers: model X in the lean profile; every other model in guided.
Preserve the current requirements and prepare the evaluation cases.
```

```text
Use skill-refactor to review skills/summary/SKILL.md without editing files.
Point out the changes that would reduce context and how to measure their effect.
```

```text
Use skill-refactor to compare the summary candidate with the previous version.
Run only the two models I named, with three cases, one repetition, and the
budget authorized in this task.
```

The executor profile controls the guidance the refactorer receives; the target
profiles control the core and the support delivered inside the refactored skill.
Profiles come from the request — an unspecified profile resolves to `guided` — and
`lean`/`guided` are defined in [the refactoring protocol](references/refactoring.md).

## Distribution and validation

The folder ships in the `pwdev-skills` plugin (`plugins/pwdev-skills/skills/skill-refactor`),
exposed as `pwdev-skills:skill-refactor` in Claude Code, `$skill-refactor` in Codex and
`skill_view("pwdev-skills:skill-refactor")` in Hermes. It can also be copied as a unit
to any runtime compatible with Agent Skills. Invocation syntax and discovery depend on
the host. A change in this source tree does not install or update user caches.

`SKILL.md` follows the Agent Skills format, with provenance under `metadata`. This
README and `references/` follow OKF v0.2. The sibling skills in this plugin do not use
OKF; validate each kind with its own tool: the runtime entry with skill-creator's
`scripts/quick_validate.py` when that plugin and its dependencies are installed, the
narrative documents with an OKF validator when one is available.

The [evaluation cases](evals/evals.json) cover a real refactoring, an unknown model,
and a review-only request. `fixture_protocol` in that file describes how a harness
materializes the embedded fixture; `fixture`, `matrix`, `trigger_evals`, and
`routing_checks` are harness extensions that stock skill-creator scripts are not
assumed to run.

## Measuring

```bash
# what can run here: runtimes installed and signed in, default model/effort, models per runtime
python3 scripts/discover.py                                               # add --json for data

# sizes per file, context layer and load scenario; generic tokenizer, deltas against a baseline
python3 scripts/tokens.py . --baseline /path/to/previous-version        # add --json for data

# the matrix: cases × {candidate, baseline, no_skill} × (runtime, model), graded objectively, under a budget
python3 scripts/bench.py --skill . --baseline git:<sha> --no-skill-arm --out "$(mktemp -d)" --publish evals/benchmarks/$(date +%F) \
  --runtimes claude,codex,hermes,opencode \
  --claude-models claude-haiku-4-5-20251001,claude-sonnet-5 \
  --codex-models gpt-5.6-luna,gpt-5.6-terra \
  --hermes-model <model chosen by you> --hermes-provider openrouter \
  --opencode-models opencode/big-pickle \
  --acknowledge-hermes-automation --budget-usd 5

# cases in the domain of the skill being refactored: extract (free) -> propose (one call) -> approve (you)
python3 scripts/cases.py --extract /path/to/that-skill
python3 scripts/cases.py --propose /path/to/that-skill/evals/cases/<name> --runtime claude --model claude-sonnet-5
python3 scripts/cases.py --approve /path/to/that-skill/evals/cases/<name> --skill /path/to/that-skill
python3 scripts/bench.py --skill /path/to/that-skill --cases /path/to/that-skill/evals/cases/<name> ...

# a finished round after a grader or classifier fix: re-grade from disk, no new calls
python3 scripts/bench.py --regrade <out-dir> --cases evals/evals.json --publish evals/benchmarks/<date>
```

`tokens.py` uses `tiktoken` (`pip install tiktoken`) and labels every number `estimate`
when it is missing. `bench.py` makes **paid calls**: one per case, version, runtime,
model and repetition, cheapest models first, stopping at the budget (Claude runs also
carry `--max-budget-usd`). It needs the runtimes on `PATH` and their own sessions
logged in, runs each call inside a throw-away workspace with the runtime's bypass flags
(see [the runtime contract](references/runtimes.md)), and fails the round if anything
outside that workspace changes. Hermes runs only with `--acknowledge-hermes-automation`.
`--dry-run --fake-bin <dir>` exercises the whole pipeline with fake executables; the
marketplace's `tests/test_skill_refactor_bench.py` does exactly that. Keep `--out` outside the
skill: a round writes workspaces and version copies that contain `SKILL.md` files, and
`--publish` copies only the summaries back.

Outputs land in `evals/benchmarks/<date>/`: `summary.json` (per-model efficiency table,
runtime versions, cost), `benchmark.md`, `tokens.json`, and — when the skill-creator
plugin is installed — its `benchmark.json` and a static `review.html`.

Profiles declare an intent to support. Only results obtained on the real models can
demonstrate performance or behavioral compatibility across them.
