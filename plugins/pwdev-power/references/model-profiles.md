# Model Profiles

Turn count beats token price. A cheap model that needs four rounds and a fix loop costs more
than a mid-tier one that lands the task, and it costs the human's attention too. How a tier is
applied depends on the active runtime.

## Runtime application

- **Codex** inherits host or session model and reasoning-effort settings by default. Explicit user,
  governance, configuration, or approved-profile overrides win, but only when the host exposes a
  supported model-and-effort combination.
- **Claude Code** keeps explicit model routing from the profile table on every dispatch. Its fix
  rounds escalate one tier and its final review uses the most capable supported model as described
  by the execution skill.
- **Hermes Agent** follows [hermes-tools](hermes-tools.md) and the runtime mapping. Use documented
  model/provider controls where available, and never invent per-dispatch parameters.

## Profiles

`config.json` carries `model_profile`, one of `economy`, `balanced` (default), or `performance`.
The table drives Claude Code's explicit routing. On Codex it applies only as an approved override;
on Hermes Agent it is realized only through the controls documented by its adapter.

| Role | economy | balanced | performance |
|---|---|---|---|
| implementer | mid | mid | top |
| task-reviewer | mid | mid | top |
| verifier | mid | top | top |
| roadmap | mid | mid | top |
| mapper | cheap | mid | mid |

Read "cheap", "mid" and "top" as tiers of whatever family the runtime offers, not as fixed
names. Before applying a tier, inspect that runtime and choose only a supported model-and-effort
combination. The mapper is the one role that reads widely and writes little, so an explicit route
does not need the top tier — but do not give it the smallest one either, since deciding what is
worth recording is a judgement.

## Complexity overrides the profile row

The plan declares `Complexity:` per task. For the implementer, that wins over the profile:

| Complexity | Tier |
|---|---|
| low — mechanical, one or two files | cheapest tier that is not the smallest |
| medium — integration across a couple of modules | mid |
| high — architecture, concurrency, security, data migration | top |

Two floors that always hold: never the smallest tier for an implementer or reviewer that
works from prose, and `economy` never escalates to the top tier. Fix plans are implicitly
`high`.

## Fix rounds escalate

Rounds 1–3 keep the original implementer and its settings. Rounds 4–5 use a fresh implementer.
Claude Code moves one tier up; Codex does so only when an explicit override applies; Hermes Agent
uses only its documented route. Escalate only to a choice the runtime supports. Repeating the same
setup on the same failure with nothing changed is not a retry, it is a loop.

## Explicit overrides win

Explicit user instructions, repository governance, and `model_overrides` in `config.json` take
precedence over the profile table. A role-keyed override lets the human pin a choice; respect it
when the runtime supports the requested model-and-effort combination. If it does not, report the
unsupported override instead of guessing a substitute.
