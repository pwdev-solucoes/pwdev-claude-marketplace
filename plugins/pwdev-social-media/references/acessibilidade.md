# Acessibilidade em Criativos

Portão de aprovação, não recomendação. Peça que não passa aqui não vai para
`04 — Aprovado`.

## Contraste

Alvos — mais altos que WCAG AA, porque compressão de rede social degrada borda:

| Elemento | WCAG AA | Alvo social | Setor público |
|---|---|---|---|
| Texto < 24 px | 4.5:1 | 7:1 | 7:1 |
| Texto ≥ 24 px | 3:1 | 4.5:1 | 7:1 |
| Gráfico essencial | 3:1 | 4.5:1 | 4.5:1 |

**Texto sobre foto** nunca é medido contra a média da imagem. Meça contra a
**região mais clara sob o texto**. Se variar, use sobreposição sólida, gradiente
ou caixa — não confie na sorte do enquadramento.

## Legibilidade

- Mínimo absoluto: **24 px** em base 1080. Abaixo disso é inacessível no celular.
- Miniatura do YouTube: testar reduzida a **168 × 94 px**.
- Peso de fonte abaixo de Regular perde na compressão — evite Light em corpo.
- Entrelinha mínima 1.2; em texto sobre imagem, 1.4.

## Cor

- **Cor nunca é o único portador de significado.** Gráfico com séries só
  diferenciadas por cor exclui daltônicos — acrescente rótulo, padrão ou forma.
- Verifique as três formas mais comuns de daltonismo antes de aprovar paleta
  de dado (deuteranopia, protanopia, tritanopia).

## Texto

- Texto essencial **nunca** apenas dentro da imagem. Repita na legenda —
  leitor de tela não lê pixel.
- Sem emoji no meio de frase: o leitor de tela lê o nome do emoji e quebra a leitura.
- Sem texto em caixa alta em blocos longos — reduz velocidade de leitura.
- Sem justificação: cria rios de espaço e prejudica dislexia.

## Movimento

- Sem piscar acima de 3 Hz — risco de convulsão fotossensível.
- Animação essencial precisa de alternativa estática.
- Legenda embutida obrigatória em vídeo. A maioria assiste sem som — e sem
  legenda o conteúdo é inacessível para pessoa surda.

## Texto alternativo

Obrigatório em toda peça. Ver a skill `alt-text`.

## Checklist de aprovação

- [ ] Contraste medido e registrado, elemento a elemento
- [ ] Nenhum texto abaixo de 24 px
- [ ] Texto essencial replicado na legenda
- [ ] Cor não é único portador de significado
- [ ] Texto alternativo escrito
- [ ] Área segura respeitada
- [ ] Legibilidade testada em tamanho real de celular
- [ ] Vídeo com legenda embutida
