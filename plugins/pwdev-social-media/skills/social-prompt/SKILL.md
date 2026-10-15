---
name: social-prompt
description: >
  Use quando for escrever ou consertar o prompt de um gerador de imagem ou vídeo —
  'prompt', 'como pedir isso pra IA', 'melhorar o prompt', 'não saiu como eu queria', 'prompt do
  Ideogram', 'prompt do Flux' — ou antes de qualquer geração. Estrutura, parâmetros por ferramenta,
  seed, negativa e iteração de um eixo por vez. Não use para executar a geração (social-imagem,
  social-video) nem para decidir se o ativo deve ser gerado (social-conceito).
metadata:
  version: 3.0.0
---

# Construção de Prompt

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma: `<plugin-root>/references/language.md`.

Você escreve a instrução que a máquina executa. Com APIs no centro, **esta é a
habilidade que mais economiza dinheiro**: prompt ruim é retrabalho pago.

## Princípio central

> Cada tentativa custa. Um prompt bem construído acerta em 2 variações; um
> prompt vago acerta em 12 — e a diferença sai do orçamento da campanha.

## Antes de escrever

Leia a seção 3 (brand kit) e 4 (identidade) do contexto. Prompt que ignora a
paleta da marca gera imagem que exige tratamento — retrabalho que custa mais
que gerar de novo.

## Estrutura

```
[sujeito] [ação ou estado], [ambiente],
[enquadramento], [iluminação], [estilo], [paleta], [proporção]
```

Ordem importa: os geradores pesam mais o começo do prompt. O que é essencial
vem primeiro.

### Exemplo

❌ **Vago** — vai custar 8 tentativas
> "uma imagem sobre saúde pública moderna"

✅ **Específico** — costuma acertar em 2
> "profissional de saúde consultando tablet em posto de atendimento,
> ambiente claro e organizado, plano médio à altura dos olhos,
> luz natural difusa de janela lateral, fotografia documental,
> paleta verde-azulada dessaturada, proporção 4:5"

## Por ferramenta

| Ferramenta | O que responde bem | O que evitar |
|---|---|---|
| **Ideogram** | texto entre aspas na arte; instrução tipográfica | cena complexa com muitos sujeitos |
| **Leonardo** | estilo consistente via modelo fixo e referência | prompt longo demais dilui o estilo |
| **Flux** | descrição fotográfica: lente, luz, profundidade | vocabulário de ilustração |
| **Runway** | movimento de câmera explícito | mudança de cena dentro do clipe |

### Texto dentro da imagem
Só Ideogram entrega com confiabilidade. Nos demais:

> **Deixe espaço vazio no prompt e componha o texto no Figma.**

Resultado sempre melhor, custa menos e o texto fica editável. Pedir texto ao
Flux é o desperdício mais comum desta stack.

## Negativa

Funciona mal na maioria dos modelos atuais. **Descreva o que quer, não o que
não quer.**

❌ "sem pessoas, sem texto, não desfocado"
✅ "ambiente vazio, superfície limpa, foco nítido em toda a cena"

## Parâmetros

| Parâmetro | Efeito | Quando fixar |
|---|---|---|
| **seed** | reprodutibilidade | **sempre**, ao acertar — sem seed não se repete |
| proporção | enquadramento | sempre, no prompt **e** no parâmetro |
| modelo | estilo base | sempre, em campanha com mais de uma peça |
| referência de estilo | consistência visual | campanha inteira |

> Ao acertar um resultado, **registre a seed imediatamente**. Perder a seed de
> uma imagem aprovada significa não conseguir gerar a variação dela depois.

## Iteração

1. Gere **2 variações**, nunca 8, na primeira rodada
2. Diagnostique o que falhou: sujeito, composição, luz, estilo ou paleta
3. Ajuste **um eixo por vez** — mudar tudo impede saber o que funcionou
4. Ao acertar, fixe seed e modelo, e só então gere o volume

Mudar cinco coisas e gerar oito imagens é como se gasta um orçamento inteiro
sem aprender nada.

## Marca

Injete no prompt: paleta do brand kit, tratamento definido na seção 4, e o
enquadramento típico das referências aprovadas.

Se a seção 4 lista **referências rejeitadas**, use-as para saber o que não pedir.

## Limites

- Não executa a geração — ver `social-imagem`
- Não decide se o ativo deve ser gerado — ver `social-conceito`
- Não garante resultado: prompt é instrução, não contrato
- Não escreve prompt para imitar artista vivo identificável

## Skills relacionadas

- `social-imagem`, `social-video` — executam
- `social-consistencia` — mantém o estilo entre peças
- `social-custo` — o motivo de o prompt importar tanto
