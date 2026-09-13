---
type: PRD
okf_version: "0.2"
generated:
  by: agent:codex
  at: "2026-09-12T10:26:09Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
sources:
  - resource: user:conversation/specflow
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T10:35:43Z"
    scope: specflow_v1_power_plan
    source: "user: aprovado"
---

# SpecFlow — Product Requirement Document

Status: APPROVED
Updated: 2026-09-12T10:26:09Z
Sources: decisões do usuário nesta conversa; desenho consolidado local em `.planning/power/features/specflow/spec.md`.

## 1. Overview

SpecFlow é uma extensão nativa do CompozyOS para conduzir desenvolvimento orientado por especificações com contratos verificáveis, gates humanos explícitos e evidências auditáveis. O problema atual é que o método SDD existente depende de convenções e recursos de outros runtimes, enquanto usuários do CompozyOS precisam do mesmo rigor em uma extensão somente de recursos, sem instalar componentes ou ativar integrações automaticamente.

O produto atende equipes que querem executar uma Feature completa, uma mudança pequena pelo fluxo QUICK ou promover um item opcional de roadmap sem perder rastreabilidade, qualidade ou controle humano. O nome público é **SpecFlow**. Identificadores internos, agentes, skills e Loops usam o prefixo exato `sdd-flow-*`; o identificador e diretório da extensão são `sdd-flow` e `plugins/sdd-flow/`.

## 2. Goals and metrics

| ID | Objetivo | Métrica | Meta da v1 |
|---|---|---|---:|
| G-001 | Preservar o método SDD no CompozyOS | Gates obrigatórios representados e testados | 100% |
| G-002 | Atender os três caminhos de entrada | Jornadas aceitas: roadmap, Feature independente e QUICK | 3 de 3 |
| G-003 | Operar sem capacidades opcionais | Jornadas básicas concluídas sem Docker, worktree, Live, playwright-cli ou exportador PDF | 3 de 3 |
| G-004 | Produzir evidência rastreável | Critérios aceitos ligados a teste, resultado, arquivo e hash válidos | 100% |
| G-005 | Manter observação segura | Consultas de status que criam execução, alteram estado ou enviam mensagens | 0 |
| G-006 | Distribuir uma extensão coerente | Inventário validado de agentes, skills, Loops e templates | 9 agentes, 20 skills, 4 Loops e 11 templates SDD |

## 3. Functional requirements (MoSCoW)

### Must have

- FR-001 — Conduzir INIT, MAP, contratos de produto, especificação, tarefas, execução, QA, evidência, revisão, verificação e conclusão com gates humanos separados.
- FR-002 — Permitir iniciar por Feature independente ou QUICK sem exigir roadmap; permitir promover um item de roadmap quando ele existir.
- FR-003 — Impedir avanço quando a aprovação correspondente estiver pendente, rejeitada, desatualizada ou vinculada a conteúdo diferente.
- FR-004 — Oferecer status mínimo somente leitura, informando Feature, tarefa, gates, próxima ação, ambiente e capacidades opcionais com fonte, horário e confiança.
- FR-005 — No INIT, detectar capacidades opcionais e recomendar instalação ou configuração, sem instalar, baixar, provisionar ou ativar recursos.
- FR-006 — Usar checkout atual e Network Local como padrões; disponibilizar worktree, Docker Compose e Network Live apenas quando solicitados e autorizados.
- FR-007 — Quando Docker for escolhido, limitar o ambiente à aplicação e às dependências de teste, mantendo agentes e daemon no host e permitindo ambientes isolados em portas distintas.
- FR-008 — Tratar playwright-cli como auxílio opcional de QA; sua ausência não pode transformar teste obrigatório não executado em aprovação.
- FR-009 — Gerar evidência estruturada ligada a requisitos e testes, com exportação HTML e PDF quando declarada no contrato da entrega.
- FR-010 — Permitir retomada a partir do último estágio publicado com sucesso, sem repetir gates ou etapas concluídas e sem perder histórico.
- FR-011 — Aplicar ciclo de correção limitado a três iterações por tarefa, interrompendo por ausência de progresso, ampliação de escopo, ambiguidade arquitetural, operação destrutiva, autorização externa ou falha irrecuperável.
- FR-012 — Entregar a extensão como pacote somente de recursos e sem dependência operacional de outros plugins.

