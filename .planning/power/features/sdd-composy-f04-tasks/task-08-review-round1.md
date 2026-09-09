# Task 08 review — round 1

## Verification

The previously missing public CLI path is now implemented in
`plugins/sdd-composy/scripts/sdd_sync.py`:

- `apply <markdown-root> <state> <plan>` loads a JSON plan;
- `--authority` is constrained to `markdown|json`;
- `--confirmation-token` is required and forwarded unchanged to the guarded
  `apply()` API;
- stale fingerprints, malformed inputs, symlink destinations, and post-apply
  verification remain enforced by the shared API;
- CLI errors exit non-zero through argparse.

Focused CLI tests cover successful application and rejection of an invalid
token and authority. The portable skill and Claude adapter already document
and route this same contract without duplicating policy.

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
Ran 115 tests in 3.539s
OK
```

## Verdict

**APPROVED.** The Task 08 CLI contract now matches the portable skill and Task
07 guarded apply implementation. No further findings.
