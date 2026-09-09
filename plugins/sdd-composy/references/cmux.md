# cmux presentation adapter

cmux is presentation only; fleet state and process lifecycle remain owned by
the fleet core. `ui-cmux.sh` records workspace and surface handles and proves
the workspace is owned by `sdd-composy` before every mutation. Missing, stale,
or foreign handles fail closed. Teardown closes only the recorded surface.

The JSON handle contains `driver`, `workspace_id`, `surface_id`, and `cwd`.
Status decoration and attention flashes are supported. UI selection falls back
to tmux and then headless when cmux is unavailable.

Ownership protocol: immediately after `new-workspace --json`, the adapter sends
`set-workspace-meta --workspace WORKSPACE_ID --owner sdd-composy
--fleet-driver cmux`. The handle is written only after this succeeds. Later
`list-workspaces --json` responses must contain the same workspace ID and the
`owner: sdd-composy` marker before any status, flash, or close operation.
