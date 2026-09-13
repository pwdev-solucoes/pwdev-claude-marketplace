# Task 02 review — multi-runtime read-only

SPEC: PASS
QUALITY: FAIL

## Findings by severity

- Critical: none.
- Important: none.
- Minor: the supplied test patch references `plugins/pwdev-glpi/.codex-plugin/plugin.json`,
  but that path is absent in the reviewed checkout (the plugin currently contains
  `.claude-plugin/plugin.json`). As a result, the advertised runtime-adapter test
  suite cannot be executed against this tree until the manifest baseline/path is
  reconciled. The supplied patch also declares `CONTEXT_SPILL_LIMIT = 4000` but
  never applies it; if the brief requires bounded bootstrap context, that limit is
  currently declarative only.

## Evidence

- `plugin.yaml` declares `name: pwdev-glpi`, version `1.2.0`, and the
  `pre_llm_call` hook.
- `register(ctx)` resolves the shared `skills/glpi/SKILL.md`, registers the
  `glpi` skill, and registers `pre_llm_call`; implementation uses Python stdlib
  (`pathlib`) only.
- `_plugin_dir()` supports both the cloned `.hermes-plugin/__init__.py` layout and
  the flattened layout where `__init__.py` is at the plugin root. The supplied
  test exercises both layouts.
- The hook returns bootstrap context only when `is_first_turn=True`; subsequent
  turns return `None`. It reads the skill and does not mutate the supplied config.
- The registered skill is the existing GLPI skill and its documented operations
  distinguish read-only entities from ticket mutations, with confirmation rules
  for writes.
- The supplied test additions cover manifest/bootstrap registration, clone and
  flattened layouts, first-turn/no-mutation behavior, and the existing contract
  checks (eight tests claimed by the task). Execution was not possible in this
  checkout because `plugins/pwdev-glpi/tests/test_runtime_adapters.py` and the
  referenced `.codex-plugin` manifest are absent.
- Brief and report paths named by the task were also absent; this review therefore
  does not infer requirements beyond the supplied review package and repository
  evidence.

VERDICT: Task 02 requires correction of the manifest/test baseline before quality
can pass.
