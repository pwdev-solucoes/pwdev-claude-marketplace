---
name: social-entrega
description: >
  Use quando for exportar e entregar peças aprovadas — 'exportar', 'baixar as peças',
  'pacote final', 'entregar para publicação', 'handoff', 'mandar para o social'. Só exporta o que
  passou na revisão; monta o pacote com peças nomeadas, legendas, alt text e instruções. Nunca
  publica. Não use para revisar (social-revisao).
metadata:
  version: 3.0.0
---

# Export e Handoff

Runtime, subagentes e conectores: `<plugin-root>/references/runtime.md`. Idioma: `<plugin-root>/references/language.md`.

Você fecha o pacote. O que sai daqui é o que vai para a publicação.

## Princípio central

> Só sai de `04 — Aprovado`. Exportar de rascunho é como peça errada chega ao ar
> — o acidente mais comum e mais caro deste fluxo.

## Portão

Antes de exportar, verifique:

- [ ] `social-revisao` rodou e o veredito é APROVADO
- [ ] `social-alt-text` escrito para cada peça (carrossel: um por slide)
- [ ] Nenhum `[PREENCHER]` remanescente
- [ ] Peça está em `04 — Aprovado`
- [ ] Aprovador humano confirmou, se a seção 9 exigir

Falhou qualquer item: **não exporte**. Diga o que falta.

## Export

| Uso | Formato | Escala |
|---|---|---|
| Feed, stories | PNG | 1× (já em 1080) |
| Carrossel LinkedIn | PDF | 1× |
| Miniatura YouTube | JPG < 2 MB | 1× |
| Origem editável | link do Figma | — |

Exportar de vetor na escala certa é **sempre melhor** que exportar pequeno e
fazer upscale depois.

### Nomenclatura
```
{{campanha}}_{{plataforma}}_{{formato}}_{{n}}_{{versão}}.{{ext}}
```
Exemplo: `dashsaude-out_IG_4x5_01_v2.png`

Sem espaço, sem acento, sem maiúscula fora da versão. Nome de arquivo é o que
sobrevive quando o contexto se perde.

## Pacote

```
{{campanha}}/
├── pecas/
│   ├── dashsaude-out_IG_4x5_01_v2.png
│   └── ...
├── legendas.md          copy por peça, pronta para colar
├── alt-text.md          alt por peça (e por slide)
├── publicacao.md        canal, data, ordem, observações
└── origem.md            links do Figma
```

Legenda e alt **junto** da peça. Alt que chega depois não é aplicado — é a falha
de acessibilidade mais comum e a mais fácil de evitar.

## Instruções de publicação

Para cada peça: canal, formato, data e hora sugeridas, legenda, alt, primeiro
comentário se houver, hashtags, e a ordem quando for sequência.

## Publicação

Este plugin **não publica**. Publicar é ato externo e irreversível, e depende de
credencial que o plugin não deve manipular.

Mesmo com MCP de publicação conectado no futuro, a regra permanece: confirmação
explícita do usuário antes de cada publicação, nunca em lote automático.

## Formato de saída

```
Pacote: {{caminho}}
Peças: {{n}} exportadas
Formatos: {{lista}}
Revisão: APROVADO em {{data}}
Alt text: {{n}}/{{n}} escritos
Pendências: {{lista ou "nenhuma"}}
```

## Limites

- Não exporta peça não aprovada
- Não publica nem agenda
- Não corrige peça — devolve para `social-figma`
- Não escreve legenda — ver `pwdev-copy`

## Skills relacionadas

- `social-revisao` — portão anterior
- `social-alt-text` — entra no pacote
- `social-vault` — arquiva o pacote
