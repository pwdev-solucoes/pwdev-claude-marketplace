---
name: social-video
description: >
  Use quando a pessoa pedir vídeo curto gerado por IA ou o roteiro dele — 'vídeo de IA',
  'animar essa imagem', 'Runway', 'Higgsfield', 'storyboard', 'roteiro de reels', 'clipe de 5 s'.
  Entrega roteiro, storyboard e prompt por cena e, com chave, anima a imagem aprovada pelo Runway
  via `pwdev-media gerar` com confirmação de custo separada. Não use para editar vídeo gravado ou
  montar criativo animado com legenda (social-video-curto) nem para peça estática (social-reels).
metadata:
  version: 3.0.0
---

# Vídeo gerado por IA

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma:
`<plugin-root>/references/language.md`. Provedores: `<plugin-root>/references/apis.md`.

Você produz o formato de maior alcance e maior custo. Custo aqui é restrição de projeto, não detalhe.

## Alinhar a expectativa primeiro

| Caminho | Situação | O plugin entrega |
|---|---|---|
| **Runway** (`runway:gen4_turbo`) | API oficial | **gera de fato** a partir de uma imagem |
| Outros modelos de vídeo (Veo, Kling, Seedance…) | via agregador | gera — escolha com `pwdev-media catalogo recomendar --categoria video-gerar --so-com-chave` |
| **Higgsfield** | sem API pública estável | prompt e storyboard, execução manual |
| Vídeo com a pessoa falando, legenda e animações | edição, não geração | `social-video-curto` |

Diga isso no começo. Não deixe ninguém esperando um `.mp4` que não vai existir.

## Princípio central

> Os **3 primeiros segundos** decidem tudo. E precisam funcionar **mudos** — a maioria assiste sem som.

## Antes de produzir

**O Runway gera a partir de imagem, não do nada.** A ordem é:

```
social-imagem → social-curadoria → pwdev-media gerar runway:gen4_turbo
```

Sem imagem aprovada, não há vídeo. Não pule para o vídeo antes de fechar o frame.

## Estrutura

```
0-3s      gancho — funciona mudo, sem contexto anterior
3-10s     problema ou promessa
10-25s    desenvolvimento, demonstração, prova
25s-fim   fechamento + CTA
```

Reels e Shorts: até 30 s rende mais retenção.

## Storyboard

```
### Cena {{n}} — {{duração}}
Visual:      {{o que se vê}}
Imagem base: {{arquivo}}          ← o Runway precisa disto
Movimento:   {{estático | pan | dolly | orbital}}
Texto tela:  {{conteúdo}} — {{posição, dentro da zona segura}}
Legenda:     {{transcrição}}
Prompt:      {{movimento, para a cena gerada}}
```

## Com chave — gerar

```bash
pwdev-media gerar runway:gen4_turbo --imagem-inicial '{{arquivo-ou-url}}' --prompt '{{movimento}}' \
  --duration 5 --aspect-ratio 720:1280 --saida '.pwdev-social/gerados/{{AAAA-MM-DD}}-{{slug}}' --estimar
```

Mostre a estimativa e **confirme duração e quantidade separadamente da imagem** — um clipe de 10 s
custa muito mais que dez imagens. Só depois do "sim", repita com `--confirmar` no lugar de
`--estimar`. Vídeo leva minutos: avise.

Gere **um clipe de teste** antes de qualquer série. Nunca a sequência inteira de primeira.

## Sem chave, ou Higgsfield

Roteiro, storyboard e prompts com status **"ESPECIFICADO, não gerado"** em destaque. Não descreva o
vídeo como se existisse.

## Prompt de movimento

```
[sujeito e ação], [movimento de câmera], [ritmo], [duração]
```

**Movimento de câmera é o parâmetro que mais muda o resultado** e o mais esquecido.

Limitações reais — diga antes que a pessoa descubra pagando:

- texto na tela sai ilegível → **componha o texto na edição** (`social-video-curto`)
- mãos e rostos ainda falham
- consistência entre cenas é difícil → planeje cortes, não continuidade
- clipes são curtos; vídeo longo é montagem

## Obrigatório

- **Legenda embutida.** Sem som a peça é inacessível para pessoa surda.
- Texto dentro da zona segura (`pwdev-media formatos mostrar reels-9x16`)
- Sem piscar acima de 3 Hz
- Alternativa estática quando a animação carrega informação essencial
- Marcar como conteúdo gerado por IA ao publicar

## Setor público

Não simule atendimento, depoimento ou situação real com vídeo gerado por IA. Se a peça sugere
registro documental, precisa ser registro.

## Formato de saída

```markdown
# Vídeo — {{peça}}
Formato: {{9:16}} · Duração: {{n}}s · Canal: {{qual}}
Status: GERADO ({{n}} clipes) | ESPECIFICADO, não gerado
Custo: {{valor informado}} · {{n}} chamadas de vídeo

## Roteiro
## Storyboard
## Prompts por cena
## Legenda completa
## Checklist de acessibilidade
```

## Limites

- Não edita nem monta o corte final — ver `social-video-curto`
- Não gera áudio nem trilha (o `pwdev-media` tem `media-gerar` para isso)
- Não monta peça estática — ver `social-reels`
- Não escreve copy — ver `pwdev-copy`
- **Não gera sem confirmação de custo separada da imagem**

## Skills relacionadas

- `social-imagem` — a imagem base que o Runway anima
- `social-prompt`, `social-custo`, `social-curadoria`, `social-reels`, `social-video-curto`
