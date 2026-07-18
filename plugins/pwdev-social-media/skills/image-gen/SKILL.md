---
name: image-gen
description: >
  Gera imagem por IA via Ideogram, Leonardo ou Flux usando os scripts do plugin,
  ou entrega o prompt otimizado quando não há chave. Use quando o usuário disser
  "gerar imagem", "criar ilustração", "imagem por IA", "Ideogram", "Leonardo",
  "Flux", "preciso de uma foto que não temos", ou quando creative-concept marcar
  um ativo como "gerar". Skill central deste plugin. Toda chamada gasta crédito
  e exige confirmação prévia.
metadata:
  version: 2.0.0
---

# Geração de Imagem

Skill central do plugin. Você executa geração paga — **cada chamada tira dinheiro
da conta do usuário**.

## Princípio central

> Antes de gerar, verifique se precisa gerar. A geração mais barata é a que não
> acontece.

Texto sobre cor sólida, sobre foto do acervo ou sobre vetor do design system é
**composição**, não geração. Figma resolve na hora, de graça, e com texto
editável. Rode a triagem de `cost-control` antes de qualquer chamada.

## Sequência obrigatória

```
1. cost-control        triagem — o ativo precisa mesmo ser gerado?
2. prompt-craft        construir o prompt
3. visual-consistency  aplicar bloco base, modelo e seed da campanha
4. [CONFIRMAR CUSTO]   esperar aprovação explícita
5. executar            script correspondente, com --confirm
6. asset-curation      comparar e selecionar
```

Pular a etapa 1 é o erro mais caro. Pular a 4 é o mais grave.

## Escolha da ferramenta

| Necessidade | Ferramenta | Script |
|---|---|---|
| **Texto legível dentro da arte** | Ideogram | `gen-ideogram.sh` |
| Ilustração repetível na campanha | Leonardo | `gen-leonardo.sh` |
| Fotorrealismo | Flux | `gen-flux.sh` |

> Texto dentro da imagem: **só Ideogram entrega com confiabilidade**. Nos demais,
> deixe espaço vazio e componha o texto no Figma. Pedir texto ao Flux é o
> desperdício mais comum desta stack.

## Path A — Chave configurada

Verifique com `${CLAUDE_PLUGIN_ROOT}/scripts/check-keys.sh`.

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/gen-ideogram.sh \
  --prompt "{{prompt}}" --ratio 4x5 --n 2 --seed {{seed}} --confirm
```

**Regra das 2 variações.** Primeira rodada gera 2, nunca 8. Com 2 já se
diagnostica se o prompt está na direção certa. Só gere volume depois de fixar
seed e modelo.

Os scripts:
- recusam rodar sem `--confirm` — segunda barreira além da conversa
- nunca imprimem a chave
- registram tudo em `.pwdev-social/gerados/manifest.jsonl`
- falham alto quando o contrato da API muda, em vez de retornar silêncio

Se um script reclamar de "contrato pode ter mudado", **confira a documentação e
corrija o script** — não contorne com outra chamada.

## Path B — Sem chave

Entregue o prompt otimizado e declare **"NÃO GERADO"** em destaque.

Não descreva a imagem como se existisse. Não diga "gerei três variações". Não
invente nome de arquivo.

Modo prompt é operação legítima, não falha: prompt bem construído roda na
interface web de qualquer uma das ferramentas.

## Depois de gerar

1. `asset-curation` — comparar, inspecionar em tamanho real, selecionar
2. **Registrar a seed da aprovada** — sem seed, a peça é irreproduzível
3. `figma-pipeline` — compor texto e marca sobre o ativo
4. `creative-review` — auditar a peça composta

Registrar a seed é o passo que todo mundo pula e todo mundo lamenta depois.

## Limites éticos e legais

- **Não gerar rosto de pessoa real**, nem "no estilo de" pessoa identificável
- **Não imitar estilo de artista vivo identificável** — risco jurídico e ético
- **Não gerar imagem que simule situação real** (atendimento, evento, depoimento)
  para publicar como se fosse registro
- Sinalizar que a imagem é gerada por IA quando a peça sugerir documentação
- Conferir a licença da ferramenta antes de uso comercial

## Setor público

Regra padrão: **não usar imagem gerada por IA para representar serviço, equipe
ou beneficiário**. Pessoa em contexto de política pública precisa ser real e
autorizada.

Gerador é aceitável para elemento gráfico abstrato, textura e fundo.
Levante isso com o usuário antes de gerar — não decida sozinho.

## Formato de saída

### Path A
```
Gerado: {{n}} variações — {{ferramenta}}/{{modelo}}
Prompt: {{texto}}
Seed: {{valor}}
Arquivos: {{caminhos}}
Chamadas nesta rodada: {{n}} · Acumulado na campanha: {{n}}
Próximo: asset-curation
```

### Path B
```
⚠ NÃO GERADO — {{VAR}} não configurada

Prompt otimizado para {{ferramenta}}:
{{prompt}}

Parâmetros: proporção {{x}} · modelo {{y}} · seed sugerida {{z}}
Execução manual: {{passo a passo na interface}}
```

## Limites

- Não compõe a peça final — ver `figma-pipeline`
- Não faz upscale — ver `asset-upscale`
- Não gera vídeo — ver `video-gen`
- Não escreve o prompt do zero — ver `prompt-craft`
- Não seleciona entre variações — ver `asset-curation`
- **Não gasta crédito sem confirmação explícita**
- **Não simula resultado que não produziu**

## Skills relacionadas

- `cost-control` — triagem antes, acompanhamento depois
- `prompt-craft`, `visual-consistency` — insumos
- `asset-curation` — o passo seguinte
