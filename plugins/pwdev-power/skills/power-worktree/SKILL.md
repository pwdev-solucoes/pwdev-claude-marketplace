---
name: power-worktree
description: Use when starting feature work that needs isolation from the current workspace, or before executing an implementation plan
---

# Work in an Isolated Workspace

## Step 0 — You may already be isolated

Check before creating anything:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
git rev-parse --show-superproject-working-tree
```

If `GIT_DIR` differs from `GIT_COMMON` **and** the third command prints nothing (you are not in
a submodule, where the same difference appears for an unrelated reason), you are already in a
worktree. Skip to Step 2.

## Step 1a — Native tooling first

If your harness has its own worktree mechanism — an `EnterWorktree` tool, a `/worktree`
command, a `--worktree` flag — **use it**.

Running `git worktree add` when a native tool exists is the most common mistake here: it
creates a worktree the harness does not know about, so its own bookkeeping points at the old
one, and everything after that is confusing in a way that is hard to trace back.

## Step 1b — Fallback

Only if there is no native tool. Get consent first: this changes where the human's work
happens.

Choose the location by priority: what the human specified, then an existing `.worktrees/`, then
an existing `worktrees/`, then `.worktrees/` as the default.

**Check it is ignored before creating it:**

```bash
git check-ignore -q .worktrees/ || echo "not ignored — add it to .gitignore first"
git worktree add .worktrees/<slug> -b <branch>
```

An un-ignored worktree directory turns the entire checkout into untracked noise inside the
parent repository.

If `git worktree add` fails on permissions, you are probably in a sandbox that cannot write
where you asked. Say so; do not retry with `sudo` or a path outside the repository.

## Step 2 — Set it up

Install dependencies with the project's real command, read from its manifest. Copy the local
environment files the project needs — **except** anything holding a secret, which the human
provides.

## Step 3 — Green baseline

Run the test suite **before** changing anything.

A baseline you did not take is a baseline you will invent later, and the first failure will
look like yours whether it is or not. If the suite is already red, say so now and agree what
"green" means for this work.
