---
name: vrm-editar
description: >
  Use quando a pessoa pedir para editar um vídeo falado gravado no celular ou na câmera (anúncio,
  Reels, TikTok, VSL, aula, resposta) com Remotion — 'edita o vídeo da pasta X', 'tira as pausas
  e os erros', 'deixa dinâmico com legenda', 'faz um criativo com esse vídeo', 'continua a edição'.
  Conduz o fluxo inteiro: corte pela onda, plano em blocos, amostra no estúdio, vídeo completo,
  portão de qualidade e entrega. Não use para gerar vídeo do zero por IA (media-gerar), para vídeo
  em HyperFrames (pwdev-video-hyperframes) nem para tutorial de sistema (pwdev-video-tutorial).
metadata:
  version: 0.1.0
---

# Editar um vídeo falado com Remotion

Você é editor e diretor: as ferramentas medem e executam, você decide o que cortar, o que aparece
em cada momento e por quê. Leia antes de começar:

- `<plugin-root>/references/regras.md` (vale em toda etapa);
- `<plugin-root>/references/language.md` (como falar com a pessoa);
- `<plugin-root>/references/runtime.md` (ferramentas e caminhos `<VIDEOS>`, `<EDIT>`, `<PROJ>`).

## 0. Início

1. **Ferramentas:** `pwdev-media versao` e `pwdev-media video ffmpeg`. Faltou algo: `vrm-setup`.
2. **Vídeos:** ache a pasta (.mov, .mp4, .m4v, .mkv, .webm). Não está clara: pergunte. Arquivos
   espalhados: com o ok, copie para uma pasta nova; nunca mova os originais.
3. **Retomar ou começar:** se `<EDIT>/estado.md` existe, leia, conte em uma linha onde pararam e siga
   dali. Senão, crie `<EDIT>` e o `estado.md` (pedido, formato, estilo, etapa atual, decisões).
4. **No máximo uma pergunta**, só se não der para deduzir: "para que é esse vídeo?". Todo o resto
   tem padrão (`<plugin-root>/references/modelos.md`): formato do vídeo gravado, legenda conforme a
   receita, sem trilha se a pessoa não tiver música, nada de oferta que não esteja na fala. Conte
   as suposições numa frase.

## 1. Corte → `vrm-corte`

Transcrição, tomadas, EDL, corte pela onda, conferência. Modo automático: confira você mesmo e siga;
mostre o corte para aprovar só se a pessoa pediu.

## 2. Projeto

```bash
python3 '<plugin-root>/templates/projeto-remotion/build.py' novo '<PROJ>' --edit '<EDIT>' --formato <id> --nome <nome-curto>
python3 '<PROJ>/build.py' instalar     # npm install nas versões fixas (~1 min, uma vez por projeto)
```

Licença: antes do primeiro projeto de uma empresa, confira `<plugin-root>/references/licenca.md`
(Remotion é grátis só para pessoas e empresas de até 3 pessoas).

`<id>` vem de `pwdev-media formatos listar` (o do vídeo gravado: 9:16 em pé → `reels-9x16`).

## 3. Plano em blocos → `vrm-plano`

Divide a fala por ideia e decide o que aparece em cada bloco. Escreve `blocos` e `textos` no
`<PROJ>/projeto.json`.

## 4. Amostra (8 a 15 s)

Escolha um trecho com fala, legenda, ao menos uma peça e uma troca de enquadramento (nunca só a
abertura). Cenas sob medida: `vrm-cenas`. Som: `vrm-som`.

```bash
python3 '<PROJ>/build.py' amostra <inicio> <fim>
python3 '<PROJ>/build.py' checar
python3 '<PROJ>/build.py' estudio
```

Confira você primeiro, com som (`<plugin-root>/references/estudio.md`), depois mostre. Sem amostra
conferida, não monte o vídeo inteiro.

## 5. Vídeo inteiro e entrega → `vrm-revisar`

`completo`, conferência, render com portão. Só entregue com **PASSOU**.

## 6. Estado

Ao fim de cada etapa, atualize `<EDIT>/estado.md` (uma linha por decisão). Assim outra conversa
continua de onde esta parou.
