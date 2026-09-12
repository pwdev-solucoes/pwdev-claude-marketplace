# PWDEV QA — especificação para planejamento
Status: APPROVED
Source: conversa; tasks/prd-pwdev-qa/prd.md; tasks/prd-pwdev-qa/design.md
Updated: 2026-09-12

## Objetivo e autoridade
Entregar o plugin completo solicitado, com QA geral/especializado e relatórios HTML/PDF verificáveis.
O usuário solicitou elaborar o plano após escolher Power e desconsiderar AGENTS.md. Esta especificação consolida decisões técnicas propostas para aprovação com os planos; não registra aprovação de implementação.
Os documentos em tasks/prd-pwdev-qa/ são fontes históricas. Para execução, este pacote substitui suas referências ao SDD Composy e elimina gates de STORIES/TECHSPEC/TASKS daquele processo. Os gates próprios do Power permanecem.
Nenhum arquivo de outra feature Power será modificado.

## Contexto observado
O repositório usa plugins/<nome>/skills, commands, references e manifests por runtime.
tests/test_power_hermes.py usa unittest e verifica registro com pathlib.Path e layouts clone/flattened.
scripts/validate_readme_plugins.py e tests/test_marketplace_readmes.py verificam catálogo e documentação.
Não existe mapa .planning/power/context/ nesta sessão. A inspeção dos arquivos acima fornece os padrões usados.
Python padrão observado: 3.9.6; Python empacotado: 3.12.14. ReportLab 4.4.9, pypdf 6.10.0, pdfplumber 0.11.9 disponíveis neste último.
Executáveis claude, codex e hermes foram localizados; autenticação e funcionamento ainda não foram testados.

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

## Decisões
1. Núcleo + workflows + especialistas, aprovado em conversa. Alternativas monolítica ou especialistas sem roteador descartadas por duplicação/contexto. Custo: matriz de roteamento e testes de cobertura. Reversível sem alterar evidências.
2. Python/ReportLab em vez de browser headless para PDF: biblioteca disponível, exportação local e independência do runtime de IA. Custo: dois renderizadores; paridade verificada por modelo comum e extração. Reversível conservando schema.
3. Não inferir critérios de Markdown arbitrário automaticamente. Receber catálogo explícito de IDs/textos e localizar cada par no contrato UTF-8 identificado por hash. Um avaliador registra completude da transcrição, aplicabilidade e suficiência semântica. Sem confirmação, BLOCKED. Hash não prova completude nem verdade de uma avaliação.
4. Sanitização não promete detecção universal. Aceitar somente evidências sintéticas ou sanitizadas e revisadas, com ator/data. Rejeitar padrões conhecidos de credenciais; imagens exigem revisão visual registrada. Anexo não revisado não é copiado; impede PASS. Custo: participação humana ou avaliador competente para conteúdo semântico.
5. Dois estados independentes: parecer QA e exportação. CLI: 0 = ambos formatos exportados (mesmo se QA FAIL/BLOCKED); 2 = entrada/segurança inválida; 3 = dependência ausente ou exportação incompleta. Automação lê verdict no JSON, nunca deduz QA pelo exit code.
6. Relatórios completos publicados em diretório temporário irmão e renomeados após ambos formatos válidos. Colisão falha; falha de PDF preserva diagnóstico em diretório parcial exclusivo explicitamente nomeado, nunca usa nome de relatório completo.
7. Não criar agentes obrigatórios nem bootstrap intrusivo. Hermes registra as mesmas 29 skills na inicialização do plugin; conteúdo carregado sob demanda, sem injetar QA em toda conversa.

