---
name: fumadocs-content
description: >
  Use quando o usuário quiser escrever, organizar ou migrar o conteúdo de um site Fumadocs —
  'criar uma página de docs', 'organizar a sidebar', 'meta.json', 'separar em abas / versões',
  'traduzir as páginas', 'usar Callout / Tabs / Steps / Files no MDX', 'migrar do Docusaurus /
  Nextra / Mintlify para o Fumadocs'. Trabalha em content/ (MDX, frontmatter, meta.json) seguindo
  as convenções do projeto e a documentação oficial, e valida com o scanner e o build. Não use
  para instalar o Fumadocs (fumadocs-setup), adicionar features como busca ou OpenAPI
  (fumadocs-feature) ou para erros de build fora do conteúdo (fumadocs-doctor).
metadata:
  version: 0.1.0
---

# Conteúdo no Fumadocs

## 1. Ler o projeto antes de escrever

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text
```

Anote `content_dirs`, `base_urls`, `i18n_parser` e a fonte de conteúdo. Leia `lib/source.ts`
(ou `source.config.ts`) para o schema do frontmatter — campos extras (`pageSchema.extend`) são
obrigatórios se não tiverem default. Leia 2–3 páginas e os `meta.json` existentes e imite o
estilo (tom, idioma, ordem, ícones, uso de componentes).

## 2. Consultar a convenção certa

Leia a página oficial do assunto (`<plugin-root>/references/docs-access.md`):

| Pedido | Página |
|---|---|
| slugs, `meta.json`, grupos `(pasta)`, pastas raiz, abas, versões | `/docs/page-conventions`, `/docs/navigation` |
| Markdown: callouts, código (título, tabs, destaque), heading ids, include | `/docs/markdown` |
| componentes MDX (Tabs, Steps, Files, Accordion, TypeTable, Banner...) | `/docs/ui/components/<nome>` |
| i18n de conteúdo (`.pt.mdx` ou pasta por idioma) | `/docs/page-conventions#i18n-routing`, `/docs/internationalization` |
| Mermaid, Math, Twoslash | `/docs/markdown/<nome>` — exigem plugin: use fumadocs-feature |

## 3. Regras que valem sempre

- Todo `.mdx`/`.md` tem `title` no frontmatter; `description` é recomendada (vira subtítulo e
  metadado). `icon` só funciona com handler de ícones no `loader()`.
- O caminho do arquivo é a URL: `guia/instalacao.mdx` → `<baseUrl>/guia/instalacao`;
  `index.mdx` é a página da pasta; `(grupo)/` não entra na URL. Nomes em kebab-case.
- `meta.json` com `pages` **exclui** o que não lista — inclua `"..."` para o resto.
- A mesma URL nunca aparece duas vezes na page tree (nem via `...pasta` e o caminho da pasta).
- Links internos: caminho relativo ao arquivo (`./outra.mdx`) funciona quando a página usa
  `createRelativeLink` — confira no componente da página; senão use a URL absoluta.
- Componente que não está em `components/mdx.tsx` (ex.: `Tabs`, `Steps`, `Files`) precisa ser
  importado no MDX ou registrado lá — prefira registrar se for usado em várias páginas.
- Mover ou renomear página muda a URL: avise e ofereça redirecionamento no framework.

## 4. Escrever

Proponha a estrutura (árvore de arquivos + trechos de `meta.json`) antes de criar mais de três
páginas ou de reorganizar pastas; crie após o "sim". Arquivo existente → edite o mínimo.

Migração de outra ferramenta: mapeie a navegação antiga (sidebars.js, `_meta.json`,
`mint.json`) para `meta.json`, frontmatter para `title`/`description`, e admonitions
(`:::note`) para `<Callout>` — ou ative `remark-admonition` (`/docs/headless/mdx/remark-admonition`).
Converta em lotes pequenos e valide cada lote.

## 5. Validar

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text   # FD013 = página sem title
<pm> run build
```

O build valida o frontmatter e compila todo MDX. Com dev server, abra as páginas criadas e
confira sidebar e breadcrumb. Links: `/docs/integrations/validate-links` (bom para CI).

Relate as páginas criadas/alteradas com suas URLs finais e o resultado do build.

Idioma: escreva o conteúdo no idioma das páginas existentes (ou no pedido pelo usuário) e
responda no idioma do usuário. Caminhos `<plugin-root>/...`, `references/` e `scripts/` são
relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do
runtime (`<plugin-root>/references/runtime.md`).
