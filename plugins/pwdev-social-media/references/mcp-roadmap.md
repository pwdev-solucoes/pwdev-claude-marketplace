# Conectores — status verificado

Levantamento honesto. **Nada aqui está pré-configurado no seu ambiente hoje** —
a verificação feita em 18/07/2026 não encontrou nenhum MCP nem chave de API
configurada.

| Símbolo | Significado |
|---|---|
| ✅ | MCP oficial existe, verificado |
| 🔑 | Sem MCP conhecido; tem API REST — integração via Bash + chave |
| ❓ | Sem evidência de API pública estável — validar antes de planejar |
| 🚫 | Não precisa de conector |

---

## Declarados em `.mcp.json`

### ✅ Figma
**Espinha dorsal do plugin.** Lê design system e escreve criativos.
Exige a skill `/figma-use` antes de `use_figma` — ver `figma-pipeline.md`.

### ✅ Notion
Brief, calendário editorial, aprovação, biblioteca de peças publicadas.

---

## Sem conector, por decisão

### 🚫 Obsidian
**Não construa integração.** Um vault do Obsidian é uma pasta de arquivos
markdown no disco — o Claude Code lê e escreve direto com Read/Write/Glob.
Adicionar MCP aqui seria complexidade sem nenhum ganho.

Configure apenas o caminho do vault na seção 7 do contexto. Ver `social-vault`.

### 🚫 Claude design (skills nativas)
`frontend-design`, `canvas-design` e `artifact-design` já estão disponíveis no
ambiente. Não são conectores — são skills. `canvas-design` gera PNG e PDF
diretamente e serve como caminho alternativo quando o Figma não está disponível.

---

## Exigem chave de API (Path C)

Nenhum tem MCP oficial conhecido. Desde a v3 a integração é a CLI `pwdev-media` (plugin
pwdev-media), com a chave da pessoa no Keychain. Itens: `<plugin-root>/references/apis.md`.

| Ferramenta | Uso | Endpoint |
|---|---|---|
| 🔑 **Ideogram** | imagem com texto legível — o melhor da lista para peça com tipografia | api.ideogram.ai |
| 🔑 **Leonardo** | ilustração e imagem de marca | cloud.leonardo.ai/api/rest |
| 🔑 **Flux** | imagem fotorrealista | api.bfl.ai, ou via Replicate / fal.ai |
| 🔑 **Runway** | vídeo a partir de imagem ou texto | dev.runwayml.com |
| 🔑 **Magnific** (antigo Freepik) | upscale e enhance de imagem existente | api.magnific.com |

**Regras inegociáveis para qualquer uma delas:**

1. Toda chamada **gasta crédito do usuário**. Confirmar antes, sempre, com
   estimativa de quantas chamadas e para quê.
2. Chave vem do Keychain ou do ambiente, via `pwdev-media`. **Nunca** escrever chave em arquivo do
   projeto, nem em skill, nem em log.
3. Sem chave configurada, a skill entrega o **prompt otimizado** para execução
   manual — não simula o resultado.
4. Nunca afirmar que uma imagem foi gerada se a chamada não aconteceu.

### ⚠️ Canva
Há indicação de MCP oficial, **não confirmado nesta verificação**. Validar antes
de declarar em `.mcp.json`. Enquanto isso, tratar como handoff manual: o plugin
entrega a especificação, alguém monta no Canva.

### ❓ Higgsfield
Segundo levantamento consecutivo sem evidência de MCP nem de API pública estável.
**Não planeje integração automatizada.** O caminho real hoje é `social-video`
entregar o prompt e o storyboard para execução manual na interface (ou outro modelo de
vídeo do catálogo do `pwdev-media`).

---

## Degradação

Toda skill funciona sem conector nenhum. Ausente o conector, a skill:

1. declara que está em modo degradado;
2. entrega especificação em vez de artefato;
3. registra no relatório o que não pôde ser produzido.

`/pwdev-social-media:status` (Codex: `$social-contexto`) mostra o que está conectado.