## Modelo e interfaces
Arquivo Python importável via sys.path do diretório scripts, sem instalar pacote no sistema.
qa_contract.py:
- load_manifest(path: Path) -> dict
- validate_manifest(data: dict) -> dict
- ValidationError(ValueError)
qa_evidence.py:
- inspect_evidence(root: Path, manifest: dict) -> list[dict]
qa_verdict.py:
- build_report(manifest: dict, evidence: list[dict]) -> dict
qa_html.py:
- render_html(report: dict) -> str
qa_pdf.py:
- render_pdf(report: dict, destination: Path) -> None
qa_report.py:
- generate_report(manifest_path: Path, project_root: Path) -> dict
- main(argv: list[str] | None = None) -> int (escrever Optional[List[str]] para compatibilidade Python 3.9)
Resultado generate_report: {run_id: str, verdict: str, export_status: str, output_dir: str, diagnostics: list[str]}.
Dependências: contract -> evidence -> verdict -> html/pdf -> report CLI. Renderizadores não reavaliam critérios.

Manifesto schema_version=1, campos obrigatórios:
run_id; project; target{id,kind}; executed_at (ISO-8601 com fuso);
contract{path,sha256,criteria_review{actor,at,complete}};
criteria[{id,text,applicable,applicability_reason,assessment{actor,at,expected,observed},case_ids}];
cases[{id,case_id,criterion_ids,status,required,expected,observed,command,exit_code,evidence_ids,attempt,supersedes}];
evidence[{id,path,sha256,media_type,size_bytes,target_id,sanitization{status,actor,at}}];
defects[{id,summary,in_scope,status,severity,criterion_ids,evidence_ids,supersedes,retest_attempt_id}].
Listas podem ser vazias; critérios/casos vazios não produzem PASS. IDs únicos por coleção, referências resolvidas, timestamps válidos e valores enum conhecidos. Campos extras são preservados, mas não exibidos automaticamente.
Media types aceitos: text/plain, application/json, image/png, image/jpeg. JSON de evidência é tratado como texto inerte; SVG/HTML/PDF e executáveis não são anexados na v1.
status de sanitização: synthetic, reviewed, pending; pending bloqueia cópia. Status de defeito: open, resolved, out_of_scope. Estruturalmente resolved exige retest_attempt_id existente; demais estados podem usar null. PASS e evidência do reteste são avaliados pelo consolidador, não pelo schema.
Modelo derivado report preserva manifesto normalizado, adiciona criterion_results, verdict, counts, diagnostics, verified_evidence. A exportação usa somente verified_evidence.
Identidade: cases[].id é ID único de tentativa; cases[].case_id é ID lógico estável do caso; attempt é inteiro positivo crescente por case_id. criteria[].case_ids aponta IDs lógicos. cases[].supersedes e defects[].retest_attempt_id apontam IDs únicos de tentativa. Referência inexistente é erro estrutural.
Política de reteste: supersedes só referencia tentativa anterior do mesmo case_id e mesmo alvo, sem ciclos ou ramificações. Selecionar a tentativa terminal declarada; se bloqueada, não retornar a uma tentativa antiga PASS. Todas permanecem no histórico.
Defeito marcado resolved só é considerado encerrado quando o reteste referenciado é PASS e sua evidência é válida. Se o reteste não comprovar resolução, manter defeito vigente: FAIL se sua falha original possui evidência válida, senão BLOCKED por insuficiência de evidência. Não rejeitar o manifesto por essa insuficiência semântica.
Exposição do comando de teste no relatório é apenas texto sanitizado. Nenhum eval, shell ou execução do comando armazenado.

## Contrato de skill
Todas as skills têm frontmatter name/description e seções Inputs, Procedure, Output, Failure modes, Safety e Related skills.
Workflows consomem contexto e contratos existentes; produzem plano/resultado de teste, defeito ou relatório conforme objetivo.
Roteador qa prioriza intenção explícita, depois superfície e risco; retorna nomes qa-* existentes e explica não aplicabilidade.
Especialistas usam qa-specialist-*; workflows usam qa-<workflow>. O prefixo separa strategy/regression/readiness especializados das entradas de workflow e evita colisões de descoberta.
Especialidades são orientações executáveis por ferramentas disponíveis, não promessa de instalação automática.
QA de acessibilidade exige verificar o comportamento real, inclusive primitivas de bibliotecas; automação não garante acessibilidade completa.

