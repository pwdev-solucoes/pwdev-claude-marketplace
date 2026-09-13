# F04 — Dez workflows de uso
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Depends on: F01, F02, F03

For agentic workers: execute this with pwdev-power:power-execute after plan approval.

## Goal
Entregar dez workflows de uso, com critérios rastreáveis e verificação independente.

## Architecture
Usar o contrato e assinaturas exatos da especificação. Tarefas desta feature são sequenciais; não executar tarefas que dependam de uma feature incompleta.
Os arquivos abaixo são novos sob plugins/pwdev-qa/ e tests/test_qa_*, exceto READMEs e catálogos existentes explicitamente listados.

## Tech Stack
Markdown, JSON, YAML e Python >=3.9. PDF via ReportLab; verificação PDF no Python 3.12 empacotado.
Comandos usam python3; nos testes PDF escolher o Python com as dependências declaradas. Não instalar implicitamente.
Python PDF disponível nesta sessão: /Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.

## Global Constraints
- Plugin v1: 10 workflows, 17 especialidades, 29 skills (1 roteador, 1 recomendador de ferramentas, 10 workflows, 17 especialistas), 10 comandos Claude, 0 servidores MCP obrigatórios.
- Runtimes: Claude Code, Codex e Hermes; contratos equivalentes, limitações explícitas e smoke real obrigatório para declarar cada runtime verificado.
- Python do plugin: >=3.9. Dependência de exportação: reportlab==4.4.9. Dependências de verificação PDF: pypdf==6.10.0 e pdfplumber==0.11.9 em Python 3.12.
- Resultados de caso/critério: PASS, FAIL, BLOCKED, NOT_RUN, NOT_APPLICABLE. Parecer global: PASS, FAIL, BLOCKED.
- Falha comprovada vigente dentro do escopo, inclusive defeito sem critério associado, implica FAIL. Sem falha, pendência ou zero critérios aplicáveis implica BLOCKED. PASS exige todos os aplicáveis aprovados e ausência de defeitos vigentes no escopo.
- Carga, pentest, produção e efeitos externos exigem autorização explícita. Correções de produto somente quando solicitadas. Relatório não executa comandos de evidência.
- HTML estático offline, UTF-8, sem JavaScript e sem recursos remotos. PDF A4, margens de 18 mm, paginação e rótulos textuais de status.
- HTML e PDF derivam do mesmo manifesto normalizado e incluem mesmos IDs, textos, esperado/observado, referências de evidência, defeitos e parecer.
- Evidências: arquivos regulares locais, caminhos relativos confinados, sem symlinks; SHA-256, alvo e contrato identificados; revisão de sanitização obrigatória antes de exportar.
- Limites de entrada v1: manifesto 5 MiB, até 1000 critérios, até 1000 evidências, 10 MiB por evidência, 100 MiB no conjunto e 20 megapixels por imagem. Exceder limite é erro explícito, nunca truncamento silencioso.
- Nova execução usa ID fornecido validado por ^[a-z0-9][a-z0-9-]{0,63}$ e nunca sobrescreve diretório existente. Artefatos em .planning/pwdev-qa/reports/<run-id>/.
- Schema inválido ou evidência insegura: recusar exportação. Evidência ausente/alterada ou sanitização pendente: produzir diagnóstico sem copiar o anexo e impedir PASS.
- Nenhuma instalação, publicação, push, merge ou alteração de configuração pessoal automática. Sem mudanças nos plugins usados como referência.
- Execução sequencial por padrão; cada tarefa tem até 5 arquivos e 7 passos; cada feature tem até 8 tarefas.

## File Structure
- plugins/pwdev-qa/skills/qa-init/SKILL.md
- plugins/pwdev-qa/commands/init.md
- plugins/pwdev-qa/skills/qa-strategy/SKILL.md
- plugins/pwdev-qa/commands/strategy.md
- tests/test_qa_workflows.py
- plugins/pwdev-qa/skills/qa-test/SKILL.md
- plugins/pwdev-qa/commands/test.md
- plugins/pwdev-qa/skills/qa-explore/SKILL.md
- plugins/pwdev-qa/commands/explore.md
- plugins/pwdev-qa/skills/qa-regression/SKILL.md
- plugins/pwdev-qa/commands/regression.md
- plugins/pwdev-qa/skills/qa-bug/SKILL.md
- plugins/pwdev-qa/commands/bug.md
- plugins/pwdev-qa/skills/qa-review/SKILL.md
- plugins/pwdev-qa/commands/review.md
- plugins/pwdev-qa/skills/qa-release/SKILL.md
- plugins/pwdev-qa/commands/release.md
- plugins/pwdev-qa/skills/qa-report/SKILL.md
- plugins/pwdev-qa/commands/report.md
- plugins/pwdev-qa/skills/qa-status/SKILL.md
- plugins/pwdev-qa/commands/status.md

