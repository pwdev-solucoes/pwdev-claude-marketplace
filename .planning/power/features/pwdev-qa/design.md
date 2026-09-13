---
type: design-proposal
okf_version: "0.2"
sources:
  - resource: "conversation:pwdev-qa"
  - resource: "plugins/pwdev-flow/skills/flow-review/SKILL.md"
  - resource: "plugins/pwdev-devops/skills/performance-engineer/SKILL.md"
  - resource: "plugins/pwdev-power/.hermes-plugin/__init__.py"
generated:
  by: agent:codex
  at: "2026-09-12"
lifecycle:
  status: DRAFT
human_approval: PENDING
verified: []
---

# PWDEV QA — desenho consolidado da v1

## Problema e objetivo

Oferecer QA geral e especializado durante todo o ciclo de software: prevenir defeitos,
planejar e executar testes, registrar evidências reproduzíveis e comunicar risco residual.
Atender projetos de diferentes stacks em Claude Code, Codex e Hermes.

## Decisões já aprovadas na conversa

- Abrangência geral e especializada nas atribuições de QA discutidas.
- Portabilidade entre Claude Code, Codex e Hermes.
- Arquitetura de núcleo, especialistas e workflows.
- Inspeção e testes ordinários dentro do escopo solicitado; carga, pentest e produção
  exigem autorização explícita. Correção de produto exige pedido do usuário.
- Os dez workflows e as dezessete especialidades abaixo.
- Relatório de evidências em HTML e PDF com validação individual dos critérios de
  aceite, solicitado explicitamente após a revisão do desenho.

Essas aprovações cobrem as decisões listadas; não representam aprovação automática
dos detalhes novos deste documento, de PRD, STORIES, TECHSPEC ou TASKS futuros.

## Superfície aprovada

Workflows: `init`, `strategy`, `test`, `explore`, `regression`, `bug`, `review`,
`release`, `report` e `status`.

Especialidades:

1. Fundamentos e estratégia de QA.
2. Requisitos e critérios de aceitação.
3. Testes funcionais e exploratórios.
4. Web/UI e compatibilidade entre navegadores.
5. APIs, contratos e integrações.
6. Mobile.
7. Banco de dados e qualidade de dados.
8. Acessibilidade.
9. Performance, carga, estresse e capacidade.
10. Segurança de aplicação.
11. Automação de testes.
12. CI/CD e quality gates.
13. Regressão baseada em risco.
14. Gestão, severidade e triagem de defeitos.
15. Observabilidade e validação em produção.
16. Métricas, cobertura e relatórios.
17. Release readiness.

## Arquitetura proposta

### Núcleo e roteamento

Uma skill `qa` orienta seleção por objetivo, superfície e risco. As skills de workflow
usam prefixo `qa-`; especialistas carregam referências apenas quando pertinentes.
Referências compartilhadas definem segurança, evidência, classificação, linguagem,
artefatos e adaptação de ferramentas. Não há obrigação de executar todas as
especialidades em todo projeto. Não aplicabilidade exige justificativa.

Opções consideradas: skill monolítica; especialistas independentes; núcleo com
especialistas e workflows. A terceira opção foi aprovada por reduzir duplicação e
permitir entrada simples com aprofundamento específico. Custo: manter roteamento
e contratos compartilhados. Reversível mediante ajuste dos pontos de entrada.

### Empacotamento e runtimes

Fonte em `plugins/pwdev-qa/`, com `skills/`, `references/`, `templates/`, `scripts/`,
documentação em inglês e português e manifests próprios para cada runtime.
Claude usa comandos finos em `commands/`; Codex descobre as mesmas skills;
Hermes usa `plugin.yaml` e registro de skills em `__init__.py`, seguindo a estrutura
observada no Power. Não se pressupõe um `plugin.json` para Hermes.

O adaptador Hermes registra skills sob demanda, sem impor QA a toda conversa.
Ferramentas disponíveis são detectadas; ausência de browser, emulador, dispositivo,
scanner ou runner produz limitação explícita. Procedimento sugerido nunca conta
como teste executado. Nenhum plugin complementar é dependência obrigatória.

### Artefatos no projeto consumidor

Raiz proposta e já aceita em direção arquitetural: `.planning/pwdev-qa/`.
Contexto, estratégia, casos, charters, bugs, execuções e relatórios são documentos
Markdown relacionados por identificadores estáveis. Cada execução registra escopo,
identificação verificável do alvo testado (commit e diff quando aplicável, build,
digest ou versão do artefato), ambiente sem segredos, ferramenta/comando, resultado e
evidências. Alvo não identificável bloqueia o parecer de prontidão. Estado operacional
JSON, se necessário, preserva campos desconhecidos
e usa publicação atômica validada. A TECHSPEC fechará os schemas antes da execução.

