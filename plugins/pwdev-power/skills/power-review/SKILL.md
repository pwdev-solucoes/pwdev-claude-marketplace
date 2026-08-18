---
name: power-review
description: Use when work needs reviewing before it is merged, and when review feedback has arrived and needs acting on
---

# Review, and Receive Review

## Requesting a review

Build the reviewer's context; do not hand it your session history. It needs the requirements,
the diff, and the constraints — not how you got there.

1. Fix the range: `BASE_SHA` and `HEAD_SHA`.
2. Build the package with `scripts/review-package.sh`.
3. Dispatch a reviewer with: what this was supposed to do, the plan or requirements path, the
   package path, and the constraints quoted verbatim.

Two clauses belong in every reviewer prompt:

- **Read-only**: never move HEAD in this checkout. To inspect another state, `git worktree add`
  a temporary directory.
- **No subagents**: the reviewer reviews; it does not delegate.

Never tell a reviewer what not to flag, and never cap severity in advance. A review shaped to
agree with you is not evidence.

## Acting on findings

| Severity | When |
|---|---|
| Critical | Now, before anything else. |
| Important | Before this work proceeds. |
| Minor | Recorded; batched or deferred deliberately. |

## Receiving review

The failure mode here is agreement — implementing a suggestion because it arrived, not because
it is right. The other failure mode is defensiveness. Both skip the same step.

1. **Read** every finding before acting on any of them.
2. **Understand** it. Restate it in your own words. If you cannot, ask — do not implement what
   you have not understood.
3. **Verify** it against the codebase. Reviewers are sometimes wrong about what the code does,
   especially external ones.
4. **Evaluate.** Is it correct? Is it in scope? Does it contradict a decision the human already
   made — if so, stop and raise that rather than silently reversing it.
5. **Respond** with your technical assessment, including disagreement with a reason.
6. **Implement** one finding at a time, testing each.

If **any** finding is unclear, stop and ask before implementing **any** of them. Findings
interact; implementing three and misreading the fourth can undo the three.

## No performative agreement

Do not write "You're absolutely right!", "Great catch!", or thanks. If you find yourself typing
gratitude, delete it and state the fix instead. The reviewer needs to know what you are
changing, not how you feel about being told.

Disagreement is a normal outcome. State the technical reason and let it be discussed.
