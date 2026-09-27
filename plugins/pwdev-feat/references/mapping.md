# Codebase map contract (feat-map)

Adapted from the repository's SDD map workflows: a deterministic, read-only evidence scan
followed by interpreted context documents.

## 1. Evidence scan — `scripts/feat_map.py`

```sh
python3 <plugin-root>/scripts/feat_map.py --repo-root .            # print JSON, write nothing
python3 <plugin-root>/scripts/feat_map.py --repo-root . --write    # publish codebase.json
```

Output `schema: pwdev-feat.codebase`, `schema_version: "1"`, with sorted keys:
`source_commit`, `languages` (extension counts), `manifests`, `frameworks`, `commands`
(declared scripts — evidence only, **never executed**), `style_configs`, `testing`
(frameworks, e2e, test dirs, test file count), `ci`, `containers`, `migrations`, `modules`
(top-level source dirs with file counts), `sensitive_areas` (paths matching auth, payment,
webhook, token, permission, admin), `instructions_files`, `excluded` (count of skipped secret
paths) and `staleness` (previous vs. current commit).

The scanner skips dependency, build and VCS directories and never opens secret-looking paths.
With `--write`, the only file written is `.planning/feat/context/codebase.json`.

## 2. Context documents (interpreted by the skill)

Rendered from `templates/context/*.md`, each claim followed by the evidence path(s) that support
it and a confidence (`high` = read in code/config, `medium` = inferred from several files,
`low` = inferred from names only):

| File | Content |
|---|---|
| `.planning/feat/context/architecture.md` | stack and versions, architectural pattern, directory structure, module boundaries and dependencies, entry points |
| `.planning/feat/context/conventions.md` | naming (classes, files, tables, routes), imports/aliases, error handling, validation, commit style — with 1–2 real examples each |
| `.planning/feat/context/testing.md` | frameworks, test locations, real commands (unit, integration, e2e, lint), `tests_dir`, E2E scenarios dir, coverage config, Playwright presence |
| `.planning/feat/context/concerns.md` | sensitive areas, risks, technical debt, fragile modules, dependency audit results (only when the human allows running `npm audit`/`composer audit`) |
| `.planning/feat/codebase.md` | the index: 1-screen summary + links to the four documents (kept for 2.x compatibility) |

Sample key files to interpret patterns (2–3 per module type); do not read the whole repository.

## 3. Staleness

Planning skills run `feat_map.py --repo-root . --staleness`, which prints only the staleness record. A stale or missing
map is reported with the previous and current commit and a suggestion to run `feat-map`; the
planner may continue with the human's consent, noting it in §6 Assumptions.
