# Review contract (feat-review)

Adapted from the repository's SDD review workflows: explicit scope, stable findings with rule
citations, recorded commands, and no silent fixes.

## Scope

- The scope is an explicit `BASE..TARGET` range (commits, a branch, or `base_commit..HEAD`
  from a `plan.done.md`), or an explicit list of paths.
- `scripts/review_package.sh <base> <target> <out-dir>` writes the package the executor reviews:
  `range.txt`, `changed-files.txt`, `diffstat.txt`, `diff.patch`. An empty, ambiguous or
  unresolvable range stops the review; never widen it silently.

## Findings

Each finding is a row in the review file (`.planning/feat/features/{slug}/review.md`, rendered
from `templates/review-report.md`):

| Field | Rule |
|---|---|
| `finding_id` | `CR-001`, `CR-002`, ... stable within the report |
| `severity` | `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| `location` | `path:line` |
| `rule` | the rule violated: plan AC or prohibition, a Golden Rule of the project instructions file, `.planning/feat/context/conventions.md`, OWASP item, or a failing command |
| `evidence` | code excerpt, command output, or reasoning with the exact lines |
| `suggestion` | the concrete fix |

A finding without a rule citation can be at most `LOW`. Cosmetic issues are never above `LOW`.
`BLOCKER` = violates an approved contract, a security rule, or makes verification impossible.

## Dimensions

1. **Correctness** — logic bugs, edge cases, null handling, error paths.
2. **Security** — OWASP Top 10, injection, authn/authz, hardcoded secrets, unsafe deserialization.
3. **Performance** — N+1 queries, missing pagination, unbounded loops, memory leaks.
4. **Conventions** — the project's rules and observed patterns.
5. **Tests** — changed behavior covered by meaningful tests; UI changes have E2E scenarios or a
   justification.

## Verification during review

Run the project's lint and test commands on the target state and record each with its exit
code. A reviewer never moves HEAD in the working checkout; to inspect another state, use
`git worktree add <tmp> <target>` and remove only that worktree afterwards.

## Outcome

- `verdict: APPROVED` — no `BLOCKER`/`HIGH`.
- `verdict: CHANGES_REQUESTED` — at least one `BLOCKER` or `HIGH`. The report lists a ready-made
  fix scope (finding IDs → files) that `feat-feature` or `feat-quick` can turn into a fix plan.

Never fix code in a review, never omit or soften a finding to make the verdict pass, and never
cap severities in advance.

## Receiving a review (when executing a fix plan)

Read every finding before acting. Verify each against the code — reviewers can be wrong. Is it
correct and in scope? If it contradicts a decision the human already made, raise it instead of
reversing it silently. Disagree with a technical reason when warranted. No performative
agreement.