## Task 17 — Workflows init / strategy
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-init/SKILL.md
- plugins/pwdev-qa/commands/init.md
- plugins/pwdev-qa/skills/qa-strategy/SKILL.md
- plugins/pwdev-qa/commands/strategy.md
- tests/test_qa_workflows.py
Interfaces:
  Consumes: Contrato comum F01, especialistas F02 e CLI report de F03
  Produces: Skills qa-init, qa-strategy e wrappers Claude correspondentes
Acceptance: CA-001, CA-004, CA-005, CA-007, CA-012, CA-014, CA-015, CA-022
Behavior: Implementar saídas definidas no spec.md; wrappers apenas carregam skill e encaminham argumentos. Verificar intenção explícita, registro de limitações, autorização e ausência de mutação em review/status. report usa qa_report.py report --manifest PATH --project-root PATH; não reexecuta testes. init/strategy consultam qa-tooling.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 18 — Workflows test / explore
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-test/SKILL.md
- plugins/pwdev-qa/commands/test.md
- plugins/pwdev-qa/skills/qa-explore/SKILL.md
- plugins/pwdev-qa/commands/explore.md
- tests/test_qa_workflows.py
Interfaces:
  Consumes: Contrato comum F01, especialistas F02 e CLI report de F03
  Produces: Skills qa-test, qa-explore e wrappers Claude correspondentes
Acceptance: CA-001, CA-004, CA-005, CA-007, CA-012, CA-014, CA-015, CA-022
Behavior: Implementar saídas definidas no spec.md; wrappers apenas carregam skill e encaminham argumentos. Verificar intenção explícita, registro de limitações, autorização e ausência de mutação em review/status. report usa qa_report.py report --manifest PATH --project-root PATH; não reexecuta testes. init/strategy consultam qa-tooling.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 19 — Workflows regression / bug
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-regression/SKILL.md
- plugins/pwdev-qa/commands/regression.md
- plugins/pwdev-qa/skills/qa-bug/SKILL.md
- plugins/pwdev-qa/commands/bug.md
- tests/test_qa_workflows.py
Interfaces:
  Consumes: Contrato comum F01, especialistas F02 e CLI report de F03
  Produces: Skills qa-regression, qa-bug e wrappers Claude correspondentes
Acceptance: CA-001, CA-004, CA-005, CA-007, CA-012, CA-014, CA-015, CA-022
Behavior: Implementar saídas definidas no spec.md; wrappers apenas carregam skill e encaminham argumentos. Verificar intenção explícita, registro de limitações, autorização e ausência de mutação em review/status. report usa qa_report.py report --manifest PATH --project-root PATH; não reexecuta testes. init/strategy consultam qa-tooling.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 20 — Workflows review / release
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-review/SKILL.md
- plugins/pwdev-qa/commands/review.md
- plugins/pwdev-qa/skills/qa-release/SKILL.md
- plugins/pwdev-qa/commands/release.md
- tests/test_qa_workflows.py
Interfaces:
  Consumes: Contrato comum F01, especialistas F02 e CLI report de F03
  Produces: Skills qa-review, qa-release e wrappers Claude correspondentes
Acceptance: CA-001, CA-004, CA-005, CA-007, CA-012, CA-014, CA-015, CA-022
Behavior: Implementar saídas definidas no spec.md; wrappers apenas carregam skill e encaminham argumentos. Verificar intenção explícita, registro de limitações, autorização e ausência de mutação em review/status. report usa qa_report.py report --manifest PATH --project-root PATH; não reexecuta testes. init/strategy consultam qa-tooling.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 21 — Workflows report / status
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-report/SKILL.md
- plugins/pwdev-qa/commands/report.md
- plugins/pwdev-qa/skills/qa-status/SKILL.md
- plugins/pwdev-qa/commands/status.md
- tests/test_qa_workflows.py
Interfaces:
  Consumes: Contrato comum F01, especialistas F02 e CLI report de F03
  Produces: Skills qa-report, qa-status e wrappers Claude correspondentes
Acceptance: CA-001, CA-004, CA-005, CA-007, CA-012, CA-014, CA-015, CA-022
Behavior: Implementar saídas definidas no spec.md; wrappers apenas carregam skill e encaminham argumentos. Verificar intenção explícita, registro de limitações, autorização e ausência de mutação em review/status. report usa qa_report.py report --manifest PATH --project-root PATH; não reexecuta testes. init/strategy consultam qa-tooling.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_workflows` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Gate e entrega
Plano proposto, não aprovado por sua existência. Nenhum commit ou publicação é automático.
Falhas de cenário em skills são problemas de comportamento mesmo se o parser de frontmatter passar.
