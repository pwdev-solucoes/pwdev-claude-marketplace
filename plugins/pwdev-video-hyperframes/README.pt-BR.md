# PWDEV Video HyperFrames

Edição de vídeo falado por conversa, com qualidade de agência: anúncio, Reels, TikTok, VSL, aula ou
resposta. Você entrega a pasta com as gravações e conversa; a IA corta, monta e renderiza com o
[HyperFrames](https://github.com/heygen-com/hyperframes) (HTML → MP4, Apache-2.0), mostrando tudo no
estúdio antes do render. Funciona no Claude Code, no Codex e no Hermes Agent.

## O que ele faz

- **Corte pela onda do áudio:** transcreve no seu computador, separa frases, fica com a última
  tomada certa e tira toda pausa de 0,25 s ou mais, sem comer o fim das palavras.
- **Plano em blocos:** decide o que aparece em cada momento, com uma ideia por vez e algo mudando a
  cada 2 a 4 s.
- **Na tela:**
  - legenda de até 3 palavras com a palavra falada em destaque;
  - zooms de câmera;
  - rótulos e títulos dentro da zona segura de cada rede;
  - cenas animadas sob medida, escritas com as skills oficiais do HyperFrames.
- **Som:** efeitos casados com o movimento e trilha 22–24 dB abaixo da voz (sua música ou gerada por
  IA com o seu ok).
- **Revisão:** amostra de 8 a 15 s no estúdio antes do vídeo inteiro; render na versão fixa do
  HyperFrames; entrega só com o portão de qualidade **PASSOU** (sem respiro, sem estouro, legenda
  cobrindo toda palavra).
- **Versões:** lote de ganchos, outros formatos (4:5, 1:1, 16:9) e versões curtas.

## Instalação

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-hyperframes@pwdev-claude-marketplace
```

Numa conversa nova: `/pwdev-video-hyperframes:init` (Codex: `$vhf-setup`). Ele confere e instala,
sem sudo:
- a CLI `pwdev-media`;
- o ffmpeg, em `~/.pwdev/bin`;
- o Node 22+;
- as skills oficiais do HyperFrames.

Ele também desliga a telemetria do HyperFrames. Na primeira transcrição, o modelo de voz (~1,6 GB)
é baixado uma vez.

## Manual de uso

1. **Editar:** "edita o vídeo da pasta ~/Videos/anuncio-bolsa" (`/pwdev-video-hyperframes:editar`).
   Pode gravar do jeito que sair, com erros e repetições.
2. **A IA conta as suposições** (formato, estilo, sem trilha se você não tiver música) e segue no modo
   automático. Quer aprovar o corte antes? Diga "quero ver o corte primeiro".
3. **Amostra no estúdio:** ela abre um trecho de 8–15 s. Peça ajustes em palavras do dia a dia
   ("o texto entrou atrasado", "tira o zoom do começo").
4. **Vídeo final:** fica em `<pasta-do-vídeo>/<nome>/renders/<nome>.mp4`, entregue só com PASSOU.

| Comando (Claude Code) | Codex / Hermes | Para quê |
|---|---|---|
| `/pwdev-video-hyperframes:init` · `:status` | `$vhf-setup` | preparar e conferir as ferramentas |
| `:editar` | `$vhf-editar` | edição completa (comece aqui) |
| `:corte` | `$vhf-corte` | só o corte, ou ajustar o corte |
| `:plano` | `$vhf-plano` | o que aparece em cada momento |
| `:cenas` | `$vhf-cenas` | animação sob medida (número, lista, gráfico, antes e depois) |
| `:som` | `$vhf-som` | trilha e efeitos |
| `:revisar` | `$vhf-revisar` | vídeo inteiro, render e entrega |
| `:versoes` | `$vhf-variacoes` | ganchos, formatos e versões curtas |

## Como funciona por dentro

```
gravações ─▶ pwdev-media video transcrever ─▶ frases.md ─▶ montar (EDL) ─▶ cortar (cut.mp4)
          ─▶ projeto.json (plano) ─▶ build.py montar (index.html HyperFrames) ─▶ estúdio
          ─▶ build.py render ─▶ portão PASSOU ─▶ entrega
```

- **Pastas:** os originais ficam intocados. A pasta `edit/` guarda transcrição, frases, EDL, corte
  e legendas. O projeto HyperFrames fica ao lado, com o nome do vídeo.
- **`projeto.json`:** usa o schema `pwdev-projeto-video/1`, o mesmo do `pwdev-video-remotion`.
  Referência: [`references/projeto.md`](./references/projeto.md).
- **Regras de edição:** [`references/regras.md`](./references/regras.md).

## Segurança

- Nunca altera, move ou apaga os vídeos originais.
- Tudo roda no seu computador. Só sai dele o que você autorizar: geração por IA com custo, pelo
  `pwdev-media`, sempre com estimativa e "sim".
- O GSAP do projeto é baixado na versão fixa e conferido por integridade (SHA-384). Sem internet, o
  projeto usa o CDN com SRI.
- A telemetria do HyperFrames fica desligada nas chamadas do plugin.

## Para quem desenvolve

```bash
python3 -m unittest tests.test_pwdev_video_hyperframes tests.test_pwdev_media_video
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_hyperframes   # + lint oficial do HyperFrames
claude plugin validate plugins/pwdev-video-hyperframes
hermes plugins doctor --ci plugins/pwdev-video-hyperframes
```

## Licença

Apache-2.0. A fonte Montserrat do template segue a SIL Open Font License (`OFL-Montserrat.txt`).
