# F03 Task 06 — Review

Review scope: uncommitted Task 06 files in the `sdd-composy` worktree; no Git state was
changed.

## SPEC

FAIL. The portable skill, Codex discovery metadata, and Claude command exist and expose the
requested `$sdd-techspec` and `/sdd-composy:techspec` routes. The skill consumes the Task 05
specification, workflow, and template contracts; enforces approved PRD plus approved required
stories or a human-verified, justified `NOT_APPLICABLE` disposition; confines its write to
`tasks/prd-<slug>/techspec.md`; and keeps the new artifact at the explicit human gate.

The output contract is internally inconsistent. Procedure step 9 requires the result presented
for review to contain the exact draft, unresolved decisions, risks, and trace summary, but the
normative `Return exactly:` list omits both the exact draft and risks. Because `exactly` closes
the return shape, a conforming runtime cannot satisfy both instructions. The unchanged-result
Claude adapter propagates that ambiguity rather than resolving it, as a thin adapter should.

## QUALITY

CHANGES REQUESTED. Runtime neutrality and adapter thinness are otherwise sound. The Claude
adapter is 370 bytes and contains only command metadata, portable skill routing, argument and
repository-context forwarding, and unchanged-result behavior. It does not duplicate approval,
applicability, architecture, or test-trace policy. The portable skill uses the shared reference
for detailed architecture and gate semantics and routes conditional persistence/API detail to
that reference rather than reproducing it.

The focused tests cover route identity, upstream gate vocabulary, progressive-disclosure
markers, output fields, runtime-specific-tool exclusions, and adapter thinness. However, the
exact-output test codifies the incomplete list and does not reconcile it with procedure step 9;
therefore the green suite does not protect the full skill contract.

## FINDINGS

- **Major — contradictory exact return contract**
  (`plugins/sdd-composy/skills/sdd-techspec/SKILL.md:61-71`,
  `tests/test_sdd_composy.py:443-452`). Step 9 mandates presenting the exact draft and risks,
  while `Return exactly:` omits them. A runtime following the output list may drop material risk
  information and the reviewable draft; a runtime including them violates the declared exact
  shape. Add `exact draft` and `risks` to the exact output list (or explicitly make the path the
  draft presentation and remove the conflicting requirement), then extend the structural test
  to require the reconciled fields.

## REVIEW

CHANGES_REQUESTED.

Verification performed:

- `python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_product` — 59 tests passed.
- `git diff --check -- plugins/sdd-composy/skills/sdd-techspec/SKILL.md plugins/sdd-composy/skills/sdd-techspec/agents/openai.yaml plugins/sdd-composy/commands/techspec.md tests/test_sdd_composy.py` — passed.
- Inspected the Task 06 brief and implementation report, feature plan and ledger, portable
  skill, Codex metadata, Claude adapter, focused structural tests, Task 05 template/reference,
  workflow contract, and adjacent PRD/story adapter conventions.

HEAD was not moved and no commit was created.
