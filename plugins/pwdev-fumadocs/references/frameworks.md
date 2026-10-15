# Mapa de arquivos por framework

Retirado dos templates do `create-fumadocs-app` (fumadocs-core 16.15, fumadocs-mdx 15.4,
2026-09-28) e, para Waku, da página de instalação manual. Serve para **localizar** arquivos num projeto existente; para **escrever** um
arquivo, leia a página de instalação do framework (`references/docs-access.md`).

Peças comuns a todos:

| Peça | Papel |
|---|---|
| `lib/source.ts` | `defineDocs({ dir })` (Macro API) + `loader({ baseUrl, source, plugins })`; às vezes `llms(source, ...)` |
| `lib/shared.ts` | constantes de rota (`docsRoute`, `docsContentRoute`, `docsImageRoute`) e `gitConfig` — o CLI lê e escreve aqui |
| `lib/layout.shared.tsx` | `baseOptions()` com `nav`, `links`, `githubUrl` compartilhados pelos layouts |
| `components/mdx.tsx` | `getMDXComponents()` = `fumadocs-ui/mdx` + componentes próprios |
| CSS global | `@import 'tailwindcss'; @import 'fumadocs-ui/css/<tema>.css'; @import 'fumadocs-ui/css/preset.css';` |
| Layout raiz | `<html suppressHydrationWarning>` + `<body className="flex flex-col min-h-screen">` + `RootProvider` |
| `content/docs/` | páginas `.mdx` e `meta.json` |
| `cli.json` | criado pelo `@fumadocs/cli` (aliases de diretórios, framework, `uiLibrary`) |

| | Next.js 16 | React Router 7 | TanStack Start | Waku |
|---|---|---|---|---|
| Plugin MDX | `next.config.mjs`: `createMDX()` de `fumadocs-mdx/next` | `vite.config.ts`: `fumadocsMdx()` de `fumadocs-mdx/vite` | `vite.config.ts`: `fumadocsMdx()` | `waku.config.ts` → `vite.plugins` |
| Raiz do código | raiz (ou `src/` com `--src`) | `app/` | `src/` | `src/` (caminhos abaixo relativos a ela) |
| RootProvider | `fumadocs-ui/provider/next` em `app/layout.tsx` | `fumadocs-ui/provider/react-router` em `app/root.tsx` | `fumadocs-ui/provider/tanstack` em `src/routes/__root.tsx` | `fumadocs-ui/provider/waku` em `components/provider.tsx`, usado por `pages/_layout.tsx` |
| Layout de docs | `app/docs/layout.tsx` | `app/routes/docs.tsx` | `src/routes/docs/$.tsx` | `pages/docs/_layout.tsx` |
| Página | `app/docs/[[...slug]]/page.tsx` (+ `generateStaticParams`) | `app/routes/docs.tsx` (loader) | `src/routes/docs/$.tsx` (loader + server fn) | `pages/docs/[...slugs].tsx` |
| Registro de rotas | sistema de arquivos | `app/routes.ts` (`route('docs/*', ...)`) | sistema de arquivos (`routeTree.gen.ts`) | sistema de arquivos |
| Busca | `app/api/search/route.ts` | `app/routes/search.ts` | `src/routes/api/search.ts` | `pages/_api/api/search.ts` |
| llms | `app/llms.txt/route.ts`, `app/llms-full.txt/route.ts`, `app/llms.mdx/docs/[[...slug]]/route.ts` | `app/llms/*.ts` | `src/routes/llms[.]txt.ts`, `docs/{$}[.]md.ts` | gerado por `feature llms` |
| Negociação Markdown | `proxy.ts` (Next 16; antigo `middleware.ts`) | rota `.md` | rota `{$}[.]md.ts` | gerado por `feature llms` |
| OG | `app/og/docs/[...slug]/route.tsx` | `app/routes/og.docs.tsx` | `feature og --engine takumi` | `feature og --engine takumi` |
| Type-check | `next typegen && tsc --noEmit` | `react-router typegen && tsc --noEmit` | `tsc --noEmit` | `tsc --noEmit` |
| Build | `next build` | `react-router build` | `vite build` | `waku build` |
| Estático | `output: 'export'` | `ssr: false` (SPA) em `react-router.config.ts` | `spa: { enabled: true, prerender }` no `tanstackStart()` do `vite.config.ts` | render `static` em todas as páginas |

Astro: suporte parcial (React islands), só instalação manual — `/docs/manual-installation/astro`.

Biblioteca de componentes: o padrão é Base UI — `fumadocs-ui` declarado como alias
`npm:@fumadocs/base-ui@<versão>` (e `uiLibrary: "base-ui"` no `cli.json`). Instalar
`fumadocs-ui` direto, sem alias, usa Radix UI (`/docs/ui/component-library`). Não troque um pelo
outro sem o usuário pedir.
