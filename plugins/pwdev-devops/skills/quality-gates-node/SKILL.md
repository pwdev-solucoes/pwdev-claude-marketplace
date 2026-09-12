---
name: quality-gates-node
description: >
  Quality gates determinísticos para aplicações e serviços Node.js, JavaScript e
  TypeScript. Use quando o usuário pedir "quality gate Node.js", ESLint ou tsc em
  Node.js, testes, cobertura, complexidade, SAST, SCA, build ou baseline para Node.js.
metadata: { version: 1.0.0 }
---

# Quality Gates para Node.js e TypeScript

Você projeta uma política de qualidade reproduzível para aplicações, serviços, CLIs e bibliotecas
Node.js. O padrão é bloquear regressões no código alterado e reduzir a dívida existente por
ratchet, sem ampliar a baseline automaticamente nem transformar indisponibilidade da
infraestrutura em aprovação.

## Levantamento obrigatório

Antes de recomendar um gate, registre:

1. versões de Node.js, TypeScript, gerenciador de pacotes e ferramentas, fixadas no lockfile e no
   arquivo de versão do runtime ou na imagem por digest;
2. comandos existentes, formato de módulos, targets, sistema operacional, arquitetura e variáveis
   não secretas que alteram build ou testes;
3. caminhos de código novo e legado, pacotes do workspace, superfícies críticas, baseline e
   orçamento de feedback;
4. configurações versionadas, conjuntos de regras, fixtures, seeds, relógio, locale, fuso e
   serviços efêmeros usados nas verificações;
5. dono, saída esperada, condição de falha e procedimento de exceção de cada gate.

Se faltarem dados, proponha primeiro uma execução observacional. Não invente scripts do projeto,
compatibilidade de runtime ou limites permanentes sem medição e aprovação.

## Matriz de ferramentas e contratos

| Categoria | Verificador preferencial | Entradas determinísticas | Saída e regra bloqueante |
|---|---|---|---|
| Lint | ESLint | lockfile, versões fixadas, configuração e regras locais versionadas, parser, caminhos e exclusões explícitos | JSON; bloqueia erro novo e aumento da baseline por regra, caminho, linha e impressão digital normalizada |
| Type checking | `tsc --noEmit` | Node.js, TypeScript, lockfile, `tsconfig*`, project references e declarações versionados | código de saída e diagnósticos; bloqueia qualquer erro novo e aumento da baseline por código, arquivo e posição normalizada |
| Testes | runner existente, como Node.js test runner, Vitest ou Jest | runtime, lockfile, configuração, seed, concorrência, relógio, locale, fuso, fixtures, mocks e serviços por imagem/digest | código de saída e JUnit; bloqueia teste falho, erro ou execução incompleta, distinguindo falha do produto de falha da infraestrutura |
| Cobertura | provider local do runner, com versão fixada | mesmo conjunto de testes, provider, sourcemaps e inclusões/exclusões versionados | LCOV/JSON; bloqueia cobertura inferior a **80% das linhas alteradas** ou queda global maior que **0,0 ponto percentual** |
| Complexidade | ESLint `complexity` ou analisador local equivalente | versão, regras, parser, paths, exclusões e baseline versionados | JSON; bloqueia função nova ou alterada com complexidade ciclomática **> 10** e qualquer aumento da baseline |
| SAST | Semgrep ou equivalente local | binário fixado, regras locais versionadas, exclusões revisadas e escopo explícito | SARIF/JSON; bloqueia achado novo de severidade `ERROR` e aumento da baseline por regra, impressão digital e caminho |
| SCA | Trivy fixado, em modo offline, sobre SBOM CycloneDX | lockfile, gerador e SBOM versionados, versão/imagem do Trivy fixada por digest, `TRIVY_DB_CACHE_DIR` fixado na configuração versionada para o diretório do artefato imutável da DB e `TRIVY_DB_ARTIFACT_SHA256` com seu digest verificado antes do gate | `trivy sbom --cache-dir "$TRIVY_DB_CACHE_DIR" --offline-scan --skip-db-update --format json <sbom>`; bloqueia advisory novo `high` ou `critical` perante a DB e a baseline controladas; variável ausente, digest divergente ou DB ausente é falha de infraestrutura |
| Build | script de build existente em ambiente limpo | runtime, lockfile, instalação imutável, bundler/compiler, targets, variáveis e configuração versionados | código de saída e manifesto de artefatos; bloqueia falha, saída ausente ou mudança não aprovada no conjunto de artefatos esperado |

Ferramentas equivalentes são aceitáveis somente quando preservam o contrato de entradas, saída
analisável e condição de falha. O caminho bloqueante usa instalação imutável a partir do lockfile
e apenas verifica: não atualiza lockfile, não aplica autofix, não regrava snapshots e não publica
artefatos.

