---
name: social-imagem
description: >
  Use quando a pessoa pedir uma imagem gerada por IA para um criativo — 'gerar imagem',
  'criar ilustração', 'imagem por IA', 'Ideogram', 'Flux', 'Leonardo', 'preciso de uma foto que não
  temos' — ou quando social-conceito marcar um ativo como "gerar". Faz a triagem (precisa mesmo
  gerar?), escolhe o item do catálogo, mostra a estimativa, gera 2 variações com `pwdev-media gerar`
  só depois do "sim" e registra a seed; sem chave, entrega o prompt (modo prompt). Não use para
  vídeo (social-video), upscale (social-upscale) nem para compor texto sobre o ativo (social-figma).
metadata:
  version: 3.0.0
---

# Geração de Imagem

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`. Provedores e itens: `<plugin-root>/references/apis.md`.

Skill central do plugin. Você executa geração paga — **cada chamada tira dinheiro da conta da
pessoa**. Com subagentes no runtime, despache o `asset-generator`; sem eles, siga os mesmos passos
aqui mesmo.

## Princípio central

> Antes de gerar, verifique se precisa gerar. A geração mais barata é a que não acontece.

Texto sobre cor sólida, sobre foto do acervo ou sobre vetor do design system é **composição**, não
geração. Figma resolve na hora, de graça, e com texto editável.

## Sequência obrigatória

```
1. triagem             o ativo precisa mesmo ser gerado? (abaixo e social-custo)
2. social-prompt       construir o prompt
3. social-consistencia aplicar bloco base, modelo e seed da campanha
4. estimar             pwdev-media gerar ... --estimar
5. [CONFIRMAR CUSTO]   esperar o "sim" explícito
6. executar            pwdev-media gerar ... --confirmar
7. social-curadoria    comparar e selecionar
```

Pular a etapa 1 é o erro mais caro. Pular a 5 é o mais grave.

## 1. Triagem: precisa mesmo gerar?

| Pergunta | Se sim |
|---|---|
| É texto sobre fundo liso? | **não gere** — composição |
| Já existe no acervo? | **não gere** — use |
| Existe vetor no design system? | **não gere** — use |
| Dá para fotografar? | avalie: foto real costuma sair melhor e mais barata |
| É fundo, textura ou cena inexistente? | gere |

Se a resposta for "não gere", **diga isso** e proponha o caminho de composição.

## 2. Escolha do item do catálogo

| Necessidade | Item | Por quê |
|---|---|---|
| **Texto legível dentro da arte** | `ideogram:ideogram-3` | o único confiável em tipografia |
| Fotorrealismo | `bfl:flux-2-pro` (ou `bfl:flux-pro-1.1`) | melhor foto que não existe |
| Ilustração repetível na campanha | `leonardo:conta` | estilo fixo pelo modelo da conta (`LEONARDO_MODEL_ID`) |
| Melhor custo com as chaves que a pessoa tem | `pwdev-media catalogo recomendar --categoria imagem-gerar --so-com-chave` | agregadores (OpenRouter, fal) |

> Texto dentro da imagem: **só o Ideogram entrega com confiabilidade**. Nos demais, deixe área limpa
> e componha o texto no Figma. Pedir texto ao Flux é o desperdício mais comum desta stack.

Campanha em andamento: use o item e o modelo fixados na seção 6 do contexto — trocar no meio quebra
a consistência.

## 3. Chave configurada — gerar

```bash
pwdev-media chaves listar                       # só diz onde a chave está, nunca o valor
pwdev-media gerar ideogram:ideogram-3 --prompt '{{prompt}}' --aspect-ratio 4x5 --n 2 \
  --seed {{seed}} --saida '.pwdev-social/gerados/{{AAAA-MM-DD}}-{{slug}}' --estimar
```

Mostre a estimativa (item, quantidade, valor e a data do preço) e **espere o "sim"**. Então repita o
mesmo comando trocando `--estimar` por `--confirmar`.

Flux e Leonardo usam medidas em pixel:

```bash
pwdev-media gerar bfl:flux-2-pro --prompt '{{prompt}}' --largura 1080 --altura 1350 --seed {{seed}} \
  --saida '.pwdev-social/gerados/{{AAAA-MM-DD}}-{{slug}}' --estimar