- FR-013 — Apresentar matriz de compatibilidade do runtime com comando, versão, esperado, observado, resultado e referência da prova.
- FR-014 — Produzir recibos separados para aprovações, participação Live, ambiente e exportações, sem reescrever evidência já aprovada.
- FR-017 — Concluir a Feature somente após todas as tarefas aplicáveis, revisão integrada, verificação agregada fresca, exportações contratadas e aprovação humana final.

A qualificação das garantias centrais de FR-013 é obrigatória antes de liberar recursos dependentes. Capacidades opcionais podem estar indisponíveis no consumidor; essa condição não dispensa sua qualificação para a distribuição da v1.

### Could have

- FR-015 — Disponibilizar um resumo agregado de uma Feature concluída, preservando os relatórios independentes de cada tarefa.

### Won't have in v1

- FR-016 — Fleet, paralelismo automático, merge automático, publicação externa automática, agentes em containers, Docker remoto, Network multi-daemon, MCP próprio, hooks ou migração automática do estado legado.

## 4. Non-functional requirements

- NFR-001 — QUICK do SpecFlow altera no máximo 5 arquivos de implementação; testes e evidências são contados separadamente. O limite de autoria Power consta no plano de construção.
- NFR-002 — Cada tarefa tem no máximo 3 tentativas totais, incluindo a primeira execução.
- NFR-003 — 100% dos requisitos Must têm ao menos um critério de aceitação verificável e uma prova registrada antes da conclusão.
- NFR-004 — 0 arquivos de segredo, credenciais, tokens, chaves, certificados, cookies, auth storage ou dumps de ambiente podem ser lidos ou publicados pelo produto.
- NFR-005 — 100% dos caminhos de evidência aceitos são relativos ao checkout, regulares, sem traversal ou symlink, e acompanhados de SHA-256.
- NFR-006 — 0 instalações, ativações Live, provisionamentos Docker, criação de worktree, merges ou publicações ocorrem sem ação e consentimento correspondentes.
- NFR-007 — HTML escapa conteúdo não confiável; PDF solicitado deriva do HTML validado, não executa scripts ativos ou fetch externo não autorizado e recebe inspeção visual e hash.
- NFR-008 — Todas as jornadas obrigatórias da extensão devem ter provas de execução e zero falhas de aceite. O baseline do repositório de autoria consta no plano de construção.
- NFR-009 — O pacote gerado contém exatamente 9 agentes, 20 skills, 4 Loops, 11 templates SDD preservados e os complementos explicitamente aprovados.

## 5. Scope and non-scope

### In scope

- Extensão pública SpecFlow, identificador interno `sdd-flow` e recursos internos `sdd-flow-*`.
- Ciclos de produto, Feature, QUICK e entrega.
- Roadmap opcional e promoção controlada para Feature.
- Status mínimo somente leitura.
- Worktree por Feature e Docker Compose opcionais, locais e isolados.
- Network Local padrão e Live opcional por execução.
- QA com playwright-cli opcional.
- Evidência estruturada e exportação HTML/PDF.
- Documentação, validação estrutural, testes unitários e jornadas reais autorizadas.

### Out of scope

- Fleet e execução paralela automática.
- Instalação automática de ferramentas ou dependências opcionais.
- Merge, publicação externa ou descarte automático de dados e volumes.
- Execução de agentes ou do daemon dentro de Docker.
- Docker remoto, Network multi-daemon, MCP próprio, hooks e automações agendadas.
- Conversão ou sincronização automática de estado legado.

## 6. User stories with acceptance criteria

### US-001 — Inicialização segura

Como operador, quero iniciar o SpecFlow mesmo sem ferramentas opcionais, para poder usar o fluxo básico.

- AC-001 — Dado um consumidor sem Docker, Live, playwright-cli e backend PDF, quando INIT é executado, então o produto informa as ausências e recomenda os próximos passos sem instalar nem bloquear o fluxo básico. Cobre FR-005 e FR-006.

### US-002 — Feature independente

Como responsável de produto, quero iniciar uma Feature sem roadmap, para entregar uma necessidade isolada com todos os gates.

- AC-002 — Dado um problema de Feature sem roadmap, quando o fluxo é iniciado, então PRD, Stories quando aplicáveis, especificação e tarefas passam por aprovações independentes antes da execução. Cobre FR-001, FR-002 e FR-003.

### US-003 — Mudança QUICK

Como desenvolvedor, quero executar uma mudança pequena por QUICK, para reduzir cerimônia sem perder testes, revisão e verificação.

