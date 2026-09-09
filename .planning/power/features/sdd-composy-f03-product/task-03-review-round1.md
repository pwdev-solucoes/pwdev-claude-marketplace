# Task 03 — User-story contract and skill re-review, round 1

Date: 2026-09-08
Mode: read-only
Disposition: CHANGES_REQUIRED

## SPEC

The template correction satisfies the normative content contract. Every current actor entry
now asks for goal, context, capabilities, and constraints. Every current journey entry now
asks for a trigger, ordered interaction, expected outcome, alternate or recovery path,
participating actors, and applicable story links. The prior template/reference mismatch is
resolved.

The remaining Task 03 contract continues to conform: approved PRD and domain inputs,
conditional project provenance, unique stable US/SC identifiers, RF/CA links, dependencies,
edge cases, the `REQUIRED` versus justified `NOT_APPLICABLE` gate, OKF v0.2 provenance and
lifecycle, and explicit human approval/verification behavior.

## QUALITY

The revised test extracts every actor and every journey block and applies assertions to each
entry, so coverage no longer stops at headings or the first example. It validates all four
actor fields and trigger, ordered interaction, outcome, actors, and stories for every journey.

One required journey field is still absent from the assertions. The reference requires every
journey to record an “alternate or recovery path,” but the per-journey required-field tuple in
`tests/test_sdd_composy_product.py:120-126` does not check either `alternate` or `recovery`.
Removing that field from every journey would therefore leave the focused suite green. Add a
per-entry assertion accepting `alternate` or `recovery` so every normative journey field is
regression-protected.

Fresh verification:

- `python3 -m unittest tests.test_sdd_composy_product` — PASS, 10 tests.
- `python3 -m unittest tests.test_sdd_composy` — 35 pass, 1 failure. The sole failure is the
  planned Task 04 absence of the `sdd-stories` Claude adapter and is not a Task 03 finding.

## DISPOSITION

CHANGES_REQUIRED. The artifact content is corrected, but Task 03 is not yet fully protected
by the requested regression test. Add an all-entry assertion for each journey’s alternate or
recovery path and rerun the focused and structural suites. No Task 04 adapter work is required
for this disposition.
