# APIs de Geração — contrato e operação

Este plugin opera com **orquestração de APIs no centro**. Nenhuma dessas
ferramentas tem MCP oficial conhecido: a integração é `Bash` + `curl`, via os
wrappers em `${CLAUDE_PLUGIN_ROOT}/scripts/`.

> **Aviso de contrato.** Endpoints, parâmetros e nomes de modelo mudam sem aviso.
> Os wrappers foram escritos para **falhar alto** quando o contrato muda, em vez
> de retornar silêncio. Se um script reclamar de "contrato pode ter mudado",
> confira a documentação oficial e corrija o script — não contorne.

---

## Ferramentas

| Ferramenta | Melhor para | Variável | Script |
|---|---|---|---|
| **Ideogram** | **imagem com texto legível** — único confiável nisso | `IDEOGRAM_API_KEY` | `gen-ideogram.sh` |
| **Leonardo** | ilustração, consistência de estilo de marca | `LEONARDO_API_KEY` | `gen-leonardo.sh` |
| **Flux (BFL)** | fotorrealismo | `BFL_API_KEY` | `gen-flux.sh` |
| **Runway** | vídeo a partir de imagem | `RUNWAY_API_KEY` | `gen-runway.sh` |
| **Freepik / Magnific** | upscale | `FREEPIK_API_KEY` | `upscale-freepik.sh` |

Documentação: developer.ideogram.ai · docs.leonardo.ai · docs.bfl.ai ·
docs.dev.runwayml.com · docs.freepik.com

---

## Escolha da ferramenta

| Necessidade | Ferramenta | Por quê |
|---|---|---|
| Peça com frase dentro da arte | **Ideogram** | os demais produzem texto deformado |
| Ilustração repetível na campanha | **Leonardo** | fixar modelo e referência de estilo |
| Foto que não existe | **Flux** | melhor fotorrealismo da lista |
| Animar uma peça estática | **Runway** | image-to-video |
| Imagem pequena demais | **Freepik** | mas veja o diagnóstico antes |

**Regra que economiza mais dinheiro que qualquer outra:** se a peça é texto
sobre cor sólida ou sobre foto que já existe, **não gere nada**. Isso é
composição — Figma resolve melhor, na hora, de graça.

---

## Custo

Não há tabela de preços neste arquivo, de propósito: preço muda e número errado
aqui vira decisão errada lá. Consulte o painel de cada ferramenta.

O que o plugin garante:

1. `--confirm` obrigatório em todo script que gasta — segunda linha de defesa
   além da instrução da skill
2. estimativa apresentada em **chamadas e variações**, não em reais inventados
3. manifesto de tudo que foi gerado, em `.pwdev-social/gerados/manifest.jsonl`
4. orçamento por campanha na seção 6 do contexto

**Vídeo é o item mais caro da stack, por larga margem.** Confirme duração e
quantidade antes de qualquer repetição.

---

## Manifesto

Toda geração registra uma linha em `manifest.jsonl`:

```json
{"ts":"...","ferramenta":"ideogram","modelo":"...","prompt":"...",
 "seed":"...","arquivo":"...","custo_estimado":"..."}
```

Sem isso não há reprodução nem auditoria: seis meses depois ninguém lembra qual
prompt gerou a peça que funcionou.

---

## Segurança

- Chave vive **apenas** em variável de ambiente
- **Nunca** gravar chave em arquivo do projeto, skill, log ou manifesto
- Os scripts nunca imprimem o valor da chave — só presença
- `check-keys.sh` reporta status sem revelar nada

---

## Modo prompt (sem chave)

Sem chave configurada, a skill entrega o **prompt otimizado** e declara
**"NÃO GERADO"**. Não simula resultado, não descreve imagem que não existe.

É um modo legítimo de operação, não uma falha: o prompt bem construído é
executável na interface web de qualquer uma das ferramentas.