- AC-003 — Dada uma mudança elegível de até 5 arquivos de implementação, quando QUICK é aprovado, então ela percorre contrato, TDD, QA, evidência, revisão e verificação; arquitetura, migração, destruição, ampliação ou verificação desconhecida causa escalonamento antes da edição. Cobre FR-002, FR-003 e NFR-001.

### US-004 — Roadmap opcional

Como responsável de produto, quero promover uma Feature de um roadmap aprovado, para preservar origem e decisões sem tornar o roadmap obrigatório.

- AC-004 — Dado um item de roadmap aprovado, quando ele é promovido, então a nova Feature registra a origem e inicia seus próprios gates; na ausência de roadmap, Feature independente e QUICK continuam disponíveis. Cobre FR-002.

### US-005 — Ambiente isolado opcional

Como desenvolvedor, quero usar worktree com Docker Compose em portas diferentes, para testar duas Features sem colisão.

- AC-005 — Dadas duas Features autorizadas, quando cada uma recebe worktree e Compose, então checkout, nome do projeto, portas, processos e dados permanecem distintos; apenas aplicação e dependências de teste entram nos containers. Cobre FR-006 e FR-007.

### US-006 — Network Live com consentimento

Como operador, quero ativar Live somente para uma execução específica, para colaborar sem ampliar silenciosamente o alcance da rede.

- AC-006 — Dado o padrão Local, quando Live não tem consentimento válido, então a participação é bloqueada; quando há consentimento delimitado, a execução registra escopo e recibo sem transmitir segredos. Cobre FR-006 e FR-014.

### US-007 — Evidência exportável

Como aprovador, quero receber evidência em HTML e/ou PDF, para revisar e arquivar o que foi realmente verificado.

- AC-007 — Dada uma entrega que solicita HTML, PDF ou ambos, quando QA, evidência, revisão e verificação terminam, então a exportação contém os artefatos vinculados, identifica resultados pendentes ou falhos, usa conteúdo sanitizado e recebe hash; falha de formato solicitado impede concluir a entrega. Cobre FR-008, FR-009 e FR-014.

### US-008 — Status confiável

Como operador, quero consultar o estado atual sem efeitos colaterais, para saber o próximo passo permitido.

- AC-008 — Dada qualquer fase do fluxo, quando status é consultado, então nenhuma execução, mensagem ou mutação é criada e a resposta distingue ausência opcional, pendência, bloqueio e divergência com fonte, horário e confiança. Cobre FR-004 e FR-010.

### US-009 — Correção limitada e retomável

Como aprovador, quero que correções sejam limitadas e retomáveis, para evitar loops sem progresso ou perda de rastreabilidade.

- AC-009 — Dada uma tarefa rejeitada, quando a correção é autorizada, então o contador anterior é preservado, apenas o escopo aprovado é alterado e o processo termina em sucesso ou em uma das condições de parada após no máximo 3 tentativas. Cobre FR-010 e FR-011.

### US-010 — Instalação nativa

Como usuário do CompozyOS, quero instalar o SpecFlow como extensão somente de recursos, para não depender da instalação dos plugins usados como referência durante sua autoria.

- AC-010 — Dado o pacote construído, quando instalado em ambiente limpo suportado, então todos os recursos `sdd-flow-*` necessários são descobertos e nenhuma referência de runtime exige `sdd-composy`, `pwdev-flow`, `pwdev-code` ou `pwdev-power`. Cobre FR-012.

### Cenários complementares obrigatórios

- AC-011 — Dada uma aprovação pendente, rejeitada ou cujo conteúdo mudou, quando um estágio tenta avançar, então a transição é recusada e identifica o contrato que exige nova decisão. Adicionar metadados de uma aprovação real não autoriza alterar outros bytes. Cobre FR-003 e FR-014.
- AC-012 — Dado um teste de browser obrigatório sem playwright-cli, quando QA avalia a capacidade, então utiliza alternativa qualificada ou registra `NOT_RUN` e impede o aceite correspondente; ausência da ferramenta nunca produz PASS ou N/A. Cobre FR-008.
- AC-013 — Dada uma interrupção após publicação bem-sucedida de uma etapa, quando a execução é retomada, então conserva resultado, contadores e decisões válidos e inicia a próxima etapa permitida; conteúdo alterado invalida os resultados afetados. Cobre FR-010.
- AC-014 — Dado um runtime candidato, quando a qualificação central é executada, então cada garantia de aprovação vinculada a bytes, isolamento de papéis, validação, confinamento, atomicidade, histórico/retomada e exclusão mútua recebe cenário positivo e negativo, comando e resultado observados. Garantia central não comprovada bloqueia o módulo dependente. Cobre FR-013.
- AC-015 — Dadas todas as tarefas completas, quando o fechamento da Feature é solicitado, então a Feature permanece incompleta até revisão integrada, verificação agregada fresca, exportações contratadas e aprovação final; uma Run encerrada não substitui esses requisitos. Cobre FR-001 e FR-017.
- AC-016 — Dado um relatório exportado aguardando aceite, quando o humano aprova, então um recibo separado vincula a decisão aos hashes do snapshot e das exportações; o arquivo aprovado permanece imutável. Cobre FR-009 e FR-014.

