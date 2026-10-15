# PWDEV Video Remotion

Edição de vídeo falado por conversa com [Remotion](https://www.remotion.dev) (React). O fluxo e o
`projeto.json` são os mesmos do `pwdev-video-hyperframes`: muda só o motor que desenha o vídeo.
Funciona no Claude Code, no Codex e no Hermes Agent.

## Quando usar este plugin

- Seu time já trabalha com React e quer as cenas como componentes tipados.
- Você vai produzir **em lote a partir de dados** (muitas versões de uma planilha) ou quer render
  distribuído (Remotion Lambda).
- A licença do Remotion cobre o seu caso: pessoa física ou empresa de até 3 pessoas, ou empresa com
  a Company License. Veja [`references/licenca.md`](./references/licenca.md).

Fora disso, use o `pwdev-video-hyperframes` (Apache-2.0), que é o padrão da suíte.

## O que ele faz

- **Corte pela onda do áudio:** sem respiros, com a última tomada certa e o fim das palavras
  preservado. É o mesmo núcleo `pwdev-media` do plugin HyperFrames.
- **Na tela:**
  - legenda de até 3 palavras com a palavra falada em destaque;
  - zooms suaves;
  - rótulos e títulos dentro da zona segura;
  - cenas sob medida em componentes React (`compositions/*.tsx`).
- **Som:** trilha com fade e efeitos no quadro do movimento.
- **Revisão:** Remotion Studio em segundo plano, quadros em PNG para conferir e render com o portão
  de qualidade **PASSOU**.

## Instalação

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-video-remotion@pwdev-claude-marketplace
```

Numa conversa nova: `/pwdev-video-remotion:init` (Codex: `$vrm-setup`). Ele confere, sem sudo:
- a licença;
- a CLI `pwdev-media`;
- o ffmpeg;
- o Node 20+;
- as skills oficiais do Remotion.

Cada projeto roda `npm install` uma vez (~1 min). O primeiro render baixa o Chrome Headless Shell
(~170 MB).

## Manual de uso

1. **Editar:** "edita o vídeo da pasta ~/Videos/anuncio em Remotion" (`/pwdev-video-remotion:editar`).
2. **Corte:** a IA corta, planeja e abre uma amostra de 8–15 s no Remotion Studio
   (http://localhost:3123). Peça ajustes em palavras do dia a dia.
3. **Cenas:** "anima os três passos" vira um componente em `compositions/`, entrando na palavra certa.
4. **Vídeo final:** fica em `<projeto>/renders/<nome>.mp4`, entregue só com PASSOU.

| Comando (Claude Code) | Codex / Hermes | Para quê |
|---|---|---|
| `/pwdev-video-remotion:init` · `:status` | `$vrm-setup` | licença e ferramentas |
| `:editar` | `$vrm-editar` | edição completa (comece aqui) |
| `:corte` | `$vrm-corte` | só o corte, ou ajustar o corte |
| `:plano` | `$vrm-plano` | o que aparece em cada momento |
| `:cenas` | `$vrm-cenas` | cena sob medida em React |
| `:som` | `$vrm-som` | trilha e efeitos |
| `:revisar` | `$vrm-revisar` | vídeo inteiro, render e entrega |
| `:versoes` | `$vrm-variacoes` | ganchos, formatos, versões e lote por planilha |

## Como funciona por dentro

```
projeto.json ─▶ pwdev-media video plano-render ─▶ build.py ─▶ src/dados.json + public/
             ─▶ src/Video.tsx (Remotion) ─▶ render ─▶ portão PASSOU
```

- **Projeto:** `projeto.json` (`pwdev-projeto-video/1`) é o mesmo do HyperFrames. As cenas `.tsx`
  são as únicas peças específicas do motor.
- **Versões fixas:** Remotion 4.0.535, React 19.3.1 e TypeScript 5.9.3, exatas no `package.json`.
- **Referências:** [`references/projeto.md`](./references/projeto.md) e
  [`references/regras.md`](./references/regras.md).

## Segurança

- Nunca altera, move ou apaga os vídeos originais; a mídia é copiada para `public/` do projeto.
- Tudo roda no seu computador. Geração por IA só pelo `pwdev-media`, com estimativa e "sim".
- O render é determinístico: as cenas não usam relógio, aleatório nem rede (os testes conferem).
- A licença do Remotion é verificada antes do primeiro projeto.

## Para quem desenvolve

```bash
python3 -m unittest tests.test_pwdev_video_remotion tests.test_pwdev_media_video
PWDEV_E2E=1 python3 -m unittest tests.test_pwdev_video_remotion   # + npm install e TypeScript
claude plugin validate plugins/pwdev-video-remotion
hermes plugins doctor --ci plugins/pwdev-video-remotion
```

## Licença

O plugin e o template são Apache-2.0. Os pacotes `remotion` e `@remotion/*` instalados no projeto
seguem a licença do Remotion. A fonte Montserrat segue a SIL Open Font License.
