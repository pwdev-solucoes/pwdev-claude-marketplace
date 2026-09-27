# Changelog

## 0.1.1 — 2026-09-27

Correções do primeiro teste de ponta a ponta (hermes-orca-smoke: 2 issues, workers Claude e
Codex, os dois PRs com review APPROVED):

- A skill diz onde fica a raiz do plugin e manda rodar o preflight na raiz do repositório (o
  Hermes perdeu duas chamadas procurando `references/`).
- Preflight: agente roteado sem login que o Orca use (`orca account list`) vira blocker com
  `orca account add --agent <agente>`. Sem isso, o worker Claude parava na tela de primeiro uso e
  o Orca acusava timeout em `agent_readiness`.
- Retry separado em falha de lançamento (um relançamento automático, reaproveitando a worktree) e
  falha do trabalho (só com decisão do usuário). Novos procedimentos para cancelar ou trocar o
  agente a pedido do usuário (`stop_unknown` → pergunta → `worker-abandon` → Task substituta).
- Worktrees que sobram e mudanças de configuração feitas a pedido entram no relatório final.
  Proibido alterar configuração de runtime dos agentes sem pedido explícito.
- O spec do worker diz se o PR tem gate (`pr_gate`).

## 0.1.0 — 2026-09-27

Primeira versão.

- Skill `hermes-orca`, que faz o Hermes coordenar workers supervisionados do Orca. Carrega o
  contrato atual do Orca com `orca skills get orchestration`, sem copiá-lo.
- Intake de issues do GitHub com DAG em ondas, um gate de aprovação do usuário e roteamento de
  agente por label (`agent:<nome>`, regras, padrão).
- Cada worker roda o `feat-loop` do pwdev-feat (≥ 3.2.0) em modo orquestrado. Os gates dele
  chegam como `ask`: o Hermes responde o que está dentro do escopo aprovado e escala o resto ao
  usuário.
- Fechamento por issue: valida o `worker_done` contra o Dispatch, o PR com `Closes #N` e o review
  `APPROVED`; comenta na issue, move a worktree para `in-review` e libera ou retém o worker.
  Nunca faz merge.
- `scripts/preflight.py`, só leitura: terminal do Orca, runtime, worktree, skill de orquestração,
  `gh` e versão do pwdev-feat por agente.
- Adaptador Hermes: registra a skill com `Path` e injeta o bootstrap no primeiro turno somente
  dentro de um terminal do Orca.
