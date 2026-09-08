# Task 07 Review — Round 1

Base: `bd5aee9`  
Scope: current uncommitted `sdd-composy` worktree; read-only review.

## Verdict

SPEC: **FAIL**  
QUALITY: **FAIL**

Severity counts for remaining findings: **P0 0 · P1 2 · P2 3 · P3 0**

## Prior-finding disposition

| Prior finding | Disposition | Evidence |
|---|---|---|
| Task 07-specific failing-first tests absent | **NOT ADDRESSED (P1)** | `tests/test_sdd_composy.py` still contains no tests for the Task 07 linter, parser, actors, sources, reserved files, index generation, or CLI. The existing suite remains the same structural/schema suite. |
| Hand-written parser is fragile | **NOT ADDRESSED (P1)** | Parser now raises on unsupported lines instead of silently skipping them, but remains a narrow line parser: no quoted-colon handling, multiline YAML, YAML escapes, nested structures, or real JSON frontmatter despite its comment claiming JSON support. The list normalization remains indentation-fragile. |
| Actor validation asymmetric | **ADDRESSED** | `validate_frontmatter` now compares every `generated` and `verified` `by` value to the configured actor. |
| Reserved index bypassed validation | **ADDRESSED** | `index.md` is parsed, requires `okf_version: "0.2"`, validates frontmatter (including `type`), and scans its body links. Generated index now includes `type: Index`. `log.md` remains intentionally skipped. |
| Broken links only warning/untested | **NOT ADDRESSED (P2)** | Links are still warnings and do not affect `ok`; there are still no tests defining this behavior, and no explicit contract says whether a broken link must fail lint. |
| Index guarantees incomplete | **NOT ADDRESSED (P2)** | Index generation still directly calls the fragile parser, does not escape Markdown title/description content, has no tests, and silently excludes any document below a directory named `output`. |
| CLI duplicate lint work | **ADDRESSED** | `main()` now computes `result = lint(...)` once and reuses it for output and exit status. |

## New finding

### P2 — Reserved `log.md` can contain invalid frontmatter and broken links without any report

`lint()` continues to `continue` for `log.md`, so it does not parse, validate, or
scan links in the reserved log. The brief requires reserved index/log behavior,
but the reference only says the log is not treated as a concept; it does not
authorize silently ignoring malformed metadata or broken links. This needs an
explicit contract and test (either validate reserved-log syntax/links or clearly
state the exact exemption).

## Positive changes

- Both actor sections are now checked against the configured actor.
- Index frontmatter now includes the required `type`.
- Index links are scanned, malformed frontmatter is surfaced as an error, and
  duplicate lint execution was removed.
- The script remains dependency-free and executable by shebang.

## Verification

- Inspected current `references/okf.md`, `scripts/sdd_okf.py`, and
  `tests/test_sdd_composy.py`.
- Existing focused suite still has no Task 07-specific coverage.
- No credentials, environment files, private keys, certificates, or fleet
  environment files were read.

## Recommendation

Add the required red/green tests first, then replace or formally constrain the
parser, define reserved log semantics, specify warning-versus-failure behavior
for links, and test index escaping/exclusion and CLI exit behavior.
