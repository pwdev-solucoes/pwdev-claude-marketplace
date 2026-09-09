---
type: PLAN
okf_version: "0.2"
generated:
  by: agent:codex
  at: "2026-09-09T17:02:36Z"
lifecycle:
  status: APPROVED
human_approval:
  status: APPROVED
  at: "2026-09-09T17:14:54Z"
verified: []
---

# SDD Composy — Plano completo de correção
Status: APPROVED
Spec: .planning/power/features/sdd-composy-corrections/spec.md
Updated: 2026-09-09

For agentic workers: execute this with pwdev-power:power-execute.

## Goal

Corrigir os achados da revisão e provar funcionamento do mesmo fluxo em Hermes, Codex e Claude Code.
A elaboração deste plano não altera implementação nem executa inferência remota.

## Architecture

Core Python mantém contratos, idioma, tarefas, trace e gates. Adaptadores traduzem apenas a
invocação e a resposta de cada provider. Shell da fleet mantém identidade, isolamento e processos.
Um harness externo executa cenários descartáveis e recolhe evidências independentemente do modelo.

## Tech Stack

Python 3/unittest, Bash, jq, Git, schemas JSON existentes, Hermes 0.20.4, Codex CLI 0.153.4 e Claude Code 2.1.265
observados no ambiente. Docker Compose e cmux são detectados antes da integração.
Usar interpretadores e validação de schemas já adotados pelos testes; se faltar dependência,
registrar bloqueio ou instalar somente no ambiente de teste autorizado, sem modificar ambiente global.

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

## File Structure

Os caminhos abaixo são relativos ao repositório. Cada tarefa enumera todos os arquivos que pode
alterar, até cinco por tarefa. Arquivos marcados NOVO ainda serão criados. Artefatos administrativos
desta fase ficam em .planning/power/features/sdd-composy-corrections/.

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

## Task 05 — Fleet e schema concordantes nos três runtimes
Complexity: high
Files:
- plugins/sdd-composy/scripts/fleet/launch.sh
- plugins/sdd-composy/scripts/fleet/run.sh
- plugins/sdd-composy/schemas/fleet-member.schema.json
- tests/test_sdd_composy.py (adicionado por ruling após revisão: reconciliação do schema v2)
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

## Ordem e dependências

01 → 02 → 03 → 04 → 05 → 06 → 07 → 08.
Tasks 02 e 03 compartilham testes; 05 e 06 compartilham fleet. Executar implementações
serialmente. Qualquer alteração de interface exige atualizar os consumidores antes do gate final.

## Matriz de rastreabilidade

| Critério | Tarefas |
|---|---|
| AC-01, AC-02 | 01, 08 |
| AC-03 | 02, 08 |
| AC-04 | 02, 03, 08 |
| AC-05 | 04, 08 |
| AC-06 | 04, 06, 08 |
| AC-07 | 01, 05, 06, 08 |
| AC-08, AC-09 | 05, 06, 08 |
| AC-10 | 08 |
| AC-11 | 07, 08 |

## Verificação final

```bash
python3 -m unittest discover -s tests -p 'test_sdd_composy*.py' -v
python3 scripts/validate_readme_plugins.py
python3 -m unittest tests.test_readme_marketplace -v
git diff --check
```

Aplicar bash -n aos arquivos fleet alterados. A contagem baseline de 299 testes é histórica;
registrar a nova contagem real, não usá-la como meta. Um exit code zero de testes textuais ou
do plugin doctor não substitui os cenários reais descritos em matrix.md.

## Aprovação e evidências

Este plano está pronto para revisão; não registra aprovação do usuário por antecipação.
Após aprovação, atualizar spec/plan/state com timestamp real. Criar ledger com baseline,
rulings, testes RED/GREEN e revisões por tarefa. Testes reais autorizados em sessão anterior
não autorizam bypass irrestrito; aplicar os limites de isolamento desta especificação.
