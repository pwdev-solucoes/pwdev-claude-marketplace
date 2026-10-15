# Geração paga — itens, chaves e operação

Desde a v3, nenhuma chamada paga sai deste plugin: tudo passa pela CLI `pwdev-media` (plugin
pwdev-media ≥ 0.4.0), que guarda as chaves, estima o custo pelo catálogo, exige confirmação, respeita o
orçamento mensal, registra o ledger e falha alto quando o contrato de uma API muda.

> **Aviso de contrato.** Endpoints e parâmetros mudam sem aviso. O `pwdev-media` sai com código 5 e a
> mensagem da API quando isso acontece. **Pare e reporte** — não contorne com outra chamada.

---

## Itens do catálogo

| Necessidade | Item | Parâmetros principais | Chave |
|---|---|---|---|
| **Imagem com texto legível** | `ideogram:ideogram-3` | `--aspect-ratio 4x5` · `--n` · `--seed` | `IDEOGRAM_API_KEY` |
| Fotorrealismo | `bfl:flux-2-pro`, `bfl:flux-pro-1.1` | `--largura --altura` ou `--aspect-ratio` · `--seed` | `BFL_API_KEY` |
| Ilustração, estilo de marca | `leonardo:conta` | `--largura --altura --n` (modelo da conta: `LEONARDO_MODEL_ID`) | `LEONARDO_API_KEY` |
| Animar imagem aprovada | `runway:gen4_turbo` | `--imagem-inicial` · `--duration` · `--aspect-ratio 720:1280` | `RUNWAYML_API_SECRET` (aceita `RUNWAY_API_KEY`) |
| Upscale | `magnific:upscale` | `--arquivo` · `--escala 2x\|4x\|8x\|16x` | `MAGNIFIC_API_KEY` (aceita `FREEPIK_API_KEY`) |
| Melhor custo com as chaves que existem | `pwdev-media catalogo recomendar --categoria imagem-gerar --so-com-chave` | — | OpenRouter, fal |

Detalhes, preço com fonte e data, licença comercial: `pwdev-media catalogo mostrar <item>`.

**Regra que economiza mais dinheiro que qualquer outra:** se a peça é texto sobre cor sólida ou sobre
foto que já existe, **não gere nada**. Isso é composição — Figma resolve melhor, na hora, de graça.

---

## Operação

```bash
pwdev-media gerar <item> --prompt '<texto>' [parâmetros] --saida '.pwdev-social/gerados/<AAAA-MM-DD>-<slug>' --estimar
# mostrar a estimativa · esperar o "sim" explícito
pwdev-media gerar <item> --prompt '<texto>' [parâmetros] --saida '.pwdev-social/gerados/<AAAA-MM-DD>-<slug>' --confirmar
```

| Código | Significado | O que fazer |
|---|---|---|
| 0 | gerado (ou reaproveitado do cache, sem custo) | seguir para a curadoria |
| 3 | chamada paga sem `--confirmar` | mostrar a estimativa e pedir o "sim" |
| 4 | passaria do orçamento mensal | avisar; só com o "sim" usar `--acima-do-orcamento` |
| 5 | erro do provedor ou contrato mudou | parar e reportar a mensagem |
| 6 | sem chave | modo prompt, ou `social-contexto` para guardar a chave |
| 7 | item sem adaptador | escolher outro item (`pwdev-media catalogo recomendar`) |

## Custo

Estimativa em dólares vem do catálogo, sempre com fonte e data; item sem preço é estimado em chamadas
e o provedor informa o custo real depois. Gasto: `pwdev-media custo extrato`. Teto mensal:
`pwdev-media custo orcamento <valor>`.

**Vídeo é o item mais caro da stack, por larga margem.** Confirme duração e quantidade separadamente.

## Registro

O ledger do `pwdev-media` guarda item, custo e arquivos de cada geração; os arquivos de cada campanha
ficam em `.pwdev-social/gerados/<data>-<slug>/`. A seed da peça aprovada vai para a seção 6 do contexto
e para a biblioteca de prompts (`social-vault`).

## Segurança

- Chave no Keychain (`pwdev-media chaves guardar <provedor>`) ou em variável de ambiente
- **Nunca** gravar chave em arquivo do projeto, skill, log ou contexto
- `pwdev-media status` só diz **onde** a chave está, nunca o valor

## Modo prompt (sem chave)

Sem chave, a skill entrega o **prompt otimizado** e declara **"NÃO GERADO"**. Não simula resultado. É
um modo legítimo: o prompt roda na interface web de qualquer uma das ferramentas.
