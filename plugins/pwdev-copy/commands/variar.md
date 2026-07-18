---
description: Gera N variações de headline, CTA ou anúncio com ângulos distintos e matriz de teste
argument-hint: "[elemento] [quantidade]"
---

# /pwdev-copy:variar — Gerar variações

## STEP 0 — Idioma
`${CLAUDE_PLUGIN_ROOT}/references/language.md`

## Regra central
Variação não é sinônimo. **Cada variação testa uma hipótese diferente.**
Cinco reformulações da mesma ideia é uma opção, não cinco.

## Matriz de ângulos
Distribua as variações entre ângulos, nunca todas no mesmo:

| Ângulo | Testa |
|---|---|
| Resultado | o benefício importa? |
| Dor | o problema é reconhecido? |
| Prova | credibilidade destrava? |
| Público | especificidade destrava? |
| Objeção | a hesitação é o gargalo? |
| Novidade | a notícia gera interesse? |

## Saída
```
A) {{copy}}
   ângulo: {{ângulo}} · hipótese: {{o que aprendemos se vencer}}
```

Feche com recomendação de qual par testar primeiro e por quê.
Consulte `${CLAUDE_PLUGIN_ROOT}/references/formulas-headline.md`.
