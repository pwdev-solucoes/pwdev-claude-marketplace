# Task 03 — User-story contract and skill review

Date: 2026-09-08
Mode: read-only
Verdict: CHANGES_REQUIRED

## SPEC

The implementation satisfies most of the Task 03 interface: it consumes an explicitly
human-approved PRD plus required domain and optional project context, confines output to
`tasks/prd-<slug>/stories.md`, preserves the product/architecture boundary, defines stable
US/SC identifiers with RF/CA trace links, records dependencies and edge cases, and provides
the required `REQUIRED` versus justified `NOT_APPLICABLE` human gate.

OKF v0.2 provenance and lifecycle are present across the template, reference, and skill:
consumed `sources`, generated actor/timestamp, `DRAFT` lifecycle, exactly one pending
`human_approval` field, empty initial `verified` events, and explicit human-recorded approval,
non-applicability, and rejection behavior. The skill also rejects missing, pending, rejected,
stale, or incompletely verified PRD input and prevents downstream TechSpec work while the
stories gate remains unresolved.

One contract mismatch remains: the reference requires every actor and journey to record the
complete actor/journey shape, but the second examples in the template omit required fields.
That makes the template capable of producing an artifact that does not satisfy its own
normative reference.

## QUALITY

The reference is concise and owns semantics, the template owns document shape, and the skill
is runtime-neutral. OpenAI metadata routes directly to `$sdd-stories`. YAML/frontmatter for
the template, skill, and metadata parses successfully.

The product tests pass, but the actor/journey coverage is too shallow: it checks headings and
the existence of one actor/journey ID without checking the required content of every example.
Consequently it does not detect the contract mismatch below. Dependency and edge-case
sections, US/SC uniqueness, RF/CA example links, applicability language, provenance, and the
human gate are otherwise represented in the implementation.

Verification run:

- `python3 -m unittest tests.test_sdd_composy_product` — PASS, 10 tests.
- `python3 -m unittest tests.test_sdd_composy` — 35 pass, 1 failure: the missing
  `sdd-stories` Claude adapter. Per the approved plan, Task 04 owns that adapter, so this is
  not a Task 03 finding.
- `python3 -m unittest discover -s tests` — 374 tests, 9 failures, 5 errors, 1 skipped. The
  Task 03-relevant failure is the same Task 04 adapter check. Other failures concern
  repository inventory, `pwdev-power`, fleet timing, or sandbox-denied socket binding and are
  outside Task 03.

## FINDINGS

### Important — Template permits incomplete actors and journeys

`plugins/sdd-composy/references/stories.md:22-24` requires each actor to record goals,
context, capabilities, and constraints, and each journey to record a trigger, ordered
interaction, outcome, alternate/recovery paths, participating actors, and linked stories.
However, `plugins/sdd-composy/templates/stories.md:27-29` describes `Actor-002` only by how it
participates or is affected, omitting its goal, context, capabilities, and constraints.
Likewise, `plugins/sdd-composy/templates/stories.md:38-40` asks `Journey-002` only for an
alternate path, interruption, or recovery, omitting the trigger, ordered interaction,
outcome, participating actors, and story links.

The template is the declared document shape, so following it faithfully can yield an
incomplete stories contract. Update both example prompts to require the complete normative
shape (or provide one repeatable actor/journey entry whose instructions explicitly apply to
every entry). Strengthen `tests/test_sdd_composy_product.py:93-105` so removing any required
actor or journey field from an example fails the product suite.

## REVIEW

CHANGES_REQUIRED. Correct the incomplete actor/journey template guidance and add regression
assertions for the required fields. Re-run the focused product test and the structural suite.
The absent Claude stories adapter remains explicitly deferred to Task 04 and is not part of
this verdict.
