# PWDEV Media

Núcleo da suíte pwdev de mídia. Uma CLI, `pwdev-media`, e seis skills portáveis (Claude Code,
Codex e Hermes Agent) que respondem três perguntas antes de qualquer geração por IA:

1. **Qual modelo ou app usar?** Catálogo por categoria, com preço, qualidade e licença comercial.
2. **Quanto vai custar?** Estimativa, confirmação obrigatória, orçamento mensal e ledger.
3. **Em que formato entregar?** Tamanhos e zonas seguras por plataforma.

Os plugins de vídeo (`pwdev-video-hyperframes`, `pwdev-video-remotion`, `pwdev-video-tutorial`)
e o `pwdev-social-media` v3 usam esta CLI.

## Instalação

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
```

Depois, numa conversa nova: `/pwdev-media:init` (Codex: `$media-setup`; Hermes:
`skill_view("pwdev-media:media-setup")`). A skill instala a CLI com
`uv tool install <plugin>/engine`, sem sudo, e guia a configuração das chaves.

Requisitos: Python 3.10+ e [uv](https://docs.astral.sh/uv/). A CLI só usa a biblioteca padrão.

## Comandos

| Claude Code | Codex / Hermes | O que faz |
|---|---|---|
| `/pwdev-media:init` | `$media-setup` | instala, guarda chaves, testa provedores |
| `/pwdev-media:status` | `$media-setup` | ferramentas, chaves (teste ao vivo), idade do catálogo, gasto |
| `/pwdev-media:catalogo` | `$media-catalogo` | "qual modelo usar para…", recomendação por objetivo |
| `/pwdev-media:atualizar` | `$media-atualizar` | atualiza o catálogo e mostra o que mudou; agenda opcional |
| `/pwdev-media:gerar` | `$media-gerar` | gera imagem, vídeo, trilha, efeito ou narração |
| `/pwdev-media:custo` | `$media-custo` | extrato e orçamento mensal |
| `/pwdev-media:formatos` | `$media-formatos` | formatos de criativos e zonas seguras |

## Manual rápido

**Configurar a primeira chave (OpenRouter).** Rode `/pwdev-media:init`. Quando a skill pedir,
digite `! pwdev-media chaves guardar openrouter`; a chave é digitada escondida e vai para o
Keychain. Ela nunca aparece na conversa.

**Escolher um modelo.** "Qual o modelo de vídeo mais barato para um clipe de 5 s em 9:16?" A
skill responde com uma tabela curta e uma recomendação. Na CLI:

```bash
pwdev-media catalogo recomendar --categoria video-gerar --objetivo barato
```

**Gerar.** "Gera um clipe de 5 s, 9:16, de uma xícara de café fumegando." A skill mostra a
estimativa e espera o seu "sim":

```bash
pwdev-media gerar openrouter:google/veo-3.1 --prompt '...' --duration 5 --aspect-ratio 9:16 --estimar
pwdev-media gerar openrouter:google/veo-3.1 --prompt '...' --duration 5 --aspect-ratio 9:16 --confirmar
```

**Controlar o gasto.** `pwdev-media custo orcamento 30` define US$ 30/mês. Uma geração que
passaria do teto é bloqueada até você confirmar de novo.

**Manter o catálogo em dia.** `/pwdev-media:atualizar` uma vez por mês, ou
`pwdev-media catalogo agendar --instalar` (macOS) para rodar sozinho no dia 1.

## Catálogo

14 categorias: imagem (gerar, upscale, recorte), vídeo (gerar, upscale, lip sync, recorte da
pessoa), áudio (limpar voz, trilha, efeitos, TTS), transcrição, LLM/visão e motores de render
(HyperFrames, Remotion, FFmpeg). Cada item diz se é **agregador** (OpenRouter, fal), **API** direta,
**assinatura** (Runway, Higgsfield, Magnific, Topaz, Adobe) ou **local** (grátis).

- Fica em `~/.pwdev/media/catalogo.json`, criado da semente do plugin.
- Preço só com fonte e data; sem fonte, fica "a verificar".
- A atualização busca o OpenRouter (modelos de vídeo e imagem) e o npm (HyperFrames, Remotion),
  **nunca** sobrescreve nota de qualidade, licença ou observações, e **nunca** apaga: o que some
  vira `removido`. Assinaturas sem API viram lembretes de conferência manual no relatório.

Detalhes e regras de curadoria: [`references/catalogo.md`](./references/catalogo.md).

## Provedores desta versão

| Provedor | Faz | Chave |
|---|---|---|
| OpenRouter | imagem e vídeo (Veo, Seedance, Wan, Sora…) | `OPENROUTER_API_KEY` |
| fal | qualquer modelo da fila (Kling, Hailuo, Flux, upscale…) | `FAL_KEY` |
| ElevenLabs | trilha, efeito sonoro e narração | `ELEVENLABS_API_KEY` |

Runway, Higgsfield, Magnific, Kling direto, BFL, Ideogram, Leonardo e Replicate já são reconhecidos
pelo gerenciador de chaves; os adaptadores diretos chegam numa versão futura. Detalhes e códigos
de saída: [`references/provedores.md`](./references/provedores.md).

## Segurança

- **Chaves:** lidas da variável de ambiente ou do Keychain do macOS (`pwdev-media-<provedor>`).
  Você digita a chave no seu terminal; a IA nunca vê o valor, e `status` só diz onde ela está.
- **Dinheiro:** nenhuma chamada paga sem `--confirmar`, que a skill só usa depois do seu "sim"
  nesta conversa. Orçamento mensal opcional; ledger em `~/.pwdev/media/ledger.jsonl`.
- **Cache:** o mesmo pedido já gerado é reaproveitado, sem pagar de novo.
- **Contrato de API:** se um provedor mudar o formato da resposta, a CLI para com erro claro.
- **Publicação:** a CLI lembra quando o conteúdo deve ser marcado como gerado por IA e avisa
  licença comercial diferente de "sim".

## Para quem desenvolve

```bash
python3 -m unittest tests.test_pwdev_media      # da raiz do marketplace, sem rede
claude plugin validate plugins/pwdev-media
hermes plugins doctor --ci plugins/pwdev-media
```

Adicionar um provedor: um módulo em `engine/src/pwdev_media/providers/` com `op_<operacao>` e
`ping`, registro em `providers/__init__.py`, variável em `keys.ENV`, testes com `FakeHttp`.
Adicionar uma categoria: `categorias` e itens na semente (`engine/src/pwdev_media/data/catalogo.json`),
depois `pwdev-media catalogo validar` e os testes.

## Licença

Apache-2.0.
