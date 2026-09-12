# F05 — Empacotamento e validação dos runtimes
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Depends on: F01, F02, F03, F04

For agentic workers: execute this with pwdev-power:power-execute after plan approval.

## Goal
Entregar empacotamento e validação dos runtimes, com critérios rastreáveis e verificação independente.

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
- plugins/pwdev-qa/.claude-plugin/plugin.json
- plugins/pwdev-qa/.codex-plugin/plugin.json
- plugins/pwdev-qa/.hermes-plugin/plugin.yaml
- plugins/pwdev-qa/.hermes-plugin/__init__.py
- tests/test_qa_packaging.py
- plugins/pwdev-qa/README.md
- plugins/pwdev-qa/README.pt-BR.md
- .claude-plugin/marketplace.json
- .agents/plugins/marketplace.json
- tests/test_qa_catalog.py
- README.md
- README.pt-BR.md
- plugins/pwdev-qa/references/runtime-smoke.md
- tests/test_qa_scenarios.py
- plugins/pwdev-qa/references/acceptance-scenarios.md

## Task 22 — Manifests e registro Hermes
Complexity: high
Files:
- plugins/pwdev-qa/.claude-plugin/plugin.json
- plugins/pwdev-qa/.codex-plugin/plugin.json
- plugins/pwdev-qa/.hermes-plugin/plugin.yaml
- plugins/pwdev-qa/.hermes-plugin/__init__.py
- tests/test_qa_packaging.py
Interfaces:
  Consumes: 29 skills no diretório skills/; mappings F01
  Produces: register(ctx) -> None com ctx.register_skill(name: str, path: Path); manifests versão 0.1.0
Acceptance: CA-001, CA-002, CA-003
Behavior: Testar layouts clone/flattened, caminhos pathlib.Path, ausência de árvore, descoberta de exatamente 29 skills e zero hook intrusivo. Autor/repositório/licença seguem manifests PWDEV existentes. Codex defaultPrompt tem no máximo 3 itens; não inventar MCP/hooks.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_packaging` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_packaging` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 23 — Documentação e catálogos
Complexity: medium
Files:
- plugins/pwdev-qa/README.md
- plugins/pwdev-qa/README.pt-BR.md
- .claude-plugin/marketplace.json
- .agents/plugins/marketplace.json
- tests/test_qa_catalog.py
Interfaces:
  Consumes: Manifests e comandos F05-01/F04
  Produces: Instalação manual documentada por runtime; entradas de catálogo locais
Acceptance: CA-003, CA-018, CA-022, CA-023
Behavior: Adicionar plugin sem reordenar entradas existentes nem mudar nome do marketplace. Documentar 29 skills/10 comandos, dependência PDF, qa-tooling, playwright-cli, execução/exportação distintas, limitações da sanitização. Catálogo Codex preserva políticas/unknown fields. Nenhuma instalação nesta tarefa.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_catalog` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_catalog` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 24 — Integração documental e smoke real
Complexity: high
Files:
- README.md
- README.pt-BR.md
- plugins/pwdev-qa/references/runtime-smoke.md
- tests/test_qa_scenarios.py
- plugins/pwdev-qa/references/acceptance-scenarios.md
Interfaces:
  Consumes: Plugin completo e executáveis reais disponíveis
  Produces: Evidência de descoberta/invocação por runtime, avaliação de cenários e inventário final
Acceptance: CA-001, CA-002, CA-003, CA-004, CA-018, CA-022, CA-023
Behavior: Preservar layout atual e adicionar pwdev-qa ao catálogo e agrupamento por objetivo dos dois READMEs raiz. Documentação detalhada de instalação/inventário fica nos READMEs do plugin. Testar arquivos e cenários completos. Executar smoke real em ambiente de teste autorizado segundo ajuda/documentação verificada do runtime: descobrir qa-tooling, responder cenário sem ferramenta, produzir relatório de fixture; registrar runtime/versão/resultado. Não mudar instalação pessoal implicitamente; se acesso faltar, marcar runtime não verificado e não alegar conclusão.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_scenarios tests.test_readme_marketplace && python3 scripts/validate_readme_plugins.py` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_scenarios tests.test_readme_marketplace && python3 scripts/validate_readme_plugins.py` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Gate e entrega
Plano proposto, não aprovado por sua existência. Nenhum commit ou publicação é automático.
Falhas de cenário em skills são problemas de comportamento mesmo se o parser de frontmatter passar.
