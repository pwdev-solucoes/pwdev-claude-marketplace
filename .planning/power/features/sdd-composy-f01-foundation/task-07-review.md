# Task 07 Review — OKF v0.2 contract and linter

Base compared: `bd5aee9`  
Review scope: uncommitted Task 07 files in the `sdd-composy` worktree; no Git state was changed.

## Verdict

SPEC: **FAIL**  
QUALITY: **FAIL**

Severity counts: **P0 0 · P1 3 · P2 3 · P3 1**

## Findings

### P1 — Required failing-first tests were not added

`tests/test_sdd_composy.py` contains the earlier 21 structural/schema tests, but no
Task 07 tests for `type`, extensions, generated/verified actors, timestamps,
sources, reserved `index.md`/`log.md`, broken-link reporting, index generation,
or executable CLI behavior. The report's “21 tests passed” therefore does not
verify this task's requirements, and the required red/green test step is absent.

### P1 — Frontmatter parser is not robust YAML and can silently corrupt metadata

`parse_frontmatter` is a hand-rolled line parser. It does not support quoted
colons, multiline values, nested lists/scalars, YAML escapes, or standard YAML
documents beyond a narrow subset; malformed lines are silently skipped. The
special `verified`/`sources` normalization is indentation-fragile and can attach
subsequent fields to the wrong list item. A valid OKF document can consequently
be accepted with missing metadata, while malformed frontmatter can be treated as
partially valid. The JSON claim in the comment is also inaccurate: a JSON
frontmatter object is parsed as ordinary YAML-like lines, not as JSON.

### P1 — Actor semantics are incomplete and asymmetric

The configured `actor` is checked only against `verified[].by`; `generated.by`
is never compared with the configured actor, despite the requirement to validate
generated/verified actors. `generated` is optional even when an actor is supplied,
and `require_generated=True` is not exposed by the CLI. Actor syntax is not
validated either; any non-empty string is accepted.

### P2 — Reserved index behavior bypasses core validation

`lint` skips `index.md` after checking only `okf_version` when frontmatter exists.
It therefore permits an index with missing/unparseable frontmatter and does not
validate its required `type` or report links in the index body. Since the root
index is generated with no `type`, this conflicts with the global rule that
generated project Markdown requires `type` unless the reserved-file exception is
explicitly and consistently specified (it is not).

### P2 — Broken-link reporting is not tested and is only a warning channel

Broken relative links are collected as warnings and do not affect the `ok` exit
status. This may be acceptable only if the contract explicitly defines warnings
as non-failing, but neither the brief nor `okf.md` specifies that behavior and no
test locks it down. Links in reserved `index.md` are skipped entirely, so broken
links in the generated root index are never reported.

### P2 — Index generation does not fully guarantee progressive disclosure

`generate_index` emits title/description from parsed metadata but does not verify
frontmatter, does not escape Markdown title/description content, and excludes any
path containing a directory named `output` rather than defining a documented
artifact policy. It can therefore generate malformed links or silently omit
documents. There is no CLI test asserting `okf_version: "0.2"`, entries, and
reserved-file exclusion.

### P3 — CLI performs duplicate lint work

The `lint` branch calls `lint(a.root, a.actor)` twice (once for printing and once
for the exit code). This is minor, but makes behavior needlessly non-deterministic
if files change during execution and should be corrected while adding CLI tests.

## Positive observations

- The script is dependency-free and has an executable shebang.
- Base `type` presence, ISO-shaped timestamps, source `resource`, extension
  preservation, and `okf_version: "0.2"` index output are represented.
- Optional metadata is not required for ordinary documents, matching the brief's
  base-conformance requirement.

## Verification performed

- `python3 -m unittest tests.test_sdd_composy`: 21 existing tests passed; none are
  Task 07-specific.
- Direct inspection of `references/okf.md` and `scripts/sdd_okf.py`.
- No credentials, environment files, private keys, certificates, or fleet
  environment files were read.

## Recommendation

Add the specified failing-first tests, replace the ad-hoc parser with a robust
portable YAML approach or a deliberately documented strict parser, define and
test reserved-file semantics, validate both actor sections against the configured
actor, and make broken-link/index behavior explicit before accepting Task 07.
