# Task 08 — independent offline review

Review scope: offline phase only, package `3e491f8..1b00701`.
Review mode: read-only except for this report. No real provider was invoked.

## SPEC

`REJECTED` for the offline-phase acceptance claim. The harness CLI runs and its focused/full
test suites pass, but the six offline scenario implementations do not exercise the observable
contracts described by `matrix.md`. They can report `PASS` from static file presence or in-memory
toy values without using the isolated project fixture, provider adapters, lifecycle engines,
handoff artifacts, or fleet launcher.

The global Task 08 status correctly remains `INCOMPLETE`; this review does not authorize real
inference, fleet acknowledgement, evidence verification, completion, merge, or publication.

## QUALITY

- Fresh focused verification: `python3 -m unittest tests.test_sdd_composy_runtime_smoke tests.test_sdd_composy_hermes -v` — 13 tests, PASS.
- Fresh offline CLI run, output under `/tmp`: 36 records, all `PASS`; provider calls were exactly
  `{"hermes": 0, "codex": 0, "claude": 0}`; timeout 300; budget 28.
- Fresh full suite: `python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -v` — 362 tests, PASS in 25.540s.
- `git diff --check` — PASS.
- Persisted evidence hashes reproduce: summary
  `be2d3e6dfe324c5951c5005294d3c2a74f10b9f7aa9bc222913e74ada3b75364`; plugin tree
  `d101d5fb9b03048a1342a104c9786b0e210e329c190239b6f805e52282d0b9e3`.
- Hermes behavioral registration is materially improved: the tests load the plugin, preserve
  native `Path`, resolve exactly 17 skills, exercise first-turn bootstrap, and fail diagnostically
  before partial registration when bootstrap discovery is unavailable.
- Budget enforcement, timeout process-group termination, zero automatic retry, closed status
  validation, real-fleet blocking without acknowledgement, null usage, and same-directory temp +
  `os.replace` publication each have focused coverage.

Passing tests are not sufficient evidence for the scenario-level claims because the assertions
mirror the shallow implementation rather than the acceptance matrix.

## FINDINGS

### Important — Offline scenarios do not execute the acceptance fixture or behavioral contracts

`scripts/sdd_runtime_smoke.py:137-178` implements all six scenarios as static presence checks or
in-memory examples. `run_acceptance` never calls `isolated_fixture`. Concretely:

- read-only fingerprints the plugin directory twice without invoking `sdd_status.py`, and has no
  project/UI sentinels;
- lifecycle checks only that four scripts and five skill files exist; it does not run
  init → map → import → next or the five-stage LOOP;
- fleet checks two hard-coded IDs/paths and launcher filenames, without running two isolated
  members, runtime mismatch, or launcher behavior;
- handoff serializes one in-memory dict, rather than transferring durable artifacts among runtime
  adapters and checking projected IDs/gates;
- evidence hashes a synthetic byte string, rather than exercising absent/stale/tampered evidence
  and divergent status through the real validators;
- compose checks schema/template file presence, without cmux/compose/post-merge fixtures.

Therefore 36/36 `PASS` is coverage of selectors, not evidence that the matrix scenarios passed.
The focused test at `tests/test_sdd_composy_runtime_smoke.py:30-47` asserts only that these records
exist and say `PASS`, so it cannot detect this gap.

### Important — Isolation and secret-exclusion guarantees are not enforced end to end

`isolated_fixture` is tested independently but is not used by `run_acceptance`. Its copy filter at
`scripts/sdd_runtime_smoke.py:103-105` excludes a small name list and `.env*` only; it does not
fail closed on symlinks and does not establish a general secret/private-key/certificate exclusion
contract. Since `shutil.copytree` dereferences symlinks by default, a symlink within the plugin
source may copy content from outside the source tree. This does not satisfy the matrix requirement
that the temporary plugin copy contain no secrets or operational state.

### Important — Evidence records omit required per-scenario measurements

`_record` at `scripts/sdd_runtime_smoke.py:181-190` always writes `duration_seconds: null`,
`result_sha256: null`, `command: null`, empty resources, and null runtime/version/provider/model.
It also discards any such fields returned by a launcher. The persisted offline summary consequently
has timestamps but no duration, exit code, result hash, fixture identity, or resources for each
scenario. `matrix.md` requires scenario evidence with duration, exit code, hashes, and runtime/task/
worktree identity; unavailable usage may be null, but the locally measurable fields are not
unavailable.

### Important — Output confinement does not reject symlink ancestors before writing

`write_summary` calls `output.mkdir(parents=True, exist_ok=True)` before checking only
`output.is_symlink()` (`scripts/sdd_runtime_smoke.py:193-209`). It does not inspect controlled
ancestors. An existing symlink in an ancestor can redirect directory creation and atomic replacement
outside the intended tree. `tree_fingerprint` likewise follows file symlinks. The focused atomicity
test checks only successful temp cleanup (`tests/test_sdd_composy_runtime_smoke.py:113-125`), not
destination/ancestor symlink refusal or preservation after failed replacement.

### Important — The real-mode CLI has no provider entry point and loses launcher evidence

The CLI's `main` never supplies `provider_launcher` (`scripts/sdd_runtime_smoke.py:266-275`), so
every non-fleet real scenario is unconditionally `NOT_RUN`, while fleet is `BLOCKED`; there is no
CLI acknowledgement input. Injection through the Python API can call a fake launcher, but it is not
a production adapter/launcher entry point and its structured output is reduced to status/reason/
exit code. This is consistent with keeping real acceptance gated, but it means the proposed real
interface and adapter validation are not implemented and must not be described as ready for an
acknowledged real run.

### Minor — Budget exhaustion aborts without publishing a closed scenario result

`budget.consume` raises `SmokeBlocked` before the record append (`scripts/sdd_runtime_smoke.py:236-243`).
If the limit is reached, the whole run exits without a `BLOCKED` record or recoverable summary. The
unit test validates the counter exception in isolation, not run-level recovery. The acceptance
contract calls for a recorded limit-reached result and no retry.

## REVIEW

`CHANGES_REQUIRED`.

Before the offline phase can be approved, replace the static scenario predicates with behavioral
tests against the exclusive temporary repository and copied plugin; make read-only sentinels,
lifecycle/LOOP, two-member fleet, handoff, evidence recovery, and compose/cmux checks observable;
fail closed on source/destination symlinks and secret-bearing copy candidates; preserve measurable
per-scenario evidence; and add adversarial tests that would fail when those behaviors are bypassed.

Real-provider execution remains separately gated and was not attempted by this review.
