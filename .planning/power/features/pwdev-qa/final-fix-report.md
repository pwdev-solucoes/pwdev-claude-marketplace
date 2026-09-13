# PWDEV QA — final-fix report

Date: 2026-09-13
Scope: one bounded correction round for FR-01 through FR-04 from `final-review.md`.
Status: IMPLEMENTED_AND_VERIFIED; the branch has not advanced to finish.

## Root causes

- FR-01: `generate_report` validated only the manifest declaration and evidence attachments. It
  never opened the referenced acceptance contract, recomputed its SHA-256, or verified the
  declared criterion ID/text pairs before consolidation.
- FR-02: `_public_manifest` provided a structural allowlist but no content safety gate. Known
  credential patterns could therefore enter the shared public report model through ordinary
  text fields or diagnostics and flow unchanged to JSON, HTML, and PDF.
- FR-03: the schema intentionally permits empty expected/observed values for legitimate
  not-run states, but the consolidator did not distinguish those states from applicable
  assessments and executed required cases that must carry substantive observations.
- FR-04: the dependency test encoded the wrong package split, so verification-only PDF readers
  were duplicated in runtime requirements despite the Python 3.9 contract.

## RED evidence

The new focused regressions were executed before production changes. They produced 14 expected
behavioral failures for missing/changed/unpaired contracts, unsafe contract traversal, public
text disclosure, and blank semantic observations. The dependency regression initially had one
test-authoring `NameError`; after correcting the fixture constant and before changing
requirements, it failed for the intended mismatch. The complete focused RED was 15 failures.

After the first GREEN, production changes alone were removed while retaining the committed
regressions. The same focused command failed again with 15 behavioral failures, proving the
tests detect the original defects. Restoring the implementation returned the command to GREEN.

Regression commit: `ecaf57d` (`test(pwdev-qa): reproduce final review blockers`).

## Implemented controls

- Contract inspection now opens from the project-root descriptor with no-follow traversal,
  accepts only a regular file, reads at most 5 MiB, confirms a stable file identity and size,
  verifies the actual SHA-256, decodes strict UTF-8, and locates every exact ID/text pair using
  only bounded separator matching. Missing, changed, invalid, or incomplete contract content
  adds a neutral blocker; unsafe paths are refused without echoing source content.
- The final shared public model is recursively checked by the existing bounded known-credential
  policy before any JSON, HTML, or PDF write. Unsafe publication is refused with a neutral
  diagnostic, all three public artifacts remain absent, and the private input is unchanged.
- Applicable criterion assessments and executed required cases require non-whitespace expected
  and observed content to permit PASS. NOT_RUN and NOT_APPLICABLE cases keep the legitimate empty
  representation; expected and observed values are not required to be equal.
- `requirements.txt` now contains only `reportlab==4.4.9`; `requirements-dev.txt` retains
  `pypdf==6.10.0` and `pdfplumber==0.11.9`. The contract test enforces this split.

Implementation commit: `9da1b03` (`fix(pwdev-qa): enforce final publication gates`).

## GREEN evidence

- Focused report/verdict/PDF/contract/evidence/HTML/E2E regression group: 85 tests, OK.
- Bundled Python 3.12.14, all `test_qa_*.py`: 207 tests, OK in 14.144 s.
- System Python 3.9.6 compatible contract/core group: 63 tests, OK in 3.706 s.
- JSON parsing for the report schema and Claude/Codex manifests: OK.
- Python 3.9 byte-compilation for all seven QA scripts: OK.
- Marketplace README validation: 17 plugins in both READMEs, OK.
- `git diff --check`: OK before each implementation/report commit.

## Limitations and preserved boundaries

- Runtime acceptance remains independently BLOCKED at 0/3 VERIFIED as recorded in
  `references/runtime-smoke.md`; deterministic tests do not promote that status.
- The deferred flaky-quarantine Minor was not changed.
- `final-review.md` and the pre-existing untracked review packages were left untouched.
- No dependency was installed, no runtime or personal configuration changed, no external smoke
  was attempted, and no finish/merge/push action was performed.
