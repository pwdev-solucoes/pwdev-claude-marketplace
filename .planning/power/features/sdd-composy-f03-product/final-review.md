# F03 Product Contracts — Final integrated review

Date: 2026-09-09
Mode: read-only review (this report is the only file created)
Verdict: CHANGES_REQUIRED

## SPEC

The implementation provides the three intended human contracts at
`tasks/prd-<slug>/{prd,stories,techspec}.md`, portable Codex skills, and thin Claude command
adapters. PRD and stories keep solution architecture out of product documents; TechSpec owns
components, interfaces, decisions, risks, conditional persistence/API detail, and planned
tests. The skills enforce explicit upstream gates, preserve assigned identifiers on revision,
use consumed-source provenance, begin generated artifacts as `DRAFT`/`PENDING` with empty
`verified`, and prohibit deriving human approval from file existence or agent confidence.

The applicability rule is consistently stated: user-facing behavior and externally consumed
APIs require stories; only pure internal work may be `NOT_APPLICABLE`, with a non-empty
justification and an explicit human verification event. The TechSpec skill rejects missing,
pending, rejected, stale, contradictory, or incompletely verified upstream state. Its
conditional detail is progressively disclosed through `references/specification.md`.

Two cross-document contract defects prevent approval. The lifecycle mutation does not name a
canonical approved status, despite portable resumption requiring lifecycle meaning to be
identical between runtimes. In addition, the stories template and its tests require concrete
links to `RF-002`/`CA-002` even though the upstream PRD template guarantees only
`RF-001`/`CA-001`; following the template literally can therefore publish dangling links that
the normative story reference says must block publication.

## QUALITY

The division of responsibilities is otherwise clean. References own detailed policy,
templates own artifact shape, portable skills own execution procedure, and the three Claude
commands are small routing adapters (368, 353, and 370 bytes) with no copied approval,
architecture, applicability, or trace policy. The three template frontmatters parse with the
bundled strict YAML-subset parser.

Fresh verification:

- `python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_product` — PASS, 59 tests.
- `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'` — PASS, 80 tests.
- `git diff --check` — PASS.

The green tests are principally static presence/regex checks. They do not render a minimal
PRD→STORIES→TECHSPEC bundle and validate referential integrity or an approved lifecycle
transition. Consequently they do not detect either finding below.

## FINDINGS

### Important — Approved lifecycle state is undefined

`references/product.md:36-38`, `references/stories.md:46-50`, and the corresponding skill and
template gate text instruct a runtime to set lifecycle status to a “corresponding” or
“matching” approved state, but no F03 contract names that value. TechSpec repeats the same
open-ended instruction at `references/specification.md:61-65`. The shared workflow defines
stage names and gate authority but not a document lifecycle-status vocabulary. The bundled
OKF validator validates neither `lifecycle.status` nor consistency between it,
`human_approval`, and `verified`.

Thus Claude and Codex can validly choose different statuses (for example `APPROVED`,
`VERIFIED`, or a stage-specific spelling), after which the TechSpec's requirement for “an
approved lifecycle state” has no deterministic interpretation. This violates the approved
design's portable-resumption guarantee and makes the upstream gate non-machine-verifiable.
Define the exact draft/approved/rejected/not-applicable lifecycle values and the required
consistency relationship among lifecycle, `human_approval`, applicability, and the human
event; add transition-oriented tests for each PRD and stories gate path.

### Important — Stories template mandates potentially dangling RF-002/CA-002 links

`templates/stories.md:56-64` contains literal `US-002 — RF-002` and
`SC-002 — CA-002` entries. `tests/test_sdd_composy_product.py:137-140` explicitly requires
those literal links. However, `templates/prd.md:56-70` establishes only `RF-001` and `CA-001`;
there is no contract that every approved PRD contains a second requirement and criterion.
The literals are not rendering markers, so a worker that follows the declared document shape
can retain them for a one-requirement PRD and create dangling downstream trace IDs. That
directly contradicts `references/stories.md:26-31`, which requires every US/SC link to resolve
to approved RF/CA identifiers and says missing links block publication.

Make repeated story/scenario entries explicitly conditional placeholders derived from the
actual approved upstream IDs (or remove the mandatory second example). Replace the current
literal-presence assertions with a rendered-chain test that checks uniqueness and that every
US→RF and SC→CA target exists upstream.

### Minor — No end-to-end product-contract fixture protects the promised chain

The focused product tests inspect each template independently and assert headings, keywords,
and example IDs. They never construct a representative approved PRD, required-stories path,
`NOT_APPLICABLE` path, and TechSpec, then verify sources, gates, and all
RF/CA/US/SC/TU/TI/E2E targets together. This allowed the mandatory dangling examples and
undefined lifecycle transition to remain green. Add at least one required-stories fixture and
one pure-internal fixture exercising the full contract chain with the deterministic OKF/gate
validator.

## VERDICT

CHANGES_REQUIRED. The content boundaries, applicability policy, upstream blocking language,
progressive disclosure, and dual-runtime adapter structure are sound, and all current suites
pass. F03 should not be accepted as an end-to-end portable product contract until the approved
lifecycle vocabulary is deterministic and story links are derived from actual upstream IDs,
with rendered-chain regression coverage for both the required and `NOT_APPLICABLE` paths.