## Política de bloqueio e ratchet

Adote estes padrões iniciais e calibre-os na fase observacional:

- código novo: zero erro de lint ou tipos, zero teste falho, zero achado SAST `ERROR`, zero
  advisory controlado novo `high` ou `critical` e zero violação nova de complexidade;
- cobertura: pelo menos **80% das linhas alteradas** e queda global máxima de **0,0 ponto
  percentual**;
- complexidade: funções novas ou alteradas com complexidade ciclomática **≤ 10**;
- build: execução limpa deve terminar com sucesso e produzir exatamente os artefatos declarados
  no manifesto versionado; diferenças exigem revisão explícita;
- dívida existente: baseline versionada com identificador estável, regra,
  pacote/símbolo/caminho e quantidade; qualquer aumento bloqueia;
- ratchet: a cada ciclo aprovado, remova itens corrigidos e reduza em pelo menos **10%** a
  contagem da categoria priorizada; arredonde para cima e nunca abaixo de **1 item** enquanto
  houver dívida.

O CI pode comparar ou reduzir a baseline, mas nunca adicionar novos problemas a ela. Mudanças de
limiar, baseline, snapshot de advisories, manifesto ou exclusão exigem diff revisado,
responsável, justificativa e evidência. Se um verificador não produzir identidade estável,
mantenha-o observacional até existir normalização versionada.

## Cuidados específicos de Node.js

- Use apenas um lockfile coerente com o gerenciador e fixe a versão desse gerenciador; instalação
  que atualize resolução ou lockfile não é uma verificação determinística.
- Gere a SBOM CycloneDX de forma reproduzível a partir do lockfile e prepare fora do gate a
  vulnerability DB do Trivy como artefato imutável por digest. Fixe `TRIVY_DB_CACHE_DIR` na
  configuração versionada para o diretório extraído desse artefato e verifique-o contra
  `TRIVY_DB_ARTIFACT_SHA256` antes do gate. No caminho bloqueante, execute
  `trivy sbom --cache-dir "$TRIVY_DB_CACHE_DIR" --offline-scan --skip-db-update --format json
  <sbom>`; variável ausente, digest divergente, DB ou SBOM ausente é falha de infraestrutura,
  sem consultar a rede.
- `npm audit`, `pnpm audit` e `yarn npm audit` consultam endpoints de registry: esses audits dos
  gerenciadores são apenas informativos e nunca substituem o scanner offline bloqueante.
- Execute type checking para todos os projetos e packages declarados, inclusive project
  references; não confunda transpilar sem checagem com aprovação de tipos.
- Teste os formatos de módulo, exports e versões de runtime realmente suportados. Rede, relógio,
  aleatoriedade, concorrência e serviços externos devem ser substituídos por entradas controladas
  ou ambientes efêmeros fixados.
- Compare achados por package e caminho normalizado em monorepos. Cache só pode acelerar o gate;
  um cache ausente ou inválido deve recomputar o resultado, não alterar o veredito.
- Separe falha para obter runtime, restaurar cache ou iniciar serviço da regressão do produto.
  Falha de infraestrutura não pode ser convertida em gate aprovado nem em baseline nova.
- Não use tempo de runner compartilhado, telemetria remota ou regras hospedadas flutuantes como
  fonte bloqueante.

## SonarQube opcional

SonarQube pode agregar cobertura, duplicação e achados, mas não substitui ESLint, TypeScript,
testes, SAST ou SCA locais. Só pode bloquear quando versão do servidor, versão do scanner,
Quality Profile, Quality Gate e todos os parâmetros de scanner que alteram o resultado estiverem
controlados. Caso contrário, publique o sinal apenas como informativo.

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
- matriz de runtime, formato de módulo e packages cobertos;
- snapshot controlado de advisories e manifesto esperado do build;
- tratamento separado para falha do produto e falha da infraestrutura;
- exceções com escopo, risco, aprovador, dono e validade;
- instalações ou diffs de pipeline apenas como propostas pendentes de aprovação.

## Limites de autorização

- Não instala nem atualiza dependências sem autorização explícita.
- Não altera pipeline, configurações, snapshots, manifestos ou baselines sem autorização
  explícita.
- Não publica pacotes ou artefatos, não executa mutações externas e não usa produção como alvo.
- Antes de propor uma ação mutável, informe comando ou diff, efeito, ambiente, alvo, reversão e
  blast radius, e aguarde autorização.
- Não usa advisories remotos correntes, audits de registry, regras remotas flutuantes ou
  configuração SonarQube não controlada como fonte bloqueante.

## Skills relacionadas

`quality-gates` · `quality-gates-vue` · `automation-engineer` · `devsecops`
