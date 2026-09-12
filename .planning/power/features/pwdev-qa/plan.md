# PWDEV QA — plano de implementação
Status: APPROVED
Spec: .planning/power/features/pwdev-qa/spec.md
Updated: 2026-09-12
Source: solicitação de elaborar o plano; acréscimos playwright-cli e qa-tooling.

## Resultado
Plugin portátil para Claude Code, Codex e Hermes, com 29 skills, 10 workflows/comandos,
17 especialistas e relatórios HTML/PDF com validação de aceite. As 29 skills incluem
roteador e recomendador de ferramentas, além de workflows e especialistas.

## Plano de entrega
- [F01 — Núcleo e recomendação de ferramentas](f01-plan.md): 3 tarefas; depende de nenhuma.
- [F02 — Dezessete especialistas](f02-plan.md): 6 tarefas; depende de F01.
- [F03 — Validação de aceite e relatórios HTML/PDF](f03-plan.md): 7 tarefas; depende de F01.
- [F04 — Dez workflows de uso](f04-plan.md): 5 tarefas; depende de F01, F02, F03.
- [F05 — Empacotamento e validação dos runtimes](f05-plan.md): 3 tarefas; depende de F01, F02, F03, F04.

Ordem padrão: F01 -> F02 -> F03 -> F04 -> F05.
F02 e F03 têm dependências independentes, mas execução paralela não é necessária
nem autorizada implicitamente. Não reduzir o escopo da v1 para fechar uma fase.

