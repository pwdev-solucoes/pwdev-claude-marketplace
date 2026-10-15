# Remotion Studio

O estúdio é onde a pessoa revê a edição antes do render: player e linha do tempo com uma faixa por
sequência (cenas, textos, legendas, trilha, efeitos).

```bash
python3 '<PROJ>/build.py' estudio            # monta e abre em segundo plano em http://localhost:3123
python3 '<PROJ>/build.py' estudio --status
python3 '<PROJ>/build.py' estudio --parar    # ao terminar a revisão
```

O estúdio roda desacoplado da sessão (log em `<PROJ>/.pwdev/estudio.log`), então não some quando o
comando termina. Pare sempre ao fim da revisão.

## Como revisar

1. Abra no trecho da amostra e **toque com som**: quadro parado confere posição, não sincronia.
2. Confira: cada coisa entra na palavra, nada cobre o rosto, dá para ler no tamanho do celular.
3. Pedido pequeno (texto, posição, cor, tempo): mude o `projeto.json` ou a cena e rode `montar`; o
   estúdio recarrega sozinho.
4. Para mostrar sem estúdio (Codex sem navegador, por exemplo): `python3 '<PROJ>/build.py' quadro <s>`
   gera o PNG de um quadro (segundos contados no início da amostra, se houver amostra).

O arquivo renderizado é a referência final.
