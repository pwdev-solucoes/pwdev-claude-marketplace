# Documentação viva do Fumadocs

O Fumadocs muda rápido (Macro API, Next.js 16, Tailwind 4, `fumadocs-ui` como alias de
`@fumadocs/base-ui`, `proxy.ts` no lugar de `middleware.ts`). **Nunca escreva código de API
do Fumadocs de memória.** Antes de criar ou alterar um arquivo, leia a página oficial
correspondente e copie a forma que ela mostra — ajustando só nomes e caminhos do projeto.

## Ordem de acesso

1. **MCP oficial `fumadocs`** (`https://www.fumadocs.dev/api/mcp`, HTTP, sem autenticação),
   quando o runtime o expõe. Ferramentas publicadas pelo servidor:

   | Ferramenta | Uso |
   |---|---|
   | `search` (`query`) | achar a página certa por assunto |
   | `get_page` (`url`, ex.: `/docs/manual-installation/next`) | Markdown completo da página |
   | `list_pages` | índice com todos os caminhos |
   | `ask-ai` (`message`) | pergunta aberta a um assistente do Fumadocs — use só quando `search` + `get_page` não resolverem, e confira a resposta contra a página |

   Inspecione as ferramentas realmente disponíveis; o prefixo muda por runtime
   (`mcp__plugin_pwdev-fumadocs_fumadocs__get_page`, `mcp_fumadocs_get_page`...). Não invente nomes.

2. **HTTP direto**, quando o MCP não está conectado (ou o runtime não tem MCP):

   ```bash
   curl -sL https://www.fumadocs.dev/llms.txt                       # índice (títulos + caminhos)
   curl -sL https://www.fumadocs.dev/docs/manual-installation/next.mdx   # uma página em Markdown
   ```

   Qualquer caminho `/docs/...` do índice vira Markdown com o sufixo `.mdx`. Evite
   `llms-full.txt` (≈700 KB): só use com `grep` para localizar um termo.

3. **Sem rede** (sandbox que bloqueia acesso externo): diga isso ao usuário, não contorne. Use
   então os tipos instalados como fonte — `node_modules/fumadocs-*/dist/**/*.d.ts` — e marque o
   resultado como "não conferido com a documentação".

## Como ler uma página

- Blocos ` ```npm ` são comandos de instalação: traduza para o gerenciador detectado pelo
  `fdscan.py` (`pnpm add`, `bun add`, `yarn add`).
- ` ```tsx tab="app/docs/layout.tsx" ` e `title="..."` indicam o caminho do arquivo.
- `// [!code ++]` marca linhas a adicionar; `[!code highlight]` só destaca. Remova esses
  comentários ao escrever o arquivo.
- `<Callout type="warn">` e `<Accordion>` de FAQ costumam conter as armadilhas — leia-os.
- Links relativos (`/docs/...`) são outras páginas: siga só os necessários para a tarefa.

## Páginas por assunto

| Assunto | Caminho |
|---|---|
| Visão geral, FAQ, Node 22 | `/docs` |
| Instalação manual por framework | `/docs/manual-installation/{next,react-router,tanstack-start,waku,astro}` |
| CLI (`init`, `feature`, `add`, `customize`, `tree`) | `/docs/cli` |
| Novo app | `/docs/cli/create-fumadocs-app` |
| Fumadocs MDX: Next / Vite / Macro / Config | `/docs/mdx/next`, `/docs/mdx/vite`, `/docs/mdx/macro`, `/docs/mdx/collections` |
| `loader()`, ícones, plugins do loader | `/docs/headless/source-api`, `/docs/headless/source-api/plugins` |
| Slugs, `meta.json`, pastas raiz, versões | `/docs/page-conventions`, `/docs/navigation` |
| Markdown (callouts, tabs, código, include) | `/docs/markdown` |
| Componentes da UI | `/docs/ui/components` e `/docs/ui/components/<nome>` |
| Layouts (Docs, Notebook, Flux, Glass, Home), página, provider | `/docs/ui/layouts/*` |
| Tema e cores | `/docs/ui/theme`, `/docs/guides/customize-ui` |
| Busca (padrão, Algolia, Orama Cloud, Typesense...) | `/docs/search`, `/docs/search/<provedor>`, `/docs/headless/search/<provedor>` |
| i18n | `/docs/internationalization/<framework>`, `/docs/ui/translations` |
| llms.txt, Markdown por página, MCP, Ask AI | `/docs/integrations/llms`, `/docs/headless/utils/mcp` |
| OG images | `/docs/integrations/og`, `/docs/integrations/og/{next,takumi}` |
| OpenAPI / AsyncAPI / GraphQL | `/docs/integrations/openapi` (+ `/generate-files`), `/docs/integrations/asyncapi`, `/docs/integrations/graphql` |
| TypeScript, Twoslash, Mermaid, Math | `/docs/integrations/typescript`, `/docs/markdown/{twoslash,mermaid,math}` |
| Validar links | `/docs/integrations/validate-links` |
| Deploy e export estático | `/docs/deploying`, `/docs/deploying/static` |
| Outras fontes (Content Collections, Notion, Obsidian, Sanity, MDX Remote) | `/docs/headless/content-collections`, `/docs/integrations/content/<fonte>` |

A tabela é um atalho, não a verdade: se um caminho der 404, procure no `llms.txt` ou com
`search` e siga o caminho atual.
