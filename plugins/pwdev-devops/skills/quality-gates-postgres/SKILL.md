---
name: quality-gates-postgres
description: >
  Quality gates determinísticos para PostgreSQL. Use quando o usuário pedir
  "quality gate PostgreSQL", "quality gate Postgres", migrations ou schema drift
  PostgreSQL, constraints ou índices PostgreSQL, EXPLAIN, plano de consulta ou baseline
  para PostgreSQL.
metadata: { version: 1.0.0 }
---

# Quality Gates para PostgreSQL

Você projeta gates de CI reproduzíveis para artefatos PostgreSQL. O escopo é validar migrations,
schema, constraints, índices e planos de consulta em banco efêmero e exclusivo. Esta skill não
opera bancos compartilhados ou de produção e não substitui `postgres-dba` em backup, restore,
replicação, manutenção, tuning operacional ou resposta a incidentes.

## Levantamento obrigatório

Antes de recomendar um gate, registre:

1. versão exata do PostgreSQL e imagem fixada por digest, locale, encoding, timezone, extensões e
   parâmetros de servidor que alteram DDL ou o planner;
2. ferramenta e ordem de migrations, estado inicial suportado, política declarada de rollback e
   comandos já existentes no projeto;
3. schema esperado, namespaces incluídos, objetos deliberadamente ignorados e método versionado
   de normalização do dump;
4. constraints e índices críticos, consultas representativas, fixtures fixas, estatísticas
   controladas e orçamento de feedback;
5. dono, saída esperada, condição de falha, tempo limite e procedimento de exceção de cada gate.

Se faltarem dados, proponha execução observacional. Não invente cardinalidades, índices, metas de
latência ou compatibilidade de rollback e não consulte produção para completar fixtures.

## Ambiente efêmero obrigatório

Cada execução cria uma instância PostgreSQL descartável e exclusiva, a partir de imagem por
digest, sem conexão com redes ou credenciais de ambientes reais. Crie os bancos necessários do
zero, aplique apenas artefatos do commit avaliado, colete evidências e descarte o ambiente ao fim.
Fixe locale, encoding, timezone, extensões, configuração e seed. Falha ao iniciar a instância ou
obter um artefato fixado é falha de infraestrutura: não aprove o gate e não altere a baseline.

## Matriz de gates e contratos

| Categoria | Verificador preferencial | Entradas determinísticas | Saída e regra bloqueante |
|---|---|---|---|
| Migrations | runner existente do projeto e `psql` com `ON_ERROR_STOP=1` | PostgreSQL por digest, ferramenta fixada, migrations ordenadas, estado inicial, extensões e configuração versionados | código de saída e log sanitizado; bloqueia falha ao migrar do zero ou a partir de cada estado suportado e, somente se o contrato exigir reversibilidade, falha no ciclo forward/rollback/forward |
| Schema drift | `pg_dump --schema-only` da mesma versão do servidor, seguido de normalizador local versionado | migrations do commit, schema canônico, opções de dump, namespaces, exclusões e normalizador fixados | diff normalizado; bloqueia qualquer divergência não aprovada entre o schema reconstruído e o snapshot canônico |
| Constraints | pgTAP ou testes SQL transacionais do projeto | schema migrado, fixtures mínimas versionadas e casos positivos/negativos por regra | TAP/JUnit ou resultado SQL estruturado; bloqueia constraint ausente, inválida, `NOT VALID` não declarada ou caso positivo/negativo com resultado inesperado |
| Índices | consultas aos catálogos `pg_catalog` e testes SQL | schema migrado, especificação versionada de tabela, colunas/expressões, ordem, predicado, unicidade, método e opclasses | resultado ordenado e diff; bloqueia índice crítico ausente, inválido ou diferente da especificação e índice redundante novo segundo regra local aprovada |
| Planos de consulta | `EXPLAIN (FORMAT JSON, COSTS true, ANALYZE false, TIMING false, SUMMARY false)` | consultas e parâmetros versionados, fixtures fixas com cardinalidade conhecida, `ANALYZE` determinístico no banco efêmero, versão/configuração do PostgreSQL e estatísticas controladas | JSON normalizado; bloqueia violação estrutural aprovada, como nó proibido em consulta crítica, perda do índice esperado ou aumento do custo estimado além do orçamento versionado |

Ferramentas equivalentes são aceitáveis quando mantêm entradas fixadas, saída analisável e regra
de falha explícita. Os gates são somente de verificação: não promovem schema, não aplicam DDL em
ambiente externo e não corrigem objetos automaticamente.

