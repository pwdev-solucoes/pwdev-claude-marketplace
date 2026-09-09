# Task 08 review

## Scope

Read-only review of the Task 08 brief, implementation report, portable
`sdd-sync` skill, Codex metadata, Claude adapter, structural tests, and the
Task 07 synchronization implementation.

## Verification

```text
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py'
Ran 113 tests in 2.953s
OK
```

The structural tests cover discoverability, runtime neutrality, operation
names, approval language, and the thin Claude adapter boundary. The Task 07
tests cover the Python API's token, authority, stale-plan, symlink, atomic
write, and post-apply behavior.

## Findings

### Important — the advertised `apply` command is not available through the helper CLI

`plugins/sdd-composy/skills/sdd-sync/SKILL.md` explicitly routes all three
operations through `sdd_sync.py inspect|plan|apply` and documents an `apply`
CLI invocation. However, `plugins/sdd-composy/scripts/sdd_sync.py:main()` only
registers `inspect` and `plan` subcommands and has no parser for `apply`, a plan
file, `--authority`, or `--confirmation-token`. A caller following the
portable skill therefore reaches an argparse error instead of the guarded
Task 07 apply path. The Python API exists, but it is not the interface promised
by Task 08. This is a Task 07/Task 08 integration gap and must be fixed before
the task can be approved; add a failing CLI test and implement the thin CLI
adapter by loading the plan JSON and forwarding to the existing `apply()` API,
preserving its exact token and authority guards.

## Quality assessment

- Portable skill: structurally sound and runtime-neutral.
- Codex metadata: present and routes `$sdd-sync`.
- Claude command: thin and correctly forwards to the portable skill.
- Read-only inspect/plan and explicit approval language: clearly specified.
- Duplication and safety boundaries: the skill delegates policy to the helper.
- Task 07 compatibility: Python API is compatible, but the documented CLI
  contract is currently incomplete as described above.

## Verdict

**REJECTED — one Important integration finding.** Re-review after the helper
CLI supports the advertised guarded `apply` operation and has focused tests
for that path. No files were modified by this review other than this report.
