---
name: quality-gates-php
description: >
  Quality gates determinísticos para PHP e Laravel. Use quando o usuário pedir
  "quality gate PHP", "quality gate Laravel", "PHPStan", "Larastan", "Pest",
  "PHPUnit", "PHPMD", "Composer Audit", cobertura PHP ou baseline PHP.
metadata: { version: 1.0.0 }
---

# Quality Gates para PHP e Laravel

Você projeta uma política de qualidade reproduzível para aplicações PHP e Laravel. O padrão é
bloquear regressões no código alterado e reduzir a dívida existente por ratchet, sem esconder a
baseline nem ampliá-la automaticamente.

## Levantamento obrigatório

Antes de recomendar um gate, registre:

1. versões de PHP, framework, Composer e ferramentas, todas fixadas no lockfile ou na imagem;
2. comandos existentes, extensões PHP, sistema operacional e serviços usados nos testes;
3. caminhos de código novo e legado, criticidade, baseline atual e orçamento de feedback;
4. configurações versionadas, conjuntos de regras, fixtures, seeds e variáveis não secretas;
5. dono, saída esperada, condição de falha e procedimento de exceção de cada gate.

Se faltarem dados, proponha primeiro uma execução observacional. Não invente compatibilidade,
comandos do projeto ou limites globais para substituir medições.

## Matriz de ferramentas e contratos

| Categoria | Verificador preferencial | Entradas determinísticas | Saída e regra bloqueante |
|---|---|---|---|
| Análise estática | PHPStan; Larastan quando houver Laravel | `composer.lock`, versão do PHP, extensões, `phpstan.neon*`, stubs e baseline versionada | Saída estruturada do analisador; bloqueia erro novo e aumento da contagem por identificador e caminho na baseline |
| Testes | Pest ou PHPUnit | lockfile, `phpunit.xml`, seed, relógio/fuso fixados, fixtures e serviços efêmeros por imagem/digest | código de saída e relatório JUnit; bloqueia teste falho, erro ou execução incompleta, separando falha de infraestrutura |
| Cobertura | cobertura do Pest/PHPUnit via PCOV ou Xdebug | mesmo conjunto de testes, driver e versão fixados; relatório Cobertura/HTML versionado como evidência | relatório de cobertura; bloqueia valor inferior a **80% nas linhas alteradas**; cobertura global existente não pode cair mais que **0,0 ponto percentual** |
| SAST | Semgrep ou equivalente local | binário fixado, regras locais versionadas, exclusões revisadas e escopo explícito | SARIF/JSON; bloqueia achado novo de severidade `ERROR` e aumento da baseline por regra, impressão digital e caminho |
| SCA | Composer Audit | `composer.lock`, versão do Composer e snapshot versionado da base de advisories | JSON; bloqueia advisory novo no snapshot controlado; consulta a base remota corrente é apenas informativa |
| Complexidade | PHPMD | versão fixada, ruleset XML versionado, caminhos e exclusões explícitos | XML/texto; bloqueia nova violação e aumento da baseline por regra e símbolo; para código novo, padrão inicial é complexidade ciclomática **≤ 10 por método** |
| Estilo | PHP-CS-Fixer ou PHP_CodeSniffer em modo de verificação | versão fixada e configuração versionada | diff ou saída estruturada; bloqueia arquivo alterado fora do padrão, sem reescrever código no gate |
| Laravel | verificações de boot/configuração, rotas, container e migrations em banco efêmero | `artisan`, caches recriados no job, `.env.testing` sem segredo, fixtures e imagem do banco fixadas | código de saída e logs; bloqueia falha de boot, resolução do container, cache de configuração/rotas ou migration do zero |

Ferramentas equivalentes são aceitáveis somente quando preservam o mesmo contrato de entradas,
saída analisável e condição de falha. Nunca execute correção automática no gate bloqueante.

## Política de bloqueio e ratchet

Adote estes padrões iniciais, sujeitos a revisão após a fase observacional:

