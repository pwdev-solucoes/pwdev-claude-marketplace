# Task 02 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T17:33:43Z

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

## Task 02 — Init verdadeiro, idempotente e localizado
Complexity: high
Files:
- plugins/sdd-composy/scripts/sdd_init.py
- plugins/sdd-composy/scripts/sdd_localization.py (NOVO)
- tests/test_sdd_composy_runtime.py
- tests/test_sdd_composy_language.py
Interfaces:
  Consumes: resolve_language(root, explicit=None, init=False); persist_language(root, language); plan/apply/verify existentes.
  Produces: created contendo apenas criações efetivas; claude_link_ok verdadeiro apenas para link correto; claude_compatibility com symlink/existing_directory/conflict; render_governance(contents, language) sem traduzir dados dinâmicos.

Steps:
- [ ] Reproduzir apply com conflitos, diretórios .agents/.claude existentes, symlink ancestral, config inválida, falha no meio da publicação e reaplicação; observar falhas com python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v.
- [ ] Localizar todos os textos dos documentos gerados AGENTS.md, CLAUDE.md e quatro regras através de renderer de blocos estáticos, preservando caminhos, IDs e conteúdo de usuário; proibir substituição indiscriminada sobre o documento renderizado.
- [ ] Tornar plan/inspect read-only; validar token e colisões antes de escrever; reportar criações, arquivos existentes, conflitos e publicação parcial com precisão. Nunca retornar ok quando restar falha obrigatória.
- [ ] Criar estado INIT conforme state.schema.json somente após geração válida; preservar estado existente e campos desconhecidos. verify exige idioma/configuração válidos e relata estado ausente em instalações antigas com ação explícita de reconciliação.
- [ ] Compatibilidade com .claude existente exige arquivo ponte coerente; não adotar conteúdo por mera existência de diretório. Regras e configuração existentes permanecem intactas.
- [ ] Reexecutar testes nos dois idiomas e em segunda aplicação; demonstrar created vazio na reaplicação e ausência de mutação no preview.
- [ ] Registrar revisão, resultado e commit da tarefa.