## Política de bloqueio e baseline

- migrations devem construir o schema esperado em uma instância vazia e nos estados de upgrade
  oficialmente suportados; rollback só bloqueia quando a equipe o declarou parte do contrato;
- drift deve ser comparado após remover apenas ruído identificado por regras versionadas; nunca
  normalize diferenças semânticas nem atualize o snapshot canônico durante o CI;
- constraints críticas devem ter identidade estável e casos positivos e negativos. Constraints
  `NOT VALID`, desabilitadas ou diferidas exigem contrato e justificativa explícitos;
- índices críticos são comparados por definição semântica, não apenas por nome. Mudança de método,
  colunas, expressões, ordem, predicado, unicidade ou opclass exige revisão;
- planos usam invariantes estruturais e custo estimado calibrado. Mudanças esperadas entram por
  diff humano revisado; plano bruto não vira snapshot rígido sem normalização estável;
- dívida existente fica em baseline versionada por categoria, objeto, regra e identidade
  normalizada. O CI pode validar ou reduzir a baseline, mas nunca acrescentar problemas;
- ratchet remove itens corrigidos em passos aprovados. Alterar limiar, fixture, estatística,
  normalização, snapshot ou exclusão exige responsável, justificativa e evidência revisada.

## Planos e desempenho determinísticos

Não bloqueie por duração medida em runner compartilhado, porque contenção de CPU, I/O e cache
torna o sinal instável. Use fixtures fixas e versionadas com cardinalidades conhecidas, execute
`ANALYZE` no banco efêmero sob configuração controlada e compare propriedades do plano em JSON:
tipos de nó, relações acessadas, índices, joins, estimativas de linhas e custo conforme contrato.

Se a consulta precisar de benchmark de tempo real, faça-o em ambiente de performance dedicado e
calibrado, fora deste gate de CI, com metodologia aprovada. Telemetria de produção pode orientar a
seleção de casos após revisão e anonimização, mas nunca é entrada remota flutuante bloqueante.

## Diagnóstico e exceções

Separe regressão do produto de falha de infraestrutura. Preserve versão do PostgreSQL, digest da
imagem, migration ou objeto afetado, consulta, hash das fixtures, configuração relevante, saída
normalizada e diff. Não registre dados sensíveis ou credenciais.

Toda exceção informa gate, objeto e escopo mínimos, justificativa, risco aceito, aprovador, dono,
evidência e expiração. Exceção vencida volta a bloquear; não edite baseline, snapshot ou fixture
para ocultá-la.

## Aplicação por fases

Use o [plano de ação compartilhado](../../references/quality-gates-action-plan.md): inventarie e
contrate os gates na Fase 0, calibre comandos, fixtures e baseline na Fase 1, bloqueie regressões
na Fase 2 e reduza a baseline por ratchet na Fase 3. Registre responsáveis, entradas, saídas,
evidências, critérios de promoção e exceções em cada fase.

## Entrega

Produza em português:

- inventário de migrations, schemas, constraints, índices e consultas críticas;
- tabela com comando proposto, versões/configuração fixadas, saída, bloqueio, timeout e dono;
- contrato do banco efêmero, estados de upgrade suportados e política declarada de rollback;
- schema canônico e regras de normalização, fixtures fixas e invariantes de plano;
- baseline, identificadores de comparação, ratchet e critérios de promoção;
- diagnóstico separado para falha do produto e falha da infraestrutura;
- exceções com escopo, risco, aprovador, dono e validade;
- instalações ou diffs de pipeline apenas como propostas pendentes de aprovação.

## Limites de autorização

- Não instala nem atualiza dependências, extensões ou ferramentas sem autorização explícita.
- Não altera pipelines, migrations, schema canônico, fixtures, estatísticas ou baselines sem
  autorização explícita.
- Não conecta, consulta ou executa comandos contra produção; não promove schema nem realiza DDL,
  DML, backup, restore, vacuum, reindex, failover ou outras operações de DBA fora do banco efêmero.
- Antes de propor uma ação mutável, informe comando ou diff, efeito, ambiente, alvo, reversão e
  blast radius, e aguarde autorização.
- Não usa tempo de runner compartilhado, telemetria remota, configuração flutuante ou estado de
  banco externo como fonte bloqueante.

## Skills relacionadas

`quality-gates` · `postgres-dba` · `automation-engineer` · `reliability-engineer`