- código novo: zero erro de análise estática, zero teste falho, zero achado SAST `ERROR`, zero
  advisory novo controlado e zero violação nova de complexidade ou estilo;
- cobertura: pelo menos **80% das linhas alteradas** e queda global máxima de **0,0 ponto
  percentual**;
- complexidade: métodos novos ou alterados com complexidade ciclomática **≤ 10**;
- dívida existente: baseline versionada por identificador estável, regra, símbolo/caminho e
  quantidade; qualquer aumento bloqueia;
- ratchet: a cada ciclo aprovado, remova da baseline os itens corrigidos e reduza em pelo menos
  **10%** a contagem da categoria priorizada; arredonde a meta para cima e nunca abaixo de
  **1 item** enquanto houver dívida;
- o CI pode validar ou reduzir a baseline, mas nunca adicionar novos problemas a ela. Toda mudança
  de patamar exige diff revisado, responsável e justificativa.

Se o analisador não oferecer identidade estável para comparar achados, mantenha-o observacional
até existir normalização versionada. Tempo de runner compartilhado e sinal remoto flutuante não
são fontes bloqueantes.

## Verificações específicas de Laravel

Em projeto Laravel, avalie também:

- boot da aplicação nos ambientes de teste suportados e resolução de bindings críticos;
- criação dos caches de configuração e rotas em ambiente descartável, sem publicar os artefatos
  como configuração de produção;
- migrations do zero e rollback/forward quando o projeto declarar essa compatibilidade, sempre em
  banco efêmero exclusivo;
- testes de autorização para policies/gates e testes de arquitetura para limites entre camadas;
- filas, eventos e scheduler com fakes ou serviços efêmeros e expectativas explícitas;
- proibição de `env()` fora dos arquivos de configuração por regra estática versionada.

Não rode migrations, limpezas de cache, filas ou qualquer comando mutável em produção como parte
da avaliação. Falha na criação do ambiente é falha de infraestrutura e deve ser distinguida de
regressão do produto, sem converter ausência de teste em aprovação.

## SonarQube opcional

SonarQube pode agregar cobertura, duplicação e achados, mas não substitui os verificadores locais.
Só pode bloquear quando versão do servidor, versão do scanner, Quality Profile, Quality Gate e
todos os parâmetros de scanner que alteram o resultado estiverem controlados. Caso contrário,
publique o resultado apenas como informativo.

## Aplicação por fases

Use o [plano de ação compartilhado](../../references/quality-gates-action-plan.md): inventarie e
contrate os gates na Fase 0, calibre ferramentas e baseline na Fase 1, bloqueie regressões na Fase
2 e reduza a baseline por ratchet na Fase 3. Registre responsáveis, entradas, saídas, evidências,
critérios de promoção e exceções em cada fase.

## Entrega

Produza em português:

- inventário por categoria, ferramenta escolhida, versão/configuração e justificativa;
- tabela com comando proposto, entradas fixadas, saída, condição de bloqueio, tempo limite e dono;
- baseline e identificadores usados para comparar regressões;
- limiares adotados, passos do ratchet e critérios de promoção;
- tratamento separado para falha do produto e falha da infraestrutura;
- exceções com escopo, risco, aprovador, dono e validade;
- comandos ou diffs de instalação/pipeline apresentados apenas como proposta pendente de aprovação.

## Limites de autorização

- Não instala nem atualiza dependências sem autorização explícita.
- Não altera pipeline, configurações do projeto ou baselines sem autorização explícita.
- Não executa mutações externas nem comandos contra produção.
- Antes de propor uma ação mutável, informe comando ou diff, efeito, ambiente, alvo, reversão e
  blast radius, e aguarde autorização.
- Não usa advisories remotos correntes, regras remotas flutuantes ou configuração SonarQube não
  controlada como fonte bloqueante.

## Skills relacionadas

`quality-gates` · `automation-engineer` · `devsecops` · `laravel-platform`
