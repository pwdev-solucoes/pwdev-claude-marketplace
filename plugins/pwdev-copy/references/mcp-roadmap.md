# Roteiro de MCPs — pwdev-copy

Status honesto de cada conector desejado. **Nada aqui está integrado na v1.0** —
esta é a especificação para a v1.1+.

## Legenda

| Símbolo | Significado |
|---|---|
| ✅ | MCP oficial existe e foi verificado |
| ⚠️ | Não há MCP oficial conhecido — exigiria construir wrapper |
| ❓ | Não verificado — validar antes de planejar |

---

## Fase 1 — MCPs que existem hoje

### ✅ Playwright
**Skills beneficiadas:** `voc-research`, `seo-audit`, `page-cro`

Coleta de avaliações, fóruns e páginas de concorrente; auditoria de página
renderizada (o que só aparece após JS).

**Cuidado obrigatório:** respeitar `robots.txt` e termos de uso. Site que
bloqueia coleta automatizada é registrado como fonte não acessada — nunca
contornar bloqueio.

### ✅ Notion
**Skills beneficiadas:** `content-strategy`, `voc-research`, `brand-voice`

Calendário editorial, base versionada de verbatims, guia de voz vivo,
aprovação de copy.

**Nota:** este MCP já aparece disponível no ambiente PWDEV.

### ✅ Perplexity (Sonar)
**Skills beneficiadas:** `voc-research`, `content-strategy`

Pesquisa com citação de fonte. É a peça de maior ganho para `voc-research` —
resolve o problema de pesquisa sem procedência.

---

## Fase 2 — Exige construção

### ⚠️ Meta / Facebook Business
**Skills beneficiadas:** `copy-ads`, `copy-social`

Não há MCP oficial da Meta conhecido. Seria necessário um wrapper sobre a
Marketing API.

**Custo real, não subestimar:**
- App no Meta for Developers + App Review
- Token de sistema com permissão `ads_read` / `ads_management`
- Rate limit por conta de anúncio
- Renovação de token e tratamento de expiração

**Recomendação:** começar somente leitura (importar desempenho de criativo para
alimentar a matriz de ângulos). Escrita/publicação de anúncio é escopo bem maior
e cai nas regras de ação irreversível — sempre exigir confirmação humana.

### ❓ Higgsfield
**Skills beneficiadas:** `copy-video`

Não tenho evidência de MCP nem de API pública estável. **Validar antes de
planejar qualquer coisa.** Se não houver API, a integração real é exportar o
roteiro em formato consumível e a produção segue manual.

---

## Fase 3 — Outros provedores de IA

O pedido de "conectores para IA de outros provedores" merece precisão:
**um plugin do Claude Code não roteia prompts para GPT, Gemini ou outro modelo.**
Isso não é um recurso de plugin.

Caminhos que realmente funcionam:

| Caminho | Como | Quando vale |
|---|---|---|
| **MCP wrapper** | servidor MCP que expõe a API do outro provedor como tool | uso recorrente, vale o esforço de manter |
| **CLI via Bash** | `openai`/`gemini` CLI chamado pelas skills | uso pontual, muito mais barato |
| **Fora do fluxo** | rodar em paralelo e trazer o resultado | comparação de saída |

**Onde isso faria diferença de verdade:** gerar variações de anúncio em massa
com outro modelo e comparar. Para o resto do framework, o ganho é pequeno
frente ao custo de manutenção.

---

## Princípio de degradação

Toda skill precisa funcionar **sem** MCP nenhum. O conector melhora a qualidade
do insumo; nunca é pré-requisito.

Quando um MCP estiver ausente, a skill deve:
1. dizer explicitamente que está em modo degradado;
2. seguir com WebSearch/WebFetch ou pedindo dado ao usuário;
3. marcar no relatório final o que não pôde ser verificado.

`/pwdev-copy:status` reporta quais MCPs estão instalados.
