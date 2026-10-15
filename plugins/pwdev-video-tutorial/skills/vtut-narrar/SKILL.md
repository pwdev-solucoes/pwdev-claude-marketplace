---
name: vtut-narrar
description: >
  Use quando for gerar ou trocar a narração de um vídeo tutorial — 'narra o roteiro', 'gera a voz',
  'quero voz masculina', 'usa a minha voz', 'voz mais natural', 'troca a narração'. Gera a fala de
  cada cena com a voz local em português (grátis), importa áudios gravados pela pessoa ou usa a
  ElevenLabs pelo pwdev-media com estimativa e "sim", e mede a duração de cada cena para a
  gravação. Não use para escrever o roteiro (vtut-roteiro) nem para gravar a tela (vtut-gravar).
metadata:
  version: 0.1.0
---

# Narração

Runtime: `<plugin-root>/references/runtime.md`. A narração vem **antes** da gravação: a gravação
segura cada cena pelo tempo da fala dela.

## Opções (recomende a 1 para começar)

1. **Voz local, grátis** (Kokoro): `pf_dora` (feminina), `pm_alex` ou `pm_santa` (masculinas).

   ```bash
   python3 '<plugin-root>/scripts/tutorial.py' narrar '<V>/roteiro.json' --pasta '<V>' --voz pf_dora [--velocidade 1.05]
   ```

2. **Voz da pessoa:** ela grava um arquivo por cena com o nome do id (`C01.m4a`, `C02.m4a`…) lendo
   a fala do `roteiro.md`; depois

   ```bash
   python3 '<plugin-root>/scripts/tutorial.py' narrar '<V>/roteiro.json' --pasta '<V>' --de-arquivos '<pasta-dos-audios>'
   ```

3. **ElevenLabs (paga):** por cena, `pwdev-media gerar elevenlabs:tts --prompt '<fala>' --voz <voice_id>
   --estimar`; mostre o total, espere o "sim", gere com `--confirmar --saida '<pasta>'`, renomeie para
   `<id>.mp3` e importe com `--de-arquivos`.

## Conferir

Ouça (ou peça para a pessoa ouvir) 2 cenas: pronúncia de nomes do sistema, ritmo, volume. Nome mal
pronunciado: escreva como se fala na `narracao` (ex.: "Ê-erre-pê" para "ERP") e gere de novo só
aquela cena. Próximo: `vtut-gravar`.
