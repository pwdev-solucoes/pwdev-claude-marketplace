# Estúdio do HyperFrames

O estúdio é onde a pessoa revê a edição antes do render: player em cima e linha do tempo com uma
faixa por camada (fala, legenda, textos, cenas, trilha, efeitos).

```bash
python3 '<PROJ>/build.py' estudio            # monta e abre em segundo plano (seguro para agentes)
python3 '<PROJ>/build.py' estudio --status   # confere se está no ar
python3 '<PROJ>/build.py' estudio --parar    # ao terminar a revisão
```

Nunca deixe o estúdio rodando preso ao terminal da sessão (`npm run dev` em primeiro plano): ele
some quando a sessão fecha e o navegador fica sem resposta. Use sempre `estudio`.

## Como revisar

1. Abra no trecho da amostra e **toque com som**: quadro parado confere posição, não sincronia.
2. Confira: cada coisa entra na palavra, nada cobre o rosto, dá para ler no tamanho do celular.
3. Pedido pequeno (texto, posição, cor, tempo): mude o `projeto.json` ou a cena e rode `montar`;
   o estúdio recarrega, sem render.
4. Para mostrar sem estúdio (Codex sem navegador, por exemplo): `python3 '<PROJ>/build.py' hf snapshot`
   gera quadros-chave em PNG.

O arquivo renderizado é a referência final: o estúdio pode piscar uma camada numa emenda que o
render não tem.

## Telemetria

O HyperFrames coleta uso anônimo por padrão. O `build.py` desliga a telemetria nas chamadas dele
(`HYPERFRAMES_NO_TELEMETRY=1` e `DO_NOT_TRACK=1`). Para desligar de vez na máquina: `python3 '<PROJ>/build.py' hf telemetry disable`.
