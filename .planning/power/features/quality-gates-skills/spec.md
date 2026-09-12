# Quality Gates Skills — Design
Status: APPROVED
Source: conversa com o usuário em 2026-09-11
Updated: 2026-09-11

## Problem

O plugin `pwdev-devops` não possui orientação específica para projetar quality gates
determinísticos. As skills existentes cobrem automação, segurança e operação de banco, mas não
consolidam critérios de reprodutibilidade, adoção incremental, políticas de bloqueio e métricas de
qualidade. Também é necessário atender com precisão a PHP/Laravel, Vue.js, Node.js e PostgreSQL
sem tornar a orientação genérica dependente dessas tecnologias.

## Approach

Adicionar cinco skills complementares ao `pwdev-devops`:

- `quality-gates`: projeta estratégias independentes de linguagem e seleciona gates conforme
  risco, maturidade, custo e velocidade do pipeline.
- `quality-gates-php`: especializa a estratégia para PHP e Laravel.
- `quality-gates-vue`: especializa a estratégia para Vue.js, JavaScript e TypeScript.
- `quality-gates-node`: especializa a estratégia para aplicações e serviços Node.js.
- `quality-gates-postgres`: especializa a estratégia para PostgreSQL e migrations, sem assumir
  responsabilidades operacionais de DBA.

As cinco skills compartilharão um plano de ação de referência. A skill genérica encaminhará os
detalhes de cada stack para a especialização correspondente, sem duplicar suas matrizes de
ferramentas e limiares. SonarQube será tratado como agregador opcional, com servidor, scanner,
Quality Profile e Quality Gate fixados, sem substituir os verificadores locais bloqueantes.

## Decisions

### DEC-001 — Cinco skills no plugin existente

- Decision: definir onde as skills serão publicadas.
- Options: plugin separado; uma única skill; cinco skills no `pwdev-devops`.
- Choice: cinco skills no `pwdev-devops`.
- Why: preserva a descoberta no domínio de CI/CD e separa princípios universais de detalhes do
  stack solicitado.
- Trade-off: o plugin passa a manter cinco entradas relacionadas.
- Reversible: sim; elas podem ser extraídas em versão futura.

### DEC-002 — Ratchet como política padrão

- Decision: definir como tratar projetos existentes com dívida técnica.
- Options: limites globais imediatos; apenas relatório; zero regressão com redução progressiva.
- Choice: zero regressão no código novo e redução progressiva da baseline existente.
- Why: cria gates bloqueantes sem exigir uma correção total antes da adoção.
- Trade-off: a dívida anterior não desaparece imediatamente.
- Reversible: sim; os limiares globais podem ser elevados após estabilização.

### DEC-003 — Determinismo antes da quantidade de ferramentas

- Decision: definir o critério principal de recomendação.
- Options: cobertura máxima de scanners; conjunto mínimo reprodutível; escolha automática por
  popularidade.
- Choice: conjunto mínimo reprodutível, com versões e configurações fixadas.
- Why: o mesmo commit precisa produzir o mesmo veredito e os sinais precisam ser acionáveis.
- Trade-off: ferramentas remotas ou regras flutuantes ficam fora do caminho bloqueante.
- Reversible: sim; scanners adicionais podem entrar após calibração.

## Interfaces

- `plugins/pwdev-devops/skills/quality-gates/SKILL.md`: entrada genérica.
- `plugins/pwdev-devops/skills/quality-gates-php/SKILL.md`: entrada especializada.
- `plugins/pwdev-devops/skills/quality-gates-vue/SKILL.md`: especialização Vue.js.
- `plugins/pwdev-devops/skills/quality-gates-node/SKILL.md`: especialização Node.js.
- `plugins/pwdev-devops/skills/quality-gates-postgres/SKILL.md`: especialização PostgreSQL.
- `plugins/pwdev-devops/references/quality-gates-action-plan.md`: plano de adoção reutilizável.
- `plugins/pwdev-devops/README.md`: descoberta em inglês.
- `plugins/pwdev-devops/README.pt-BR.md`: descoberta em português.
- `plugins/pwdev-devops/.claude-plugin/plugin.json`: contagem e descrição das capacidades.

## Constraints

- Os nomes serão exatamente `quality-gates`, `quality-gates-php`, `quality-gates-vue`,
  `quality-gates-node` e `quality-gates-postgres`.
- As skills serão publicadas em `plugins/pwdev-devops/skills/`.
- O plano de ação será escrito em português e será aplicável por fases.
- A skill genérica não duplicará as matrizes tecnológicas das especializações.
- Nenhum gate recomendará configuração remota flutuante como fonte bloqueante.
- SonarQube será opcional e só poderá bloquear com versão, Quality Profile, Quality Gate e
  parâmetros de scanner controlados.
- Nenhuma baseline adicionará automaticamente novos problemas durante o CI.
- Nenhuma skill executará mutações externas, instalará dependências ou alterará pipelines sem
  autorização explícita.
- A descrição do plugin passará de 19 para 24 skills.

## Out of scope

- Implementar um pipeline concreto em uma aplicação consumidora.
- Instalar scanners ou adquirir licenças comerciais.
- Substituir as skills `automation-engineer` ou `devsecops`.
- Fixar versões de ferramentas que pertencem aos projetos consumidores.

## Acceptance criteria

- A skill genérica identifica stack, risco, baseline, orçamento de tempo e política de bloqueio
  antes de recomendar gates.
- A especialização PHP cobre PHP e Laravel e distingue SAST, SCA, análise estática, testes,
  cobertura, complexidade e estilo.
- A especialização Vue cobre Vue.js e TypeScript e distingue lint, type checking, testes,
  cobertura, complexidade, bundle e acessibilidade.
- A especialização Node cobre Node.js, JavaScript e TypeScript e distingue lint, type checking,
  testes, cobertura, complexidade, SAST, SCA e build.
- A especialização PostgreSQL cobre migrations, schema drift, constraints, índices, planos de
  execução e testes com banco efêmero.
- O plano de ação define fases, responsáveis, entradas, saídas, critérios de promoção, exceções
  e métricas de eficácia.
- A política padrão bloqueia regressões novas e usa ratchet para dívida existente.
- As versões, regras, imagens, lockfiles e fixtures que afetam o veredito são exigidas como
  entradas fixadas.
- SonarQube aparece no plano compartilhado e nas especializações aplicáveis como camada opcional
  com configuração reprodutível.
- As cinco skills passam no validador de skills usado pelo repositório.
- Os READMEs e o manifesto tornam as cinco skills descobríveis sem links quebrados.
- Os arquivos novos não contêm placeholders ou seções de scaffold vazias.

## Risks

- Limiares rígidos podem gerar rejeição ou falsos positivos; mitigação: baseline, ratchet e
  período de observação.
- A recomendação de ferramentas pode envelhecer; mitigação: separar princípios estáveis de
  exemplos substituíveis.
- A skill genérica pode se sobrepor a `automation-engineer`; mitigação: limitar seu escopo ao
  desenho, avaliação e governança dos quality gates.
- A especialização PostgreSQL pode se sobrepor a `postgres-dba`; mitigação: limitar seu escopo a
  verificações automatizadas de CI, sem diagnóstico ou operação do banco.
