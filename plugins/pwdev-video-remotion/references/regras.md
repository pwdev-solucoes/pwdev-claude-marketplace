# Regras de edição

Valem em toda etapa. Quando uma regra não puder ser cumprida, diga qual e por quê na nota de
entrega.

## Fidelidade

- **A fala gravada manda.** Corte, legenda, texto, animação e som nascem da transcrição e da onda
  do áudio. Roteiro escrito só confere palavras. Tempo estimado não vale.
- **Nada inventado.** Número, nome, preço, prova, depoimento, tela, resultado e oferta só entram se
  estão na fala ou nos arquivos da pessoa. Faltou material: diga o que falta.
- **Originais intocáveis.** Nada é alterado, movido ou apagado na pasta dos vídeos brutos. Tudo o
  que é gerado fica na pasta `edit/` e na pasta do projeto, ao lado.

## Corte

- **Respiro é erro:** nenhum silêncio de 0,25 s ou mais no meio do vídeo; emendas com ~0,12 s.
- **A última tomada inteira é a certa.** Tomada abandonada no meio sai.
- **Nunca comer o fim da palavra.** As bordas são medidas na onda, com folga depois do último som.

## Tela

- **Uma ideia por vez.** Dois textos, ou texto e cena, nunca ao mesmo tempo (`projeto.json`
  reprova a sobreposição).
- **Tudo entra pela palavra:** texto, cena e som entram no tempo medido da palavra que os chama
  (pode antecipar até 0,15 s). Pegue os tempos com `pwdev-media video fala` e em
  `cut_timeline.json`, nunca de estimativa.
- **Ritmo:** algo muda na tela a cada 2 a 4 s (zoom, texto, cena). Cena de tela cheia sem a pessoa:
  no máximo uma a cada 15–20 s.
- **Rosto livre:** nada sobre olhos e boca. Peças sobre a pessoa ficam acima da cabeça.
- **Zona segura:** todo texto dentro da zona segura do formato (`pwdev-media formatos mostrar <id>`).
  O `build.py` já posiciona legenda e textos dentro dela.
- **Legenda:** até 3 palavras por vez; nenhuma palavra dita some dela (o portão confere).

## Som

- Cada animação tem o seu efeito, com o pico no quadro do movimento; sem animação, 5 ou 6 efeitos
  no vídeo todo, no máximo.
- Trilha 22 a 24 dB abaixo da voz (`volume_db` -22 a -24), entra e sai com fade.
- Trilha só se a pessoa tiver uma música ou autorizar gerar uma (custo, com `media-gerar`).

## Dinheiro e pausas obrigatórias

Pare e pergunte antes de: gastar dinheiro (imagem, vídeo, trilha ou efeito gerado por IA) e quando
uma técnica pedida não funcionar. Nunca peça de novo o que já foi autorizado nesta conversa.

## Entrega

O vídeo só é entregue quando `build.py render` imprime **PASSOU**. A nota de entrega lista: onde
ficou o arquivo, a duração, as suposições feitas e qualquer troca (fonte, técnica, material).
