# F03 — Validação de aceite e relatórios HTML/PDF
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Depends on: F01

For agentic workers: execute this with pwdev-power:power-execute after plan approval.

## Goal
Entregar validação de aceite e relatórios html/pdf, com critérios rastreáveis e verificação independente.

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
- plugins/pwdev-qa/schemas/report.schema.json
- plugins/pwdev-qa/scripts/qa_contract.py
- tests/test_qa_contract.py
- plugins/pwdev-qa/scripts/qa_evidence.py
- plugins/pwdev-qa/references/evidence.md
- tests/test_qa_evidence.py
- plugins/pwdev-qa/scripts/qa_verdict.py
- tests/test_qa_verdict.py
- plugins/pwdev-qa/scripts/qa_html.py
- tests/test_qa_html.py
- plugins/pwdev-qa/scripts/qa_pdf.py
- plugins/pwdev-qa/requirements.txt
- tests/test_qa_pdf.py
- plugins/pwdev-qa/scripts/qa_report.py
- tests/test_qa_report_cli.py
- plugins/pwdev-qa/references/reports.md
- tests/test_qa_reports_e2e.py
- plugins/pwdev-qa/scripts/qa_demo.py
- plugins/pwdev-qa/requirements-dev.txt

## Task 01 — Schema e validação de entrada
Complexity: high
Files:
- plugins/pwdev-qa/schemas/report.schema.json
- plugins/pwdev-qa/scripts/qa_contract.py
- tests/test_qa_contract.py
Interfaces:
  Consumes: Manifesto schema_version=1 definido no spec.md
  Produces: load_manifest(path: Path) -> dict; validate_manifest(data: dict) -> dict; ValidationError(ValueError)
Acceptance: CA-005, CA-006, CA-021
Behavior: Casos válidos e inválidos: enums, tipos bool vs int, duplicação, referências pendentes, datas, limites, campos desconhecidos e caminhos absolutos. Garantir preservação de extras sem exibi-los automaticamente.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_contract` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_contract` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 02 — Integridade e sanitização de evidências
Complexity: high
Files:
- plugins/pwdev-qa/scripts/qa_evidence.py
- plugins/pwdev-qa/references/evidence.md
- tests/test_qa_evidence.py
Interfaces:
  Consumes: validate_manifest(data: dict) -> dict
  Produces: inspect_evidence(root: Path, manifest: dict) -> list[dict]
Acceptance: CA-010, CA-016, CA-019, CA-021
Behavior: Testar hash/size/target, arquivos ausentes, caminho externo, symlink inclusive diretórios, limites, mime real e imagem excessiva. Credenciais sintéticas em log/JSON e imagem pending não são copiadas. Saída de inspeção só contém diagnóstico sanitizado, identidade e caminho aprovado, nunca conteúdo rejeitado.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_evidence` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_evidence` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 03 — Consolidação determinística do parecer
Complexity: high
Files:
- plugins/pwdev-qa/scripts/qa_verdict.py
- tests/test_qa_verdict.py
Interfaces:
  Consumes: inspect_evidence(root: Path, manifest: dict) -> list[dict]
  Produces: build_report(manifest: dict, evidence: list[dict]) -> dict
Acceptance: CA-005, CA-006, CA-010, CA-011, CA-012, CA-013, CA-020
Behavior: Cobrir tabela completa de estados, zero critérios/casos, completude da transcrição não confirmada, dispensas inválidas, reteste, supersedes cíclico, defeito aberto sem criterion_ids e defeito fora do escopo. Preservar resultado histórico; falha de produto prevalece, incerteza não vira PASS.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_verdict` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_verdict` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 04 — Relatório HTML offline
Complexity: medium
Files:
- plugins/pwdev-qa/scripts/qa_html.py
- tests/test_qa_html.py
Interfaces:
  Consumes: build_report(manifest: dict, evidence: list[dict]) -> dict
  Produces: render_html(report: dict) -> str
