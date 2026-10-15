# projeto.json e build.py (Remotion)

`projeto.json` é o plano da edição no schema `pwdev-projeto-video/1`, **o mesmo do
pwdev-video-hyperframes**. Tempos em segundos no corte (`cut.mp4`). Valide sempre com
`pwdev-media video projeto <projeto.json>`.

| Campo | O que é |
|---|---|
| `nome` | nome curto do vídeo; vira o nome do arquivo final |
| `edit` | pasta com `cut.mp4`, `cut_timeline.json`, `legendas.json` (caminho absoluto) |
| `formato` | id de `pwdev-media formatos listar` (`reels-9x16`, `feed-4x5`, `youtube-16x9`…) |
| `fps` | 30 (ou 24/60) |
| `estilo` | `fonte`, `texto`, `destaque`, `fundo` (cores em hex) |
| `legenda` | `ativa`, `estilo` (`discreta` · `destaque` · `caixa` — faixa escura, para gravação de tela), `max_palavras` (1–6, padrão 3), `y` (0–1) |
| `blocos` | enquadramento: `{inicio, fim, tipo: "tela_cheia", zoom: 1.0–2.0, origem: "50% 35%"}` |
| `textos` | `{inicio, fim, texto, tipo: "rotulo" · "titulo", posicao: "topo" · "centro" · "base"}` |
| `cenas` | `{inicio, fim, src: "compositions/<cena>.tsx", sobre_a_pessoa}` (componentes React) |
| `audio` | `trilha: {arquivo, volume_db}` ou `null`; `efeitos: [{t, arquivo, volume_db}]` |
| `correcoes` | `{"palavra errada": "certa"}` para a legenda |
| `amostra` | `{inicio, fim}` enquanto revisa um trecho; `null` para o vídeo inteiro |

## Como o projeto é montado

```
projeto.json ─▶ pwdev-media video plano-render ─▶ src/dados.json + public/ ─▶ src/Video.tsx ─▶ render
```

O núcleo resolve janela de amostra, correções, zona segura e volumes; o `build.py` copia a mídia para
`public/`, grava `src/dados.json` e `src/cenas.generated.ts`. **Nunca edite esses dois arquivos à
mão** (a próxima montagem apaga). O visual base (legenda, textos, zoom) está em `src/Video.tsx`; mudar
o visual de todos os vídeos de um projeto é editar esse arquivo.

## build.py (fica dentro do projeto)

```bash
python3 '<PROJ>/build.py' instalar               # npm install nas versões fixas (uma vez)
python3 '<PROJ>/build.py' montar                 # dados.json a partir do projeto.json
python3 '<PROJ>/build.py' amostra 12.0 24.5      # só esse trecho (8 a 15 s)
python3 '<PROJ>/build.py' completo               # tira a amostra
python3 '<PROJ>/build.py' checar                 # TypeScript + composição encontrada
python3 '<PROJ>/build.py' quadro 3.2             # PNG de um quadro em renders/quadros/
python3 '<PROJ>/build.py' estudio [--parar|--status]
python3 '<PROJ>/build.py' rm <args>              # CLI do Remotion na versão do projeto
python3 '<PROJ>/build.py' render [--qualidade rascunho|padrao|alta]
```

`render` monta, renderiza em `renders/<nome>.mp4` (ou `<nome>-amostra.mp4`) e roda o portão de
qualidade do pwdev-media. Sai com código 0 só quando o portão diz PASSOU.

Versões fixas no `package.json` (Remotion 4.0.535, React 19.3.1, TypeScript 5.9.3). Nunca rode
`npx remotion@latest` no projeto: use `build.py rm`.
