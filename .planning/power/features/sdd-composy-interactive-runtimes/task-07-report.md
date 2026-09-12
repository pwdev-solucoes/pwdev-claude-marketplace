# Task 07 report

STATUS: DONE

- Added the offline `fleet-interactive` scenario with explicit runtime×UI records for Hermes, Codex, and Claude across cmux and tmux.
- The scenario consumes the real fleet launch, runtime adapter, UI-driver, and interactive-run contracts while executing only local fake CLIs/PTYS.
- Added negative classification for terminal Markdown, terminal JSON strings, tampered durable witness, dead panes, 300-second live-process timeout, divergent LOOP bindings, and unexecuted combinations.
- Added offline coverage for `auto` resolving to cmux and for headless execution. No provider invocation, approval inference, privileged flag, retry, or late fallback is permitted.
- Focused suite: 28 tests passed. Offline matrix: 6 PASS, 0 provider calls. Real human-assisted tests remain INCOMPLETE.

## Review fix round 1

- Replaced expected-label lookup results with executable file/process observations routed through durable witness, LOOP-binding, pane-liveness, and exact timeout decisions.
- Every runtime×UI row now executes the real bound `interactive-run.sh` path and the relevant UI driver's start/inspect path; the report lists only those exercised production components.
- `fleet_select_ui auto` is executed against cmux+tmux, tmux-only, and neither-available environments, with a mutation sentinel proving selection occurred first.
- Fresh verification: 28 focused tests PASS; offline matrix 6/6 PASS with zero provider calls. Real tests remain INCOMPLETE.
