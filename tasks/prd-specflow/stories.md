---
type: STORIES
okf_version: "0.2"
generated:
  by: agent:pwdev-power
  at: "2026-09-12T11:30:41Z"
lifecycle:
  status: APPROVED
human_approval: APPROVED
applicability: REQUIRED
applicability_justification: "Comportamento voltado a operadores, desenvolvedores e aprovadores."
sources:
  - resource: tasks/prd-specflow/prd.md
    sha256: d76143fad520c44972350d48207348c7256fb18a0e112500f6c34d1f6efd2c96
verified:
  - event: human_approval
    by: human:user
    at: "2026-09-12T18:43:31Z"
    scope: tasks/prd-specflow/stories.md
    source: "user: aprovado"
---

# SpecFlow — Stories

Derivadas do [PRD aprovado](prd.md), gate de 2026-09-12T11:28:23Z.
A aprovação do PRD não aprova estas Stories. IDs permanentes; nenhum cenário cria
requisito novo ou escolhe arquitetura. Toda menção a capacidade é requisito a provar.

## Actors

### Actor-001 — Operador

Objetivo: iniciar e acompanhar trabalho seguro. Contexto: checkout atual ou ambiente
opcional solicitado. Capacidades: escolher entrada, consultar status e autorizar
integrações de seu escopo. Limites: não presume decisões de produto nem instala
ferramentas por simples ausência.

### Actor-002 — Responsável de produto/aprovador

Objetivo: aprovar somente entregas verificáveis. Contexto: contratos, riscos e evidências.
Capacidades: aprovar/rejeitar o conteúdo apresentado e promover item de roadmap.
Limites: aprovação histórica não cobre novos bytes ou dispensa qualidade obrigatória.

### Actor-003 — Desenvolvedor e avaliadores independentes

Objetivo: executar escopo aprovado e reproduzir provas. Contexto: tarefa ready e ambiente
confinado. Capacidades: implementação, QA, review e verify em papéis separados.
Limites: não conceder aprovação humana, ampliar escopo ou usar resumo como prova.

## User Journeys

### Journey-001 — Feature independente ou QUICK

Gatilho: operador apresenta necessidade. Ordem: INIT → MAP → seleção de entrada →
contratos e gates → execução → QA → evidência → review → verify → aceite.
Atores: Actor-001/002/003; Stories US-001/002/003/007/008/009/010.
Resultado: Feature verificada ou bloqueio rastreável. Alternativa/recuperação:
QUICK inelegível escala antes de editar; aprovação stale volta ao contrato responsável.

### Journey-002 — Promoção com ambiente opcional

Gatilho: aprovador seleciona Feature de roadmap. Ordem: registrar origem → contratos
locais e gates → consentimento do ambiente/Live quando solicitado → entrega e aceite.
Atores: Actor-001/002/003; Stories US-004/005/006/007/008/009.
Resultado: origem preservada e ambientes isolados. Alternativa/recuperação:
opcional indisponível não bloqueia trabalho independente nem permite substituição silenciosa;
falha parcial preserva recursos próprios recuperáveis e exige próxima decisão segura.

## User Stories

### US-001 — Inicialização segura — RF-005, RF-006

Como operador, quero iniciar sem opcionais para utilizar o fluxo básico.

#### SC-001 — CA-001

Dado consumidor sem Docker, worktree, Live, playwright-cli e PDF, quando INIT inspeciona,
então recomenda sem instalar/baixar/provisionar/abrir browser/ativar Live e permite
trabalho independente. Checagem inconclusiva é não verificada, não capacidade disponível.

### US-002 — Feature independente — RF-001, RF-002, RF-003, RF-017

Como aprovador, quero especificar uma necessidade sem roadmap e preservar gates.

#### SC-002 — CA-002

Dada Feature independente, quando especificada, então PRD, Stories aplicáveis,
TechSpec e tarefas têm decisões separadas antes da execução. Sem gate não avança.

#### SC-011 — CA-011

Dada aprovação pendente/rejeitada ou bytes alterados, quando tenta avançar, então
bloqueia e identifica contrato a reconciliar; metadados não autorizam novos bytes.

#### SC-015 — CA-015

Dadas tarefas completas, quando fecha Feature, então exige integração fresca,
QA/review/verify independentes, dossier/exportações íntegros e gate humano final;
Run done ou tarefa contada não basta.

### US-003 — QUICK com qualidade — RF-002, RF-003, RF-011

Como desenvolvedor, quero reduzir cerimônia sem perder qualidade.

#### SC-003 — CA-003

Dada mudança elegível de até cinco arquivos de implementação, quando QUICK é aprovado,
então mantém TDD/QA/evidência/review/verify; sexta alteração, arquitetura, migração,
destruição, ampliação ou verificação desconhecida escala antes da edição. Testes e
evidências contam separadamente; a cadeia de gates não é reduzida.

### US-004 — Roadmap opcional — RF-002

Como responsável de produto, quero promover uma Feature preservando sua origem.

