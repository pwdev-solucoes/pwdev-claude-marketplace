# Collaboration

## Gates are human

A gate is a point where you stop, present, and wait. You may not approve your own work,
infer approval from silence, or treat "looks good" on a different question as approval of
this one. When a gate is refused, record `REJECTED` and stop — do not retry the same
artifact with cosmetic changes.

Gates in this plugin:

| Gate | Owner | Recorded in |
|---|---|---|
| Requirement approved | human | `state.md` + `Status:` in `prd.md` |
| Roadmap accepted | human | `state.md` |
| Design approved | human | `state.md` + exactly one `Status: APPROVED` in `spec.md` |
| Plan approved | human | `state.md` |
| Verification verdict | verifier, then human on REJECTED | `verdict.md` + `state.md` |
| Fleet launch acknowledged | human | fleet member record |

## Ask one question at a time

When you need information from the human, ask one question and wait. A numbered list of six
questions reads as a form and gets answered as a form — shallowly. Interviews in this plugin
are capped in rounds, not in questions per round, so use the rounds.

## Status contracts are short

A subagent's final message is a status, not a report. The report goes in a file; the status
comes back in at most ten lines. The orchestrator reads the status and the artifact path —
**never paste a report's contents into the orchestrating context.** That single rule is what
keeps a long feature affordable.

Implementer status:

```text
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
REPORT: <path>
COMMITS: <base7>..<head7>
NOTE: <one line, optional>
```

Reviewer status:

```text
SPEC: PASS | FAIL
QUALITY: PASS | FAIL
FINDINGS: <count by severity>
REVIEW: <path>
```

## Language

`config.json` carries `language`. Conversation and generated artifacts follow it. Skill and
reference files themselves stay in English regardless, because that is what the runtime
adapters read.

## Rulings

When you resolve an ambiguity that the plan or spec did not settle, that is a ruling. Write
it in the ledger as a single `Ruling:` line with what you decided and what it costs if you
were wrong, and surface every ruling in your final message. A ruling that dies with the
workspace was a decision taken in secret.
