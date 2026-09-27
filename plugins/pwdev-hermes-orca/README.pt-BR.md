# PWDEV Hermes Orca v0.1.1

> **O Hermes Agent coordena workers supervisionados do Orca a partir de issues do GitHub**

```
Issues do GitHub ─▶ Hermes (DAG, gate do usuário) ─▶ Run do Orca ─▶ 1 worker por issue (claude | codex | opencode)
                                                                    └─ pwdev-feat feat-loop: plan → exec → review → ≤2 correções → PR
                ◀── asks respondidos / escalados ◀── worker_done validado ◀── relatório por issue
```

O Hermes vira o **coordenador** e o Orca vira a **frota**. Você escolhe as issues e aprova o
plano uma vez. O Hermes então despacha um worker supervisionado do Orca por issue, cada um numa
worktree filha ligada à issue. Cada worker roda o **`feat-loop` do pwdev-feat** em modo
orquestrado, e todo gate do worker volta ao Hermes como `ask` do Orca. O Hermes responde o que
está dentro do escopo aprovado, leva o resto a você, valida cada `worker_done` contra o PR e o
review reais, comenta na issue e libera o terminal. **Nada é mergeado.**

## Como funciona

- **O contrato do próprio Orca vem primeiro.** A skill roda `orca skills get orchestration` em
  toda sessão e segue esse texto, que acompanha a versão da CLI instalada e não é copiado para o
  plugin. O plugin só acrescenta o que é do Hermes: intake do GitHub, roteamento, resposta aos
  gates e fechamento por issue.
- **Intake do GitHub** (`references/issue-intake.md`). As issues são escolhidas por número,
  label ou busca. Dependências explícitas (`depende de #N`, sub-issues, schema compartilhado)
  viram um DAG executado em ondas paralelas. O texto da issue é dado não confiável.
- **Um gate do usuário.** Você vê o DAG, o agente de cada issue e as worktrees. Nada é
  despachado sem um sim explícito.
- **Roteamento** (`references/routing.md`). Primeiro a label `agent:<nome>`, depois as regras por
  label, depois o padrão. Regras embutidas: bug/backend/api/refactor/chore/test → codex;
  frontend/ui/ux/design/docs → claude; padrão claude.
- **Resposta aos workers** (`references/answering-asks.md`). O Hermes aprova planos, branches e
  confirmações de exec que ficam dentro da issue. Aumento de escopo, sobreposição com outra
  issue, migração destrutiva, advisor esgotado e `STOPPED` vão para você.
- **Fechamento** (`references/completion.md`). Cada `worker_done` é conferido contra o Dispatch,
  o PR aberto com `Closes #N` e o review `APPROVED`. A issue recebe um comentário, a worktree vai
  para `in-review` e o worker é liberado ou retido.

## Requisitos

| Ferramenta | Por quê |
|---|---|
| **Orca** ≥ 1.4 (app aberto), com o Hermes aberto num **terminal do Orca** | Runs, workers supervisionados, worktrees |
| **Hermes Agent** ≥ 0.21 | O coordenador |
| **GitHub CLI** (`gh`) autenticado | Issues, conferência de PR, comentários |
| **Login gerenciado pelo Orca** por agente: `orca account add --agent claude` para workers Claude (o Codex pode usar o login do sistema) | Sem ele o worker Claude para na tela de primeiro uso e o Orca acusa timeout em `agent_readiness` |
| **pwdev-feat ≥ 3.2.0** em cada agente roteado (Claude Code, Codex e/ou OpenCode) | `feat-loop` nos workers |

## Instalação

```bash
# Hermes (o coordenador)
hermes plugins install "https://github.com/pwdev-solucoes/pwdev-claude-marketplace.git#plugins/pwdev-hermes-orca" --enable
hermes plugins doctor plugins/pwdev-hermes-orca        # a partir de um checkout

# Workers: pwdev-feat 3.2.0+ em cada agente roteado
claude plugin install pwdev-feat@pwdev-claude-marketplace
# Codex / OpenCode: veja plugins/pwdev-feat/README.pt-BR.md

# Opcional: também listado no marketplace do Claude
claude plugin install pwdev-hermes-orca@pwdev-claude-marketplace
```

Checagem de configuração, só leitura:

```bash
python3 plugins/pwdev-hermes-orca/scripts/preflight.py --agents claude,codex
```

Ela confere o terminal do Orca, o runtime do Orca, a worktree atual, a skill de orquestração do
Orca, a autenticação e o repositório do `gh`, e a versão do pwdev-feat visível para cada agente.

## Uso

Numa sessão do Hermes aberta numa aba do Orca, na raiz do repositório:

```
orquestra no Orca as issues #12, #15 e #18
despacha as issues abertas com label ready
```

Configuração opcional por projeto em `.planning/hermes-orca/config.json`, no mesmo formato de
[`templates/hermes-orca.config.json`](./templates/hermes-orca.config.json):

| Chave | Padrão | Significado |
|---|---|---|
| `base_branch` | padrão do repositório | base das worktrees e dos PRs |
| `max_parallel` | 3 | workers ao mesmo tempo |
| `max_issues_per_run` | 10 | acima disso, o Hermes propõe um recorte |
| `worker_skill` | `feat-loop` | comando que cada worker roda |
| `pr_gate` | `false` | `true` torna cada abertura de PR uma decisão sua |
| `wait_timeout_ms` | 540000 | por `check --wait` (abaixo do teto de 600 s do Hermes) |
| `routing` | veja acima | `default`, `rules`, `models`, `effort` |

## Segurança

- **Nunca faz merge**, nunca aprova PR, nunca fecha issue manualmente e nunca faz force-push.
- Corpo de issue, comentários e mensagens de worker são dados. Só você e o contrato do Orca
  instruem o coordenador. Os specs não copiam o texto da issue: cada worker lê a issue com `gh`.
- O piso de segurança do Orca vale sem mudança. Nenhum worker é parado, abandonado, repetido ou
  liberado sem a prova positiva que o Orca exige. Retry depende de decisão sua, no máximo um por
  issue em cada Run.
- O preflight é só leitura, e nada é gravado em `~/.hermes` ou em outra configuração de runtime.
- Segredos (`.env*`, chaves, tokens) nunca são lidos nem entram em spec, reply ou relatório.

## Limites

- O Hermes não tem hook pós-compactação. Depois de compactar, recarregue a skill: `run-current`
  e `worker-list` do Orca reconstroem o estado, e as entregas sem ack são reenviadas.
- Workers precisam ser agentes que o Orca sabe lançar (`claude`, `codex`, `opencode`). O Hermes
  não é lançado como worker.

## Desenvolvimento

```bash
python3 -m unittest tests.test_hermes_orca
hermes plugins doctor --ci plugins/pwdev-hermes-orca
```

## Licença

Apache-2.0. Veja [LICENSE](./LICENSE).