#### SC-004 — CA-004

Dado item aprovado, quando promovido, então registra origem e inicia novos gates
locais; ausência de roadmap não impede Feature independente/QUICK.

### US-005 — Ambiente isolado — RF-006, RF-007

Como desenvolvedor, quero testar duas Features sem colisões.

#### SC-005 — CA-005

Dadas duas Features autorizadas, quando usam worktree/Compose locais, então checkout,
projeto, portas, processos, contratos e dados são distintos. Somente app/deps de teste
entram em Docker; agentes/daemon ficam no host. Limpeza autorizada de um não afeta
outro nem remove dados por padrão; identidade desconhecida impede adoção/limpeza.

### US-006 — Live consentido — RF-006, RF-014

Como operador, quero consentir participação apenas no escopo escolhido.

#### SC-006 — CA-006

Dado Local padrão, quando não há consentimento Live válido, então não participa;
com consentimento delimitado registra escopo e recibo sem transmitir segredos.
Conversa não é gate e falta de Live não inviabiliza fluxo Local.

### US-007 — Evidência exportável — RF-008, RF-009, RF-014

Como aprovador, quero revisar o que realmente foi verificado.

#### SC-007 — CA-007

Dado contrato HTML/PDF, quando exporta, então liga critérios/artefatos, preserva falhas
e pendências, sanitiza e calcula hashes. Falha de formato solicitado impede concluir;
PDF exige inspeção visual, imagens corretas e nenhum fetch externo não autorizado.

#### SC-012 — CA-012

Dado cenário obrigatório sem browser adequado, quando QA avalia, então usa alternativa
qualificada autorizada ou marca NOT_RUN e bloqueia aceite; ausência nunca é PASS/N/A.

#### SC-016 — CA-016

Dado relatório aguardando aceite, quando aprovado, então recibo separado vincula a
decisão a hashes do snapshot/exportações sem reescrever arquivos aprovados.

### US-008 — Status confiável — RF-004, RF-010

Como operador, quero saber a próxima ação permitida sem efeitos colaterais.

#### SC-008 — CA-008

Dada qualquer fase, quando consulta status, então nenhuma execução/mensagem/mutação
é criada; resposta distingue ausência, pendência, bloqueio/divergência com fonte,
horário e confiança. Fonte indisponível não vira autorização implícita.

### US-009 — Correção retomável — RF-010, RF-011

Como aprovador, quero evitar repetição ilimitada e perda de histórico.

#### SC-009 — CA-009

Dada correção autorizada, quando executada/retomada, então conserva escopo e contador
de até 3 tentativas totais incluindo a primeira, janela sem progresso 2 e fan-out 1;
filhos não reiniciam limites, e condições de parada impedem novas ações.

#### SC-013 — CA-013

Dada interrupção após publicação bem-sucedida, quando retoma, então conserva decisões,
contadores/resultados válidos e segue próxima etapa permitida. Alteração invalida
dependentes; falha antes da publicação não fabrica sucesso.

### US-010 — Distribuição qualificada — RF-012, RF-013, RF-016

Como usuário, quero instalar recursos coerentes sem dependências nos plugins-fonte.

#### SC-010 — CA-010

Dado ambiente limpo suportado, quando instalação é autorizada, então descobre 9 agentes,
20 skills, 4 Loops, 11 templates SDD e complementos contratados, sem dependência runtime
nos plugins-fonte nem capacidades fora da v1; instalar não ativa opcionais.

#### SC-014 — CA-014

Dado runtime candidato, quando qualificado em escopo aprovado, então cada garantia
central tem caso positivo/negativo e comando/resultado reais; falha/NOT_RUN ou prova
ausente bloqueia dependentes. Help/build não provam comportamento.

## Dependencies

PRD aprovado e digest acima conferido; o gate próprio destas Stories foi aprovado
em 2026-09-12T18:43:31Z. Integrações opcionais dependem de capacidade qualificada e consentimento.
RF-015 é Could: resumo opcional não introduz jornada obrigatória nem substitui
relatórios independentes. RF-016 preserva exclusões, testadas por SC-010.
Nenhum contrato técnico é criado ou presumido aqui.

## Edge Cases

Cobertos: falta/inconclusão de opcionais (SC-001/012); aprovação stale (SC-011);
QUICK fora do limite (SC-003); colisão/limpeza alheia (SC-005); Live sem autorização
(SC-006); exportação falha ou conteúdo hostil (SC-007/016); fonte de status ausente
(SC-008); interrupção e limites persistidos (SC-009/013); garantia não provada
(SC-014); conclusão prematura (SC-015). Nunca ler segredos ou adotar perfil pessoal.

## Gate

REQUIRED por envolver comportamento externo. Estes bytes foram aprovados pelo humano
em 2026-09-12T18:43:31Z. Aprovação do PRD foi pré-requisito separado; esta decisão
libera somente a preparação do TechSpec e do escopo TASKS, sem aprová-los ou autorizar probes.
