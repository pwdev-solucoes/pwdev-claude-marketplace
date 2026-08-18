# Model Profiles

Turn count beats token price. A cheap model that needs four rounds and a fix loop costs more
than a mid-tier one that lands the task, and it costs the human's attention too. Route
deliberately; never omit the model and inherit the session's.

## Profiles

`config.json` carries `model_profile`, one of `economy`, `balanced` (default), `performance`.

| Role | economy | balanced | performance |
|---|---|---|---|
| implementer | mid | mid | top |
| task-reviewer | mid | mid | top |
| verifier | mid | top | top |
| roadmap | mid | mid | top |
| mapper | cheap | mid | mid |

Read "cheap", "mid" and "top" as tiers of whatever family the runtime offers, not as fixed
names. The mapper is the one role that reads widely and writes little, so it does not need the top
tier — but never give it the smallest one either, since deciding what is worth recording is a
judgement.

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

Rounds 1–3 keep the original implementer and its model. Rounds 4–5 use a fresh implementer one
tier up. Repeating the same model on the same failure with nothing changed is not a retry, it
is a loop.

## Explicit overrides win

`model_overrides` in `config.json`, keyed by role name, beats everything above. It exists so
the human can pin a choice; respect it without arguing.
