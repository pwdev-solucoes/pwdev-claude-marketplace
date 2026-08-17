# Semantic audit contract

PWDEV Flow uses an opt-in portable JSONL trail instead of runtime hooks. The trail records meaningful workflow events, not every tool invocation.

## Configuration and path

Enable with `"audit": true` in `.planning/flow/config.json`. Events live at `.planning/flow/audit/events.jsonl` with file mode limited to the current user when created by the helper.

The helper is `../scripts/flow_audit.py` relative to this reference. Invoke it with the active repository root:

```text
python3 flow_audit.py --root <repository> record --action completed --skill flow-execute
python3 flow_audit.py --root <repository> summary
python3 flow_audit.py --root <repository> events --limit 20
python3 flow_audit.py --root <repository> verify
```

## Event schema

Every line is one JSON object:

```json
{
  "schema_version": 1,
  "timestamp": "2026-08-16T12:00:00Z",
  "action": "gate_approved",
  "skill": "flow-design",
  "phase": "DESIGN",
  "status": "APPROVED",
  "target": ".planning/flow/phases/example/spec.md",
  "detail": {"decisions": 2}
}
```

Allowed actions are `started`, `completed`, `failed`, `gate_approved`, `gate_rejected`, `artifact_written`, `decision_recorded`, `memory_captured`, `memory_superseded`, `simplify_proposed`, `simplify_applied`, `archived`, `migrated`, `fleet_launched`, `fleet_stage`, `fleet_teardown`, and `external_run`.

## Recording rules

- Recording while audit is disabled succeeds without creating a file.
- Record only after the semantic event has occurred and its durable state is published. In particular, `fleet_launched` follows `ACTIVE` plus successful tmux launch, `fleet_stage` follows its atomic status publication, and `fleet_teardown` follows verified stop or merge completion.
- Keep detail small, structured, and free of file content.
- Never include environment variables, prompts, secrets, credentials, tokens, or private paths.
- For fleet and delegation events, record only slug, stage, status, provider, mode, exit code, timeout, and safe relative targets. Never record stdout, models, absolute worktree paths, or `.env.fleet` content.
- Unknown actions, invalid JSON, secret-like keys, every direct or nested key containing `model` or `prompt`, and secret targets fail before append.
- Audit failure must be reported with a sanitized semantic-action warning; it does not retroactively change, roll back, or replace the underlying lifecycle result.

## Query and integrity

`summary` returns counts by action, skill, and phase. `events` returns the latest valid events with optional action filter. `verify` validates every non-empty line and returns non-zero for malformed or invalid entries.

Do not repair an invalid trail automatically. Preserve it, report exact line errors, and require explicit direction before any corrective copy or replacement.
