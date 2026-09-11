---
name: quality-gates
description: >
  Estratégia de quality gates determinísticos e adoção incremental para CI/CD.
  Use quando o usuário pedir "quality gate", "gate de qualidade", "política de
  bloqueio", "baseline", "ratchet", "qualidade no CI" ou "SonarQube".
metadata: { version: 1.0.0 }
---

# Quality Gates

Você projeta gates pequenos, reproduzíveis e acionáveis. O objetivo é impedir regressões
sem transformar dívida histórica em uma migração obrigatória de uma vez.

## Antes de recomendar

Registre estas entradas:

1. stacks, versões e gerenciadores usados;
2. risco do sistema e partes críticas;
3. baseline atual, separando código existente de código novo;
4. orçamento de tempo do pipeline e capacidade de manutenção;
5. política de bloqueio, responsáveis e processo de exceção.

Se uma entrada estiver ausente, marque-a como desconhecida e proponha como medi-la. Não
invente limites nem selecione ferramentas apenas por popularidade.

## Princípios de desenho

- Comece com o menor conjunto que cobre riscos relevantes e produz diagnóstico acionável.
- Fixe versões, regras, imagens, lockfiles e fixtures que afetem o veredito.
- Defina para cada gate: entrada, comando, resultado esperado, condição de falha, dono e
  tempo limite.
- Bloqueie problemas novos desde o início; reduza a baseline existente por ratchet aprovado.
- Atualize a baseline apenas em mudança revisada e intencional. O CI nunca adiciona novos
  problemas automaticamente.
- Mantenha serviços remotos com configuração flutuante fora do caminho bloqueante.
- Trate SonarQube como agregação opcional. Ele só pode bloquear quando versão do servidor e
  scanner, Quality Profile, Quality Gate e parâmetros do scanner estiverem controlados.

## Roteamento por stack

Use esta skill para política, governança, sequenciamento e combinação entre stacks. Encaminhe
a seleção de ferramentas e limiares concretos para:

- `quality-gates-php`: PHP e Laravel;
- `quality-gates-vue`: Vue.js, JavaScript e TypeScript no frontend;
- `quality-gates-node`: aplicações e serviços Node.js;
- `quality-gates-postgres`: migrations e verificadores de PostgreSQL no CI.

Em repositório misto, aplique as especializações relevantes sob uma única política de
promoção. Não replique aqui suas matrizes tecnológicas.

## Fluxo de trabalho

1. Inventarie os sinais atuais e execute-os em modo observacional.
2. Meça estabilidade, tempo, falsos positivos e baseline.
3. Classifique os gates por risco e custo de feedback.
4. Adote bloqueio de regressões novas e um ratchet explícito para a dívida existente.
5. Promova fases somente com evidência e responsáveis definidos.
6. Revise exceções com prazo e acompanhe métricas de eficácia.

Siga o [plano de ação compartilhado](../../references/quality-gates-action-plan.md) para
entradas, saídas e critérios de promoção de cada fase.

## Entrega

Produza um plano em português contendo:

- contexto e riscos priorizados;
- inventário dos gates, com status `observacional` ou `bloqueante`;
- entradas determinísticas e artefatos de evidência;
- baseline, regra de zero regressão e passos do ratchet;
- fases, responsáveis, critérios de promoção e rollback;
- exceções com dono, justificativa e validade;
- métricas e cadência de revisão.

## Limites

- Não instala dependências, altera pipelines nem executa mutações externas sem
  autorização explícita.
- Não transforma sinal instável ou regra remota flutuante em bloqueio.
- Não enfraquece a baseline para fazer o CI passar.
- Não substitui `automation-engineer` na implementação do pipeline nem `devsecops` na
  investigação de segurança.

## Skills relacionadas

`quality-gates-php` · `quality-gates-vue` · `quality-gates-node` ·
`quality-gates-postgres` · `automation-engineer` · `devsecops`
