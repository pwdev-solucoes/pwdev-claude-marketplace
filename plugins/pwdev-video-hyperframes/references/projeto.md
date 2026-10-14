# projeto.json e build.py

`projeto.json` é o plano da edição, no schema `pwdev-projeto-video/1`, **o mesmo do
pwdev-video-remotion**: o mesmo plano renderiza nos dois motores. Tempos em segundos no corte
(`cut.mp4`). Valide sempre com `pwdev-media video projeto <projeto.json>`.

| Campo | O que é |
|---|---|
| `nome` | nome curto do vídeo; vira o nome do arquivo final |
| `edit` | pasta com `cut.mp4`, `cut_timeline.json`, `legendas.json` (caminho absoluto) |
| `formato` | id de `pwdev-media formatos listar` (`reels-9x16`, `feed-4x5`, `youtube-16x9`…) |
| `fps` | 30 (ou 24/60) |
| `estilo` | `fonte`, `texto`, `destaque`, `fundo` (cores em hex) |
| `legenda` | `ativa`, `estilo` (`discreta` · `destaque`), `max_palavras` (1–6, padrão 3), `y` (0–1) |
| `blocos` | enquadramento: `{inicio, fim, tipo: "tela_cheia", zoom: 1.0–2.0, origem: "50% 35%"}` |
| `textos` | `{inicio, fim, texto, tipo: "rotulo" · "titulo", posicao: "topo" · "centro" · "base"}` |
| `cenas` | `{inicio, fim, src: "compositions/<cena>.html", sobre_a_pessoa}` (sub-composições) |
| `audio` | `trilha: {arquivo, volume_db}` ou `null`; `efeitos: [{t, arquivo, volume_db}]` |
| `correcoes` | `{"palavra errada": "certa"}` para a legenda |
| `amostra` | `{inicio, fim}` enquanto revisa um trecho; `null` para o vídeo inteiro |

`origem` do zoom é o ponto que fica parado na tela: `50% 35%` mira o rosto de quem grava em pé
com a câmera na altura dos olhos. Ajuste olhando um quadro.

## build.py (fica dentro do projeto)

```bash
python3 '<PROJ>/build.py' montar                 # index.html a partir do projeto.json
python3 '<PROJ>/build.py' amostra 12.0 24.5      # só esse trecho (8 a 15 s)
python3 '<PROJ>/build.py' completo               # tira a amostra
python3 '<PROJ>/build.py' estudio                # monta e abre o estúdio em segundo plano
python3 '<PROJ>/build.py' estudio --parar
python3 '<PROJ>/build.py' hf check               # HyperFrames na versão fixa do projeto
python3 '<PROJ>/build.py' render [--qualidade draft|standard|high]
```

`render` monta, renderiza em `renders/<nome>.mp4` (ou `<nome>-amostra.mp4`) e roda o portão de
qualidade do pwdev-media. Sai com código 0 só quando o portão diz PASSOU.

O `index.html` é gerado: **nunca o edite à mão** (a próxima montagem apaga). Mude o
`projeto.json` ou uma cena em `compositions/` e rode `montar` de novo; o estúdio recarrega sozinho.

A versão do HyperFrames é fixa no `build.py` e no `package.json` do projeto. Nunca rode
`npx hyperframes` sem versão.
