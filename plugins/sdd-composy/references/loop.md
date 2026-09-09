# Autonomous loop contract

The loop is provider-neutral and bounded to one, two, or three iterations (three by default). It consumes a ready `TASK-NNN` identifier and publishes one atomic JSON record below `.planning/sdd-composy/loops/`. Legal active transitions are `running -> running`, or `running ->` a terminal reason. A terminal record is immutable through this interface. Terminal reasons include completion, iteration cap, missing progress, scope expansion, architectural ambiguity, destructive action, external authorization, environment failure, and cancellation. Completion requires fresh verification evidence; a phrase alone is never proof. Runtime adapters own provider-specific command vectors.

Use `python3 scripts/sdd_loop.py start TASK-001`, `status LOOP-ID`, `continue LOOP-ID [--outcome progress|complete|...]`, or `cancel LOOP-ID`.
