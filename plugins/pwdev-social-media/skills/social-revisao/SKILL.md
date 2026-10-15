---
name: social-revisao
description: >
  Use quando for revisar um criativo antes da aprovação — 'revisar a peça', 'está bom?',
  'checar o criativo', 'auditar', 'pode publicar?' — e sempre depois de qualquer montagem. Sete
  checagens (contraste, legibilidade, área segura, hierarquia, brand kit, conteúdo, acessibilidade)
  com veredito APROVADO, AJUSTAR ou REPROVADO. Não use para corrigir a peça (social-figma) nem para
  revisar a copy (pwdev-copy).
metadata:
  version: 3.0.0
---

# Revisão de Criativo

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma: `<plugin-root>/references/language.md`.

Você é o portão. Nada vai para publicação sem passar por aqui.

## Princípio central

> Peça errada publicada custa mais que peça atrasada. **Reprovar é barato.**

## Entrada

Link do Figma, arquivo de imagem ou especificação. Se vier vazio, peça. Com subagentes no runtime,
despache o `creative-reviewer` com a peça; sem eles, faça as 7 checagens aqui mesmo e rode
`social-alt-text` junto.

## Antes de revisar

Leia o brand kit (seção 3) e as restrições (seção 8). Peça pública muda o alvo
de contraste de AA para AA reforçado.

### Path A — Figma conectado
`get_screenshot` de cada frame + `get_design_context` para conferir tokens reais.

### Path B — Sem Figma
Revise a partir do arquivo de imagem ou da especificação. Declare o que não deu
para verificar — token real, por exemplo, não se confere em PNG.

## As 7 checagens

Rode todas. Cada uma reporta aprovado / ajustar / reprovar.

### 1. Contraste — reprovar em falha
| Elemento | Alvo social | Setor público |
|---|---|---|
| Texto < 24 px | 7:1 | 7:1 |
| Texto ≥ 24 px | 4.5:1 | 7:1 |
| Gráfico essencial | 4.5:1 | 4.5:1 |

Texto sobre foto: medir contra a **região mais clara sob o texto**, nunca contra
a média da imagem.

### 2. Legibilidade — reprovar em falha
- Nada abaixo de 24 px
- Miniatura de YouTube testada em 168 × 94 px
- Sem Light em corpo de texto
- Entrelinha ≥ 1.2 (≥ 1.4 sobre imagem)

### 3. Área segura — reprovar em falha
Conferir cada caixa de texto com `pwdev-media formatos conferir <formato> --caixa x,y,l,a` (ver
`social-formatos`). Nada crítico fora da zona segura do formato.

### 4. Hierarquia — ajustar
Três níveis distinguíveis. Teste: desfoque a peça mentalmente — o que sobra
legível deve ser a ideia central. Se o logo sobra e a mensagem some, está errado.

### 5. Brand kit — ajustar
- Cor é token, não hex solto
- Fonte dentro da escala
- Logo com área de proteção respeitada
- Grid respeitado

### 6. Conteúdo — reprovar em falha
- Nenhum `[PREENCHER]` remanescente
- Nenhum lorem ipsum
- **Dado com fonte e data visíveis**
- Nenhuma afirmação vetada pelo jurídico
- Texto essencial replicado na legenda

### 7. Acessibilidade — reprovar em falha
- Texto alternativo escrito
- Cor não é único portador de significado
- Vídeo com legenda embutida
- Sem piscar acima de 3 Hz

## Severidade

| Nível | Significa |
|---|---|
| **Reprovar** | não publica. Contraste, legibilidade, área segura, dado sem fonte, acessibilidade |
| **Ajustar** | publica se houver urgência, mas registra a dívida |
| **Observação** | melhoria, sem bloqueio |

Não infle severidade para parecer rigoroso, e não rebaixe para agradar prazo.
Se está tudo certo, diga que está tudo certo.

## Formato de saída

```markdown
# Revisão — {{peça}}
Veredito: APROVADO | AJUSTAR | REPROVADO
Modo: Figma conectado | a partir de imagem | a partir de spec

## Reprovações
### {{n}}. {{problema}}
Onde: {{elemento}} · Medido: {{valor}} · Exigido: {{valor}}
Correção: {{concreta}}

## Ajustes
## Observações
## Não verificado
{{o que o modo de revisão não permitiu checar}}
```

A seção final é obrigatória. Revisão que não declara seu limite dá falsa
segurança — e peça reprovada depois da publicação custa muito mais.

## Limites

- Não corrige a peça — reporta; a correção é de `social-figma`
- Não avalia a copy — ver `/pwdev-copy:revisar`
- Não julga eficácia de conversão — ver `perf-analyzer` do pwdev-copy
- Não aprova sozinho o que a seção 9 do contexto manda um humano aprovar

## Skills relacionadas

- `social-alt-text` — roda junto
- `social-formatos`, `social-marca` — as réguas
- `social-entrega` — só recebe o que passou
