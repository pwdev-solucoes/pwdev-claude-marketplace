# gh recipes — issues, sub-issues, dependencies, Project items

`R` = `owner/repo`, `O` = Project owner (`@me` or org), `P` = Project number,
`GHP="<plugin-root>/scripts/ghp.py"` (plugin root per `references/runtime.md`). Multi-line text always goes through a file.

## Issues

```bash
# create (returns the URL)
gh issue create --repo R --title "Título" --body-file /tmp/body.md \
  --label "type:task" --assignee "@me" --milestone "F01 Fundação"

# read
gh issue view 14 --repo R --json number,title,state,labels,assignees,milestone,url,body
gh issue list --repo R --state open --label "prd:catalogo" --search "FT01 in:title" \
  --json number,title,state,url --limit 100

# edit
gh issue edit 14 --repo R --title "Novo título" --add-label "bug" --remove-label "type:task" \
  --add-assignee maria --milestone "F02 Expansão"
gh issue edit 14 --repo R --body-file /tmp/body.md

# comment / close / reopen
gh issue comment 14 --repo R --body-file /tmp/comment.md
gh issue close 14 --repo R --reason completed --comment "Entregue em #52."
gh issue close 14 --repo R --reason "not planned" --comment "Fora do escopo após revisão do PRD 1.2.0."
gh issue reopen 14 --repo R --comment "Regressão encontrada em produção."
```

## Checklist of tasks inside a feature body

```bash
gh issue view 14 --repo R --json body -q .body > /tmp/body.md
# change "- [ ] F01-E01-FT01-T02 ..." to "- [x] F01-E01-FT01-T02 ..." in /tmp/body.md
gh issue edit 14 --repo R --body-file /tmp/body.md
```

## Sub-issues and dependencies (REST, wrapped by ghp.py)

```bash
python3 "$GHP" link sub     --repo R --parent 10 --child 14   # 14 becomes a sub-issue of 10
python3 "$GHP" link unsub   --repo R --parent 10 --child 14
python3 "$GHP" link block   --repo R --issue 15 --blocker 14  # 15 is blocked by 14
python3 "$GHP" link unblock --repo R --issue 15 --blocker 14
python3 "$GHP" deps         --repo R --issue 14               # blocked_by, blocking, sub_issues
```

The API takes the issue's internal `id`, not its number — `ghp.py` resolves it. Raw form:
`gh api repos/R/issues/15/dependencies/blocked_by --method POST -F issue_id=<id of #14>`.

## Project items

```bash
python3 "$GHP" project fields --owner O --number P         # names, types, options, iterations
gh project item-add P --owner O --url https://github.com/R/issues/14 --format json
python3 "$GHP" item set --owner O --number P --url https://github.com/R/issues/14 \
  --field Status --value "Em andamento"                      # single select by option name
python3 "$GHP" item set ... --field Onda --value 2           # number
python3 "$GHP" item set ... --field Início --value 2026-10-06 # date
python3 "$GHP" item set ... --field Sprint --value "Sprint 2" # iteration by title
gh project item-list P --owner O --format json --limit 200    # items with their field values
gh project item-archive P --owner O --id <item id>
```

`item set` adds the issue to the Project when it is not there yet (adding is idempotent).

## Batch pattern

```bash
gh issue list --repo R --label "prd:catalogo" --search "FT01 in:title" --state open \
  --json number,title -q '.[] | "\(.number)\t\(.title)"'
# show the table, confirm once, then loop:
for n in 21 22 23; do gh issue close "$n" --repo R --reason completed --comment "…" || echo "FAIL $n"; done
```

## Errors

| Message | Meaning |
|---|---|
| `INSUFFICIENT_SCOPES` / `project` | run `! gh auth refresh -s project` |
| `Resource not accessible by integration` / 403 | no write permission on the repo |
| 404 on `dependencies/blocked_by` | dependencies unavailable (e.g. GHES) — use a "Bloqueada por #N" comment |
| 422 on `sub_issues` | already a sub-issue elsewhere, or would exceed the depth limit |
