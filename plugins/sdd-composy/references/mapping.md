# sdd-map evidence contract

`scripts/sdd_map.py` creates a repository-bound, read-only inventory for the
SDD Composy context bundle. Its output is observation, not architectural
intent: modules and boundaries are reported only as filesystem evidence, and
domain terms carry deliberately low confidence.

## Output

The JSON object at `.planning/sdd-composy/context/codebase.json` uses
`schema: sdd-composy.codebase` and `schema_version: "0.2"`. It records the
repository path, `source_commit`, mapped commands, observed languages and
manifests, modules, boundaries, domain evidence, confidence, and a staleness
record. Lists and object keys are sorted for deterministic serialization.

The companion `project.md`, `stack.md`, `domain.md`, and `pitfalls.md` files
are OKF v0.2 context concepts. Commands are extracted from manifests but are
never executed by the mapper.

## Evidence and safety

The scanner skips build/dependency/VCS directories and excludes environment,
credential, token, secret, password, key, certificate, and private-key paths
before opening files. Existing `codebase.json` is read only to compare its
recorded commit and report staleness. A changed repository commit therefore
marks the old map stale; it never causes source files to be changed.

Use `python3 <plugin-root>/scripts/sdd_map.py --repo-root . --write` to
publish the context bundle. Without `--write`, the same inventory is printed
to stdout and the repository remains unchanged.
