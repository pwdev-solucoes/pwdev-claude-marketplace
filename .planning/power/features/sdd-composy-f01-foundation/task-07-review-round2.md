# Task 07 Review — Round 2

Base: `bd5aee9`  
Scope: current uncommitted Task 07 worktree; read-only.

## Verdict

SPEC: **FAIL**  
QUALITY: **FAIL**

Remaining severity counts: **P0 0 · P1 1 · P2 3 · P3 0**

## Finding dispositions

| Finding | Disposition | Evidence |
|---|---|---|
| Required Task 07 tests absent | **PARTIALLY ADDRESSED (P1)** | A broad `test_okf_lint_and_index_contract` was added, covering basic type/extensions, generated/verified timestamps, sources, warning output, index output, reserved files, and malformed metadata. It does not cover actor mismatch, missing/invalid required fields in all cases, parser edge cases, executable CLI/exit codes, or explicit reserved-log behavior. The brief requires the failing-first test set, so coverage remains insufficient. |
| Parser robustness | **NOT ADDRESSED (P1)** | The parser is still a custom narrow YAML subset. It raises on malformed lines, but does not support quoted colons, multiline values, YAML escapes, nested structures, or actual JSON frontmatter despite the comment claiming JSON acceptance. No edge-case tests were added. |
| Actor semantics | **ADDRESSED** | Both `generated` and `verified` entries now compare `by` against the configured actor when present; the reference documents this. |
| Reserved index behavior | **ADDRESSED** | `index.md` now requires `type` and `okf_version: "0.2"`, is linted, and its links are scanned. |
| Broken-link semantics | **ADDRESSED** | `okf.md` explicitly says broken relative links are warnings with successful exit; the broad test asserts one warning. There is still no CLI-level exit test. |
| Index guarantees | **PARTIALLY ADDRESSED (P2)** | Generated index now includes `type: Index`, `okf_version`, entries, and reserved-file exclusion. It still does not escape Markdown title/description, documents the `output` directory exclusion, or test those cases. It also calls the fragile parser directly and can abort rather than return a structured lint result on malformed source frontmatter. |
| Duplicate CLI lint work | **ADDRESSED** | `main()` computes lint once and reuses the result. |
| Reserved `log.md` semantics | **PARTIALLY ADDRESSED (P2)** | Reference now states `log.md` is reserved and the broad test checks a valid log is ignored. Invalid log frontmatter and broken links are still silently skipped, with no test or explicit statement that this exemption includes all validation/link checks. |

## New findings

### P2 — `index` command has no structured failure behavior

`generate_index()` calls `parse_frontmatter()` without catching `ValueError`.
One malformed project document therefore produces a traceback/non-contractual
CLI failure instead of the JSON error shape used by `lint`. The broad test only
checks malformed metadata through `lint`, not `index`.

### P2 — CLI executable behavior remains unverified

The script has a shebang and argparse entrypoint, but no test invokes it as an
executable or asserts `lint` success/failure exit codes and JSON output. This is
explicitly part of the requested review scope and should be covered.

## Positive changes

- A broad OKF test now exercises core happy-path behavior and malformed metadata.
- Actor comparison, explicit warning semantics, index type/version, and single
  lint evaluation are implemented/documented.

## Verification

- Inspected current script, reference, and test additions.
- No credentials, environment files, private keys, certificates, or fleet
  environment files were read.
