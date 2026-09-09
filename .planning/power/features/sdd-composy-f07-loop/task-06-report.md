# Task 06 Report — Loop skill and adapter

## Result

Implemented the portable `$sdd-loop` skill and Claude command adapter over the
existing provider-neutral `sdd_loop.py` lifecycle. The skill documents discovery,
explicit human approval, the default three-iteration bound, canonical stages,
fresh verification, cancellation, and all safe-stop conditions. Provider command
vectors remain in the dedicated Codex and Claude engine adapters.

Added Codex-facing `agents/openai.yaml` metadata and `/sdd-composy:loop` routing
for `start`, `status`, `continue`, and `cancel`.

## Tests

RED was observed before implementation: the structural registration test failed
because the loop skill, metadata, and command did not exist.

GREEN verification:

```text
python3 -m unittest tests.test_sdd_composy tests.test_sdd_composy_loop
Ran 79 tests ... OK
```

`git diff --check` passed. No commit was created.
