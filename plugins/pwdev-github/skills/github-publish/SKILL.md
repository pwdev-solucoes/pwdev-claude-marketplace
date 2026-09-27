---
name: github-publish
description: >
  Use quando um roadmap pwdev-roadmap/1 (roadmap.json) precisar ir para o GitHub — 'publicar o
  roadmap', 'criar as issues do roadmap', 'publish roadmap.json' — com issues, sub-issues,
  milestones, blocked-by e campos do Project, com dry-run, idempotente e retomável. Não use para
  uma issue avulsa (github-issues).
metadata:
  version: 0.1.0
---

# Roadmap → GitHub

Nada é escrito no GitHub antes do dry-run e de um "sim" explícito.

`GHP="<plugin-root>/scripts/ghp.py"` · contrato do roadmap em
`<plugin-root>/references/roadmap-contract.md`.

## 1. Entrada
`os argumentos` = caminho do `roadmap.json`. Leia o arquivo: `schema` deve ser
`pwdev-roadmap/1`. Se o roadmap vier do pwdev-prd, ele já passou pelo `roadmap-check.py` e
pelo gate de aprovação — não repita.

## 2. Destino
De `.planning/github.json`: `repo`, `owner`, `project.number`, `project.spec`.
- Sem config → siga a skill `github-init` primeiro.
- Sem Project → ofereça: `1. Criar agora (skill github-project)` · `2. Escolher um existente`.

## 3. Mapeamento e opções
Apresente o padrão e pergunte se quer mudar (uma pergunta):

```
Como publicar o roadmap "{título}" ({F} features, {T} tasks, {E} dependências)?
1. Padrão       — Fase=Milestone · Épico=issue · Feature=sub-issue do épico · Tasks=checklist na feature
2. Tasks viram issues — como o padrão, e cada Task vira sub-issue da feature
3. Enxuto       — só Features viram issues (fase e épico ficam no corpo e nos campos)
Histórias de usuário ({S}, {R} ready): no corpo da feature [padrão] · como sub-issues da feature
Extras: labels (type:*, priority:*, prd:<slug>) [sim] · milestones por fase [sim]
```

Mapeamento → `--mapping default | task-issues | flat`; histórias → `--stories body | issues`
(a linha de histórias só aparece se o roadmap tiver `stories`); extras desligados →
`--no-labels` / `--no-milestones`. No corpo, cada história leva a frase "Como…, quero…, para…",
os CA como checklist (Gherkin em bloco) e as RN com regra e exemplo; como sub-issue, a história
ganha label `type:story` (e `status:draft` enquanto não estiver ready), Tipo=História no Project
e "blocked by" entre histórias conforme `depends_on`.

## 4. Dry-run (obrigatório)

```bash
python3 "$GHP" publish --roadmap "<roadmap.json>" --owner "<owner>" --repo "<repo>" \
  --number <n> --mapping <m> --stories <body|issues> [--no-labels] [--no-milestones] --dry-run
```

Resuma o JSON (não cole inteiro):

```
Publicação em {repo} · Project #{n}
  Issues:        {create} novas · {update} atualizadas · {unchanged} sem mudança
  Sub-issues:    {n}      Blocked-by: {n}      Milestones: {lista}
  Labels:        {lista} (as que não existirem serão criadas)
  Mapa:          .planning/github/{slug}.map.json
Publicar? (s/n)
```

Se `create`, `update`, vínculos e milestones estiverem todos vazios: "Nada a publicar" e PARE.

## 5. Publicação
Mesmo comando sem `--dry-run`, com `--spec <project.spec>` quando existir (resolve campos
renomeados). A saída é JSON:

- `status: OK` → mostre URL do Project, contagens e o log resumido. Se houver
  `fallback_blocked_by > 0`, explique: o repositório não aceita dependências nativas, então
  o bloqueio virou comentário "Bloqueada por #N".
- `status: FAILED` → mostre o erro e diga que **rodar o mesmo publish retoma** de onde parou
  (o mapa guarda cada passo concluído). Causas comuns: scope `project` ausente
  (`! gh auth refresh -s project`), sem permissão de escrita no repo, rate limit.

## 6. Depois
- Sugira commitar `.planning/github/{slug}.map.json` com o roadmap (outro dev continua o
  publish sem duplicar issues).
- Republicar após revisar o roadmap atualiza título/corpo das issues alteradas e cria só o
  que falta; nunca fecha nem apaga issues que saíram do roadmap — liste-as como
  "órfãs" (IDs no mapa que não estão mais no roadmap) e ofereça fechá-las pela skill
  `github-issues`, com confirmação.

## Proibições
- NUNCA publicar sem dry-run e confirmação
- NUNCA editar o mapa à mão para "forçar" recriação — issues duplicadas não somem sozinhas
- NUNCA apagar issues ou Projects; no máximo fechar/arquivar, com pedido explícito

Idioma: responda no idioma de `.planning/config.json` (`lang`); sem config, no idioma do usuário. Caminhos `<plugin-root>/...`, `references/`, `scripts/` e `templates/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do runtime (`references/runtime.md`).
