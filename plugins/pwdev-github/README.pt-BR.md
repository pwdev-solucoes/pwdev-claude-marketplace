# PWDEV-GITHUB v0.1.0

*Leia em [English](./README.md)*

> **GitHub Projects a partir de templates, roadmaps publicados com a cadeia de dependências e uma skill para tocar as issues no dia a dia — no Claude Code, Codex, Hermes Agent e OpenCode.**

```
roadmap.json (pwdev-roadmap/1) → Project a partir de template → issues + sub-issues + blocked-by → trabalho diário nas issues
```

## O que faz

| Peça | O que faz |
|---|---|
| `/pwdev-github:init` | Verifica `gh`, autenticação e o scope `project`; grava repo e Project padrão em `.planning/github.json` |
| `/pwdev-github:project [nome]` | Cria um Project a partir de um preset (`roadmap-produto`, `kanban`, `scrum`) — apresentado em tabela e personalizável (nome, dono, visibilidade, repo vinculado, campos, opções, iterações) antes de criar qualquer coisa — ou copia um Project-modelo |
| `/pwdev-github:publish <roadmap.json>` | Publica um roadmap: fases → milestones, épicos/features (e opcionalmente tasks) → issues e sub-issues, dependências → **blocked by** nativo, campos do Project (Tipo, Prioridade, Estimativa, Fase, Onda). Dry-run antes; idempotente e retomável |
| `/pwdev-github:status` | gh, scopes, repo, Project e roadmaps publicados |
| Skill `github-issues` | "criar issue", "fechar a #12", "mover a #14 para Em andamento", "a #15 está bloqueada pela #14", "fechar as tasks concluídas da FT01" — issues, sub-issues, dependências e campos do Project, uma a uma ou em lote |

Funciona sozinho e também como backend de publicação do **pwdev-prd** (`/pwdev-prd:publish <slug>`).

## Instalação

1. Instale o GitHub CLI: https://cli.github.com/ (testado com gh 2.93).
2. `gh auth login` e depois `gh auth refresh -s project` — Projects exigem o scope `project`;
   issues exigem `repo`.
3. Python 3 (só biblioteca padrão) para `scripts/ghp.py`.
4. Instale o plugin no seu runtime e rode a skill de init:

| Runtime | Instalação | Uso |
|---|---|---|
| Claude Code | `claude plugin install pwdev-github@pwdev-claude-marketplace` | `/pwdev-github:init`, `/pwdev-github:project`… |
| Codex | adicione este repositório como marketplace e habilite o **pwdev-github** (`.agents/plugins/marketplace.json`) | `$github-init`, `$github-project`… |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entrada `.hermes-plugin/`) | `skill_view("pwdev-github:github-init")` ou só peça |
| OpenCode | `python3 plugins/pwdev-github/.opencode-plugin/install.py [--project <dir>]` | `/github-init`, `/github-project`… ou a ferramenta `skill` |

Cinco skills portáveis (`skills/github-*`) são a fonte única: `github-init`, `github-project`,
`github-publish`, `github-status` (cada uma com um comando wrapper no Claude) e `github-issues`
(acionada pelo pedido). Sem subagentes e sem hooks. No Codex, o sandbox precisa liberar rede
para o `gh`. Detalhes: [references/runtime.md](./references/runtime.md).

## Mapeamento do roadmap

| Roadmap | default | task-issues | flat |
|---|---|---|---|
| Fase | milestone | milestone | milestone |
| Épico | issue | issue | — |
| Feature | sub-issue do épico | sub-issue do épico | issue |
| Task | checklist na feature | sub-issue da feature | checklist |
| Dependência | blocked-by | blocked-by | blocked-by |
| História de usuário | no corpo da feature (`--stories body`, padrão) ou sub-issue da feature (`--stories issues`) | idem | idem |

Detalhes: [references/roadmap-contract.md](./references/roadmap-contract.md) ·
presets e formato de spec: [references/project-templates.md](./references/project-templates.md) ·
receitas gh: [references/gh-recipes.md](./references/gh-recipes.md).

## Limites

- A API do GitHub não cria **views** de Project; o `project` mostra as views sugeridas como
  checklist. Copiar um Project-modelo é o jeito de reaproveitar views.
- Onde dependências nativas não existem (404/422, por exemplo GitHub Enterprise Server sem o
  recurso), o publish usa um comentário "Bloqueada por #N" e avisa.
- O publish nunca fecha nem apaga issues que saíram do roadmap; ele as lista como órfãs.

## Segurança

- Toda escrita (Project, labels, milestones, issues, vínculos, campos) passa por preview ou
  dry-run e exige um "sim" explícito.
- Nada é apagado: sem `issue delete`, `project delete` ou `item-delete`, a menos que você peça
  a exclusão nominalmente.
- A autenticação é só o token do `gh`; o plugin não guarda credenciais.
  `.planning/github/*.map.json` tem números e ids de issues, não segredos.
- O corpo das issues inclui os arquivos de feature do roadmap — não coloque segredos no roadmap.

## Licença

Apache-2.0 — veja [LICENSE](./LICENSE)
