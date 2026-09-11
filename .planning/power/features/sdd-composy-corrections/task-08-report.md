# Task 08 implementation report — offline phase

Status: DONE_WITH_CONCERNS

## Entregue

- CLI offline com matriz dos três runtimes, dois idiomas e seis cenários.
- Orçamento rígido por runtime (máximo 28), timeout padrão de 300 segundos e nenhuma repetição
  automática.
- Fixture Git exclusiva com cópia local do plugin, exclusão de estado operacional/secrets e
  certificados/chaves, recusa de symlinks e cleanup pelo caminho exato criado.
- Sanitização, publicação JSON atômica, statuses fechados e uso indisponível como `null`.
- Cenários comportamentais por fixture: status/sentinelas; init→map→import→next; LOOP de cinco
  estágios; fleet com dois membros e mismatch; handoff durável; evidência negativa/divergência;
  Compose, cmux e merge.
- Registros preservam duração, exit code, result hash, runtime/version, task, worktree, comando e
  recursos mensuráveis; falha de `os.replace` preserva bytes anteriores.
- CLI real expõe `--provider-entry-point production` e `--acknowledge-real-fleet`, mantendo
  `BLOCKED` sem acknowledgement e `NOT_RUN` enquanto o adapter real não for habilitado.
- Fleet real bloqueada sem acknowledgement externo explícito.
- Re-review: handoff offline agora consome artefatos duráveis por adapters Hermes→Codex→Claude→Hermes,
  preservando IDs/gates/evidence e recusando aprovação não sintética ou fora do escopo; mismatch de
  runtime usa diagnóstico canônico.
- Re-review: cópia isolada falha fechada para token/auth, `id_*`, chaves privadas, keystores,
  credenciais e certificados, mantendo somente arquivos explicitamente `.sample`/`.example`.
- Baseline Hermes substituído por registro/discovery comportamental das 17 skills, `Path` nativo
  e falha diagnóstica do bootstrap.
- Referência Hermes alinhada com o vetor nativo e Kanban indisponível.

## TDD e verificação

- RED inicial: ausência de `scripts/sdd_runtime_smoke.py` falhou como esperado.
- Fix round 1 RED: cenário sem recursos/medidas falhou; testes adversariais cobriram symlinks,
  secrets, publicação atômica, preservação de launcher e gate da CLI real.
- GREEN focado: 18/18 testes de harness + Hermes.
- Re-review GREEN focado: 21/21 testes de harness + Hermes; execução offline 36/36 PASS.
- Suíte offline completa: 367/367 testes.
- README/marketplace: 16 plugins e 1/1 teste.
- Shell syntax e `git diff --check`: PASS.

## Correção após re-review offline 2

- `_offline_handoff` agora chama `run()` dos adapters reais em quatro invocações:
  Hermes → Codex → Claude → Hermes. Executáveis fake temporários recebem os vetores
  nativos, leem o artefato durável anterior e emitem JSON Hermes, arquivo final Codex
  ou envelope Claude. Capturas preservam argv/cwd e a origem consumida; os resultados
  validados preservam task/requirement IDs, gate, evidence e aprovação sintética.
- A fixture fleet associa o mesmo member, slug e worktree nas duas execuções.
  Alterar somente o runtime solicitado produz o stderr real
  `sdd-fleet-run: registered fleet member does not match canonical Git worktree registration`.
  O controle com runtime correto passa esse gate e chega ao gate posterior
  `sdd-fleet-run: unsafe phase contract path for task-add`. O runner agrupa identidade
  runtime no gate de registro; não existe mensagem literal `runtime mismatch` nele.
  Nenhum diagnóstico é substituído e nenhum fake provider é invocado nesse teste.
- RED: três regressões novas falharam antes da correção (2 failures, 1 error):
  ausência de capturas, adapter ignorado e stderr fabricado aceito.
- GREEN: `python3 -m unittest tests.test_sdd_composy_runtime_smoke
  tests.test_sdd_composy_runtime_adapters tests.test_sdd_composy_hermes -v`:
  31 testes PASS em 65.771s, incluindo a matriz offline 36/36 e a execução da CLI.
  Os testes detectam a omissão de qualquer uma das quatro chamadas e recusam um
  erro de registro idêntico nos dois lados do controle diferencial.
- Zero inferência real. Task 08 permanece INCOMPLETE; revisão independente e os
  gates humanos aplicáveis não são concedidos por este relatório.

## Limite da fase real

A fase real não foi executada e não pode ser chamada de aceita. A implementação desta entrega
para no gate anterior à inferência; `evidence.md` registra os cenários reais como `NOT_RUN` e a
fleet como `BLOCKED`. É necessário acknowledgement humano externo das formas de comando e do
orçamento antes de implementar/acionar os launchers reais.
