# Métricas simples de refatoração

Use o mesmo arquivo, conjunto de referências e casos antes/depois. Registre método e data no relatório; não compare números produzidos por métodos diferentes.

| Métrica | Como medir | Direção desejada |
|---|---|---|
| Descrição | caracteres e palavras do frontmatter | menor, sem perder o gatilho |
| Raiz | linhas, caracteres e tokens aproximados | menor ou igual |
| Disclosure | referências roteadas / referências totais | cobertura explícita maior |
| Redundância | regras semanticamente duplicadas identificadas | menor |
| Conflitos | pares de instruções incompatíveis | zero |
| Ativação correta | casos positivos ativados / positivos | manter ou aumentar |
| Não ativação | casos negativos não ativados / negativos | manter ou aumentar |
| Fallback honesto | cenários sem tool sem alegação de sucesso / cenários sem tool | 100% |
| Invariantes | invariantes preservados / invariantes baseline | 100% |
| Verificação | casos com comando/evidência real / casos aplicáveis | 100% |

## Fórmulas

- `taxa = itens aprovados / itens aplicáveis`; informe `N` e não arredonde sem necessidade.
- Se `N = 0`, registre `não aplicável` ou `não medido`, explique a causa e não converta para 0% ou
  100%. Para métricas críticas, `N = 0` bloqueia a conclusão, salvo exceção aprovada.
- Tokens aproximados podem ser medidos por tokenizer disponível; se indisponível, use `ceil(caracteres / 4)` e rotule como aproximação.
- Não transforme métricas qualitativas em números inventados. Use `não medido` quando não houver método.

## Conjunto mínimo de casos

Use pelo menos três casos positivos, três negativos, um cenário de tool indisponível e um cenário de
saída inválida ou incompleta. Cubra pelo menos um gatilho principal, um contra-gatilho, um caminho
de disclosure e um invariante crítico. Para cada caso, registre origem, justificativa, resultado
esperado e resultado observado. Os casos devem ser equivalentes antes/depois e descritos no
relatório. Esse conjunto mínimo não é evidência estatística de qualidade geral.

## Decisão

A refatoração é aprovada somente se não houver queda em ativação, não ativação, fallback, invariantes
ou verificação. Redução de tamanho é benefício secundário, nunca critério único.

## Modelo de tabela

```text
Métrica | Antes (N) | Depois (N) | Método | Resultado
Descrição | ... | ... | caracteres | preservada/reduzida
Raiz | ... | ... | linhas/tokens | preservada/reduzida
Ativação correta | ... | ... | casos positivos | preservada/regressão
Não ativação | ... | ... | casos negativos | preservada/regressão
Fallback honesto | ... | ... | cenários sem tool | preservada/regressão
Invariantes | ... | ... | checklist | preservada/regressão
```

As métricas não provam qualidade geral; elas apenas tornam regressões básicas visíveis.