Resultados de caso: `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `NOT_APPLICABLE`.
Defeitos distinguem severidade (impacto) de prioridade (ordem de tratamento).
Relatórios distinguem falha de produto, ambiente indisponível e execução inconclusiva.
Percentual de aprovação apresenta denominador e casos não executados separadamente.

### Relatório de evidências em HTML e PDF

O workflow `report` gera `report.html` e `report.pdf` sob
`.planning/pwdev-qa/reports/<run-id>/`, acompanhados de `manifest.json` e do
subdiretório `evidence/` com evidências sanitizadas. O identificador de execução é
único; uma nova execução não sobrescreve um relatório anterior.

O manifesto é o registro operacional validado da execução. Ele referencia a fonte
Markdown dos critérios aprovados e seu SHA-256, preservando IDs e texto dos critérios.
HTML e PDF são projeções do mesmo manifesto, com o mesmo ID, alvo, instante de
execução, resultados e parecer. Gerar um relatório não executa testes nem aprova
requisitos. O workflow `test` fornece resultados de execução; `report` verifica
sua integridade, rastreabilidade e suficiência declarada.

O relatório contém:

- Identificação: projeto, escopo, alvo testado, runtime, ambiente, autor da execução,
  datas de execução e geração e identificação do contrato de aceite.
- Resumo: contagens por resultado, cobertura avaliada, falhas e bloqueios; nenhuma
  porcentagem omite o denominador. Total zero aparece como sem critérios.
- Matriz de aceite: ID e texto original, aplicabilidade, casos associados, método,
  resultado esperado e observado, resultado consolidado, evidências e defeitos.
- Detalhamento: passos ou comando, código de saída quando aplicável, observação
  verificável, trecho sanitizado de log e capturas pertinentes com legenda.
- Parecer: `PASS`, `FAIL` ou `BLOCKED`, justificativa, riscos e ações pendentes.
  Uma decisão humana de aceitar risco, quando fornecida, é exibida separadamente
  e não converte falhas em sucesso.
- Índice de evidências: caminho relativo, tipo, tamanho e SHA-256; referências
  textuais legíveis no PDF e links locais navegáveis no HTML.

Regras para validação de aceite:

1. Todos os critérios do contrato entram na matriz, inclusive os não executados.
   Ausência de contrato verificável bloqueia o parecer; não se inventam critérios.
2. `PASS` exige todos os testes obrigatórios daquele critério aprovados, evidências
   íntegras e aplicáveis ao alvo e registro de quem avaliou a relação entre resultado
   observado e esperado. Código de saída zero, isoladamente, não prova o critério.
3. Uma falha de produto comprovada consolida o critério em `FAIL`; impede `PASS`
   mesmo se também houver testes bloqueados ou aprovados.
4. Ambiente indisponível, evidência ausente, divergência de hash ou alvo incompatível
   consolidam em `BLOCKED` quando não houver falha já comprovada. Casos nunca
   executados permanecem `NOT_RUN` e impedem parecer global `PASS`.
5. `NOT_APPLICABLE` exige justificativa vinculada ao escopo aprovado; o gerador não
   exclui critérios unilateralmente. Dispensa sem suporte bloqueia o parecer.
6. Parecer global: `FAIL` se houver critério com falha; senão `BLOCKED` se houver
   pendência, evidência inválida ou nenhum critério aplicável; `PASS` somente quando
   todos os critérios aplicáveis passarem. O parecer não publica a release.
7. Reexecução mantém histórico: falha anterior e reteste têm IDs próprios, e o
   relatório identifica qual execução sustenta o resultado atual. Alteração do alvo
   ou contrato exige nova avaliação de aplicabilidade das evidências.

Integridade estrutural pode ser automatizada. Suficiência semântica da evidência
exige avaliação registrada por critério; o gerador não promete provar automaticamente
qualquer requisito apenas inspecionando arquivos ou hashes.

O HTML é estático, funciona offline e usa escaping para conteúdo não confiável,
sem scripts ou recursos remotos. Evidências são arquivos regulares confinados à
execução, sem symlinks ou travessia de diretórios. Conteúdo sensível não é copiado.
O PDF contém a matriz e o parecer completos, paginação, cabeçalhos repetidos em
tabelas e quebra de textos longos; anexos binários permanecem no pacote de evidências.
Resultados usam texto além de cor. PDF ausente ou falha de conversão é reportado
como exportação incompleta, sem alegar entrega dos dois formatos.

Os detalhes de biblioteca e CLI serão fechados na TECHSPEC. A dependência de PDF
deve ser explícita, compartilhável pelos três runtimes e não instalada implicitamente.

### Integrações e limites de responsabilidade

Flow e Power fornecem contratos de entrada e recebem referências de evidência;
QA não altera seus estados, aprovações ou critérios. DevOps complementa investigação
de infraestrutura e performance; UI/UX complementa acessibilidade; YouTrack/GLPI
podem receber defeitos somente quando publicação externa for solicitada.

Release readiness entrega recomendação fundamentada e riscos residuais; a decisão
de publicar permanece humana. Auditoria não autoriza correção de produto.
Automação pode criar testes quando solicitada; mudanças de pipeline exigem escopo
de implementação explícito. Testes que enviem mensagens, cobrem valores ou alterem
serviços externos exigem escopo e autorização correspondentes.

## Critérios de aceitação propostos

- CA-01: dez workflows documentados com entradas, procedimento, saída e falhas.
- CA-02: dezessete especialidades com cenários positivos, negativos, limites e evidência.
- CA-03: mesmos contratos e resultados nos três runtimes, sem dependência de ferramenta
  exclusiva e sem simular execução indisponível.
- CA-04: cada conclusão de teste referencia evidência ou declara ausência de execução.
- CA-05: autorização de teste local não autoriza produção, carga ou pentest.
- CA-06: integrações preservam contratos e aprovações do workflow proprietário.
- CA-07: artefatos e templates permitem rastrear requisito, caso, execução e defeito.
- CA-08: documentação e catálogos apresentam instalação e uso conforme cada runtime.
- CA-09: validação estrutural e testes comportamentais do adaptador Hermes passam;
  smoke real de cada runtime é reportado separadamente de teste com contexto simulado.
- CA-10: uma execução válida gera HTML e PDF com mesmos critérios, resultados,
  evidências e parecer, provenientes do mesmo manifesto identificado.
- CA-11: critério não executado, ausência de evidência, hash divergente ou alvo
  incompatível impedem aprovação; falha comprovada resulta em `FAIL`.
- CA-12: critérios não aplicáveis exigem justificativa sustentada pelo contrato;
  zero critérios ou zero critérios aplicáveis não produz `PASS`.
- CA-13: entradas com HTML malicioso, caminhos externos ou symlinks não executam
  conteúdo nem permitem leitura fora do pacote autorizado.
- CA-14: relatório extenso com acentos, capturas e critérios longos mantém todos os
  critérios legíveis no HTML e no PDF; validação visual inspeciona páginas renderizadas.
- CA-15: a falta da dependência PDF produz diagnóstico de exportação incompleta;
  resultados de testes e sucesso da geração de arquivos são estados separados.

## Verificação planejada

Reutilizar os padrões unittest observados em `tests/test_power_hermes.py` e testes
de marketplace. Validar manifests, links, descoberta, templates e roteamento; testar
o registro Hermes com contexto controlado e falhas de instalação. Avaliar cenários
de prompt para ferramenta ausente, critério ambíguo, falso sucesso, efeitos externos
e recomendação de release com testes bloqueados. Comandos exatos e fixtures serão
fixados em TASKS após a especificação técnica.

Para os relatórios, testar fixtures de todos os critérios aprovados, falha de produto,
execução bloqueada, casos não executados, critérios dispensados e contrato vazio;
testar evidência ausente, alterada e de outra versão. Verificar paridade de conteúdo
entre manifesto, HTML e texto extraído do PDF, além da inspeção visual do PDF
renderizado. Testar escaping, confinamento de arquivos e falha da dependência PDF.
Fixtures sintéticas são identificadas como demonstração, nunca evidência de produto.

## Fora do escopo

Publicação/instalação automática, correções não solicitadas de produto, decisões
autônomas de release, certificação regulatória, infraestrutura própria de execução,
serviço MCP obrigatório e alteração dos plugins usados como referência.

## Riscos e mitigação

- Amplitude superficial: cada especialista exige procedimento e saída concretos.
- Ferramentas ausentes: distinguir orientação, simulação e execução real.
- Duplicação de governança: integração por referência, com proprietário explícito.
- Evidências sensíveis: dados sintéticos, sanitização e exclusão de segredos.
- Portabilidade aparente: separar testes de contrato de smoke real por runtime.

## Próximo gate

Revisar este desenho consolidado. Após sua aprovação, produzir PRD, STORIES,
TECHSPEC e TASKS conforme AGENTS.md para aprovação do contrato de execução.
Este documento usa `tasks/prd-pwdev-qa/` porque a governança canônica do repositório
prevalece sobre a sugestão de `.planning/power/features/` do power-brainstorm.
