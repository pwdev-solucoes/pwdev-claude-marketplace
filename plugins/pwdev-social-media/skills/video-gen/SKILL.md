---
name: video-gen
description: >
  Produz vídeo curto — roteiro, storyboard, prompts por cena e geração via
  Runway quando há chave. Use quando o usuário disser "vídeo", "reels",
  "roteiro de vídeo", "Runway", "Higgsfield", "animação", "storyboard",
  "vídeo de IA". Runway gera de fato a partir de imagem; Higgsfield não tem API
  pública estável e segue manual. Vídeo é o item mais caro da stack.
metadata:
  version: 2.0.0
---

# Vídeo

Você produz o formato de maior alcance e maior custo. Custo aqui é restrição de
projeto, não detalhe.

## Situação por ferramenta

| Ferramenta | Situação | O plugin entrega |
|---|---|---|
| **Runway** | API oficial existe | **gera de fato** — `gen-runway.sh` |
| **Higgsfield** | sem evidência de API pública estável | prompt e storyboard, execução manual |

Diga isso no começo. Não deixe ninguém esperando um `.mp4` que não vai existir.

## Princípio central

> Os **3 primeiros segundos** decidem tudo. E precisam funcionar **mudos** —
> a maioria assiste sem som.

## Antes de produzir

**Runway gera a partir de imagem, não do nada.** A ordem é:

```
image-gen → asset-curation → gen-runway.sh
```

Sem imagem aprovada, não há vídeo. Não pule para o vídeo antes de fechar o frame.

## Estrutura

```
0-3s      gancho — funciona mudo, sem contexto anterior
3-10s     problema ou promessa
10-25s    desenvolvimento, demonstração, prova
25s-fim   fechamento + CTA
```

Reels e Shorts: até 30s rende mais retenção.

## Storyboard

```
### Cena {{n}} — {{duração}}
Visual:      {{o que se vê}}
Imagem base: {{arquivo}}          ← Runway precisa disto
Movimento:   {{estático | pan | dolly | orbital}}
Texto tela:  {{conteúdo}} — {{posição, dentro da área segura}}
Legenda:     {{transcrição}}
Prompt:      {{movimento, para a cena gerada}}
```

## Path A — Runway com chave

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/gen-runway.sh \
  --image "{{caminho}}" --prompt "{{movimento}}" \
  --dur 5 --ratio 720:1280 --confirm
```

**Confirme duração e quantidade separadamente da imagem.** Um clipe de 10s custa
muito mais que dez imagens.

Gere **um clipe de teste** antes de qualquer série. Nunca a sequência inteira de
primeira.

## Path B — Sem chave, ou Higgsfield

Roteiro, storyboard e prompts com status **"ESPECIFICADO, não gerado"** em
destaque. Não descreva o vídeo como se existisse.

## Prompt de movimento

```
[sujeito e ação], [movimento de câmera], [ritmo], [duração]
```

**Movimento de câmera é o parâmetro que mais muda o resultado** e o mais
esquecido. Especifique sempre.

Limitações reais — diga antes que o usuário descubra pagando:

- texto na tela sai ilegível → **componha o texto na edição**
- mãos e rostos ainda falham
- consistência entre cenas é difícil → planeje cortes, não continuidade
- clipes são curtos; vídeo longo é montagem

## Obrigatório

- **Legenda embutida.** Sem som a peça é inacessível para pessoa surda.
- Texto dentro da área segura (ver `story-reels`)
- Sem piscar acima de 3 Hz
- Alternativa estática quando a animação carrega informação essencial

## Setor público

Não simule atendimento, depoimento ou situação real com vídeo gerado por IA.
Se a peça sugere registro documental, precisa ser registro.

## Formato de saída

```markdown
# Vídeo — {{peça}}
Formato: {{9:16}} · Duração: {{n}}s · Canal: {{qual}}
Status: GERADO ({{n}} clipes) | ESPECIFICADO, não gerado
Custo: {{n}} chamadas de vídeo

## Roteiro
## Storyboard
## Prompts por cena
## Legenda completa
## Checklist de acessibilidade
```

## Limites

- Não edita nem monta o corte final
- Não gera áudio nem trilha
- Não monta peça estática — ver `story-reels`
- Não escreve copy — ver `pwdev-copy`
- **Não gera sem confirmação de custo separada da imagem**

## Skills relacionadas

- `image-gen` — a imagem base que o Runway anima
- `prompt-craft`, `cost-control`, `asset-curation`, `story-reels`
