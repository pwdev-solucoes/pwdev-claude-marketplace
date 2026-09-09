# Task 01 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T17:16:05Z

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

## Task 01 — Autoridade das tarefas, status e trace
Complexity: high
Files:
- plugins/sdd-composy/scripts/sdd_status.py
- plugins/sdd-composy/scripts/sdd_tasks.py
- plugins/sdd-composy/scripts/sdd_trace.py
- tests/test_sdd_composy_observability.py
- tests/test_sdd_composy_tasks.py
Interfaces:
  Consumes: status(root, feature=None, include_tasks=False, include_fleet=False); import_tasks(markdown_root, output, prd_slug=None, root=None, now=None); validate(data, root=None).
  Produces: status com sources preservado, diagnósticos malformed/divergent prioritários e fila baseada em .planning/sdd-composy/tasks/; import sem regressão silenciosa de estados JSON.

Steps:
- [ ] Criar regressões comportamentais para meta.task ausente/vazio, configuração malformada com tarefa running, loops/fleet ativos com erro prévio, tarefas completas sem ready e duas features filtradas.
- [ ] Rodar python3 -m unittest tests.test_sdd_composy_observability tests.test_sdd_composy_tasks -v e registrar falhas esperadas antes da correção.
- [ ] Validar fontes antes de agregá-las; nenhum ramo posterior pode apagar malformed/unsafe_symlink/divergent. Validar tipos JSON e IDs; fonte vazia inválida não recebe high.
- [ ] Ler a projeção JSON canônica; comparar Markdown sem sobrescrever JSON no import. Diferenciar tarefa elegível de pronta/aprovada; tarefa complete não autoriza concluir feature. Recusar promoção retroativa sem evidência.
- [ ] Resolver trace em .planning/sdd-composy/trace/; documentar na assinatura interna se sdd_trace recebe raiz operacional ou raiz de repositório e impedir dupla concatenação. Filtrar feature de fato e testar ancestrais symlink.
- [ ] Reexecutar suíte focada e comparar hashes de fixture antes/depois de status, incluindo config, Markdown, JSON, trace e arquivos sentinela.
- [ ] Registrar resultado/revisão e criar commit exclusivo da tarefa após aprovação de execução.
