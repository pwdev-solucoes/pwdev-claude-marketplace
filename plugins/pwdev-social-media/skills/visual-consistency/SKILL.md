---
name: visual-consistency
description: >
  Mantém coerência visual entre peças geradas por IA — seed, modelo fixo,
  referência de estilo e biblioteca de prompts da marca. Use quando o usuário
  disser "as peças não parecem da mesma campanha", "manter o estilo",
  "consistência", "cada imagem saiu diferente", "padronizar o visual gerado".
  É o problema mais difícil de geração por IA em escala.
metadata:
  version: 1.0.0
---

# Consistência Visual

Você resolve o defeito estrutural da geração por IA: cada chamada é independente,
e o modelo não lembra da peça anterior.

## Princípio central

> O gerador não tem memória. **A consistência não vem do modelo — vem do
> processo que você impõe a ele.**

Campanha com dez imagens que parecem de dez marcas diferentes é o resultado
padrão de quem gera sem sistema. É também o motivo mais comum de refação paga.

## As 4 âncoras

Aplique todas. Cada uma sozinha é insuficiente.

### 1. Modelo fixo
Escolha um modelo e **não troque no meio da campanha**. Modelos diferentes têm
estética diferente, por melhor que seja o prompt.

Registre na seção 6 do contexto: ferramenta, modelo, versão.

### 2. Prompt base
Construa um bloco fixo que entra em **todas** as peças:

```
BASE (não alterar durante a campanha):
  estilo:      fotografia documental, luz natural difusa
  paleta:      verde-azulado dessaturado, alto contraste
  enquadramento: plano médio, altura dos olhos
  tratamento:  sem filtro, sem vinheta

VARIÁVEL (muda por peça):
  sujeito:     {{o que muda}}
  ambiente:    {{o que muda}}
```

Só o bloco variável muda. Alterar a base no meio quebra a campanha inteira.

### 3. Seed
Ao acertar uma peça, **registre a seed**. Para gerar variação daquela imagem,
reutilize a seed e mude só o sujeito.

Seed perdida significa peça irreproduzível. Grave no manifesto, sempre.

### 4. Referência de estilo
Quando a ferramenta suportar (Leonardo é a mais forte nisso), suba uma peça
aprovada como referência e ancore as demais nela.

## Teste de coerência

Antes de aprovar o conjunto, coloque **todas as peças lado a lado**. Não avalie
uma por uma — o defeito de consistência só aparece na comparação.

| Eixo | Pergunta |
|---|---|
| Paleta | as cores convivem, ou uma destoa? |
| Luz | a direção e a temperatura batem? |
| Enquadramento | a distância do sujeito é parecida? |
| Tratamento | mesma textura, mesmo contraste, mesmo grão? |
| Época/estilo | parecem do mesmo ensaio? |

Uma peça fora do conjunto: regere **aquela**, não o conjunto.
Três ou mais fora: o problema é a base — corrija a base e regere tudo.

## Biblioteca de prompts

Guarde no vault (ver `vault-sync`):

```markdown
## Marca — bloco base
{{texto do bloco}}
Modelo: {{ferramenta}} / {{modelo}} / {{versão}}
Referência: {{caminho}}

## Peças aprovadas
| Peça | Seed | Prompt variável | Arquivo |
```

Isso é o ativo mais valioso da operação depois de três campanhas — e o mais
esquecido. Sem ele, cada campanha recomeça do zero e paga de novo pelo
aprendizado.

## Quando não insistir

Se três rodadas não trouxerem consistência, o problema pode não ter solução por
prompt. Alternativas mais baratas:

- gerar **só o fundo ou a textura** e compor o resto no Figma
- usar ilustração vetorial do design system
- usar foto real
- reduzir a dependência de imagem gerada no conceito

Insistir em prompt quando o caminho é composição é o erro caro desta arquitetura.

## Limites

- Não gera — ver `image-gen`
- Não escreve prompt do zero — ver `prompt-craft`
- Não garante consistência: reduz variação, não elimina
- Não conserta inconsistência em peça já publicada

## Skills relacionadas

- `prompt-craft`, `image-gen`, `asset-curation`, `vault-sync`
