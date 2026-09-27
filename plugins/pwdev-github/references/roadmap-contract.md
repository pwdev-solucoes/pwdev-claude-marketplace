# Input contract — `pwdev-roadmap/1`

`/pwdev-github:publish` accepts any `roadmap.json` in this format. pwdev-prd produces it
(`/pwdev-prd:roadmap`, validated by its `roadmap-check.py`); other plugins can too. The
canonical description lives in pwdev-prd `references/roadmap-format.md`; this is what
publishing relies on.

```json
{
  "schema": "pwdev-roadmap/1",
  "meta": { "slug": "catalogo-produtos", "title": "Catálogo de produtos", "language": "pt-BR" },
  "requirements": ["FR-01", "NFR-01"],
  "nodes": [
    { "id": "F01", "type": "phase", "title": "Fundação", "parent": null, "path": "F01-fundacao/PHASE.md" },
    { "id": "F01-E01", "type": "epic", "title": "Acesso", "parent": "F01", "path": "…/EPIC.md" },
    { "id": "F01-E01-FT01", "type": "feature", "title": "Login", "parent": "F01-E01", "path": "…/F01-E01-FT01-login.md",
      "priority": "must", "estimate": "M", "requirements": ["FR-01"], "acceptance": ["…"] },
    { "id": "F01-E01-FT01-T01", "type": "task", "title": "…", "parent": "F01-E01-FT01", "path": "…" }
  ],
  "edges": [ { "from": "F01-E01-FT01", "to": "F01-E02-FT01", "kind": "technical" } ]
}
```

- `edges[]`: `{from: A, to: B}` = **B is blocked by A**. Task edges are lifted to their feature
  when tasks are not published as issues.
- `meta.slug` names the map file `.planning/github/<slug>.map.json`.
- `meta.language` (`pt-BR` or `en`) picks the language of generated issue bodies.
- `path` is relative to the directory of `roadmap.json`; feature/epic files are embedded in
  the issue body (collapsed), so keep them free of secrets.

## Business rules and user stories (optional)

`rules[]` (`RN-xx`: `title`, `rule`, `example`) and `stories[]` (`US-xx` with `feature`,
`persona`, `action`, `value`, `priority`, `status` draft|ready, `rules`, `depends_on`,
`out_of_scope` and `acceptance[]` of `CA-xx` with `path` happy|error|edge, `type`
gherkin|check, `text`, optional `rules`). Format and quality bar: pwdev-prd
`references/user-stories.md`.

| `--stories` | Result |
|---|---|
| `body` (default) | each feature issue gets a "User stories" section: story line, CA checklist (Gherkin blocks), RN with rule and example; drafts are marked |
| `issues` | each story becomes a sub-issue of its feature (`[US-xx] title`, `type:story`, `status:draft` while draft, Tipo=História); `depends_on` becomes blocked-by between stories; the feature body lists its stories |

## Mapping

| Roadmap | `default` | `task-issues` | `flat` |
|---|---|---|---|
| Phase | milestone | milestone | milestone |
| Epic | issue | issue | — (named in the feature body) |
| Feature | issue, sub-issue of its epic | issue, sub-issue of its epic | issue |
| Task | checklist in the feature | issue, sub-issue of its feature | checklist in the feature |
| Edge | blocked-by between the issues | blocked-by (task-level kept) | blocked-by between features |

Issue titles are `[<id>] <title>`; labels `type:<type>`, `prd:<slug>`, `priority:<moscow>`.
Project fields filled (when the Project has them): Status=Backlog on creation, Tipo, Prioridade,
Estimativa, Fase, Onda (wave), Requisitos.

## Map file (`pwdev-github-map/1`)

Written after every successful step, so a failed run resumes where it stopped:
`issues{id → number, id, node_id, url, hash, item_id, fields}`, `milestones`, `sub_issues`
and `blocked_by` (`"child>parent"`, `"blocked>blocker"`), `fallback_blocked_by`, `project_url`.
A changed title/body/labels/milestone (hash) is PATCHed; nothing is ever closed or deleted.
