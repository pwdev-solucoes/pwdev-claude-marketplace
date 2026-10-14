# Cenas sob medida

Cada cena é uma sub-composição HyperFrames (`compositions/<nome>.html`) escrita para aquele
momento da fala, seguindo as skills oficiais do HyperFrames (`hyperframes-core`,
`hyperframes-animation`). Ela entra no vídeo pelo `projeto.json`:

```json
"cenas": [{"inicio": 12.4, "fim": 15.8, "src": "compositions/contador-vendas.html", "sobre_a_pessoa": true}]
```

Regras desta suíte, além das regras do HyperFrames:

- `data-composition-id` único, `data-width`/`data-height` iguais aos do projeto e timeline pausada
  registrada em `window.__timelines["<id>"]`.
- O tempo dentro da cena começa em 0 no `inicio` dela. Para a animação entrar na palavra certa,
  use o tempo da palavra no corte (`pwdev-media video fala` e `cut_timeline.json`) menos o `inicio`.
- `sobre_a_pessoa: true`: fundo transparente, peça pequena, acima da cabeça, dentro da zona segura.
  Sem isso, a cena cobre a tela inteira (no máximo uma a cada 15–20 s).
- Nada de número, nome, prova ou oferta que não esteja na fala ou nos arquivos da pessoa.
- Só lógica determinística: sem `Date.now()`, `Math.random()` ou fetch.
