# F02 Task 02 — Review

## SPEC

PASS. The four rule templates are present and discoverable from the canonical
`AGENTS.md` template. The links are correct for the installed layout: rules live
under `.agents/rules/`, so each `../AGENTS.md` target resolves to the governance
root. The files have focused scopes for discovery/shared boundary, architecture,
testing, and workflow, and they defer repository-wide policy to `AGENTS.md`.

## QUALITY

CHANGES_REQUESTED. The implementation is readable and the focused test command
passes (`python3 -m unittest tests.test_sdd_composy_runtime`: 7 tests passed).
However, the rule-specific tests do not adequately protect two stated parts of the
contract: actual canonical-link resolution and non-duplication of responsibilities.

## FINDINGS

### P2 — Discovery assertions do not resolve canonical Markdown links

`tests/test_sdd_composy_runtime.py:47-59` only checks that expected filenames and
URL-like substrings occur in `AGENTS.md`. It would pass if a link target had a typo,
extra suffix, or if the expected path appeared in prose while the actual Markdown
link pointed elsewhere. The per-rule check at lines 77-82 has the same substring
limitation for `../AGENTS.md`. This leaves a broken installed rule set undetected.

Remediation: parse the Markdown link destinations (or use a small exact-pattern
helper), assert the canonical `AGENTS.md` links equal the expected target set, and
resolve each rule link against a representative installed `.agents/rules/` layout.

### P2 — Responsibility/non-duplication coverage is too weak

`tests/test_sdd_composy_runtime.py:61-84` verifies filenames, a few keywords, lack
of scaffold tokens, and only that `architecture.md` is shorter than `AGENTS.md`.
It does not assert that each rule owns its stated concern or that another rule does
not reproduce a concern's policy. A rule containing duplicated workflow or testing
policy could therefore pass unchanged. This does not genuinely protect the brief's
“non-duplicative” requirement.

Remediation: assert explicit responsibility markers for each file and add
cross-responsibility checks for the canonical exclusions/ownership statements (or
compare normalized policy sections against the canonical contract) so a duplicated
governance section fails.

## REVIEW

`CHANGES_REQUESTED`

The rule templates themselves satisfy the requested structure and have no observed
functional defect. Address the two P2 test gaps before treating Task 02 as an
adequately protected contract.
