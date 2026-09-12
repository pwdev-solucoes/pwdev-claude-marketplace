# F02 — Dezessete especialistas
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Depends on: F01

For agentic workers: execute this with pwdev-power:power-execute after plan approval.

## Goal
Entregar dezessete especialistas, com critérios rastreáveis e verificação independente.

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
- plugins/pwdev-qa/skills/qa-specialist-strategy/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-requirements/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-functional/SKILL.md
- tests/test_qa_specialists.py
- plugins/pwdev-qa/skills/qa-specialist-web/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-api/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-mobile/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-data/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-accessibility/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-performance/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-security/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-automation/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-cicd/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-regression/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-defects/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-production/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-metrics/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-readiness/SKILL.md

## Task 04 — Estratégia, requisitos e funcional
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-strategy/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-requirements/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-functional/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-strategy, qa-specialist-requirements, qa-specialist-functional
Acceptance: CA-001, CA-002, CA-005
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar risco/cobertura; critério ambíguo; fronteira e erro. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 05 — Web, API e mobile
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-web/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-api/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-mobile/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-web, qa-specialist-api, qa-specialist-mobile
Acceptance: CA-002, CA-004, CA-023
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar playwright-cli com sessão própria; idempotência/autorização API; Android/iOS conforme contrato e dispositivo ausente. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 06 — Dados, acessibilidade e performance
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-data/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-accessibility/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-performance/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-data, qa-specialist-accessibility, qa-specialist-performance
Acceptance: CA-002, CA-015
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar reconciliação/transação; teclado/foco além de scanner; percentis/carga autorizada. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 07 — Segurança, automação e CI
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-security/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-automation/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-cicd/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-security, qa-specialist-automation, qa-specialist-cicd
Acceptance: CA-002, CA-015, CA-023
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar escopo de segurança; flaky tests e Playwright Test vs playwright-cli; gate por verdict não por exit code da exportação. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 08 — Regressão, defeitos e produção
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-regression/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-defects/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-production/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-regression, qa-specialist-defects, qa-specialist-production
Acceptance: CA-002, CA-011, CA-014, CA-015, CA-020
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar seleção por impacto; severidade vs prioridade e reteste; observações autorizadas e prevenção de reincidência. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 09 — Métricas e prontidão
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-specialist-metrics/SKILL.md
- plugins/pwdev-qa/skills/qa-specialist-readiness/SKILL.md
- tests/test_qa_specialists.py
Interfaces:
  Consumes: Contrato de skill e regras do spec.md; referências compartilhadas F01
  Produces: Skills qa-specialist-metrics, qa-specialist-readiness
Acceptance: CA-002, CA-006, CA-012, CA-013, CA-020
Behavior: Cada skill contém Inputs/Procedure/Output/Failure modes/Safety/Related skills e dois cenários de referência: sucesso e falha/limitação. Avaliar denominadores explícitos, zero critérios; falhas não mapeadas, riscos e decisão humana. Teste estrutural complementa, não substitui, avaliação dos cenários com agente em F05-03.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_specialists` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Gate e entrega
Plano proposto, não aprovado por sua existência. Nenhum commit ou publicação é automático.
Falhas de cenário em skills são problemas de comportamento mesmo se o parser de frontmatter passar.
