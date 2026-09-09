# F03 Product Contracts — Final integrated re-review, round 1

Date: 2026-09-09
Mode: read-only re-review (this report is the only file created)
Verdict: APPROVED

## SPEC

The integrated correction resolves every finding from `final-review.md`.

The shared workflow now defines one portable, case-sensitive lifecycle vocabulary and its
valid gate combinations. PRD and TechSpec use `DRAFT`, `APPROVED`, and `REJECTED`; stories
add the narrowly scoped `NOT_APPLICABLE` state. `DRAFT` pairs with pending human approval,
approval and rejection pair the same explicit lifecycle/human-approval value with a human
`verified` event, and the stories exemption pairs `NOT_APPLICABLE` lifecycle/applicability
with a non-empty justification, `human_approval: APPROVED`, and human verification. The PRD,
stories, and TechSpec templates, normative references, and portable skills use these exact
values. The runtime adapters remain thin and correctly inherit the shared semantics rather
than duplicating lifecycle policy.

The stories template no longer mandates `RF-002` or `CA-002`. It contains one valid
`US-001→RF-001` / `SC-001→CA-001` example and explicitly directs workers to repeat the block
only for identifiers present in the approved PRD, allocate stable downstream IDs, and discard
examples whose targets do not exist. This agrees with the normative missing-link publication
block.

The rendered-chain coverage now exercises both permitted paths. The required-stories fixture
records approved PRD, stories, and TechSpec gates, confirms bundle sources, and checks that
every US, SC, TU, TI, and E2E heading target exists upstream. The pure-internal fixture records
a justified, human-approved `NOT_APPLICABLE` stories gate, removes US/SC entries, verifies
that the TechSpec carries no US/SC references, and checks the remaining RF/CA/test chain.

## QUALITY

The fix preserves the intended separation: workflow/reference files own lifecycle and product
policy, templates own artifact shape, portable skills apply the contracts, and Claude
commands only route to those skills. No architecture was introduced into PRD or stories, and
no provider-specific behavior was introduced into the portable core.

Fresh verification:

- `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — PASS, 85 tests.
- `git diff --check` — PASS.

## FINDING DISPOSITIONS

### Resolved — Approved lifecycle state was undefined

Resolved by `references/workflow.md:34-43` and consistent exact transitions in the three
templates, references, and skills. TechSpec upstream checks now require the precise PRD and
stories combinations, including the justified `NOT_APPLICABLE` route. Regression tests cover
the canonical vocabulary and both approved upstream variants.

### Resolved — Stories template mandated potentially dangling RF-002/CA-002 links

Resolved by `templates/stories.md:44-58`. The literal second requirement/criterion targets
are gone, repetition is conditional on real upstream identifiers, and the product test rejects
their reintroduction while the rendered-chain assertions verify target membership.

### Resolved — No end-to-end product-contract fixture protected the promised chain

Resolved by `SddComposyRenderedChainTests` in
`tests/test_sdd_composy_product.py:358-415`. It covers required stories and human-resolved
pure-internal non-applicability, gate combinations, source links, unique IDs, upstream target
membership, and the absence of story/scenario links on the exempt path.

No new critical, important, or minor findings were identified in the allowed scoped
re-review.

## VERDICT

APPROVED. All prior integrated findings are resolved, the corrected contracts remain aligned
with the approved F03 scope and portability boundaries, all 85 applicable SDD Composy tests
pass, and whitespace validation is clean.
