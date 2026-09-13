# Task 23 — implementation report

## Status

DONE_WITH_CONCERNS

## Scope delivered

- Added bilingual, portable manual setup guidance for Claude Code, Codex, and Hermes Agent without
  running an installer or changing personal configuration.
- Documented the exact inventory of 29 skills (router, tool recommender, 10 workflows, and 17
  specialists) and the 10 Claude commands.
- Documented equivalent offline HTML/PDF reporting, acceptance-result and global-verdict rules,
  output location, the separation between execution and export, and the prohibition on executing
  stored evidence commands while reporting.
- Documented Python >=3.9, export dependency `reportlab==4.4.9`, and Python 3.12 development/PDF
  verification dependencies `pypdf==6.10.0` and `pdfplumber==0.11.9`.
- Documented `qa-tooling` as a contextual recommendation skill that reports availability,
  detection evidence, prerequisites, alternatives, and reasons without automatic installation or
  fictitious execution.
- Documented the official local Playwright resolution (`npx --no-install playwright --version`
  followed by `npx playwright cli`) and the already-installed global `playwright-cli` alternative,
  with session isolation and evidence limitations.
- Documented sanitization limitations, confined regular-file evidence, exact v1 input limits,
  authorization boundaries, and the requirement for a real smoke before any runtime is called
  verified.
- Appended `pwdev-qa` to both local catalogs without changing either marketplace name, reordering
  existing entries, or modifying existing Codex policies/fields.

## Files changed

- `plugins/pwdev-qa/README.md`
- `plugins/pwdev-qa/README.pt-BR.md`
- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `tests/test_qa_catalog.py`

## TDD and verification evidence

- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_catalog` — 5 tests ran with
  9 assertion failures caused by the two missing READMEs and the missing final `pwdev-qa` catalog
  entries. The run had no import or fixture error.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_catalog` — 5 tests ran,
  all passed.
- QA regression suite: `PYTHONDONTWRITEBYTECODE=1
  /Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
  -m unittest discover -s tests -p 'test_qa_*.py' -v` — 185 tests ran, all passed.
- Both marketplace files passed `python3 -m json.tool`.
- Catalog comparison confirmed all pre-existing entries retain their original order and complete
  JSON values; `pwdev-qa` is the sole appended entry in each list.
- `git diff --check` passed before staging; the staged diff is checked again before commit.

## Acceptance review

- CA-003: documentation preserves the boundary that manifest/doctor discovery is not a successful
  runtime smoke. Real discovery, invocation, missing-tool handling, and fixture report generation
  remain required for each runtime in Task 24.
- CA-018 / RNF-006: installation and usage documentation exists in English and Portuguese.
- CA-022: `qa-tooling` documents contextual recommendation, availability/evidence/alternatives,
  official-source freshness, and no automatic install or fabricated execution.
- CA-023: the documented Playwright path distinguishes local detection and invocation from the
  global alternative and states isolation and v1 evidence restrictions.

## Limitations

No plugin, runtime, Python package, or browser tool was installed or invoked by this task. No real
Claude Code, Codex, or Hermes smoke is claimed; that is explicitly assigned to Task 24. Root
README integration is also Task 24, so the pre-existing marketplace/root-README coverage suite is
expected to remain pending until that sequential task adds the new catalog entry to both root
READMEs.

## Fix round 1

### Root cause

The original README tests treated the presence of a required sentence as proof of an unambiguous
contract. A later contradictory sentence therefore survived because the positive substring still
existed. The Claude catalog test projected every historical object down to its `name`, so nested
or unknown fields and values such as `description` and `strict` were outside the oracle.

### Correction and evidence

- Added bilingual mutation fixtures for six prohibited claims: automatic installation/personal
  configuration mutation, verification without real smoke, export rerunning tests/evidence
  commands, inverted ReportLab versus pypdf/pdfplumber roles, universal sanitization guarantees,
  and `npx --no-install` downloading or installing Playwright.
- Added explicit contradiction detection while preserving both valid READMEs unchanged. Negative
  clauses such as “does not install” and “cannot guarantee” remain valid controls.
- Added exact top-level Claude catalog comparison and canonical SHA-256 snapshots for every
  complete historical plugin object. Canonical serialization includes every nested key/value and
  any unknown field; order is checked separately.
- RED: the focused suite ran 11 tests with 12 assertion failures, one per language for each of the
  six documentary mutations. Existing positive-contract and catalog tests remained green.
- Catalog mutation RED: changing both `description` and `strict` on the first historical Claude
  entry made the focused catalog test fail on its first canonical object digest. The catalog was
  restored before final verification.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_catalog` — 11 tests ran,
  all passed.
- Packaged QA suite: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py' -q` — 191 tests
  ran, all passed.
- Both marketplace files passed `python3 -m json.tool`; `git diff --check` passed. No README or
  catalog production content changed in this correction round.

## Fix round 2

### Root cause

The first contradiction scanner matched a positive predicate anywhere inside a bounded lexical
window. Negators such as `never`, `cannot`, `not`, `nunca`, and `não pode` were inside that window
but were not attached to the predicate they governed. Consequently, a stronger valid prohibition
contained the same positive tokens as a harmful permission and was classified identically.

### Correction and evidence

- Paired every harmful mutation with an explicit valid negative control for all six rules in both
  English and Portuguese: 12 harmful cases and 12 valid controls.
- Replaced broad lexical windows with subject → polarity → predicate patterns. The scanner now
  evaluates the negator immediately before the relevant installation, verification, execution,
  dependency, guarantee, or download predicate.
- Kept all harmful probes active; none was weakened or removed. Existing valid READMEs remain an
  additional control and no production documentation or catalog content changed.
- RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_catalog` — 11 tests ran with
  12 assertion failures, one for every valid EN/PT-BR control falsely classified by the old
  scanner. All 12 harmful mutations continued to be rejected.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_catalog` — 11 tests ran,
  all passed, covering both polarities for all 12 bilingual rules.
- Packaged QA suite: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py' -q` — 191 tests
  ran, all passed.
- Both marketplace files passed `python3 -m json.tool`; `git diff --check` passed.
