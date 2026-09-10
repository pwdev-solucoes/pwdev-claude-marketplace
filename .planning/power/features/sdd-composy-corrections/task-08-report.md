# Task 08 implementation report — offline phase

Status: DONE_WITH_CONCERNS

## Entregue

- CLI offline com matriz dos três runtimes, dois idiomas e seis cenários.
- Orçamento rígido por runtime (máximo 28), timeout padrão de 300 segundos e nenhuma repetição
  automática.
- Fixture Git exclusiva com cópia local do plugin, exclusão de estado operacional/secrets e
  cleanup pelo caminho exato criado.
- Sanitização, publicação JSON atômica, statuses fechados e uso indisponível como `null`.
- Fleet real bloqueada sem acknowledgement externo explícito.
- Baseline Hermes substituído por registro/discovery comportamental das 17 skills, `Path` nativo
  e falha diagnóstica do bootstrap.
- Referência Hermes alinhada com o vetor nativo e Kanban indisponível.

## TDD e verificação

- RED inicial: ausência de `scripts/sdd_runtime_smoke.py` falhou como esperado.
- RED contratual: 5 falhas/3 erros nos stubs iniciais; GREEN: 9/9 testes do harness.
- Hermes focado: 5/5 testes.
- Suíte offline completa: 362/362 testes.
- README/marketplace: 16 plugins e 1/1 teste.
- Shell syntax e `git diff --check`: PASS.

## Preocupação deliberada

A fase real não foi executada e não pode ser chamada de aceita. A implementação desta entrega
para no gate anterior à inferência; `evidence.md` registra os cenários reais como `NOT_RUN` e a
fleet como `BLOCKED`. É necessário acknowledgement humano externo das formas de comando e do
orçamento antes de implementar/acionar os launchers reais.
