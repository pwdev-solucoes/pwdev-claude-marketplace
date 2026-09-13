# GLPI Multi-Runtime — Verification Verdict

Date: 2026-09-12
Branch range: `f8f324d..15f9d63`
Verifier lens: functional + compliance (single adversarial pass)

## Verdict

`CAVEATS`

All seven feature acceptance criteria survived focused refutation. The caveat is the
pre-existing marketplace README suite: its four failures are unrelated to this feature's
runtime adapters and are already recorded in the project ledger/baseline evidence. The
feature-specific checks are green.

## Evidence

Commands run from the feature worktree:

```text
python3 -m unittest discover -s plugins/pwdev-glpi/tests -p 'test_runtime_adapters.py' -v
Ran 8 tests ... OK

python3 -m json.tool plugins/pwdev-glpi/.claude-plugin/plugin.json
python3 -m json.tool plugins/pwdev-glpi/.codex-plugin/plugin.json
python3 -m py_compile plugins/pwdev-glpi/.hermes-plugin/__init__.py
git diff --check f8f324d..15f9d63
```

All commands above exited successfully. Structural tests verified the three manifests,
shared `.mcp.json` pin `@soarescbm/mcp-glpi@0.4.0`, all five runtime environment variables,
the Hermes clone/flattened layouts and first-turn-only hook, plus exactly 20 tools, 2 prompts
and 3 resources.

Additional checks:

```text
python3 scripts/validate_readme_plugins.py
validated 16 plugins in both READMEs
```

The complete `tests.test_marketplace_readmes` run was also executed fresh. It had 4 failures
inherited from the marketplace baseline (`test_every_shipped_plugin_has_a_section`,
`test_every_shipped_plugin_has_a_table_row`, `test_every_shipped_plugin_has_an_install_command`,
and `test_inventory_lines_match_plugin_contents`); the two parity/version checks and the
non-shipped-plugin check passed. No feature-specific failure was produced.

## Refutation results

1. Claude, Codex and Hermes manifests: versions are `1.2.0`; JSON parses and Hermes YAML
   declares its hook.
2. Claude and Codex both point to the same `.mcp.json`; the MCP package is pinned to `0.4.0`.
3. Hermes bootstrap registers `glpi` in clone and flattened layouts and does not mutate the
   supplied configuration object or write user configuration.
4. The shared `skills/glpi/SKILL.md` contains no `${CLAUDE_PLUGIN_ROOT}`, `/mcp`, or runtime-
   exclusive instruction-file assumptions.
5. English and Portuguese plugin/root documentation cover Claude, Codex and Hermes and include
   the explicit `hermes mcp add glpi -- npx -y @soarescbm/mcp-glpi@0.4.0` setup.
6. Structural tests cover manifests, bootstrap, catalogue counts and the shared MCP contract.
7. Secret scan of changed manifests, tests and documentation found no literal credentials;
   examples use placeholders or environment/keychain references only.

No provider-real acceptance was inferred, and no personal configuration, publish, tag, push or
merge operation was performed.
