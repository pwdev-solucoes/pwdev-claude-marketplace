# F02 Task 02 — Round 1 Review

## SPEC

PASS. The four rule templates remain present, concern-specific, and linked from
the canonical `AGENTS.md`. The updated tests now parse Markdown destinations and
assert the exact four rule links. Each rule also has an explicit responsibility
marker, and the tests reject reuse of those markers by another rule.

## QUALITY

CHANGES_REQUESTED. The focused suite passes (`python3 -m unittest
tests.test_sdd_composy_runtime`: 7 tests passed) and the previous responsibility
markers are a meaningful improvement. The two prior findings are only partially
closed:

### P2-1 — Partially addressed: link resolution is still tautological

`tests/test_sdd_composy_runtime.py:59-65` parses the canonical destinations and
checks the exact set, which closes the substring/typo portion of the finding.
However, the “resolution” assertion compares two path expressions constructed
from the same destination; it never creates or checks a representative installed
file (`Path.exists()`). Lines 90-96 repeat the same tautological comparison for
each rule's `../AGENTS.md` link. A broken destination can still pass if both sides
of the assertion derive from that broken string.

Disposition: parsing addressed; actual target resolution remains open. Add a
temporary representative install layout (or resolve against explicit expected
paths) and assert the resolved targets exist and are regular files.

### P2-2 — Partially addressed: responsibility markers are covered, but policy
non-duplication is not strongly protected

`tests/test_sdd_composy_runtime.py:75-100` now requires one marker per rule and
rejects that exact marker in other files. This closes the earlier absence of
explicit ownership checks. It does not detect duplicated responsibility text or
policy expressed with different wording, so a second rule could reproduce the
workflow/testing/architecture rules while avoiding the marker. The brief requires
non-duplicative templates, not merely unique labels.

Disposition: explicit responsibility coverage addressed; strong non-duplication
coverage remains open. Add stable ownership/exclusion assertions for each rule's
policy sections (and corresponding forbidden cross-concern markers), or compare
normalized responsibility sections against an expected per-file contract.

## REVIEW

`CHANGES_REQUESTED`

No template defect was observed, and HEAD remains unchanged. Close the two
remaining test gaps before treating Task 02 as fully verified.
