# Task 24 — independent review, round 3

## SPEC

CHANGES_REQUESTED. Reviewed `3d944e3e0ca0a3a11e76c98ffbe4b2aa6ab0e1fe..e673e4bc5cf2dda5db79fabeabdb3d51e8acbd24` and its supplied package using PWDEV Power review constraints. HEAD remained `e673e4bc5cf2dda5db79fabeabdb3d51e8acbd24`; no implementation changes, commits, or subagents.

PA-01 is substantially improved: all three named temporary transcripts exist and their complete byte counts and SHA-256 digests match the ledger. Claude/Codex tool events independently demonstrate skill use, negative probe handling, report generation and inspection within their respective sessions. Hermes proves the probe and export/inspection chain, but its claimed skill preload is not evidenced by this source. PA-02's original three mutations are rejected, but a new explicit denial still passes the strengthened oracle.

## QUALITY

- Fresh declared-environment focused suite: 12 tests passed in 3.843s (`tests.test_qa_scenarios tests.test_readme_marketplace`).
- Fresh complete QA suite: 209 tests passed in 15.088s (`unittest discover -s tests -p 'test_qa_*.py' -q`).
- README validator: 17 plugins validated in both READMEs.
- `git diff --check 3d944e3..e673e4b`: passed.
- Independently hashed all nine public files at the three ledger artifact roots: every digest and byte size matches. Parsed each PDF with pypdf: 171 pages, all 100 IDs CA-000..CA-099, FAIL and BUG-OPEN-UNMAPPED present in HTML/PDF and corresponding manifest.
- Re-ran the plugin credential-pattern scanner without printing matches: Claude=true, Codex=true, Hermes=false, as documented. Claude/Codex raw sources are explicitly not publishable; only observation tables are called sanitized. `git ls-files '*transcript*'` returns no tracked transcript; the commit changes only the four declared documentation/test files.
- Fresh in-memory adversarial probes rejected negative discovery, negative missing-tool classification, and a removed transcript digest. They accepted a negative inspection assertion and a contradicted negative-probe exit code. Appending a legitimate historical denial outside authoritative sections remained accepted.

## FINDINGS

### R3-01 — Important: Hermes source does not establish skill discovery/preload

Location: `plugins/pwdev-qa/references/runtime-smoke.md:95` and `:112`.

The referenced `/tmp/pwdev-qa-evidence-hermes-2/transcript.log` has the expected session `20260913_064516_ed1c02` and hash, but neither the cited lines 75/490–556 nor the whole transcript contains `qa-tooling`, `preload`, or `a80b97b`. Line 75 establishes a conversation session; the conclusion establishes tool absence and fixture inspection. Neither proves that the named installed skill was selected and loaded. The parent confirmed there is no captured launcher argument in this transcript. The documented all-three-step Hermes VERIFIED claim and aggregate 3/3 therefore remain unsupported, without implying that the execution was fabricated.

Correction: capture a consultable launcher/skill-loading record bound to the same successful session, including the selected skill and actual runtime/plugin provenance, then cite/hash that source. Until then retain Hermes discovery and CA-003 as unverified/BLOCKED.

### R3-02 — Important: exact Claude version disagrees with authoritative session

Location: `plugins/pwdev-qa/references/runtime-smoke.md:13` and `:22`; mirrored in `tests/test_qa_scenarios.py:48` and task-24 report.

The ledger binds the new successful session to Claude 2.1.269, but its init event at transcript line 16 explicitly reports `claude_code_version: 2.1.270`. All Claude transcript events share session `b522acbc-c139-4dec-af75-abb245a7f905`. A previous version probe must not be presented as the exact version of this successful run.

Correction: update the authoritative version from the actual session metadata, reconcile all summaries and test constants, and retain any older probe only as historical evidence. The behavior trace itself is valid.

### R3-03 — Important: explicit negative inspection still satisfies PA-02 oracle

Location: `tests/test_qa_scenarios.py:430`–`:451`.

Fresh mutation: replace the first `the session inspected ` with `the session never inspected ` in the fixture-report affirmative observation. `TestRuntimeSmokeLedger.assert_runtime_contract` accepts the modified document. Its positive regex searches an unanchored `inspected ...` substring and its rejection regex only catches `were not inspected`, so `OBSERVED — the session never inspected ... then confirmed ...` remains accepted. A second probe changes the same runtime's structured missing-tool result from exit 1 to exit 0 and is also accepted because the legacy narrative still contains exit 1. These are contradictions within the supposedly authoritative structured rows, not historical diagnostics.

Correction: validate explicit per-step result fields and the affirmative observation relationship rather than joined vocabulary; reject negation in authoritative observation rows and contradictory exit outcomes. Add these mutations, retaining a positive test that historical negative diagnostics remain valid.

### R3-04 — Minor: Codex interpreter differs from recorded command

Location: `plugins/pwdev-qa/references/runtime-smoke.md:63`.

The row says bundled Python 3.12, but transcript command events 95–100 execute `/Users/paulosoares/.local/share/uv/python/cpython-3.11.16-macos-aarch64-none/bin/python3.11` with explicit cached dependency paths. The final response at line 101 also states 3.11.16. Report creation and inspection both genuinely succeed, so this does not invalidate their behavior evidence, but the purported exact command is inaccurate.

Correction: record the actual interpreter/version and dependency-path context used by this session, distinguishing it from the separate Python 3.12 verification suite.

## REVIEW

CHANGES_REQUESTED. No new exporter implementation defect or raw-transcript publication was observed. Resolve R3-01 through R3-03 before treating this correction as accepted; reconcile R3-04 alongside the provenance correction. Previously deferred implementation-review minors remain outside this documentation correction and are not silently closed.

## ACCEPTANCE

CA-003: BLOCKED — real same-session behavior is substantially verified, but Hermes skill loading lacks consultable proof and Claude's claimed exact runtime version is contradicted by its session. Aggregate PASS/3-of-3 is not yet justified. Public fixture generation/inspection succeeds for all three recorded sessions; the fixture's intentional FAIL verdict is correctly distinct from runtime acceptance.