pwdev-media gerar leonardo:conta --prompt '{{prompt}}' --largura 1080 --altura 1350 --n 2 \
  --saida '.pwdev-social/gerados/{{AAAA-MM-DD}}-{{slug}}' --estimar
```

**Regra das 2 variações.** Primeira rodada gera 2, nunca 8. Só gere volume depois de fixar seed e
modelo.

O `pwdev-media`:
- recusa gastar sem `--confirmar` — segunda barreira além da conversa;
- recusa passar do orçamento mensal (`pwdev-media custo orcamento`) sem `--acima-do-orcamento`;
- nunca imprime a chave;
- registra cada geração no ledger (`pwdev-media custo extrato`) e reaproveita pedido idêntico, sem
  cobrar de novo;
- falha alto (código 5) quando o contrato da API muda. **Pare e reporte** — não contorne com outra
  chamada.

Códigos de saída: 3 = precisa do "sim"; 4 = orçamento; 6 = sem chave (vá para o modo prompt ou
`social-contexto`); 7 = item sem adaptador.

## 4. Sem chave — modo prompt

Entregue o prompt otimizado e declare **"NÃO GERADO"** em destaque. Para guardar a chave, a pessoa
roda `pwdev-media chaves guardar <provedor>` no próprio terminal (a IA nunca vê a chave).

Não descreva a imagem como se existisse. Não diga "gerei três variações". Não invente nome de
arquivo. Modo prompt é operação legítima: o prompt roda na interface web de qualquer ferramenta.

## Depois de gerar

1. `social-curadoria` — comparar, inspecionar em tamanho real, selecionar
2. **Registrar a seed da aprovada** — sem seed, a peça é irreproduzível
3. `social-figma` — compor texto e marca sobre o ativo
4. `social-revisao` — auditar a peça composta

## Limites éticos e legais

- **Não gerar rosto de pessoa real**, nem "no estilo de" pessoa identificável
- **Não imitar estilo de artista vivo identificável** — risco jurídico e ético
- **Não gerar imagem que simule situação real** (atendimento, evento, depoimento) para publicar como
  se fosse registro
- Marcar como conteúdo gerado por IA ao publicar (o `pwdev-media` lembra quando o item exige)
- Licença comercial: confira a do item no catálogo (`pwdev-media catalogo mostrar <item>`)

## Setor público

Regra padrão: **não usar imagem gerada por IA para representar serviço, equipe ou beneficiário**.
Pessoa em contexto de política pública precisa ser real e autorizada. Gerador é aceitável para
elemento gráfico abstrato, textura e fundo. Levante isso com a pessoa antes de gerar.

## Formato de saída

### Gerado
```
Gerado: {{n}} variações — {{item do catálogo}}
Prompt: {{texto}}
Seed: {{valor}}
Arquivos: {{caminhos}}
Custo informado pelo provedor: {{valor}} · Acumulado do mês: {{pwdev-media custo}}
Próximo: social-curadoria
```

### Modo prompt
```
⚠ NÃO GERADO — sem chave de {{provedor}}

Prompt otimizado para {{ferramenta}}:
{{prompt}}

Parâmetros: proporção {{x}} · modelo {{y}} · seed sugerida {{z}}
Execução manual: {{passo a passo na interface}}
```

## Limites

- Não compõe a peça final — ver `social-figma`
- Não faz upscale — ver `social-upscale`
- Não gera vídeo — ver `social-video`
- Não escreve o prompt do zero — ver `social-prompt`
- Não seleciona entre variações — ver `social-curadoria`
- **Não gasta crédito sem confirmação explícita**
- **Não simula resultado que não produziu**

## Skills relacionadas

- `social-custo` — triagem antes, acompanhamento depois
- `social-prompt`, `social-consistencia` — insumos
- `social-curadoria` — o passo seguinte
