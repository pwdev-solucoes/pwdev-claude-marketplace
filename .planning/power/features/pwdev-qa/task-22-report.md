# Task 22 — implementation report

## Status

DONE

## Scope delivered

- Added equivalent Claude Code, Codex, and Hermes Agent manifests for `pwdev-qa` at version
  `0.1.0`, using the existing PWDEV author, repository, homepage, and Apache-2.0 license.
- Declared the Codex skill directory and a three-item default prompt.
- Added a passive Hermes adapter whose `register(ctx) -> None` discovers installed skills and
  passes each `SKILL.md` as a `pathlib.Path` to `ctx.register_skill`.
- Supported repository-clone and flattened Hermes layouts, with an explicit safe error when the
  skills tree is absent.
- Registered no hooks, injected no conversation bootstrap, and declared no MCP server.
- Added packaging tests that close the inventory at exactly 29 installed skills.

## Files changed

- `plugins/pwdev-qa/.claude-plugin/plugin.json`
- `plugins/pwdev-qa/.codex-plugin/plugin.json`
- `plugins/pwdev-qa/.hermes-plugin/plugin.yaml`
- `plugins/pwdev-qa/.hermes-plugin/__init__.py`
- `tests/test_qa_packaging.py`

## TDD and verification evidence

- RED: `python3 -m unittest tests.test_qa_packaging` — 4 tests ran and failed with 4 assertion
  failures because the manifests and Hermes adapter did not exist.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_qa_packaging` — 4 tests ran,
  all passed.
- Default-Python QA suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p
  'test_qa_*.py'` — 166 tests ran; 2 import errors because Python 3.9 lacks `pdfplumber`.
- Packaged QA suite: `PYTHONDONTWRITEBYTECODE=1
  /Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
  -m unittest discover -s tests -p 'test_qa_*.py'` — 177 tests ran, all passed.
- Both JSON manifests passed `python3 -m json.tool`; the adapter and test compiled successfully
  with Python 3.9 `compile()`; `git diff --check` passed.

## Limitations

This task validates packaging contracts and adapter behavior with deterministic local fixtures.
It does not claim a real runtime smoke; discovery and invocation in Claude Code, Codex, and Hermes
Agent remain assigned to Task 24. The system Python 3.9 environment does not include the PDF test
dependency `pdfplumber`; the approved packaged Python 3.12 runtime provides it and passed the full
QA suite.
