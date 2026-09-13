# F01 — Núcleo e recomendação de ferramentas
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Depends on: nenhuma

For agentic workers: execute this with pwdev-power:power-execute after plan approval.

## Goal
Entregar núcleo e recomendação de ferramentas, com critérios rastreáveis e verificação independente.

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
- plugins/pwdev-qa/skills/qa/SKILL.md
- plugins/pwdev-qa/references/workflow.md
- plugins/pwdev-qa/references/safety.md
- plugins/pwdev-qa/references/artifacts.md
- tests/test_qa_core.py
- plugins/pwdev-qa/skills/qa-tooling/SKILL.md
- plugins/pwdev-qa/references/tooling.md
- tests/test_qa_tooling.py
- plugins/pwdev-qa/references/claude-tools.md
- plugins/pwdev-qa/references/codex-tools.md
- plugins/pwdev-qa/references/hermes-tools.md
- tests/test_qa_runtime_contracts.py

## Task 01 — Roteador e contratos comuns
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa/SKILL.md
- plugins/pwdev-qa/references/workflow.md
- plugins/pwdev-qa/references/safety.md
- plugins/pwdev-qa/references/artifacts.md
- tests/test_qa_core.py
Interfaces:
  Consumes: Objetivo explícito do usuário e contexto do projeto
  Produces: Roteamento para qa-*; contrato comum de status, autorização e evidência
Acceptance: CA-001, CA-004, CA-014, CA-015
Behavior: Verificar pedido de review somente leitura, critério ausente BLOCKED e seleção de workflow por intenção. Referências inexistentes são erro. Na entrega desta tarefa testar apenas entradas já implementadas; inventário completo será fechado em F05.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_core` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_core` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 02 — Skill de recomendação e catálogo de ferramentas
Complexity: medium
Files:
- plugins/pwdev-qa/skills/qa-tooling/SKILL.md
- plugins/pwdev-qa/references/tooling.md
- tests/test_qa_tooling.py
Interfaces:
  Consumes: stack, OS/runtime, objetivo, executáveis detectados, restrições
  Produces: Tabela com tool/purpose/availability/evidence/prerequisites/alternative/reason
Acceptance: CA-004, CA-022, CA-023
Behavior: Fixture Web inclui playwright-cli e Playwright Test com finalidades distintas; fixture mobile oferece opção compatível com plataforma; ambiente sem CLI preserva missing e não instala. Catálogo cita documentação oficial antes de afirmar versões/custos. Testes estruturais acompanham cenários de avaliação do comportamento, sem tratar palavras-chave como prova de eficácia.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_tooling` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_tooling` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 03 — Mapeamentos dos três runtimes
Complexity: medium
Files:
- plugins/pwdev-qa/references/claude-tools.md
- plugins/pwdev-qa/references/codex-tools.md
- plugins/pwdev-qa/references/hermes-tools.md
- tests/test_qa_runtime_contracts.py
Interfaces:
  Consumes: Superfície de ferramentas efetivamente disponível
  Produces: Mapeamento de leitura, escrita, execução e carregamento de skill; diagnóstico de capacidade ausente
Acceptance: CA-003, CA-004
Behavior: Verificar instruções independentes de ferramentas exclusivas, sem mudança de configuração pessoal, sem usar flags de bypass. Separar registro de skills Hermes e carregamento sob demanda.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_runtime_contracts` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_runtime_contracts` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Gate e entrega
Plano proposto, não aprovado por sua existência. Nenhum commit ou publicação é automático.
Falhas de cenário em skills são problemas de comportamento mesmo se o parser de frontmatter passar.
