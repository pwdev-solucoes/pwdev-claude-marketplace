# Orchestrated mode (Orca worker)

Applies when the prompt carries a live Orca worker preamble: a Task ID, a Dispatch ID, a worker
handle, a dispatch capability and the exact `orca orchestration` commands to use. Today only
`feat-loop` supports this mode.

The preamble is authoritative. Copy its executable, handle, capability and IDs exactly; never
reconstruct, translate or broaden them. If the preamble and this file disagree, the preamble wins.
When it leaves a question open, run `<orca> skills get orchestration --reference
references/worker-contract.md` with the same executable and follow that.

## Gates become `ask`

The coordinator (usually a Hermes session running `pwdev-hermes-orca`) is your human. Every gate
the chained skills would put to the human goes to the coordinator through the preamble's `ask`
command. Never open a local question prompt the coordinator cannot answer, and never infer
approval from silence or a timeout.

Question format, so the coordinator can classify it without reading your transcript:

```
[feat-loop #<N>][gate:<kind>] <one-line question>
<≤8 lines of context: what you would do, files, commands, risks>
```

Pass the choices with `--options` (for example `approve,revise,abort`).

| `<kind>` | Raised by | Typical options |
|---|---|---|
| `interview` | the planning method's questions (≤2 rounds) | free text, or `you-decide` |
| `plan` | presenting the plan summary before execution | `approve,revise,abort` |
| `quick` | the feat-quick mini-plan | `approve,revise,abort` |
| `exec` | feat-exec's confirmation (dirty planned files, default branch) | `proceed,abort` |
| `branch` | creating or reusing a branch | `approve,abort` |
| `advice` | a second `NEEDS_ADVICE`, or the advisor budget is spent | free text, or `abort` |
| `stopped` | any `STOPPED:<condition>` a stage raises | `continue,abort` |
| `pr` | **only** when the Task spec says PRs need approval; otherwise open the PR without asking | `open,abort` |

Answer handling:
- `approve` / `proceed` / `open` / `continue`: carry on.
- `revise` with a note: change the artifact, then ask again with the same `<kind>`.
- `abort`: stop the loop and finish with `--outcome failed`.
- Free text: treat it as the human's answer to that gate.
- Timeout: the question stays pending. Resume the **same message ID** with `ask --resume`; never
  ask a duplicate.

## Checkpoints

- Heartbeats only at the cadence the preamble sets, with the `--phase` that fits: planning maps
  to `investigating`, exec and fix to `implementing`, review to `reviewing`, and a blocking ask to
  `waiting`. Skip heartbeats while blocked inside `ask`.
- Read coordinator follow-ups with the preamble's `check` command after each stage (plan, exec,
  each review, each fix cycle) and once more right before `worker_done`. A redirect or a cancel
  applies from that point on.
- `consumer_fenced` from `check`: you no longer own the Dispatch. Stop at once, send nothing, and
  leave the branch and reports in place.
- Escalate (`--type escalation`) only when the coordinator must act and no gate fits, such as
  `gh` not authenticated or the worktree on an unexpected branch.

## Completion

Send exactly **one** `worker_done` from this terminal:
- `--outcome succeeded` only when the result line is `APPROVED` **and** the PR exists.
- `--outcome failed` for every other ending: `STOPPED:*`, `FAILED` or `abort`.
- `--body` is three sentences: what changed, what the review found, and what remains. Include the
  PR URL when there is one.
- `--report-path .planning/feat/features/{slug}/review.md` (the final review), and
  `--files-modified` with the real files changed outside `.planning/`.

Then end the turn and idle. Do not poll, close the terminal or start other work.
