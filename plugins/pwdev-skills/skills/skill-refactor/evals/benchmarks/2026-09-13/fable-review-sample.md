Review complete. Nothing was written to disk and no benchmark was run. The token count below is a static estimate from the skill's own script, not evidence of efficiency.

**Scope and profiles.** Target profile is `lean`, as requested. No benchmark summary exists in this workspace, so the executor profile defaults to `guided` per the protocol. The target is one file with no references, so every rule in it is paid on every activation.

Current static layers (chars/4 estimate, tiktoken not installed):

| Layer | Tokens |
|---|---:|
| description | 14 |
| frontmatter | 39 |
| body (loaded on every activation) | 238 |

## Findings

1. **Duplication.** Lines 11 and 12 are repeated verbatim at lines 17 and 18. Same rules, two sources of truth.
2. **Contradiction.** None found. There is no reference to disagree with the core.
3. **Unconditional reading.** Lines 20 to 26 hold CSV export rules that only apply when the user asks for CSV. The heading itself admits they load on every task. Lines 15 and 16 also impose unconditional reading of every document and of the skill itself.
4. **Over-broad description.** Line 3 claims any text, document, message, or information task. It will fire on email rewrites or article summaries, and it never mentions meetings, minutes, decisions, or action items. Only the `paths` glob on minutes.txt carries a real trigger.
5. **Procedure without purpose.** Lines 15 and 16 demand a long plan, rereading the skill, and explaining every tiny step. No requirement or outcome in the file explains them, and they add output and latency for a lean consumer.

## Proposed changes

Every change keeps these requirements intact: use only supplied content, never invent decisions, assignees, or dates, output the exact labels Key points, Decisions, and Actions, label missing assignees and dates, preserve the editorial note REVIEW_WINDOW=14, keep the name, `paths`, and the user_extension metadata, and never export CSV without a request.

- **Description, answers finding 4.** Rewrite as a capability with conditions: summarize meeting notes, minutes, or transcripts into Key points, Decisions, and Actions, with optional CSV export of actions. Use when the user supplies meeting content or asks for decisions or action items. Add a negative clause for general text and document tasks. Keep the glob and metadata untouched.
- **Core, answers findings 1 and 5.** Keep lines 11 to 13 once. Delete lines 15 to 18. Add one completion condition: done when the three sections are output and every missing assignee or date is labelled. Lean profile adds no example, checklist, or worked sequence.
- **CSV reference, answers finding 3.** Move lines 22, 23, 25, and 26 into a reference file with the condition "read only when the user requests CSV export". Keep "do not export without a request" and the empty-cell rule in the core, since they are limits that apply before any action. Because the file is tiny, the alternative of leaving the CSV block in the core under a conditional heading is legitimate. The layer measurement decides, not opinion.

## How to verify the effect

Static diagnosis first. After a refactor copies the current target to a baseline directory, run this and read the per-layer and per-scenario deltas:

```
python3 scripts/tokens.py <candidate> --baseline <old>
```

The expected pattern is a smaller description and body, with CSV tokens appearing only in the CSV load scenario.

Then a measured A/B, which this review did not perform. Freeze before running: cases, rubric, models, budget, timeouts, retries, and limits such as acceptance rate no lower than the previous version and cost per accepted task lower. A is the current SKILL.md, B is the lean candidate. Add C, B plus a guided reference, only if B fails the acceptance limit on a model. Write two or three domain cases, not this skill's own evals:

- Minutes with one missing assignee and one missing date. Expect the three labels, missing-value labels, no invented names, and the editorial note preserved.
- The same input plus a CSV request. Expect the three columns, quoted commas, dates verbatim, empty cells, header row, and a parse check.
- A negative case with no CSV request. Expect no CSV.

Run `scripts/bench.py` paired by case, context reset, A/B order varied, and read the runtime contract first. Report the protocol's fields per model: acceptance from pass_rate equal to 1.0 in grading.json, cost_per_success_usd from summary.json, accumulated context tokens plus which references the transcript shows were opened, duration p50 and p95, and timeouts.

Measure triggering separately with trigger evals on the real catalogue. Positives include "summarize these minutes", "what were the action items from Tuesday's call", a minutes.txt file, and a Portuguese "resuma a ata". Negatives include "rewrite this email" and "summarize this article". Report precision and coverage per model. The current description should score low precision, and the candidate must not lose coverage.

Count a gain only when acceptance stays inside the limit and cost per accepted task drops on that model. A shorter file or a single run is not evidence.