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

## Fix round 1

### Root cause

The first adapter treated directory discovery as the runtime inventory and interleaved that
discovery with registration callbacks. It therefore accepted 28 or 30 skills and could expose a
partial result before discovering a later problem. Its `is_dir()` and `is_file()` checks also
followed symlinks, while the test context stored calls in a dictionary and compared sets, erasing
observable order and duplicate registrations.

### Correction and evidence

- Added a closed 29-name inventory and a deterministic, confined preflight before the first
  callback. Missing, extra, non-directory, missing-file, root-symlink, directory-symlink, and
  file-symlink states now fail explicitly without any registration call.
- Registration paths are canonical `pathlib.Path` instances below the canonical skills root.
- A callback exception propagates immediately and prevents later callbacks. The adapter documents
  that Hermes exposes no transaction for rolling back callbacks that already succeeded.
- Replaced dictionary/set recording with an ordered call list and exact comparison of all 29
  `(name, path)` pairs.
- RED: focused suite ran 7 tests with 5 failures, all in the previously accepted 28/30 and symlink
  cases. Clone/flattened, manifest, missing-tree, normal inventory, and callback-stop scenarios
  remained valid.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_packaging` — 7 tests ran,
  all passed.
- Packaged suite: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py'` — 180 tests ran, all
  passed.
- Mutation probe removing deterministic sorting failed the focused suite; mutation probe
  duplicating each callback failed exact sequence/cardinality assertions. Both mutations were
  reverted and the focused suite returned to green.

## Fix round 2

### Root cause

The first symlink fixtures pointed only outside the skills root. Confinement validation therefore
rejected them even when either explicit no-symlink guard was removed, so those fixtures coupled two
rules and could not prove that internal aliases were independently forbidden.

### Correction and evidence

- Added an internal directory alias from one expected skill name to another expected skill
  directory and an internal `SKILL.md` alias to another expected skill file. Both destinations
  remain below the canonical skills root, isolating the explicit no-symlink policy.
- Directory-guard mutation RED: removing `skill.is_symlink()` made the internal-directory subtest
  fail because registration returned without raising.
- File-guard mutation RED: removing `skill_file.is_symlink()` made the internal-file subtest fail
  for the same reason.
- Both product mutations were reverted. No product relaxation or implementation change was kept.
- GREEN: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_qa_packaging` — 7 tests ran,
  all passed, including five root/directory/file symlink variants.
- Packaged suite: Python 3.12 `unittest discover -s tests -p 'test_qa_*.py'` — 180 tests ran, all
  passed.
