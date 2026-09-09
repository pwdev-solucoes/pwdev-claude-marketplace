# Task 03 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-09T19:02:09Z

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

## Task 03 — Mapa sem bypass de idioma e sem inventário duplicado
Complexity: medium
Files:
- plugins/sdd-composy/scripts/sdd_map.py
- tests/test_sdd_composy_runtime.py
- tests/test_sdd_composy_language.py
Interfaces:
  Consumes: resolve_language(root); build_map(root, output_dir=None); write_map(root, data, output_dir=None).
  Produces: write_map retorna NOT_INITIALIZED sem mutação quando idioma ausente, independentemente de files_observed; saída confinada e mapa estável.

Steps:
- [ ] Adicionar fixture não vazia sem init, com .worktrees, contexto gerado e destino symlink; executar python3 -m unittest tests.test_sdd_composy_runtime tests.test_sdd_composy_language -v e observar regressões.
- [ ] Remover fallback inglês de write_map; validar contexto/destino e idioma antes de criar arquivos.
- [ ] Excluir worktrees aninhados e o diretório de saída do mapa; testar repetição com contagem estável e preservação de diretórios legítimos.
- [ ] Restaurar teste de falha atômica de publicação dos companions com fixture previamente inicializada; manter teste separado que recusa ausência de init.
- [ ] Validar os dois idiomas, limpeza de temporários e preservação dos arquivos anteriores quando houver erro.
- [ ] Registrar revisão, resultado e commit.
