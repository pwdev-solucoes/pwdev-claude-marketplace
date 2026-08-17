# PWDEV Code migration contract

Migration adopts a legacy PWDEV Code project without rewriting its existing `.planning/` workspace. Flow writes only under `.planning/flow/`.

## Detect

A project is a migration candidate when `.planning/config.json` exists and `.planning/flow/config.json` does not. Read only the legacy configuration and structural artifact paths; never read secret files or external provider credentials.

## Configuration plan

Use `../scripts/migrate_legacy.py` relative to this reference:

```text
python3 migrate_legacy.py --root <repository> plan
python3 migrate_legacy.py --root <repository> apply
```

`plan` is read-only and reports mappings, excluded field names, and target conflicts. `apply` requires prior user approval, creates `.planning/flow/config.json` exclusively, and preserves `.planning/config.json` byte-for-byte.

Mappings:

| PWDEV Code | PWDEV Flow |
|---|---|
| `lang` | `language` |
| `audit` | `audit` |
| `type` | `repository_type` |
| `framework`, `version` | `migration` metadata |
| `default_intensity`, `branch_strategy`, `commit_convention` | `legacy` compatibility metadata |

Flow sets `schema_version: 1`, `runtime: codex`, and `auto_commit: false`. Model profiles, overrides, parallel execution, external agents, unknown keys, and secret-like fields are excluded.

## Legacy artifacts

Do not bulk move or rename `.planning/context`, `.planning/product`, `.planning/phases`, `.planning/quick`, `.planning/memory`, audit databases, or archives.

After configuration migration:

1. inventory legacy Markdown artifacts and their links;
2. identify the active legacy phase and approval state;
3. propose exact files that Flow should consult or copy;
4. require approval before copying;
5. never overwrite a Flow artifact;
6. write `.planning/flow/migration.md` with source path, adopted paths, skipped paths, conflicts, and date.

SQLite audit databases remain legacy evidence. Flow may link to them but does not convert them into JSONL events or claim semantic equivalence.

## Compatibility

Use `$flow-compat` for supported old command intent. A legacy command does not authorize moving data, changing Git, or enabling deferred Marco 5 functionality.
