# Verification contract

Verification is the adversarial gate for a `verify_required` task. It is
independent from generation, QA, review, and implementation: the verification
actor runs fresh commands and records a truth table rather than trusting prior
claims.

For every required claim, reproduce the exact command in the declared
environment, record exit code, sanitized output, confined relative evidence
path, and SHA-256 digest (sha256). `PASS` means the fresh result supports the claim;
`FAIL` means it refutes it. stale evidence is evidence predating the current
inputs. `STALE` means the evidence predates the current
inputs, commit, or command and must be rejected. `ENVIRONMENT_FAILURE` means
the command could not be meaningfully executed because the environment was
missing, unavailable, or misconfigured; it is not a test failure.
`NOT_RUN` is never approval. An environment failure is classified separately
from a failed test.

The verifier must actively try to refute claimed truths, reject stale or
hash-inconsistent evidence, and distinguish test failures from environment
failures. Artifact existence, a zero exit code from a different command, prior
summaries, or agent confidence cannot produce `PASS`. Missing claims, unknown
commands, unsafe paths, contradictory results, and unresolved QA/review
blockers fail closed with `REJECTED`.

Only when every required row is fresh and `PASS`, all upstream gates are
non-blocking, and a human approval is recorded may it transition to `complete`.
Record generation and verification actors separately; sanitize secrets and
include the next action for every rejection.
