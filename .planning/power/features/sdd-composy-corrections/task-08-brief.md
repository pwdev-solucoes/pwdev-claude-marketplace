# Task 08 — brief

Plan: .planning/power/features/sdd-composy-corrections/plan.md
Generated: 2026-09-10T00:55:20Z

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

## Task 08 — Aceitação real dos três runtimes
Complexity: high
Files:
- scripts/sdd_runtime_smoke.py (NOVO)
- tests/test_sdd_composy_runtime_smoke.py (NOVO)
- tests/test_sdd_composy_hermes.py
- plugins/sdd-composy/references/hermes-tools.md
- .planning/power/features/sdd-composy-corrections/evidence.md (NOVO na execução)
Interfaces:
  Consumes: plugin e contratos corrigidos das Tasks 01–07.
  Produces: CLI proposta sdd_runtime_smoke.py com --mode offline|real, --runtime hermes|codex|claude|all, --language pt-BR|en-US|both, --scenario read-only|lifecycle|fleet|all, --output e --max-calls-per-runtime; sumário JSON e relatório de evidência.

Steps:
- [ ] Escrever testes do harness: nenhum provider real no modo offline, teto de invocações, timeout, diretório exclusivo, saída sanitizada, cleanup próprio e recusa de fixture com aprovação inventada.
- [ ] Substituir assertivas de substring em test_sdd_composy_hermes.py por registro/discovery reais ou fake ctx que preserve o tipo original de Path; validar resolução das 17 skills e falha diagnóstica após indisponibilidade do bootstrap.
- [ ] Executar aceitação offline completa e preflight real conforme matrix.md; guardar versões, fingerprint do código e snapshot do Git antes das execuções.
- [ ] Executar os três providers em sequência com o mesmo objetivo, através de adaptadores/launcher reais, nas fixtures descritas em matrix.md; validar JSON retornado externamente, comparar hashes e permissões.
- [ ] Exercitar handoff Hermes para Codex, Codex para Claude Code e Claude Code para Hermes no mesmo contrato sem alterar IDs/gates; verificar sem novas chamadas remotas a recuperação de evidência adulterada e status divergente.
- [ ] Produzir evidence.md com cada cenário PASS/FAIL/BLOCKED/NOT_RUN, duração, exit code, hashes e uso disponível. Rever com lente funcional e de contratos; sem aprovação global se qualquer critério obrigatório faltar.
- [ ] Rodar a suíte final, registrar veredito e commits; publicação/push continuam fora desta fase.
