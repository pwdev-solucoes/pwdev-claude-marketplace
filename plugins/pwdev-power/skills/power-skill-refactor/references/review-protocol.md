# Protocolo de três revisões

Cada rodada recebe a versão atual e o registro anterior, mas não deve aceitar uma mudança apenas
porque reduz texto. Classifique cada achado como `bloqueador`, `importante`, `opcional` ou `rejeitado`,
com evidência no arquivo. Corrija bloqueadores e importantes confirmados antes da rodada seguinte.
Qualquer mudança de requisito, contrato, escopo ou invariante exige parada e aprovação humana
explícita. Uma alteração apenas registrada não está autorizada.

## Rodada 1 — contrato e segurança

Verifique ativação, contra-ativação, escopo, entradas, saídas, segurança, privacidade, fallback,
honestidade, critérios de parada e autorização. Pergunte: alguma regra crítica foi perdida,
contradita ou enfraquecida? Resultado: lista de invariantes preservados e lacunas.

## Rodada 2 — seleção e disclosure

Verifique se a descrição roteia corretamente, se a raiz contém somente o mínimo operacional, se cada
referência tem um gatilho claro, se não há leitura global obrigatória e se modelos inferiores ainda
possuem microfluxos explícitos. Teste casos positivos e negativos. Resultado: tabela de roteamento e
casos com decisão esperada/observada.

## Rodada 3 — métricas e portabilidade

Recalcule as métricas em `metrics.md`; verifique frontmatter, links relativos, nomes de tools sem
invenção, compatibilidade entre runtimes e comandos de validação. Compare baseline e resultado.
Resultado: tabela antes/depois, limitações e decisão final.

## Registro por rodada

```text
Rodada: 1 | 2 | 3
Escopo revisado:
Evidências:
Achados:
Decisões:
Correções aplicadas:
Pendências:
Veredito: aprovado | aprovado com ressalvas | bloqueado
```

Uma revisão não deve esconder uma pendência: preserve-a no registro e bloqueie a conclusão se ela
ameaçar um invariante ou critério de aceitação. Se uma correção for aplicada, reexecute a rodada ou
as verificações afetadas e registre a revalidação antes de avançar.

## Casos mínimos de avaliação

Registre sempre resultado esperado e observado:

| Classe | Exemplo | Decisão esperada |
|---|---|---|
| Positivo | skill longa e repetitiva | ativar e medir baseline |
| Positivo | detalhes condicionais extraíveis | ativar e propor referências |
| Positivo | skill com fallback inconsistente | ativar e preservar honestidade |
| Negativo | auditoria sem alteração | não ativar esta skill |
| Negativo | mudança de requisito | parar e pedir aprovação |
| Negativo | criação de skill nova | não usar refatoração de skill existente |
| Indisponibilidade | tokenizer/tool ausente | registrar limitação, sem inventar resultado |
| Saída inválida | referência quebrada ou frontmatter inválido | bloquear conclusão |

## Verificação reproduzível mínima

Registre no `review-record.md` os comandos efetivamente usados e seus resultados. Quando o projeto
oferecer validadores próprios, prefira-os. Na ausência deles, execute pelo menos:

1. leitura do frontmatter e resolução de cada referência relativa;
2. busca por caminhos absolutos, segredos e symlinks fora do escopo;
3. teste ou validador disponível para a skill/runtime;
4. inspeção de diff e verificação de whitespace;
5. reexecução das verificações afetadas após cada correção.

Não substitua a saída real por uma afirmação de que o comando "deveria passar". Se um runtime não
for exercitado, registre-o como não testado.
