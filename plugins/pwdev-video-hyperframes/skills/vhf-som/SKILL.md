---
name: vhf-som
description: >
  Use quando o vídeo precisar de trilha ou efeitos sonoros, ou de ajuste no som — 'põe uma música',
  'trilha animada', 'efeito no texto', 'whoosh na transição', 'a música está alta', 'tira o
  efeito'. Escolhe e posiciona efeitos no quadro do movimento e a trilha 22–24 dB abaixo da voz,
  gerando por IA só com o ok e a estimativa de custo. Não use para limpar ruído da gravação (fase
  futura) nem para cortar (vhf-corte).
metadata:
  version: 0.2.0
---

# Trilha e efeitos

Regras: `<plugin-root>/references/regras.md` (seção Som).

## 1. De onde vem o som

1. Arquivo da pessoa (música ou efeitos que ela tem direito de usar): pergunte o caminho.
2. Gerado por IA, só com o ok: `media-gerar` do pwdev-media (ElevenLabs Music ou Sound Effects).
   Mostre a estimativa antes. Anúncio: a licença comercial tem de ser "sim" no catálogo.
3. Sem nenhum dos dois: entregue sem trilha e diga numa frase que dá para pôr depois.

## 2. Efeitos

- Um efeito por animação, no tempo do movimento (o `inicio` do texto ou a entrada da peça na cena).
- Sem animação: 5 ou 6 efeitos no vídeo todo, no máximo.
- `volume_db` de -14 a -10; nunca mais alto que a voz.

```json
"audio": {"efeitos": [{"t": 3.42, "arquivo": "/abs/whoosh.mp3", "volume_db": -12}]}
```

## 3. Trilha

```json
"audio": {"trilha": {"arquivo": "/abs/trilha.mp3", "volume_db": -23}}
```

Entra com fade de 0,5 s e sai com fade de 1 s. Trilha mais curta que o vídeo: avise e escolha outra
ou gere com a duração do corte.

## 4. Conferir

```bash
python3 '<PROJ>/build.py' amostra <inicio> <fim>
python3 '<PROJ>/build.py' render --qualidade draft
```

Ouça a amostra: a voz continua clara? O efeito bate no movimento? O portão do render avisa volume
fora da faixa das redes.
