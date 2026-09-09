# Task 05 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T19:33:58Z

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

## Task 05 — Fleet e schema concordantes nos três runtimes
Complexity: high
Files:
- plugins/sdd-composy/scripts/fleet/launch.sh
- plugins/sdd-composy/scripts/fleet/run.sh
- plugins/sdd-composy/schemas/fleet-member.schema.json
- tests/test_sdd_composy_fleet.py
- tests/test_sdd_composy_fleet_runner.py
Interfaces:
  Consumes: adapters sdd_engine_RUNTIME_* e task contracts validados; runtime CLI claude/codex/hermes.
  Produces: registro schema_version 2 com runtime claude-code/codex/hermes, worktree_path absoluto canônico e estados pending/running/completed/failed/blocked/cancelled; reader legado com diagnóstico antes de migração.

Steps:
- [ ] Criar teste que valida os JSON realmente emitidos pelo launcher contra schema, incluindo required fields e estados terminais; executar python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_fleet_runner -v para observar falhas.
- [ ] Adicionar Hermes ao schema, normalizar claude para claude-code nos registros e de volta apenas para selecionar CLI. Exigir runtime explícito inclusive em prepare-only; rejeitar runtime desconhecido antes de qualquer mutação.
- [ ] Emitir todos os campos obrigatórios; versionar evolução para caminho absoluto, validar registro Git e confinamento de evidências. Rejeitar metadata de outro repositório mesmo que o path contenha fleet/members.
- [ ] Corrigir caminho Compose para HERE/../../templates/docker-compose.sdd-fleet.yml; vincular Compose ao owner e aos recursos de cada membro para que teardown saiba exatamente o que encerrar.
- [ ] Provar dois membros com IDs, worktrees, branches e portas distintos, impedimento de sobreposição e nenhum fallback de runtime; resultado inválido nunca publica completed.
- [ ] Testar rollback de falha antes/depois da criação do worktree verificando git worktree list --porcelain e existência de todos os caminhos registrados, sem depender de substring do nome.
- [ ] Registrar revisão, resultado e commit.
