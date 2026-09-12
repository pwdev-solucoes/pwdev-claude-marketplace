# Task 08 Report

- Status: DONE
- Scope: restored machine-checked plugin tables, per-plugin sections, install commands, filesystem-accurate inventories, and the public pwdev-flow dual-runtime command contract in both root READMEs while preserving the concise introductions.
- RED: `python3 -m unittest tests.test_flow_claude_compat.ClaudeCompatibilityTests.test_public_docs_describe_dual_runtime_commands tests.test_marketplace_readmes.TestMarketplaceCoverage` — failed with 6 failures before the change.
- GREEN: the same command — 9 tests passed.
- Verification: `python3 -m unittest tests.test_readme_marketplace` — 1 test passed; `git diff --check -- README.md README.pt-BR.md` — passed.
- Commit range: `a2205f7..4fa3960`
- Commit: `4fa3960 docs: restore root README contracts`