## Mapa de tarefas
| ID | Entrega | Complexidade | Arquivos | Contrato |
|---|---|---|---:|---|
| F01-01 | Roteador e contratos comuns | medium | 5 | [arquivos, interfaces e testes](f01-plan.md#task-01--roteador-e-contratos-comuns) |
| F01-02 | Skill de recomendação e catálogo de ferramentas | medium | 3 | [arquivos, interfaces e testes](f01-plan.md#task-02--skill-de-recomendacao-e-catalogo-de-ferramentas) |
| F01-03 | Mapeamentos dos três runtimes | medium | 4 | [arquivos, interfaces e testes](f01-plan.md#task-03--mapeamentos-dos-tres-runtimes) |
| F02-04 | Estratégia, requisitos e funcional | medium | 4 | [arquivos, interfaces e testes](f02-plan.md#task-04--estrategia-requisitos-e-funcional) |
| F02-05 | Web, API e mobile | medium | 4 | [arquivos, interfaces e testes](f02-plan.md#task-05--web-api-e-mobile) |
| F02-06 | Dados, acessibilidade e performance | medium | 4 | [arquivos, interfaces e testes](f02-plan.md#task-06--dados-acessibilidade-e-performance) |
| F02-07 | Segurança, automação e CI | medium | 4 | [arquivos, interfaces e testes](f02-plan.md#task-07--seguranca-automacao-e-ci) |
| F02-08 | Regressão, defeitos e produção | medium | 4 | [arquivos, interfaces e testes](f02-plan.md#task-08--regressao-defeitos-e-producao) |
| F02-09 | Métricas e prontidão | medium | 3 | [arquivos, interfaces e testes](f02-plan.md#task-09--metricas-e-prontidao) |
| F03-10 | Schema e validação de entrada | high | 3 | [arquivos, interfaces e testes](f03-plan.md#task-10--schema-e-validacao-de-entrada) |
| F03-11 | Integridade e sanitização de evidências | high | 3 | [arquivos, interfaces e testes](f03-plan.md#task-11--integridade-e-sanitizacao-de-evidencias) |
| F03-12 | Consolidação determinística do parecer | high | 2 | [arquivos, interfaces e testes](f03-plan.md#task-12--consolidacao-deterministica-do-parecer) |
| F03-13 | Relatório HTML offline | medium | 2 | [arquivos, interfaces e testes](f03-plan.md#task-13--relatorio-html-offline) |
| F03-14 | PDF paginado e dependências | high | 3 | [arquivos, interfaces e testes](f03-plan.md#task-14--pdf-paginado-e-dependencias) |
| F03-15 | CLI e publicação do pacote | high | 3 | [arquivos, interfaces e testes](f03-plan.md#task-15--cli-e-publicacao-do-pacote) |
| F03-16 | Teste integrado, fixture e inspeção visual | high | 3 | [arquivos, interfaces e testes](f03-plan.md#task-16--teste-integrado-fixture-e-inspecao-visual) |
| F04-17 | Workflows init / strategy | medium | 5 | [arquivos, interfaces e testes](f04-plan.md#task-17--workflows-init--strategy) |
| F04-18 | Workflows test / explore | medium | 5 | [arquivos, interfaces e testes](f04-plan.md#task-18--workflows-test--explore) |
| F04-19 | Workflows regression / bug | medium | 5 | [arquivos, interfaces e testes](f04-plan.md#task-19--workflows-regression--bug) |
| F04-20 | Workflows review / release | medium | 5 | [arquivos, interfaces e testes](f04-plan.md#task-20--workflows-review--release) |
| F04-21 | Workflows report / status | medium | 5 | [arquivos, interfaces e testes](f04-plan.md#task-21--workflows-report--status) |
| F05-22 | Manifests e registro Hermes | high | 5 | [arquivos, interfaces e testes](f05-plan.md#task-22--manifests-e-registro-hermes) |
| F05-23 | Documentação e catálogos | medium | 5 | [arquivos, interfaces e testes](f05-plan.md#task-23--documentacao-e-catalogos) |
| F05-24 | Integração documental e smoke real | high | 5 | [arquivos, interfaces e testes](f05-plan.md#task-24--integracao-documental-e-smoke-real) |

Cada contrato lista todos os caminhos exatos. Total: 24 tarefas.
Há arquivos de teste incrementais usados em mais de uma tarefa; a execução sequencial
preserva os testes anteriores. Contagem de arquivos por tarefa inclui esses arquivos compartilhados.

## Decisões consolidadas
- Seguir Power; os gates do AGENTS.md desconsiderado não são pré-requisitos deste plano.
- [spec.md](spec.md) é a especificação consolidada para a proposta de execução.
  Os documentos antigos em tasks/prd-pwdev-qa/ permanecem como histórico, não contratos concorrentes.
- Portabilidade se comprova com execução real em cada runtime; descoberta de executável não prova funcionamento.
- Python >=3.9 e ReportLab 4.4.9; teste PDF em Python 3.12 com dependências observadas.
- Um modelo normalizado alimenta HTML/PDF. Paridade inclui fundamentação e evidências, além do parecer.
- Sanitização verificada e defeitos comprovados fora da matriz entram nos testes negativos.
- qa-tooling recomenda ferramentas por contexto; playwright-cli aparece em Web/UI e automação.
- Aprovação deste pacote autoriza o escopo proposto das cinco features; nenhuma aprovação foi registrada ainda.

## Rastreamento e verificação
[TRACEABILITY.md](TRACEABILITY.md) liga todos os critérios às tarefas.
Cada plano contém ciclo teste falhando -> implementação -> teste aprovado, com comando específico.
Testes novos são propostas a implementar, não comandos já aprovados em execução nesta sessão.

Suíte final do plugin:
`python3 -m unittest discover -s tests -p 'test_qa_*.py'`

Regressão de integração existente:
`python3 -m unittest tests.test_readme_marketplace`
`python3 scripts/validate_readme_plugins.py`

Para PDF nesta máquina, substituir python3 pelo executável observado:
`/Users/paulosoares/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
O plugin não deve gravar esse caminho local nos seus scripts.

Além de testes determinísticos: avaliar cenários das skills em runtime real;
comparar manifesto/HTML/PDF; inspecionar páginas PDF renderizadas; abrir HTML com
playwright-cli em sessão própria quando disponível. Fixture sintética é identificada.
Não confundir aprovação do teste estrutural de uma skill com avaliação de seu comportamento.

## Baseline observado em 2026-09-12
O comando python3 -m unittest tests.test_marketplace_readmes tests.test_readme_marketplace
executou 9 testes, com 4 falhas na suíte test_marketplace_readmes. Ela exige negrito,
seções e inventário individual que o README atual não usa. Não houve alteração nesses
arquivos durante o planejamento. tests.test_readme_marketplace passou; o comando
python3 scripts/validate_readme_plugins.py validou os 16 plugins atuais.
A integração QA usará o contrato documental vigente e verificará ausência de novas
regressões; o baseline legado permanece reportado separadamente. Não enfraquecer testes
nem reformar documentação de outros plugins dentro deste escopo.

## Aceite de execução
Concluir somente quando critérios mapeados passarem, review não tiver pendências
bloqueantes e power-verify reproduzir a evidência. Registrar limitações em cada runtime.
Dependência/autenticação ausente permite concluir tarefas independentes, mas impede
declarar suporte verificado naquele runtime ou fechar a v1.
Sem publicação/instalação pessoal/commit/push automáticos.

## Revisão do plano
- [x] Escopo cobre a v1 e os dois acréscimos do usuário.
- [x] Features respeitam até 8 tarefas; tarefas respeitam até 5 arquivos e 7 passos.
- [x] Nomes de skills distinguem especialistas, workflows e qa-tooling.
- [x] Assinaturas do pipeline de relatório explicitadas na especificação.
- [x] Critérios ligados a tarefas em TRACEABILITY.md.
- [x] Revisão independente dos oito documentos; corrigidas identidade de caso/tentativa e regra de resolução de defeito.
- [x] Aprovação humana do pacote de planos em 2026-09-12.
- [ ] Execução e evidências reais.

Próximo passo: aprovar o plano; seguir pwdev-power:power-execute.
