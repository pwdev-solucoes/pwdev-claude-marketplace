# Cenas sob medida (Remotion)

Cada cena é um componente React em `compositions/<nome>.tsx`, escrito para aquele momento da fala,
com `export default` e as props `CenaProps` (`src/tipos.ts`). Ela entra no vídeo pelo `projeto.json`:

```json
"cenas": [{"inicio": 12.4, "fim": 15.8, "src": "compositions/contador-vendas.tsx", "sobre_a_pessoa": true}]
```

O `build.py montar` gera `src/cenas.generated.ts` com o import de cada cena citada. Modelo para
copiar: `exemplo-contador.tsx`.

Regras desta suíte, além das regras do Remotion (skills oficiais `remotion-dev/skills`):

- Tudo animado por `useCurrentFrame()`, `interpolate()` e `spring()`. Nada de CSS transition,
  `setTimeout`, `Date.now()`, `Math.random()` ou fetch: o render precisa ser determinístico.
- O tempo da cena começa em 0 no `inicio` dela: cada item entra em `palavra.inicio - cena.inicio`
  (tempos das palavras no `cut_timeline.json` da pasta edit).
- `sobreAPessoa`: fundo transparente, peça pequena, acima da cabeça, dentro de `zonaSegura`.
  Sem isso, a cena pode cobrir a tela inteira (no máximo uma a cada 15–20 s).
- Tamanhos multiplicados por `unidade` (1 em 1080 px), para a cena servir a qualquer formato.
- Nada de número, nome, prova ou oferta que não esteja na fala ou nos arquivos da pessoa.
- Uma cena `.tsx` não roda no HyperFrames, e uma `.html` não roda aqui. O resto do
  `projeto.json` é igual nos dois motores.
