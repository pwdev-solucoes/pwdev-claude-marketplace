# Task 06 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T20:12:20Z

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

## Task 06 — Claude Code, encerramento e gates de LOOP/fleet
Complexity: high
Files:
- plugins/sdd-composy/scripts/fleet/teardown.sh
- plugins/sdd-composy/scripts/loop-engine-claude.py
- plugins/sdd-composy/scripts/sdd_loop.py
- tests/test_sdd_composy_fleet.py
- tests/test_sdd_composy_loop.py
Interfaces:
  Consumes: registro fleet v2, formatos legados identificados, callbacks run dos adaptadores, evidência VERIFY com hash/tempo/identidade.
  Produces: término que preserva recuperação quando validação falha; nenhuma conclusão sem os cinco estágios e evidência fresca.

Steps:
- [ ] Adicionar regressões para processo filho, lock concorrente, cancelamento, VERIFY ausente/antigo/adulterado e verificação pós-merge que falha; rodar python3 -m unittest tests.test_sdd_composy_fleet tests.test_sdd_composy_loop -v e observar falhas.
- [ ] Corrigir o LOOP Claude para extrair o resultado do envelope nativo --output-format json, rejeitando is_error e final inválido; testar o processo real de fixture. Aplicar guard de contrato/aprovação/dependências à entrada pública de orquestração, além de start/continue.
- [ ] Vincular tarefa/loop/estágio ao resultado e ao registro de comandos; dois resultados iguais sem progresso devem acionar o limite existente de correção.
- [ ] Teardown valida runtime, identidade e commit; merge exige token atual e ocorre apenas na fixture autorizada. Rodar verification_commands no commit integrado e registrar hash/exit code.
- [ ] Em falha pós-merge, não apagar worktree, evidência nem marcar completo. Em cancelamento encerrar apenas grupo de processos próprio e liberar recursos comprovadamente próprios.
- [ ] Reexecutar testes com Hermes/Codex/Claude Code simulados e regressões Claude; demonstrar preservação de sentinelas e ausência de órfãos ativos.
- [ ] Registrar revisão, resultado e commit.
