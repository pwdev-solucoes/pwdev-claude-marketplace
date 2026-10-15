# Catálogo de features

Primeiro caminho: o CLI oficial (`npx @fumadocs/cli feature <id>`), que conhece o framework,
o `baseUrl`, `src/`, i18n, export estático e modo SPA do projeto e escreve rotas e componentes
atualizados. Segundo caminho: seguir a página da documentação à mão — quando o CLI não cobre
o caso, a fonte de conteúdo não é Fumadocs MDX, ou o usuário quer entender cada arquivo.

Verificado contra `@fumadocs/cli` 1.7.0 em 2026-09-28. Confira `npx @fumadocs/cli feature -h`
antes de usar: flags mudam.

| Feature | CLI | Documentação | Pré-requisito / observação |
|---|---|---|---|
| Docs no projeto existente | `init` (ou `feature docs`); `--i18n` | `/docs/cli`, `/docs/manual-installation/<fw>` | Next.js, React Router, TanStack Start, Waku. Astro: só manual |
| Busca de terceiros | `feature search --provider orama-cloud\|algolia\|typesense\|mixedbread` | `/docs/search/<provedor>` | a busca padrão (ZBSearch/Orama local) já vem no template; chaves via variáveis de ambiente |
| llms.txt + Markdown por página | `feature llms` | `/docs/integrations/llms` | requer Fumadocs MDX (Macro ou Config API) com `includeProcessedMarkdown` |
| Servidor MCP das docs | `feature mcp` | `/docs/integrations/llms#mcp-server`, `/docs/headless/utils/mcp` | requer Fumadocs MDX; cria `/api/mcp` |
| WebMCP (experimental) | `feature webmcp` | `/docs/integrations/llms#webmcp` | experimental — avise o usuário |
| Ask AI | `feature ai --provider openrouter\|llmgateway\|inkeep` | `/docs/integrations/llms#ask-ai` | precisa de chave do provedor; nunca grave a chave no repositório |
| OG image | `feature og --engine next-og\|takumi` | `/docs/integrations/og` | `next-og` só no Next.js; Takumi funciona nos demais |
| Feedback | `feature feedback` | `/docs/integrations/feedback` | o destino (GitHub Discussions, API própria) é do usuário |
| EPUB | `feature epub` | `/docs/guides/export-epub` | requer Fumadocs MDX |
| Lint | `feature lint --linter eslint\|biome\|oxlint` | `/docs/cli` | ESLint só no Next.js |
| Componentes da UI | `add <nomes>` (ex.: `add banner files`) | `/docs/ui/components` | o CLI copia o componente e reescreve imports |
| Customizar layout | `customize` | `/docs/guides/customize-ui` | copia o layout para `layouts/` e aponta as rotas para ele |
| Árvore de arquivos para `<Files>` | `tree <dir> <saida.tsx\|.mdx>` | `/docs/cli` | |

Sem CLI (manual pela documentação):

| Feature | Documentação | Observação |
|---|---|---|
| i18n num projeto que já tem docs | `/docs/internationalization/<fw>`, `/docs/ui/translations` | `defineI18n` em `lib/i18n.ts`; no Next.js 16 o redirecionamento fica em `proxy.ts`; `parser: 'dot'` (arquivo `.pt.mdx`) ou `'dir'` (pasta por idioma) |
| Export estático | `/docs/deploying/static` | busca embutida precisa do modo estático (índice no cliente); Next `output: 'export'`, React Router/TanStack em modo SPA |
| OpenAPI | `/docs/integrations/openapi`, `/generate-files` | pacote `fumadocs-openapi`; `createOpenAPI()` + `generateFiles()` a partir do schema |
| AsyncAPI / GraphQL | `/docs/integrations/asyncapi`, `/docs/integrations/graphql` | |
| TypeScript (tabelas de tipos) | `/docs/integrations/typescript`, `/docs/ui/components/auto-type-table` | pacote `fumadocs-typescript` |
| Twoslash / Mermaid / Math | `/docs/markdown/twoslash`, `/docs/markdown/mermaid`, `/docs/markdown/math` | plugins MDX na config global |
| Versões / múltiplas docs | `/docs/navigation`, `/docs/page-conventions` (pastas raiz, `root: "version"`) | Layout Tabs no `DocsLayout` |
| Validar links | `/docs/integrations/validate-links` | bom para CI |
| RSS, PDF, controle de acesso | `/docs/guides/{rss,export-pdf,access-control}` | |
| Última edição | `/docs/mdx/last-modified` | `lastModified: true` usa git; no Vercel exige `VERCEL_DEEP_CLONE=true` |

## Depois de qualquer feature

1. Rode de novo `fdscan.py` e confirme que a feature aparece em `features`.
2. Verifique no navegador ou por `curl` a rota criada (`/api/search?query=...`, `/llms.txt`,
   `/docs/<pagina>.md`, `/og/docs/.../image.png`, `/api/mcp`).
3. Rode o type-check e o build do projeto (`fumadocs-doctor` descreve os comandos por framework).
