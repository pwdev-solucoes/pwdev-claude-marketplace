# Task 04 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T19:17:18Z

These are your requirements. Every value below is exact — copy it, do not round it,
do not substitute an equivalent, do not improve it.

## Global Constraints

- Preservar alterações locais existentes em sdd_status.py e test_sdd_composy_hermes.py; registrar baseline antes da execução.
- Não marcar tarefas completas, gates aprovados ou evidências verificadas por existência de arquivo, texto do modelo ou teste de substring.
- Não traduzir IDs, enums, chaves JSON, nomes de arquivos, comandos ou evidências do usuário; idioma somente pt-BR ou en-US, escolhido no init.
- Manter campos JSON desconhecidos, publicação atômica e recusa de symlinks nos destinos e ancestrais controlados pelo plugin.
- Read-only significa nenhum arquivo de projeto criado/modificado; logs nativos do runtime são medidos separadamente.
- Não alterar autenticação, modelo padrão, configuração global, tarefas reais, branches reais ou publicar releases como parte dos testes.
- Testes reais usam repositórios temporários próprios, dois membros fleet e no máximo 300 segundos por invocação de provider; sem repetição automática de inferência malsucedida.
- Executar serialmente os providers; até 28 invocações remotas por runtime no ciclo de aceitação, registrando custo/uso quando disponível, nunca inventando zero.
- Inferência real e fleet que não possam executar por permissão, autenticação, custo ou indisponibilidade ficam BLOCKED/NOT_RUN, nunca PASS.
- Hermes, Codex e Claude Code são alvos obrigatórios de aceitação real e regressão offline.
- Kanban Hermes não está implementado neste escopo; documentação deve dizer indisponível, sem promessa de suporte operacional.

## Task 04 — Bootstrap e adaptadores reais Hermes/Codex/Claude Code
Complexity: high
Files:
- plugins/sdd-composy/.hermes-plugin/__init__.py
- plugins/sdd-composy/scripts/fleet/engine-hermes.sh
- plugins/sdd-composy/scripts/loop-engine-codex.py
- plugins/sdd-composy/scripts/loop-engine-hermes.py (NOVO)
- tests/test_sdd_composy_runtime_adapters.py (NOVO)
Interfaces:
  Consumes: register(ctx); sdd_engine_hermes_stage_command(worktree, schema, result, prompt); sdd_loop.orchestrate(root, task_id, engine, human_approved=True).
  Produces: adaptadores LOOP com run(stage_contract, root, timeout=300, executable=None) e resultado stage/status/message/verdict/evidence; adapter fleet mantém FLOW_ENGINE_* e SDD_ENGINE_*.

Steps:
- [ ] Criar providers falsos executáveis que capturam argv/cwd, produzem múltiplos eventos JSONL, resultado final, erro e timeout; executar python3 -m unittest tests.test_sdd_composy_runtime_adapters -v e observar falhas reais de protocolo.
- [ ] Trocar hermes run por interface confirmada localmente: hermes -z PROMPT --in WORKTREE. Recusar modo automatizado se não houver prova de isolamento ou consentimento específico; nunca apresentar --safe-mode como sandbox nem adicionar --yolo automaticamente.
- [ ] No LOOP Codex, separar eventos e mensagem final usando --output-last-message em destino exclusivo, com --sandbox workspace-write, e validar stage, tipos e evidence. Não fazer json.loads de JSONL completo.
- [ ] Implementar adapter LOOP Hermes com o mesmo contrato, limites de tempo e isolamento; validar JSON estrito e resultado pelo estágio solicitado. Credenciais continuam com resolução nativa do provider sem serem copiadas para contratos/logs.
- [ ] Bootstrap registra 17 skills com Path, funciona em layout original/achatado e carrega orientação de roteamento, não o corpo de init como instrução de toda sessão. Testar teto de contexto e ausência de mutação/disparo implícito.
- [ ] Validar falha do processo, resposta inválida, prompt com aspas/metacaracteres, timeout e identidade divergente. Guard de conclusão deve rejeitar resposta OK sem evidência de comando VERIFY real.
- [ ] Registrar revisão, resultado e commit.
