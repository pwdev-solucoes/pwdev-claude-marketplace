---
name: github-project
description: >
  Use quando o usuário quiser criar um GitHub Project — 'criar um project no github', 'novo
  board', 'project a partir de template', 'copiar project modelo' — a partir de um preset
  (roadmap-produto, kanban, scrum) apresentado e personalizável antes de criar, ou copiando um
  Project-modelo. Não use para publicar um roadmap (github-publish) nem para mexer em issues
  (github-issues).
metadata:
  version: 0.1.0
---

# Project a partir de template

Uma pergunta por vez. Nada é criado antes do preview final e de um "sim" explícito.

`GHP="<plugin-root>/scripts/ghp.py"` — detalhes dos presets em
`<plugin-root>/references/project-templates.md`.

## 1. Pré-requisitos
Leia `.planning/github.json`. Sem ele, ou sem o scope `project`, siga a skill
`github-init` primeiro.

## 2. Origem do template

```bash
python3 "$GHP" preset list
```

Apresente:

```
Qual template usar?
1. roadmap-produto — {summary}
2. kanban          — {summary}
3. scrum           — {summary}
4. Copiar um Project-modelo existente (preserva views, workflows e campos)
```

**Opção 4 (cópia):** pergunte o dono do modelo (usuário/org) e liste os Projects dele
(`gh project list --owner <dono> --format json -q '.projects[] | "\(.number) \(.title) \(.template // false)"'`,
marcando os que são template). Depois pergunte o título e siga direto para o passo 5 com o
comando `project copy`. `--drafts` só se o usuário quiser os rascunhos do modelo.

## 3. Mostrar o preset

`python3 "$GHP" preset show <nome>` e apresente como tabela:

```
Template: roadmap-produto
| Campo       | Tipo           | Opções / uso                                    |
|-------------|----------------|-------------------------------------------------|
| Status      | Seleção        | Backlog · Pronto · Em andamento · Em revisão · Concluído |
| Tipo        | Seleção        | Épico · Feature · Task                          |
| Prioridade  | Seleção        | Must · Should · Could · Won't                   |
| Estimativa  | Seleção        | P · M · G                                       |
| Fase        | Texto          | preenchido pelo publish (F01 Fundação)          |
| Onda        | Número         | preenchido pelo publish (paralelismo)           |
| Requisitos  | Texto          | FR-xx de origem                                 |
| Início, Fim | Data           | para a view Roadmap                             |
Views sugeridas: Quadro (por Status) · Por onda (tabela) · Linha do tempo (Roadmap)
```

## 4. Personalização
Pergunte: `Quer personalizar? (n = usar como está)`. Se sim, ofereça o menu e repita até o
usuário dizer que terminou:

```
1. Nome do Project            (padrão: os argumentos ou "<produto> — Roadmap")
2. Dono                       (@me ou organização)
3. Visibilidade               (PRIVATE padrão | PUBLIC)
4. Repositório vinculado      (padrão: repo do .planning/github.json)
5. Descrição e README do Project
6. Renomear um campo
7. Editar opções de um campo de seleção (nome, cor, descrição)
8. Adicionar campo            (Texto · Número · Data · Seleção · Iteração)
9. Remover campo
10. Iterações (scrum): início, duração em dias, quantidade
0. Pronto
```

Regras ao editar:
- Mantenha o `role` do campo ao renomear (é o que o publish usa para achar o campo); campos
  novos não têm `role` e o publish não os preenche.
- Remover um campo com `role` avisa o que o publish deixará de preencher.
- Cores válidas: GRAY, BLUE, GREEN, YELLOW, ORANGE, RED, PINK, PURPLE.
- O campo `Status` já existe em todo Project novo; o preset só troca as opções dele.

Grave a spec efetiva em `.planning/github/project-spec.draft.json` (o JSON do preset com as
mudanças, mais `title` e `visibility`).

## 5. Preview e confirmação

```
Vou criar:
  Project: "{título}" em {dono} · {visibilidade}
  Campos:  {N} ({lista curta}) · Status: {opções}
  Vínculo: {owner/repo | nenhum}
Confirmar? (s/n)
```

## 6. Criação

```bash
# preset (editado ou não)
python3 "$GHP" project create --owner "<dono>" --spec .planning/github/project-spec.draft.json \
  --title "<título>" --repo "<owner/repo>"
# ou cópia de modelo
python3 "$GHP" project copy --source-owner "<dono-modelo>" --number <n> --owner "<dono>" \
  --title "<título>" --repo "<owner/repo>"
```

A saída é JSON com `number`, `url`, os campos criados e as views sugeridas. Em seguida:
- renomeie a spec para `.planning/github/project-<number>.spec.json`;
- grave em `.planning/github.json` → `project: {number, url, spec}` (merge);
- se o script falhar no meio, mostre o erro: o Project pode ter sido criado parcialmente —
  ofereça rodar `python3 "$GHP" project fields --owner <dono> --number <n>` para ver o que
  existe. Nunca apague o Project sem pedido explícito.

## 7. Views (passo manual guiado)
A API do GitHub Projects não cria views. Liste as views do preset como checklist, com o link
do Project:

```
Abra {url} e crie:
- [ ] "Quadro"         layout Board   · Agrupar colunas por Status; filtro Tipo:Feature
- [ ] "Por onda"       layout Table   · Agrupar por Onda; ordenar por Prioridade
- [ ] "Linha do tempo" layout Roadmap · Datas Início/Fim; agrupar por Fase
Dica: marque o Project como template (`gh project mark-template <n> --owner <org>`, só
organizações) para reutilizá-lo depois pela opção 4, já com as views.
```

## 8. Próximo
```
👉 github-publish <roadmap.json>   → popular com issues e dependências
👉 prd-publish <slug> (pwdev-prd)           → a partir de um PRD aprovado
```

Idioma: responda no idioma de `.planning/config.json` (`lang`); sem config, no idioma do usuário. Caminhos `<plugin-root>/...`, `references/`, `scripts/` e `templates/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do runtime (`references/runtime.md`).
