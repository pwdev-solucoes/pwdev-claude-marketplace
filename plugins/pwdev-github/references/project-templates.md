# Project templates

Presets live in `templates/projects/<name>.json`; `ghp.py preset list|show` reads them and
`ghp.py project create --spec <name|path>` applies one (an edited copy is just another spec).

## Spec format

```json
{
  "name": "roadmap-produto", "label": "…", "summary": "…",
  "title": "optional default title", "visibility": "PRIVATE",
  "description": "short description", "readme": "Markdown README of the Project",
  "fields": [
    { "name": "Status", "role": "status", "type": "SINGLE_SELECT", "builtin": true,
      "options": [ { "name": "Backlog", "color": "GRAY", "description": "…", "value": "backlog" } ] },
    { "name": "Onda", "role": "wave", "type": "NUMBER" },
    { "name": "Sprint", "role": "sprint", "type": "ITERATION",
      "iteration": { "start": "next-monday|today|YYYY-MM-DD", "duration": 14, "count": 6, "title": "Sprint {n}" } }
  ],
  "views": [ { "name": "Quadro", "layout": "Board", "setup": "Agrupar por Status" } ]
}
```

| Key | Meaning |
|---|---|
| `type` | `TEXT`, `NUMBER`, `DATE`, `SINGLE_SELECT`, `ITERATION` |
| `builtin` | the field already exists in every new Project (`Status`): only its options are replaced |
| `role` | what publish fills: `status`, `type`, `priority`, `estimate`, `phase`, `wave`, `requirements` (`start`, `end`, `sprint` are for people) |
| option `value` | the roadmap value it stands for (`epic`, `must`, `S`, `backlog`, `done`…) |
| `color` | `GRAY BLUE GREEN YELLOW ORANGE RED PINK PURPLE` |
| `views` | not creatable through the API — shown as a manual checklist |

Without a spec (e.g. a Project copied from a template), publish finds fields by common names
(`Tipo/Type`, `Prioridade/Priority`, `Estimativa/Estimate/Size`, `Fase/Phase`, `Onda/Wave`,
`Requisitos/Requirements`) and options by common labels (`Todo`, `Done`, `High`…).

## Presets

| Preset | Fields | For |
|---|---|---|
| `roadmap-produto` | Status (5), Tipo (Épico, Feature, História, Task), Prioridade, Estimativa, Fase, Onda, Requisitos, Início, Fim | roadmaps from pwdev-prd |
| `kanban` | Status (3), Prioridade | continuous flow |
| `scrum` | roadmap-produto + Sprint (iterations) | time-boxed delivery |

## Copying a template Project

`gh project copy` keeps views, workflows, fields and (optionally) draft items — the only way to
reuse views. Organizations can flag a Project as a template with
`gh project mark-template <n> --owner <org>`.
