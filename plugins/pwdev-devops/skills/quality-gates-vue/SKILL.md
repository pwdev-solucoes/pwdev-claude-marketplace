---
name: quality-gates-vue
description: >
  Quality gates determinísticos para Vue.js, JavaScript e TypeScript. Use quando o
  usuário pedir "quality gate Vue", "quality gate frontend", "ESLint", "vue-tsc",
  "Vitest", cobertura, complexidade, bundle, acessibilidade ou baseline em Vue.js.
metadata: { version: 1.0.0 }
---

# Quality Gates para Vue.js e TypeScript

Você projeta uma política de qualidade reproduzível para frontends Vue.js. O padrão é
bloquear regressões no código alterado e reduzir a dívida existente por ratchet, sem ampliar a
baseline automaticamente nem confundir indisponibilidade do ambiente com aprovação.

## Levantamento obrigatório

Antes de recomendar um gate, registre:

1. versões de Node.js, Vue, TypeScript, gerenciador e ferramentas, fixadas no lockfile e no
   arquivo de versão do runtime ou na imagem por digest;
2. comandos existentes, modo de build, navegadores suportados, sistema operacional e variáveis
   não secretas que alteram compilação ou testes;
3. caminhos de código novo e legado, rotas e componentes críticos, baseline e orçamento de
   feedback;
4. configurações versionadas, conjuntos de regras, fixtures, seeds, viewport, locale, fuso e
   fontes usados nas medições;
5. dono, saída esperada, condição de falha e procedimento de exceção de cada gate.

Se faltarem dados, proponha primeiro uma execução observacional. Não invente comandos do projeto
nem converta limites iniciais em metas permanentes sem medição e aprovação.

## Matriz de ferramentas e contratos

| Categoria | Verificador preferencial | Entradas determinísticas | Saída e regra bloqueante |
|---|---|---|---|
| Lint | ESLint com `eslint-plugin-vue` | lockfile, versões fixadas, configuração e regras locais versionadas, caminhos e exclusões explícitos | JSON; bloqueia erro novo e aumento da baseline por regra, caminho, linha e impressão digital normalizada |
| Type checking | `vue-tsc --noEmit` | lockfile, Node.js, TypeScript, Vue, `vue-tsc`, `tsconfig*` e declarações versionados | código de saída e diagnósticos; bloqueia qualquer erro novo e aumento da baseline por código, arquivo e posição normalizada |
| Testes | Vitest | lockfile, configuração, ambiente DOM, seed, relógio, locale, fuso, fixtures e mocks versionados | código de saída e JUnit; bloqueia teste falho, erro ou execução incompleta, distinguindo falha do produto de falha da infraestrutura |
| Cobertura | Vitest Coverage com provider fixado | mesmo conjunto de testes, provider e versão fixados, sourcemaps e inclusões/exclusões versionados | LCOV/JSON; bloqueia cobertura inferior a **80% das linhas alteradas** ou queda global maior que **0,0 ponto percentual** |
| Complexidade | ESLint `complexity` ou analisador local equivalente | versão e regras fixadas, parser, caminhos, exclusões e baseline versionados | JSON; bloqueia função nova ou alterada com complexidade ciclomática **> 10** e qualquer aumento da baseline |
| Bundle | build do projeto mais analisador local de artefatos | lockfile, runtime, bundler, modo, variáveis, targets, sourcemaps e algoritmo de compressão fixados | manifesto com bytes brutos e gzip por entry/chunk; bloqueia entry inicial acima de **200 KiB gzip** ou crescimento acima de **0 bytes** perante o orçamento versionado |
| Acessibilidade | axe-core em testes de componente ou navegador fixado | versões, regras locais, navegador/imagem por digest, viewport, locale, fontes, fixtures, rotas e estados versionados | JSON; bloqueia violação nova `serious` ou `critical` por regra, alvo e contexto e qualquer aumento da baseline |

Ferramentas equivalentes são aceitáveis somente quando preservam o contrato de entradas, saída
analisável e condição de falha. O gate apenas verifica: não use autofix, atualização de snapshot
ou reescrita de artefato como parte do caminho bloqueante.

## Política de bloqueio e ratchet

