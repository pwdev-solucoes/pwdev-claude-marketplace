---
name: asset-curation
description: >
  Organiza, compara e seleciona entre as variações geradas, e publica a grade de
  comparação como Artifact para aprovação do time. Use quando o usuário disser
  "qual dessas", "comparar as variações", "escolher a melhor", "mostrar as
  opções", "montar grade de aprovação", ou após qualquer lote de geração.
  Selecionar é trabalho, não detalhe.
metadata:
  version: 1.0.0
---

# Curadoria de Ativos

Gerar cria o problema seguinte: **escolher**. Oito variações sem critério é pior
que duas com critério.

## Princípio central

> A variação mais bonita raramente é a certa. **A certa é a que serve ao
> conceito** — e o conceito foi decidido antes de gerar.

## Critérios, nesta ordem

Avalie por eliminação. O primeiro critério que reprova encerra a avaliação.

| # | Critério | Elimina quando |
|---|---|---|
| 1 | **Aderência ao conceito** | não comunica a ideia central |
| 2 | **Espaço para composição** | não há área limpa para o texto entrar |
| 3 | **Paleta da marca** | exigiria tratamento pesado para caber |
| 4 | **Defeito de geração** | mão, rosto, texto deformado, anatomia errada |
| 5 | **Consistência com o conjunto** | destoa das outras peças da campanha |
| 6 | **Qualidade técnica** | resolução, ruído, nitidez |
| 7 | **Preferência estética** | último critério, nunca o primeiro |

O critério 2 é o mais subestimado. Imagem linda sem área para o texto é imagem
inútil numa peça de social.

## Defeitos de geração

Inspecione especificamente, porque passam despercebidos em miniatura:

- **mãos** — dedos a mais, articulação impossível
- **rostos** — assimetria, olhos, dentes
- **texto** — letras deformadas em qualquer gerador que não seja Ideogram
- **repetição de padrão** — textura que se repete de forma mecânica
- **física** — sombra sem fonte de luz, reflexo inconsistente, escala errada

**Sempre inspecione em tamanho real**, nunca só na grade. Defeito que some na
miniatura reaparece no feed.

## Grade de comparação

Publique como **Artifact** para o time avaliar e aprovar:

- todas as variações lado a lado, mesmo tamanho
- identificador, seed e prompt variável sob cada uma
- sua recomendação marcada, com uma frase de justificativa
- versão em tamanho real de cada candidata

Artifact é privado por padrão — o usuário decide se compartilha. Não publique
grade com material sensível sem confirmar.

## Registro

Ao selecionar, grave:

```
Selecionada: {{arquivo}}
Seed: {{valor}}          ← sem isso, a peça é irreproduzível
Modelo: {{qual}}
Prompt variável: {{texto}}
Motivo: {{critério que decidiu}}
Descartadas: {{n}} — {{motivo por grupo}}
```

O motivo do descarte alimenta `prompt-craft` na próxima campanha. Descarte sem
diagnóstico é aprendizado jogado fora.

## Quando nenhuma serve

Diga. Não escolha "a menos ruim" para fechar a tarefa.

Se nenhuma das variações passa do critério 1 ou 2, o problema é o **prompt** ou
o **conceito** — gerar mais da mesma base repete o erro pago.

Volte para `prompt-craft`, ajuste um eixo, gere 2.

## Limites

- Não gera nem regenera — ver `image-gen`
- Não compõe a peça final — ver `figma-pipeline`
- Não aprova sozinho o que a seção 9 manda um humano aprovar
- Não publica grade com material sensível sem confirmação

## Skills relacionadas

- `image-gen` — produz as variações
- `visual-consistency` — critério 5
- `prompt-craft` — para onde volta o diagnóstico
- `creative-review` — revisão da peça composta, depois
