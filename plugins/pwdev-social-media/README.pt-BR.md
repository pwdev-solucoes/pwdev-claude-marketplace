# PWDEV Social Media — Criativos por IA

Produção de criativos para redes sociais com geração por IA no centro, para Claude Code, Codex e Hermes
Agent. Da copy aprovada à peça entregue:
- conceito, triagem de custo e prompt;
- geração com estimativa e confirmação;
- curadoria e composição no Figma (opcional);
- todos os formatos, revisão de acessibilidade e pacote de entrega.

Complementa o `pwdev-copy` — lá o texto, aqui a peça. Toda chamada paga passa pelo núcleo
[`pwdev-media`](../pwdev-media/README.pt-BR.md).

## Instalação

```bash
claude plugin install pwdev-media@pwdev-claude-marketplace
claude plugin install pwdev-social-media@pwdev-claude-marketplace
```

Numa conversa nova: `/pwdev-social-media:init` (Codex: `$social-contexto`; Hermes:
`skill_view("pwdev-social-media:social-contexto")`). A configuração:
- cria o contexto da marca (`.claude/pwdev-social-context.md`);
- confere o `pwdev-media` (0.4.0 ou mais novo);
- extrai o brand kit do Figma, quando conectado;
- guarda as chaves no Keychain. Você mesmo digita, a IA nunca vê:

```bash
pwdev-media chaves guardar ideogram    # imagem com texto legível
pwdev-media chaves guardar bfl         # Flux — fotorrealismo
pwdev-media chaves guardar leonardo    # ilustração de marca
pwdev-media chaves guardar runway      # vídeo a partir de imagem
pwdev-media chaves guardar magnific    # upscale
pwdev-media chaves guardar openrouter  # agregador (opcional)
```

**Sem chave o plugin funciona em modo prompt:** entrega o prompt otimizado para execução manual.

## Manual de uso

1. **Configurar uma vez:** `/pwdev-social-media:init`. Diga a organização, o Figma (opcional), os
   formatos que você mantém e as restrições (setor público muda o contraste exigido).
2. **Produzir a partir da copy aprovada:** "cria os criativos desta campanha"
   (`/pwdev-social-media:criar`). A IA:
   - propõe o conceito e a triagem: o que **não** precisa ser gerado;
   - mostra o custo estimado e **espera o seu "sim"**;
   - gera 2 variações e monta a grade de comparação;
   - registra a seed da escolhida.
3. **Compor:** com o Figma conectado, a peça é montada com tokens e Auto Layout. Sem Figma, você recebe
   a especificação em camadas.
4. **Todos os formatos:** "adapta para 9:16, 4:5, 1:1 e 16:9" (`/pwdev-social-media:formatos`). Cada
   texto é conferido na zona segura de cada rede.
5. **Lote de teste:** "3 ganchos × 2 visuais em 4:5" (`/pwdev-social-media:lote`). O custo do lote
   inteiro aparece antes de qualquer geração, e as versões vão para uma planilha CSV.
6. **Revisar e entregar:** `/pwdev-social-media:revisar` e depois `/pwdev-social-media:exportar`. O
   pacote leva peças nomeadas, legendas, alt text e instruções. **O plugin nunca publica.**
7. **Vídeo:**
   - `/pwdev-social-media:video` gera o clipe por IA (Runway) a partir de uma imagem aprovada.
   - Vídeo gravado com legenda e animações vai para o `pwdev-video-hyperframes`: a skill
     `social-video-curto` encaminha.

## Comandos

| Claude Code | Codex | Hermes (`skill_view`) | Para quê |
|---|---|---|---|
| `/pwdev-social-media:init` · `:status` | `$social-contexto` | `pwdev-social-media:social-contexto` | contexto, chaves, modo atual |
| `:criar` | `$social-criar` | `…:social-criar` | produção de ponta a ponta |
| `:gerar` | `$social-imagem` | `…:social-imagem` | um ativo gerado por IA |
| `:carrossel` | `$social-carrossel` | `…:social-carrossel` | carrossel completo |
| `:video` | `$social-video` | `…:social-video` | roteiro, storyboard e clipe por IA |
| `:revisar` | `$social-revisao` | `…:social-revisao` | portão de qualidade |
| `:exportar` | `$social-entrega` | `…:social-entrega` | pacote de entrega |
| `:custo` | `$social-custo` | `…:social-custo` | estimativa, orçamento, gasto |
| `:formatos` | `$social-formatos` | `…:social-formatos` | tamanhos, zonas seguras, todos os formatos |
| `:lote` | `$social-lote` | `…:social-lote` | matriz de versões para teste |

**Skills de apoio:** `social-conceito`, `social-prompt`, `social-consistencia`, `social-curadoria`,
`social-upscale`, `social-figma`, `social-post`, `social-reels`, `social-marca`, `social-alt-text`,
`social-vault`, `social-video-curto`.

**Subagentes (Claude Code):** `art-director` (conceito), `asset-generator` (geração paga),
`figma-builder` (composição) e `creative-reviewer` (revisão). No Codex e no Hermes os mesmos passos
rodam na própria conversa.

## Pipeline

```
copy aprovada (pwdev-copy)
  → conceito + triagem de ativos                      social-conceito
  → estimativa (pwdev-media gerar --estimar) → "sim"  social-custo
  → geração (pwdev-media gerar --confirmar)           social-imagem / social-video
  → curadoria + seed                                  social-curadoria
  → composição (opcional) + formatos                  social-figma / social-formatos
  → revisão + alt text                                social-revisao / social-alt-text
  → entrega                                           social-entrega
```

## Segurança

- **Dinheiro:**
  - nenhuma geração sem `--estimar` antes e o seu "sim" explícito na conversa;
  - o `pwdev-media` exige `--confirmar` e respeita o orçamento mensal (`pwdev-media custo orcamento`);
  - pedido idêntico já gerado é reaproveitado sem custo.
- **Chaves:** ficam no Keychain ou no ambiente, nunca em arquivo do projeto, no contexto ou na conversa.
- **Não simula:** sem chave ou sem Figma, declara "NÃO GERADO" ou "não montado" e entrega o prompt ou
  a especificação.
- **Conteúdo:**
  - nada de rosto de pessoa real, estilo de artista vivo ou cena que imite registro real;
  - em setor público, imagem gerada não representa serviço nem pessoa.
- **Acessibilidade é portão:** contraste, zona segura e alt text reprovam a peça.
- **Não publica.**

## Migração da v2

- **Instalação:** instale o `pwdev-media` e rode `/pwdev-social-media:init` para guardar as chaves no
  Keychain. As variáveis antigas continuam aceitas, inclusive `RUNWAY_API_KEY` e `FREEPIK_API_KEY`.
- **Scripts:** os de `scripts/` saíram. As tabelas de equivalência estão no
  [`CHANGELOG.md`](./CHANGELOG.md).
- **Nomes:** os comandos do Claude Code não mudaram. As skills ganharam o prefixo `social-`, o que só
  importa se você as chamava pelo nome.
- **Registro de gastos:** o histórico de `.pwdev-social/gerados/manifest.jsonl` continua no disco. As
  gerações novas vão para o ledger do `pwdev-media`.

## Para quem desenvolve

```bash
python3 -m unittest tests.test_pwdev_social_media
claude plugin validate plugins/pwdev-social-media
hermes plugins doctor --ci plugins/pwdev-social-media
```

## Créditos

Deriva de [social-media-skills](https://github.com/blacktwist/social-media-skills) (MIT). Detalhes em
`NOTICE.md`. Licença Apache-2.0.
