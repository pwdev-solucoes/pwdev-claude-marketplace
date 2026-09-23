# Registro de refatoração de skill

Skill avaliada:
Versão/commit baseline:
Versão/commit refatorada:
Escopo aprovado:
Data e ambiente:
Avaliador/contexto de cada rodada:
Runtimes efetivamente testados:
Tokenizer e versão, ou método de aproximação:

## Evidência

Para cada verificação, informe comando, saída resumida e caminho do artefato. Não use este registro
para reproduzir segredos; substitua qualquer valor sensível por `[REDACTED]`. `não medido` exige causa
e bloqueia métricas críticas, salvo exceção aprovada.

## Casos

| ID | Classe/origem | Resultado esperado | Resultado observado | Evidência |
|---|---|---|---|---|
| P1 | skill longa/repetitiva | ativar e medir baseline | | |
| P2 | detalhes condicionais extraíveis | ativar e propor referências | | |
| P3 | fallback inconsistente | ativar e preservar honestidade | | |
| N1 | auditoria sem alteração | não ativar | | |
| N2 | mudança de requisito | parar e pedir aprovação | | |
| N3 | criação de skill nova | não usar refatoração existente | | |
| T1 | tool/tokenizer indisponível | registrar limitação | | |
| I1 | saída inválida | bloquear conclusão | | |

## Invariantes

| Invariante | Evidência baseline | Evidência depois | Estado |
|---|---|---|---|
| Ativação e contra-ativação | | | preservado/regressão |
| Segurança e privacidade | | | preservado/regressão |
| Fallback honesto | | | preservado/regressão |
| Verificação e honestidade | | | preservado/regressão |
| Portabilidade/runtime | | | preservado/regressão |

## Três rodadas

### Rodada 1 — contrato e segurança

Cole o registro de `review-protocol.md`, incluindo correções e revalidação.

### Rodada 2 — seleção e disclosure

Cole o registro de `review-protocol.md`, incluindo casos esperados/observados.

### Rodada 3 — métricas e portabilidade

Cole o registro de `review-protocol.md`, incluindo comandos e runtimes efetivamente testados.

## Métricas

Cole a tabela de `metrics.md`, sempre com método, denominador e limitações. Se `N = 0`, use
`não aplicável` ou `não medido`, explique a causa e não converta para porcentagem.

## Verificação final

- [ ] frontmatter válido;
- [ ] referências existentes e roteadas;
- [ ] testes/casos executados;
- [ ] diff revisado;
- [ ] falhas preexistentes separadas de regressões;
- [ ] nenhum segredo ou dado privado incluído;
- [ ] arquivos alterados dentro do escopo;
- [ ] correções revalidadas;
- [ ] nenhuma mudança de requisito sem aprovação explícita.

Veredito final:
Limitações:
Exceções aprovadas:
Sem commit/push até autorização explícita.