Acceptance: CA-007, CA-008, CA-016, CA-019
Behavior: HTML sem JS/CDN: sumário, matriz, detalhes, defeitos, referências, diagnóstico e parecer. Escapar todos os textos e atributos; não renderizar campos extras. Testar conteúdo malicioso, zero itens, Unicode e referências de evidências aprovadas. IDs DOM devem ser gerados internamente, não interpolados sem escape.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_html` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_html` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 05 — PDF paginado e dependências
Complexity: high
Files:
- plugins/pwdev-qa/scripts/qa_pdf.py
- plugins/pwdev-qa/requirements.txt
- tests/test_qa_pdf.py
Interfaces:
  Consumes: build_report(manifest: dict, evidence: list[dict]) -> dict
  Produces: render_pdf(report: dict, destination: Path) -> None
Acceptance: CA-007, CA-008, CA-009, CA-019
Behavior: ReportLab 4.4.9; A4/margens 18 mm, texto em blocos quebráveis para critérios extensos, fontes com acentos, legendas e índice. Escapar markup ReportLab. Fixture de 100 critérios x 2000 caracteres: extração integral, paginação e inspeção visual. Ausência de ReportLab falha explicitamente.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_pdf` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_pdf` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 06 — CLI e publicação do pacote
Complexity: high
Files:
- plugins/pwdev-qa/scripts/qa_report.py
- tests/test_qa_report_cli.py
- plugins/pwdev-qa/references/reports.md
Interfaces:
  Consumes: load_manifest(path: Path) -> dict; inspect_evidence(root: Path, manifest: dict) -> list[dict]; build_report(manifest: dict, evidence: list[dict]) -> dict; render_html(report: dict) -> str; render_pdf(report: dict, destination: Path) -> None
  Produces: generate_report(manifest_path: Path, project_root: Path) -> dict; main(argv: Optional[List[str]] = None) -> int
Acceptance: CA-007, CA-009, CA-017, CA-019, CA-021
Behavior: CLI report --manifest PATH --project-root PATH. Comando nunca executa strings armazenadas; valida, inspeciona, consolida, renderiza e publica atomicamente. Recusar raiz de saída symlink e colisão. Testar PDF indisponível e erro de escrita sem alegar exportação completa. manifesto público exclui conteúdo rejeitado e preserva extras somente no original privado.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_report_cli` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_report_cli` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Task 07 — Teste integrado, fixture e inspeção visual
Complexity: high
Files:
- tests/test_qa_reports_e2e.py
- plugins/pwdev-qa/scripts/qa_demo.py
- plugins/pwdev-qa/requirements-dev.txt
Interfaces:
  Consumes: generate_report(manifest_path: Path, project_root: Path) -> dict
  Produces: Fixture sintética reproduzível e teste de paridade dos dois formatos
Acceptance: CA-005, CA-007, CA-008, CA-010, CA-019, CA-020, CA-021, CA-023
Behavior: Gerar dados temporários em testes; demo em diretório explicitamente fornecido. Comparar IDs/textos/esperado/observado/defeitos/evidências/parecer contra modelo de entrada, nunca só HTML contra PDF. Extrair PDF com pypdf e renderizar páginas com ferramenta disponível. requirements-dev fixa pypdf==6.10.0 e pdfplumber==0.11.9. Demonstrar snapshot e screenshot com playwright-cli em sessão própria quando disponível.
Steps:
- [ ] Ler spec.md e as interfaces consumidas; confirmar dependências e estado do worktree.
- [ ] Escrever teste de comportamento que exercite os cenários descritos, criando apenas os arquivos de teste listados.
- [ ] Executar `python3 -m unittest tests.test_qa_reports_e2e` e registrar falha esperada antes da implementação.
- [ ] Implementar nos arquivos listados o comportamento e as saídas exatas desta tarefa.
- [ ] Executar `python3 -m unittest tests.test_qa_reports_e2e` novamente; registrar resultado e limitações sem tratar falha de ambiente como aprovação.
- [ ] Revisar diff e contrato; registrar evidência na execução Power e encaminhar findings para correção antes da tarefa seguinte.

## Gate e entrega
Plano proposto, não aprovado por sua existência. Nenhum commit ou publicação é automático.
Falhas de cenário em skills são problemas de comportamento mesmo se o parser de frontmatter passar.
