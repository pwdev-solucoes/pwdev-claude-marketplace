# Armadilhas conhecidas

Os códigos `FDnnn` são os achados do `scripts/fdscan.py`; as demais linhas são sintomas que
só aparecem ao rodar o projeto. Para cada uma, confirme na página indicada antes de corrigir —
a causa pode ter mudado de versão.

## Achados do scanner

| Código | Sintoma | Correção | Página |
|---|---|---|---|
| FD001 | Node.js < 22 | atualizar o Node (erros de `require(esm)` e JSON do Turbopack vêm daqui) | `/docs` |
| FD002 | Tailwind CSS < 4 | Fumadocs UI exige Tailwind 4 — migrar o Tailwind antes | `/docs/manual-installation` |
| FD003 | UI sem estilo | importar `fumadocs-ui/css/<tema>.css` e `fumadocs-ui/css/preset.css` após `tailwindcss` | `/docs/ui/theme` |
| FD004 | aviso de hidratação ao trocar tema | `suppressHydrationWarning` no `<html>` | `/docs/ui/layouts/root-provider` |
| FD005 | busca, tema e sidebar sem contexto | renderizar o `RootProvider` do framework no layout raiz | `/docs/ui/layouts/root-provider` |
| FD006 | APIs faltando, tipos quebrados | `fumadocs-core` e `fumadocs-ui` na mesma versão; atualizar juntos (`pnpm update -i -r --latest`) | `/docs` |
| FD007 | erros de ESM ao carregar `next.config` | usar `next.config.mjs` (ou TS com o resolver nativo do Node) | `/docs/mdx/next` |
| FD008 | MDX não compila / `page.data.body` indefinido no Next | envolver a config com `createMDX()` de `fumadocs-mdx/next` | `/docs/mdx/next` |
| FD009 | MDX não compila no Vite | registrar `fumadocsMdx()` de `fumadocs-mdx/vite` | `/docs/mdx/vite` |
| FD011 | `.source/` gerado entra no git | adicionar `.source` ao `.gitignore` (Config API) | `/docs/mdx/collections` |
| FD012 | `fumadocs-mdx` sem `loader()` | criar `lib/source.ts` com `loader({ baseUrl, source })` | `/docs/headless/source-api` |
| FD013 | build falha na validação do frontmatter | todo `.mdx` do conteúdo precisa de `title` (schema padrão) | `/docs/page-conventions` |

## Sintomas em tempo de execução

| Sintoma | Causa provável | Página |
|---|---|---|
| Erro de contexto React no Vite (`useX must be used within ...`) | pré-bundling duplicou o pacote — adicionar `fumadocs-core`, `fumadocs-ui`, `@fumadocs/base-ui` (e `fumadocs-openapi` se usado) a `resolve.noExternal` | `/docs` (FAQ "For Vite") |
| `JSON file not found: ...file.json.json` no Turbopack | Node sem `require(esm)` — Node 22+ | `/docs` (FAQ "For Next.js") |
| `Could not find a production build in the '.next' directory` | bug do Node 23.1 — 23.6+ | `/docs` |
| Página duplicada / item ativo errado na sidebar | a mesma URL aparece duas vezes na page tree (`meta.json` lista a página duas vezes, ou pasta e `...folder`) — proibido por design | `/docs/page-conventions` |
| Página some da sidebar | `meta.json` com `pages` não lista o item e não tem `"..."` | `/docs/page-conventions` |
| Ícone do frontmatter não aparece | falta o handler de ícones no `loader()` (ex.: `lucideIconsPlugin()`) | `/docs/headless/source-api` |
| Página em `/docs/x` sem layout de docs dá conflito | remover o `.mdx` correspondente e mover a rota para outro grupo | `/docs` (FAQ) |
| Mudar `/docs` para outro caminho não funciona | renomear a rota no framework **e** o `baseUrl` do `loader()` (e `lib/shared.ts`) | `/docs` (FAQ) |
| Busca vazia no export estático | a busca embutida precisa do modo estático no servidor e no cliente | `/docs/deploying/static` |
| `lastModified` vazio no Vercel | clone raso — `VERCEL_DEEP_CLONE=true` | `/docs/mdx/collections` |
| `mdxOptions` na coleção removeu callouts, código etc. | opções por coleção substituem o preset — usar `applyMdxPreset()` | `/docs/mdx/collections` |
| `ERR_PNPM_IGNORED_BUILDS` ao rodar `@fumadocs/cli feature` com pnpm 10+ | o pnpm bloqueou scripts de build (ex.: `esbuild`); as dependências já foram gravadas no `package.json` — peça ao usuário para rodar `pnpm approve-builds` e depois `pnpm install` | — |
| i18n: redirecionamento não acontece no Next 16 | o middleware agora vive em `proxy.ts` (`createI18nMiddleware`) | `/docs/internationalization/next` |