## Saídas por workflow
init: contexto, ferramentas disponíveis e ausentes; strategy: risco, cobertura, ambientes, dados e critérios de entrada/saída;
test: execução e evidência; explore: charter, observações e defeitos; regression: seleção por impacto e justificativa;
bug: reprodução, severidade/prioridade, estado e reteste; review: requisitos/cobertura e findings;
release: parecer com falhas/pendências; report: CLI de exportação; status: resumo somente leitura.
Testes mobile incluem Android/iOS conforme escopo; Web inclui navegadores definidos no contrato; sem dispositivo/browser disponível, declarar limitação.
Dados: integridade, transações e reconciliação. API: contratos, autenticação/autorização, erros e idempotência.
Performance: perfil, percentis e limites acordados. Segurança: escopo autorizado e falhas reproduzíveis.
Automação/CI: isolamento, determinismo, flaky tests, artefatos e gates. Produção: observações autorizadas, incidentes e regressão preventiva.
Métricas: denominadores explícitos, zero casos sem percentual enganoso; cobertura de requisitos não é cobertura de linhas.

## Aceite consolidado
PRD CA-001 a CA-018 continuam fontes de rastreabilidade.
Correções obrigatórias: CA-003 exige smoke real bem-sucedido; capacidades distintas podem gerar limitações distintas.
CA-007 compara também textos, esperado/observado, defeitos e referências de evidência.
CA-019: fixture sintética com token em log e imagem sem revisão não aparece no pacote/manifesto público/HTML/PDF e impede PASS.
CA-020: defeito aberto comprovado dentro do escopo sem criterion_ids resulta FAIL; fora do escopo é explicitamente separado.
CA-021: manifesto inválido, colisão, limite excedido e falha de PDF não publicam relatório como completo.
Fixture visual: 100 critérios com 2000 caracteres, acentos, tabelas extensas e imagens; texto integral, sem corte/sobreposição.
Esta especificação não marca requisitos nem implementação como aprovados.

## Recomendação de ferramentas e playwright-cli
Skill adicional qa-tooling, solicitada pelo usuário, acionada pelo roteador e por init/strategy.
Inputs: stack observada, superfície a testar, runtime/OS, ferramentas instaladas, CI, orçamento e restrições de dados.
Output: tabela de ferramenta, finalidade, disponibilidade (available/missing/unverified), evidência da detecção, pré-requisitos, custo/licença quando verificados, alternativa e motivo.
Preferir ferramentas existentes e evitar migração sem benefício concreto. Consultar documentação oficial atual antes de recomendar comandos de instalação, compatibilidade ou custos; registrar fonte/data. Não instalar automaticamente.
Cobertura: Web/UI, API, mobile, dados, acessibilidade, performance, segurança, automação/CI, observabilidade e exportação.
playwright-cli é opção explícita de Web/UI exploratório: sessão própria, navegação, snapshots, ações com refs observadas e screenshots. Preferir Playwright Test para suítes repetíveis/CI quando pertinente; CLI interativo não substitui toda suíte.
Comandos globais: playwright-cli --version; playwright-cli -s=qa-report open; playwright-cli -s=qa-report snapshot; playwright-cli -s=qa-report screenshot --filename=report.png; playwright-cli -s=qa-report close. A documentação primária consultada em 2026-09-12 define o fallback local como `npx --no-install playwright --version` e a entrada como `npx playwright cli`; registrar essa proveniência e não tratar presença de `npx` como prova de Playwright instalado.
Não reutilizar perfis pessoais, exportar cookies/storage ou encerrar sessões alheias. Capturas devem ser revisadas antes de anexadas. Snapshots são normalizados como texto; traces e vídeos não entram na whitelist de anexos v1.
CA-022: qa-tooling recomenda por contexto com alternativas e disponibilidade; ferramenta ausente não gera instalação ou execução fictícia.
CA-023: qa-specialist-web e qa-specialist-automation documentam playwright-cli, isolamento de sessão e limites de evidência; fixture sem CLI oferece alternativa e registra indisponibilidade.

## Fora de escopo
Publicação, hospedagem, certificação, correção autônoma, novos MCPs, instalações pessoais e alterações em Flow/DevOps/Power.
