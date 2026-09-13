# Task 06 — static snapshot review package

- Plan: `.planning/power/features/specflow-m01/plan.md`
- Amendment: `.planning/power/features/specflow-m01/plan-amendment-05-probe-fixture-gate.md`
- Brief: `.planning/power/features/specflow-m01/task-06-brief.md`
- Report: `.planning/power/features/specflow-m01/task-06-report.md`
- Base/HEAD: `fb146297d681a1a6a77d71b5c30772655802590a`
- Packaging: integral snapshot; no task commit is authorized.

Read every file in full and verify hashes. Confirm the five-file allowlist, fixture/argv
path agreement, resource-only extension boundary, budgets 3/2/1, adversarial case
coverage, beta.25 preview and absence of runtime execution or fabricated ApprovalRef.

| File | SHA-256 |
|---|---|
| `tests/test_sdd_flow_m01_compatibility.py` | `6fbe0ce718056c925d807c8033bf84236f1611c239339bb8250f048d188f487a` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/extension.toml` | `2a295e23687684bc683c2e751c60b38f20d4fc88ceef14a4989d6a85000d9c96` |
| `.planning/power/features/specflow-m01/probe/fixture/extension/agents/probe/AGENT.md` | `9651e228e3979d26b581c2c1db11c1672248cb71362065ef941d6575f02f6bf8` |
| `.planning/power/features/specflow-m01/probe/fixture/specflow-m01-loop.yaml` | `fecabbc17bdddf452d4973b24defddd3a555dd907c0ae1de425c62e5c5a23faf` |
| `.planning/power/features/specflow-m01/probe/fixture/run-config.yaml` | `4a662133b00b1b3d3a88c5e7539b82763c389b3b0a6008c89bc57305b7564685` |
| `.planning/power/features/specflow-m01/task-06-brief.md` | `a0e8d3bfac7940684a199124519bd4e61d725d169c844a5b026edcec77aeb5c1` |
| `.planning/power/features/specflow-m01/task-06-report.md` | `14da44a9ced2223a48d8aebe0197224ef7477dc32ec3bd8c4d753b075118fbe6` |
| `.planning/power/features/specflow-m01/plan-amendment-05-probe-fixture-gate.md` | `6281465371188ee01d40c4edddeb87ddc49b471a7ce25cac7a20839dca6d70ee` |

Fresh controller verification: focused suite ran 6 tests and combined M01 suite ran
39 tests, both exit 0; `git diff --check` exit 0. No mutable probe was executed.
