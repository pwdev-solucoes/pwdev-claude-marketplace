# Task 07 report

STATUS: DONE

- Added the offline `fleet-interactive` scenario with explicit runtime×UI records for Hermes, Codex, and Claude across cmux and tmux.
- The scenario consumes the real fleet launch, runtime adapter, UI-driver, and interactive-run contracts while executing only local fake CLIs/PTYS.
- Added negative classification for terminal Markdown, terminal JSON strings, tampered durable witness, dead panes, 300-second live-process timeout, divergent LOOP bindings, and unexecuted combinations.
- Added offline coverage for `auto` resolving to cmux and for headless execution. No provider invocation, approval inference, privileged flag, retry, or late fallback is permitted.
- Focused suite: 28 tests passed. Offline matrix: 6 PASS, 0 provider calls. Real human-assisted tests remain INCOMPLETE.
