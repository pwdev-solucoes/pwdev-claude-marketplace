# Provedores, chaves e códigos de saída

## Adaptadores desta versão

| Provedor | Variável / Keychain | Operações | Contrato | Teste ao vivo (`status --ao-vivo`) |
|---|---|---|---|---|
| OpenRouter | `OPENROUTER_API_KEY` / `pwdev-media-openrouter` | `imagem` (`POST /api/v1/images`), `video` (`POST /api/v1/videos`, job assíncrono) | https://openrouter.ai/docs/guides/overview/multimodal/video-generation.md | `GET /api/v1/key` (grátis) |
| fal | `FAL_KEY` / `pwdev-media-fal` | qualquer modelo pela fila (`queue.fal.run/<slug>`) | https://fal.ai/docs/model-apis/model-endpoints/queue | sem teste gratuito; a chave é testada na 1ª geração |
| ElevenLabs | `ELEVENLABS_API_KEY` / `pwdev-media-elevenlabs` | `musica` (`/v1/music`), `sfx` (`/v1/sound-generation`), `tts` (`/v1/text-to-speech/{voice_id}`) | https://elevenlabs.io/docs/api-reference | `GET /v1/user/subscription` (grátis) |

As outras chaves (`REPLICATE_API_TOKEN`, `RUNWAYML_API_SECRET`, `FREEPIK_API_KEY`, `KLING_API_KEY`,
`BFL_API_KEY`, `IDEOGRAM_API_KEY`, `LEONARDO_API_KEY`, `HIGGSFIELD_API_KEY`) já são reconhecidas
por `pwdev-media chaves`, mas os adaptadores diretos chegam em uma versão futura. Enquanto isso,
use o mesmo modelo por um agregador (OpenRouter ou fal) ou o app do provedor.

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
| 1 | conferência falhou (`catalogo validar`, `formatos conferir`) | ler a lista de problemas |
| 2 | uso errado (falta argumento, id inexistente) | corrigir o comando |
| 3 | chamada paga sem `--confirmar` | mostrar a estimativa e pedir o ok da pessoa |
| 4 | passaria do orçamento mensal | avisar; só seguir com ok explícito (`--acima-do-orcamento`) |
| 5 | erro do provedor ou contrato mudou | mostrar a mensagem; não tentar adivinhar o formato novo |
| 6 | sem chave | pedir para a pessoa guardar a chave |
| 7 | operação ou provedor sem adaptador | sugerir outro item (`catalogo recomendar`) |
