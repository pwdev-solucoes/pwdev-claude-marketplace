# Provedores, chaves e códigos de saída

## Adaptadores desta versão

| Provedor | Variável / Keychain | Operações | Contrato | Teste ao vivo (`status --ao-vivo`) |
|---|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` / `pwdev-media-openrouter` | `imagem` (`POST /api/v1/images`), `video` (`POST /api/v1/videos`, job assíncrono) | https://openrouter.ai/docs/guides/overview/multimodal/video-generation.md | `GET /api/v1/key` (grátis) |
| fal | `FAL_KEY` / `pwdev-media-fal` | qualquer modelo pela fila (`queue.fal.run/<slug>`) | https://fal.ai/docs/model-apis/model-endpoints/queue | sem teste gratuito |
| ElevenLabs | `ELEVENLABS_API_KEY` / `pwdev-media-elevenlabs` | `musica`, `sfx`, `tts` | https://elevenlabs.io/docs/api-reference | `GET /v1/user/subscription` (grátis) |
| BFL (FLUX) | `BFL_API_KEY` / `pwdev-media-bfl` | `imagem` (`POST /v1/<modelo>`, consulta pelo `polling_url`) | https://docs.bfl.ai/quick_start/generating_images | sem teste gratuito |
| Ideogram | `IDEOGRAM_API_KEY` / `pwdev-media-ideogram` | `imagem` (`POST /v2/image/generate/ideogram-3`, multipart) | https://developer.ideogram.ai/v2/api-reference/images/generate/ideogram-3 | sem teste gratuito |
| Leonardo | `LEONARDO_API_KEY` / `pwdev-media-leonardo` | `imagem` (REST v1 legado; `LEONARDO_MODEL_ID` opcional) | https://docs.leonardo.ai | `GET /api/rest/v1/me` (a confirmar) |
| Runway | `RUNWAYML_API_SECRET` (aceita `RUNWAY_API_KEY`) / `pwdev-media-runway` | `video` a partir de imagem (`POST /v1/image_to_video`, `GET /v1/tasks/{id}`) | https://docs.dev.runwayml.com/api/ | `GET /v1/organization` (a confirmar) |
| Magnific | `MAGNIFIC_API_KEY` (aceita `FREEPIK_API_KEY`) / `pwdev-media-magnific` | `upscale` (`POST /v1/ai/image-upscaler`, consulta em `/{task_id}`) | https://docs.magnific.com/api-reference/image-upscaler-creative/post-image-upscaler | sem teste gratuito |

"A confirmar": o contrato veio da versão anterior ou de exemplos do SDK e não está escrito por
inteiro na documentação pública lida; se a resposta não bater, a CLI para com erro claro (código 5).
O Leonardo documenta uma API v2 (`model` + `parameters`); a migração está pendente.

Ainda sem adaptador: Replicate, Kling direto, Higgsfield (`REPLICATE_API_TOKEN`, `KLING_API_KEY`,
`HIGGSFIELD_API_KEY` já são reconhecidas por `pwdev-media chaves`). Use o mesmo modelo por um
agregador (OpenRouter ou fal) ou o app do provedor. Item de **assinatura** de app não gera por API:
o `gerar` recusa e indica o item de API do mesmo provedor, quando houver.

## Entradas por tipo de geração

| Opção do `gerar` | Uso |
|---|---|
| `--aspect-ratio` | proporção (`9:16`, `4:5`; o Ideogram aceita `4x5`) |
| `--largura` / `--altura` | tamanho em px (BFL, Leonardo) |
| `--n`, `--seed` | quantidade e semente |
| `--imagem-inicial` | primeiro quadro do vídeo: URL ou arquivo local (vira data URI) |
| `--arquivo`, `--escala` | upscale: imagem local e `2x`, `4x`, `8x` ou `16x` |
| `--velocidade` | Ideogram: `TURBO`, `DEFAULT`, `QUALITY` |
| `--entrada '<json>'` | campos próprios de um modelo do fal |

Arquivo local de entrada entra na chave do cache pelo tamanho e pela data: editar o arquivo gera de
novo; o mesmo arquivo reaproveita o resultado sem custo.

## Ordem de leitura da chave

1. Variável de ambiente.
2. Keychain do macOS, serviço `pwdev-media-<provedor>` (gravado com `pwdev-media chaves guardar`).
3. Fora do macOS: só variável de ambiente (`setx` no Windows, perfil do shell no Linux).

## Itens do fal

O schema de entrada e de saída é próprio de cada modelo. O item do catálogo precisa ter o
`modelo` (slug do fal, ex.: `fal-ai/flux/schnell`); campos próprios vão em `--entrada '<json>'`.
Os arquivos de saída são todos os `url` encontrados no resultado.

## Códigos de saída da CLI

| Código | Significado | O que fazer |
|---|---|---|
| 0 | ok | — |
| 1 | conferência falhou (`catalogo validar`, `formatos conferir`, `video portao`) | ler a lista de problemas |
| 2 | uso errado (falta argumento, id inexistente) | corrigir o comando |
| 3 | chamada paga sem `--confirmar` | mostrar a estimativa e pedir o ok da pessoa |
| 4 | passaria do orçamento mensal | avisar; só seguir com ok explícito (`--acima-do-orcamento`) |
| 5 | erro do provedor, contrato mudou ou ffmpeg falhou | mostrar a mensagem; não tentar adivinhar o formato novo |
| 6 | sem chave ou sem ferramenta (ffmpeg) | pedir para a pessoa guardar a chave; `pwdev-media video ffmpeg --instalar` |
| 7 | operação ou provedor sem adaptador | sugerir outro item (`catalogo recomendar`) |
