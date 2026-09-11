# Task 08 — offline re-review round 1

Scope: re-review only the five `Important` findings from
`task-08-review-offline.md`, against package `fb14629..582ae65`.
No real provider was invoked. The previously deferred `Minor` finding was not reopened.

## SPEC

`REJECTED` for approval of the offline phase. Three important findings are `ADDRESSED`; two remain
`NOT ADDRESSED`. The global Task 08 status remains correctly `INCOMPLETE`, and this review grants no
real-provider or fleet acknowledgement.

## QUALITY

- Focused suite: `python3 -m unittest tests.test_sdd_composy_runtime_smoke tests.test_sdd_composy_hermes -v`
  — 18 tests, PASS in 46.369s.
- Fresh offline CLI run to `/tmp`: 36/36 records `PASS`, all locally measurable records populated,
  provider calls exactly `{"hermes": 0, "codex": 0, "claude": 0}`.
- Full offline suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -v`
  — 367 tests, PASS in 68.140s.
- No real provider inference was executed. Runtime `--version` probes are local preflight only.

## FINDINGS

### 1. Offline scenarios use fixture and real behavioral contracts — NOT ADDRESSED

The patch materially improves this area: every offline record now receives its own
`isolated_fixture`; read-only invokes `sdd_status`; lifecycle invokes init/map/tasks/loop modules;
fleet invokes `launch.sh`; evidence invokes the evidence/trace/status modules; and compose invokes
the fleet launcher, cmux helper and real Git merge fixture.

However, the finding is not fully closed:

- `_offline_handoff` (`scripts/sdd_runtime_smoke.py:288-299`) is still entirely implemented by the
  harness writing and rereading its own JSON. No Hermes, Codex, or Claude adapter/consumer reads the
  prior runtime's artifact, so it does not prove the matrix contract that each runtime consumes the
  other's handoff while preserving IDs and gates.
- The approval guard remains disconnected from scenario execution. `validate_fixture_approval`
  (`scripts/sdd_runtime_smoke.py:161-164`) is called only by its isolated unit test. Neither the
  lifecycle fixture nor fleet contracts contain an approval marked synthetic and scoped, and no
  scenario calls this validator. Thus the harness still does not behaviorally refuse a fixture with
  invented approval as required by the Task 08 brief.
- Fleet's mismatch check asserts only a nonzero return. It sets `SDD_FLEET_RUNTIME=wrong-runtime`
  (`scripts/sdd_runtime_smoke.py:274-281`), so the runner exits at the generic unsupported-runtime
  preflight; the harness does not assert a diagnostic proving member/runtime identity mismatch.

The 36-scenario test checks aggregate `PASS` and field presence, but has no negative mutation test
for these three conditions.

### 2. Plugin copy fails closed on secrets and symlinks — NOT ADDRESSED

Symlink handling is addressed: source-tree symlinks are rejected before `copytree`, including the
plugin root, and the focused adversarial test passes.

Secret exclusion is still name-heuristic and incomplete. `_secret_name`
(`scripts/sdd_runtime_smoke.py:107-111`) recognizes `.env*`, prefixes `credential`/`secret`, two
legacy SSH filenames, and a limited extension set. A fresh adversarial fixture demonstrated that
all of these files are copied into the plugin fixture:

```text
{'token.json': True, 'id_ed25519': True, 'auth.json': True, 'keystore.jks': True}
```

These are ordinary token/private-key/auth/keystore names. Therefore the implementation does not yet
provide the requested fail-closed guarantee that the plugin copy contains no secrets, private keys,
or certificates. The added test covers only `private.key`, `client.pem`, and `credentials.json`.

### 3. Evidence records preserve measurable identity, timing, hashes, exit and resources — ADDRESSED

`_offline_check` measures duration, computes a result digest, records command/resources/worktree,
captures exit code and runtime version, and labels the offline provider. `_record` now preserves
structured launcher measurements rather than discarding them. The fresh 36-record run confirmed
non-null duration, result hash, task/worktree identity, resources and zero exit code for every
offline scenario. The fake-launcher test independently confirms preservation for the real path.

### 4. Output and fingerprint reject symlink ancestors and atomic failure preserves bytes — ADDRESSED

`tree_fingerprint` now rejects symlink ancestors and all symlinks in the tree before hashing.
`write_summary` rejects symlink path components before creating the output directory. Fresh focused
tests prove leaf/ancestor rejection. Injected `os.replace` failure preserves the prior summary bytes
and removes the temporary file; the focused test passed.

### 5. Real CLI exposes a gated provider entry and retains structured evidence — ADDRESSED

The CLI now exposes `--provider-entry-point production` and `--acknowledge-real-fleet`; `main`
passes the selected launcher and acknowledgement into `run_acceptance`. Without acknowledgement,
fleet remains `BLOCKED` before launcher invocation. The production entry remains deliberately
`NOT_RUN`, so this does not claim real acceptance. Structured measurements from an injected launcher
are retained in the scenario record, as reproduced by the focused test. This closes the offline
interface/gating finding while leaving actual provider implementation for the separately gated real
phase.

## REVIEW

`CHANGES_REQUIRED`.

Close the remaining two important findings by making handoff and mismatch checks validate the
actual consumer/identity boundary, connecting explicitly synthetic scoped approval validation to
the executed fixtures, and replacing the secret filename allow-by-omission behavior with a
fail-closed copy policy plus adversarial coverage for token, modern SSH key, auth and keystore
classes.

The deferred minor budget-recovery item was not reconsidered in this round.