Adote estes padrões iniciais e calibre-os na fase observacional:

- código novo: zero erro de lint ou tipos, zero teste falho e zero violação nova de
  acessibilidade `serious` ou `critical`;
- cobertura: pelo menos **80% das linhas alteradas** e queda global máxima de **0,0 ponto
  percentual**;
- complexidade: funções novas ou alteradas com complexidade ciclomática **≤ 10**;
- bundle: cada entry inicial deve ter no máximo **200 KiB gzip** e nenhum entry/chunk pode
  crescer mais que **0 bytes** contra o orçamento versionado; uma exceção aprovada atualiza o
  orçamento em diff revisado, nunca durante o CI;
- dívida existente: baseline versionada com identificador estável, regra, alvo/símbolo/caminho
  e quantidade; qualquer aumento bloqueia;
- ratchet: a cada ciclo aprovado, remova itens corrigidos e reduza em pelo menos **10%** a
  contagem da categoria priorizada; arredonde para cima e nunca abaixo de **1 item** enquanto
  houver dívida.

O CI pode comparar ou reduzir a baseline, mas nunca adicionar novos problemas a ela. Mudanças
de limiar, baseline, orçamento de bundle ou exclusão exigem diff revisado, responsável,
justificativa e evidência. Se um verificador não produzir identidade estável, mantenha-o
observacional até existir normalização versionada.

## Cuidados específicos de Vue

- Execute type checking de templates `.vue`, não apenas `tsc` sobre arquivos TypeScript.
- Teste componentes com plugins, router, store, traduções e estados explicitamente montados;
  não dependa da ordem da suíte nem de rede externa.
- Meça bundle sempre no mesmo modo e compare entradas pelo identificador estável do manifesto,
  não por nomes com hash; registre separadamente bytes brutos e gzip.
- Cubra acessibilidade nos estados e rotas críticos com DOM renderizado. Screenshot, auditoria
  remota flutuante e tempo de runner compartilhado podem informar, mas não bloquear.
- Classifique falha para iniciar navegador, instalar binário ou obter serviço como infraestrutura;
  ela não pode ser convertida em gate aprovado nem em baseline nova.

## SonarQube opcional

SonarQube pode agregar cobertura, duplicação e achados, mas não substitui os verificadores
locais. Só pode bloquear quando versão do servidor, versão do scanner, Quality Profile, Quality
Gate e todos os parâmetros de scanner que alteram o resultado estiverem controlados. Caso
contrário, publique o sinal apenas como informativo.

## Aplicação por fases

Use o [plano de ação compartilhado](../../references/quality-gates-action-plan.md): inventarie e
contrate os gates na Fase 0, calibre ferramentas e baseline na Fase 1, bloqueie regressões na
Fase 2 e reduza a baseline por ratchet na Fase 3. Registre responsáveis, entradas, saídas,
evidências, critérios de promoção e exceções em cada fase.

## Entrega

Produza em português:

- inventário por categoria, ferramenta, versão/configuração e justificativa;
- tabela com comando proposto, entradas fixadas, saída, bloqueio, tempo limite e dono;
- baseline, identificadores de comparação, limiares e passos do ratchet;
- estados, rotas e viewports cobertos por testes de acessibilidade;
- orçamento de bundle por entry/chunk, método de compressão e diff em bytes;
- tratamento separado para falha do produto e falha da infraestrutura;
- exceções com escopo, risco, aprovador, dono e validade;
- instalações ou diffs de pipeline apenas como propostas pendentes de aprovação.

## Limites de autorização

- Não instala nem atualiza dependências ou navegadores sem autorização explícita.
- Não altera pipeline, configurações, snapshots, budgets ou baselines sem autorização
  explícita.
- Não executa mutações externas nem comandos contra produção.
- Antes de propor uma ação mutável, informe comando ou diff, efeito, ambiente, alvo, reversão e
  blast radius, e aguarde autorização.
- Não usa regras remotas flutuantes, auditorias hospedadas ou configuração SonarQube não
  controlada como fonte bloqueante.

## Skills relacionadas

`quality-gates` · `quality-gates-node` · `automation-engineer` · `devsecops`
