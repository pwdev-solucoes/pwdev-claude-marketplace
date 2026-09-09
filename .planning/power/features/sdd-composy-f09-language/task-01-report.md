# Task 01 report — language resolver

Status: IMPLEMENTED

Implemented the runtime-neutral language contract in `scripts/sdd_language.py`.
The resolver supports exactly `pt-BR` and `en-US`, returns init-only choices
when no value exists, persists validated selections atomically in the confined
`.planning/sdd-composy/config.json`, reuses persisted preferences, and returns
`not_initialized` to downstream consumers without prompting. Invalid values
and unsafe symlink paths are rejected without mutation.

Added `references/language.md` and focused contract tests.

Verification:

```text
python3 -m unittest tests.test_sdd_composy_language
.....
OK
git diff --check
passed
```