## 7. Technical constraints

- Nome público exato: `SpecFlow`.
- Identificador e diretório da extensão: `sdd-flow` e `plugins/sdd-flow/`.
- Prefixo exato de agentes, skills e Loops: `sdd-flow-*`.
- A distribuição é somente de recursos nativos do CompozyOS; não inclui SDK, subprocesso, hook, MCP próprio ou helper executável no consumidor.
- Durante a autoria, somente recursos do `pwdev-power` conduzem planejamento, worktree, execução, revisão e verificação.
- `sdd-composy` permanece referência funcional e de templates; `pwdev-flow` e `pwdev-code` não participam do runtime nem da execução desta implementação.
- Contratos humanos permanecem Markdown; estado operacional validado permanece separado.
- Branch, checkout, baseline e limites de autoria são dados do plano Power, não requisitos dos projetos consumidores do SpecFlow.

## 8. Risks

| ID | Risco | Impacto | Mitigação |
|---|---|---|---|
| R-001 | Recursos nativos não garantirem atomicidade ou exclusão mútua | Alto | Qualificar com provas positivas e negativas antes dos módulos dependentes |
| R-002 | Fidelidade virar cópia incompatível do runtime anterior | Alto | Matriz de proveniência e testes de cláusulas preservadas/diferenças |
| R-003 | Recursos opcionais serem tratados como obrigatórios ou como PASS ausente | Alto | Jornadas básicas sem opcionais e estados explícitos `NOT_RUN`/indisponível |
| R-004 | Worktrees ou Compose compartilharem porta, dados ou contrato | Alto | Identidade única por Feature e testes com dois ambientes simultâneos |
| R-005 | Live ou relatórios vazarem dados sensíveis | Alto | Consentimento delimitado, sanitização, bloqueio de segredo e inspeção dos artefatos |
| R-006 | Renomeação deixar resíduos `pwdev-composyOs` ou `sdd-native-*` | Médio | Testes negativos em todo o pacote e inventário final |
| R-007 | Baseline integral vermelho ocultar regressão | Médio | Comparar contra as 7 falhas reproduzidas no commit `fb14629` e exigir zero falhas novas |

## 9. Timeline

A v1 será entregue em 12 marcos sequenciais, cada um com plano Power próprio e gate humano: contratos/runtime; referências e schemas; templates; INIT/MAP; produto/roadmap; especificação/tarefas; ambiente; execução/qualidade; Network; exportações; QUICK/status; integração final. Não há prazo de calendário aprovado; avanço depende do aceite e da evidência de cada marco.

## 10. Appendices

- A-001 — O plano e o desenho locais estão em `.planning/power/features/specflow/plan.md` e `.planning/power/features/specflow/spec.md`. A origem histórica está documentada no desenho; os nomes públicos e internos atuais são `SpecFlow`, `sdd-flow` e `sdd-flow-*`.
- A-002 — Baseline aceito pelo usuário: 670 testes executados no commit `fb14629`, com 7 falhas preexistentes reproduzidas; sucesso da entrega significa 0 falhas nos testes focados e nenhuma falha integral adicional.
- A-003 — Questões de produto em aberto: nenhuma. Versões, sintaxes e garantias do runtime são questões de qualificação técnica, não decisões presumidas neste PRD.

## Gate

Este PRD foi aprovado pelo usuário em 2026-09-12T10:35:43Z. A aprovação libera o planejamento e a execução Power dentro deste escopo; cada contrato humano, probe mutável e conclusão continua sujeito ao gate que lhe pertence.
