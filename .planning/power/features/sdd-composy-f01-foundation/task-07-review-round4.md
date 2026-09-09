# Task 07 Review — Round 4

Base: `bd5aee9`  
Scope: current uncommitted Task 07 implementation; read-only.

## Verdict

SPEC: **FAIL**  
QUALITY: **FAIL**

Remaining severity counts: **P0 0 · P1 1 · P2 1 · P3 0**

## Finding dispositions

| Prior finding | Disposition | Evidence |
|---|---|---|
| Required Task 07 tests and executable CLI assertions | **ADDRESSED** | `SddComposyOkfTest` now independently imports the script, tests quoted colons, escaped quotes, multiline/nested metadata, invokes the executable `lint` and `index` commands, asserts exit codes/JSON, and covers type/extensions, actor mismatch, index, log, links, and malformed metadata. |
| Parser robustness / claimed YAML support | **NOT ADDRESSED (P1)** | The reference now claims a strict subset and the tests cover several cases, but implementation does not match the claim: `scalar()` explicitly accepts block scalars (`|`/`>`), while the reference says block scalars are rejected. More importantly, inline arrays/objects use `ast.literal_eval` after global `.replace('true','True')`/`.replace('false','False')`, which can mutate quoted string content (for example `feature`), and the fallback comma split mishandles quoted commas/nested values. YAML escaping and indentation edge cases remain only partially handled. This is a contract/quality failure even though the happy-path tests pass.
| Actor semantics | **ADDRESSED** | Generated and verified actor values are compared to the configured actor; mismatch is tested. |
| Reserved index behavior | **ADDRESSED** | Index requires `type: Index` and `okf_version: "0.2"`, is linted, and its links are scanned. |
| Broken-link semantics | **ADDRESSED** | Reference explicitly defines broken relative links as warnings with successful exit, and the test asserts warning output. |
| Index guarantees and failure behavior | **ADDRESSED** | Generated index includes required metadata, escapes brackets/newlines, excludes reserved files, and the CLI test asserts structured JSON error/exit 2 for malformed input. |
| Duplicate CLI lint work | **ADDRESSED** | Lint result is computed once. |
| Reserved `log.md` semantics | **PARTIALLY ADDRESSED (P2)** | Tests establish that even a `log.md` with invalid type and a broken link is ignored, but the reference only says “not treated as a concept”; it does not explicitly state that all frontmatter/link validation is exempt. The behavior should be stated precisely to make the reserved-file contract unambiguous. |

## New verification notes

- The tests are now independent of the existing structural suite and invoke the
  script by its executable path.
- `generate_index()` catches parser errors at the CLI boundary and returns a
  structured error object with exit code 2.
- No credentials, environment files, private keys, certificates, or fleet
  environment files were read.

## Recommendation

Resolve the parser/reference mismatch (either reject block scalars or document
and test them), avoid global textual boolean replacement in inline values, add
edge-case tests for quoted commas/strings and nested inline structures, and
state explicitly that reserved `log.md` bypasses metadata and link validation.
