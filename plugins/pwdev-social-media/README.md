# PWDEV Social Media — Produção de Criativos

Plugin de produção de criativos para redes sociais com **orquestração de APIs de
geração no centro**: Ideogram, Leonardo, Flux, Runway e Freepik/Magnific.

Figma entra como **camada opcional** de composição, para quando o time de design
precisa do arquivo editável.

Complementa o `pwdev-copy` — lá o texto, aqui a peça.

---

## Instalação

```
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-social-media
```

Chaves de API vão no ambiente, **nunca em arquivo do projeto**:

```bash
export IDEOGRAM_API_KEY=...    # imagem com texto legível
export LEONARDO_API_KEY=...    # ilustração de marca
export BFL_API_KEY=...         # Flux — fotorrealismo
export RUNWAY_API_KEY=...      # vídeo
export FREEPIK_API_KEY=...     # upscale/Magnific
```

Confira com `scripts/check-keys.sh`. **Sem chave o plugin funciona em modo
prompt** — entrega o prompt otimizado para execução manual.

## Primeiro uso

```
/pwdev-social:init      # brand kit, formatos, chaves, restrições
/pwdev-social:gerar     # triagem → prompt → custo → geração → curadoria
/pwdev-social:criar     # produção end-to-end
```

---

## Pipeline

```
copy aprovada (pwdev-copy)
      ↓
conceito + triagem de ativos      art-director
      ↓
[CONFIRMAÇÃO DE CUSTO]            cost-control
      ↓
prompt → geração via API          asset-generator   ← núcleo
      ↓
curadoria das variações           asset-curation    ← Artifact para aprovação
      ↓
composição                        figma-builder     ← OPCIONAL
      ↓
revisão                           creative-reviewer
      ↓
export + handoff
```

### Comandos

| Comando | Função |
|---|---|
| `/pwdev-social:init` | Configura brand kit, formatos, chaves |
| `/pwdev-social:gerar` | Gera ativo — triagem, prompt, custo, curadoria |
| `/pwdev-social:criar` | Produção end-to-end |
| `/pwdev-social:carrossel` | Carrossel completo |
| `/pwdev-social:video` | Roteiro, storyboard e geração via Runway |
| `/pwdev-social:custo` | Estimativa e acompanhamento de gasto |
| `/pwdev-social:revisar` | Auditoria de criativo |
| `/pwdev-social:exportar` | Pacote de entrega |
| `/pwdev-social:status` | Estado, chaves e gasto acumulado |

### Subagentes

| Agente | Modelo | Papel |
|---|---|---|
| `art-director` | opus | Conceito, triagem de ativos, prompts |
| `asset-generator` | sonnet | **Núcleo** — custo, prompt, geração, curadoria |
| `figma-builder` | sonnet | Composição no Figma (opcional) |
| `creative-reviewer` | sonnet | Portão de qualidade e acessibilidade |

### Skills

**Fundação:** `social-context`, `brand-kit`, `format-specs`

**Concepção:** `creative-concept`

**Geração (núcleo):** `prompt-craft`, `visual-consistency`, `cost-control`,
`image-gen`, `video-gen`, `asset-upscale`, `asset-curation`

**Composição:** `figma-pipeline`, `carousel-builder`, `post-visual`, `story-reels`

**Qualidade:** `creative-review`, `alt-text`

**Entrega:** `export-handoff`, `vault-sync`

---

## Scripts

Wrappers em `scripts/`, com duas barreiras de segurança:

- **`--confirm` obrigatório** — o script recusa gastar sem ele, mesmo que a
  skill erre
- **nunca imprimem a chave** — só presença

Toda geração registra em `.pwdev-social/gerados/manifest.jsonl`:
ferramenta, modelo, prompt, seed, arquivo. Sem isso não há reprodução nem
auditoria.

---

## Conectores — status real

| Ferramenta | Status |
|---|---|
| **Ideogram, Leonardo, Flux, Runway, Freepik** | 🔑 sem MCP oficial — API via chave, wrappers inclusos |
| **Figma** | ✅ MCP oficial — camada opcional de composição |
| **Notion** | ✅ MCP oficial |
| **Obsidian** | 🚫 não precisa — markdown em disco, Read/Write direto |
| **Claude design** | 🚫 não é conector — Artifacts servem de superfície de preview |
| **Canva** | ⚠️ indício de MCP oficial, não confirmado |
| **Higgsfield** | ❓ sem evidência de API pública estável — segue manual |

Detalhes em `references/apis.md` e `references/mcp-roadmap.md`.

---

## Regras que o plugin não negocia

1. **Triagem antes de gerar.** A geração mais barata é a que não acontece.
2. **Não gasta crédito sem confirmação**, com estimativa em chamadas.
3. **2 variações na primeira rodada**, nunca 8.
4. **Seed da peça aprovada é registrada sempre** — sem ela é irreproduzível.
5. **Nunca grava chave de API** em arquivo do projeto.
6. **Não simula geração.** Sem chave, entrega prompt e declara "NÃO GERADO".
7. **`/figma-use` antes de `use_figma`** — exigência do MCP.
8. **Acessibilidade é portão** — contraste e alt text reprovam.
9. **Não publica.**

Codificadas em `references/anatomia-skill.md`.

---

## Créditos

Deriva de [social-media-skills](https://github.com/blacktwist/social-media-skills)
(MIT) — que produz texto e declara não fazer design visual. Este plugin cobre
essa lacuna. Detalhes em `NOTICE.md`. Licença Apache-2.0.
