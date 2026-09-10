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
- Baseline Hermes substituído por registro/discovery comportamental das 17 skills, `Path` nativo
  e falha diagnóstica do bootstrap.
- Referência Hermes alinhada com o vetor nativo e Kanban indisponível.

## TDD e verificação

- RED inicial: ausência de `scripts/sdd_runtime_smoke.py` falhou como esperado.
- Fix round 1 RED: cenário sem recursos/medidas falhou; testes adversariais cobriram symlinks,
  secrets, publicação atômica, preservação de launcher e gate da CLI real.
- GREEN focado: 18/18 testes de harness + Hermes.
- Suíte offline completa: 367/367 testes.
- README/marketplace: 16 plugins e 1/1 teste.
- Shell syntax e `git diff --check`: PASS.

## Preocupação deliberada

A fase real não foi executada e não pode ser chamada de aceita. A implementação desta entrega
para no gate anterior à inferência; `evidence.md` registra os cenários reais como `NOT_RUN` e a
fleet como `BLOCKED`. É necessário acknowledgement humano externo das formas de comando e do
orçamento antes de implementar/acionar os launchers reais.
