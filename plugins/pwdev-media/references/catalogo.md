# Catálogo de modelos e aplicativos

Arquivo de trabalho: `~/.pwdev/media/catalogo.json` (criado da semente que vem no plugin, em
`<plugin-root>/engine/src/pwdev_media/data/catalogo.json`). Schema `pwdev-media-catalogo/1`.

## Categorias

| id | O que cobre |
|---|---|
| `imagem-gerar` | gerar e editar imagem |
| `imagem-upscale` | upscale e restauração de imagem |
| `imagem-recorte` | tirar fundo, recortar |
| `video-gerar` | texto ou imagem para vídeo |
| `video-upscale` | upscale e interpolação de vídeo |
| `video-lipsync` | lip sync e dublagem |
| `video-recorte` | recortar a pessoa do fundo (tela verde sem pano) |
| `audio-voz-limpa` | tirar ruído e isolar a voz |
| `audio-trilha` | trilha musical |
| `audio-sfx` | efeitos sonoros |
| `audio-tts` | voz sintética, narração |
| `transcricao` | fala para texto com tempo por palavra |
| `llm-visao` | direção, roteiro e conferência de quadros |
| `motor-render` | HyperFrames, Remotion, FFmpeg |

## Campos de um item

| Campo | Tipo | Quem escreve |
|---|---|---|
| `id` | `provedor:modelo` | curadoria ou descoberta |
| `categoria`, `provedor`, `via` (`agregador` · `api` · `assinatura` · `local`) | texto | curadoria ou descoberta |
| `operacao` | `imagem` · `video` · `musica` · `sfx` · `tts` · `upscale` · `lipsync` · `recorte` · `voz-limpa` · `transcricao` · `llm` · `render` | curadoria |
| `modelo` | slug usado na API; `null` = ainda não dá para gerar | curadoria ou descoberta |
| `preco` | `{valor, unidade, moeda, fonte, verificado_em}`; `valor: null` = desconhecido | descoberta (ou curadoria com fonte) |
| `qualidade` | 1 a 5; `null` = sem nota, não entra em recomendação | **curadoria** |
| `licenca_comercial` | `sim` · `nao` · `a_verificar` | **curadoria** |
| `exige_rotulo_ia` | marcar como conteúdo de IA ao publicar | **curadoria** |
| `limites` | durações, resoluções, proporções | descoberta |
| `status` | `ativo` · `beta` · `deprecado` · `removido` | descoberta |
| `origem` | `curado` · `descoberto` | — |
| `url`, `notas` | página de preço/uso e observações | **curadoria** |

A descoberta **nunca** sobrescreve campo de curadoria e **nunca** apaga item: o que some da fonte
vira `removido` e volta a `ativo` se reaparecer.

## Regras de curadoria

- Preço com valor precisa de `fonte` (URL) e `verificado_em`. Sem fonte, `valor: null`.
- Fontes de terceiros que divergem: anote a faixa em `notas` e use o valor mais conservador.
- `licenca_comercial: sim` só quando os termos do provedor garantem uso comercial da saída em
  plano pago. Modelo aberto com pesos não comerciais (ex.: MusicGen, CC-BY-NC) é `nao`.
- Música sem API oficial e com licença em disputa (Suno, Udio) fica `a_verificar` e fora do uso
  automático.
- Item novo vindo da descoberta entra sem `qualidade`: dê a nota só depois de testar.

## Recomendação por objetivo

`pwdev-media catalogo recomendar --categoria <id> --objetivo barato|equilibrado|maximo`

- `barato`: qualidade ≥ 3, ordenado pelo menor preço por uso.
- `equilibrado` (padrão): qualidade ≥ 4 pelo menor preço, depois o resto.
- `maximo`: maior qualidade, depois menor preço.

Preço de assinatura (por mês ou ano) não é comparável com preço por uso: vai para o fim da lista.
Por padrão só entram itens com licença comercial `sim` (`--incluir-sem-licenca` muda isso) e com
nota de qualidade. `--so-com-chave` limita aos provedores que a pessoa já configurou.

Para editar a curadoria, edite `~/.pwdev/media/catalogo.json` e rode `pwdev-media catalogo validar`.
Para propor mudança na semente do plugin, edite o arquivo da semente e rode os testes.
