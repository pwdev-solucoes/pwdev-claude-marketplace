# Task 07 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T21:15:54Z

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

## Task 07 — Documentação coerente com os três runtimes
Complexity: medium
Files:
- plugins/sdd-composy/README.md
- plugins/sdd-composy/README.pt-BR.md
- plugins/sdd-composy/references/runtime.md
- plugins/sdd-composy/references/fleet.md
- plugins/sdd-composy/references/status.md
Interfaces:
  Consumes: CLI, schemas e respostas das Tasks 01–06.
  Produces: documentação equivalente de instalação, estado, idioma, limitações, runtime e recuperação.

Steps:
- [ ] Revisar documentação contra os comandos finais; substituir hermes run e remover a afirmação obsoleta de que a fleet nunca inicia processos.
- [ ] Explicar autoridade JSON, formato task aninhado, migração explícita e diagnóstico do bundle legado; nenhuma recomendação de editar state para simular aprovação.
- [ ] Documentar semântica de existing_directory versus symlink, idioma da governança e read-only do status.
- [ ] Explicar isolamento obrigatório da automação Hermes, ausência de fallback e ausência de Kanban implementado; separar suporte instalado de suporte efetivamente validado.
- [ ] Executar python3 scripts/validate_readme_plugins.py e python3 -m unittest tests.test_sdd_composy tests.test_readme_marketplace -v; verificar links e comandos semanticamente, sem considerar grep prova de runtime.
- [ ] Registrar revisão, resultado e commit.
