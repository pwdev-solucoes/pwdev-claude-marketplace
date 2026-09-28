---
name: fumadocs-setup
description: >
  Use quando o usuário quiser criar um site de documentação com Fumadocs ou adicionar Fumadocs a
  um app React existente — 'criar docs com fumadocs', 'instalar fumadocs no meu Next.js',
  'montar um portal de documentação em React Router / TanStack Start / Waku / Astro'. Detecta o
  projeto, escolhe entre create-fumadocs-app, @fumadocs/cli init ou instalação manual pela
  documentação oficial, executa após confirmação e verifica com type-check e build. Não use
  para escrever páginas (fumadocs-content), adicionar busca/llms/OG/OpenAPI a um projeto que já
  tem Fumadocs (fumadocs-feature) nem para investigar erros (fumadocs-doctor).
metadata:
  version: 0.1.0
---

# Instalar Fumadocs

Regra de ouro: **nada de API do Fumadocs de memória.** Todo arquivo escrito à mão segue a
página oficial lida nesta sessão (`<plugin-root>/references/docs-access.md`).

## 1. Detectar

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text
```

Sem `package.json` (ou diretório vazio) → projeto novo. Com `fumadocs` já instalado → não
reinstale: ofereça fumadocs-feature ou fumadocs-doctor. Em monorepo, rode no pacote do app.

## 2. Escolher o caminho

| Situação | Caminho |
|---|---|
| Projeto novo | `npx create-fumadocs-app@latest <nome>` — leia `/docs/cli/create-fumadocs-app` para as flags e templates atuais |
| App existente em Next.js, React Router, TanStack Start ou Waku | `npx @fumadocs/cli@latest init` (`--i18n` se pedido) — cria as rotas num grupo próprio, sem mexer nas rotas do app |
| Astro, framework fora da lista, ou o usuário quer entender cada arquivo | manual: `/docs/manual-installation/<framework>` passo a passo |
| Outra fonte de conteúdo (Content Collections, CMS, Notion, Obsidian) | manual: página da fonte em `/docs/integrations/content/...` |

Pré-requisitos a conferir antes (achados FD001/FD002 do scanner): Node.js 22+, Tailwind CSS 4
e, no Next.js, a versão exigida pela página de instalação.

## 3. Confirmar com o usuário (uma rodada)

Pergunte só o que o scanner não respondeu, com recomendação:

- framework (projeto novo) — recomende Next.js se não houver preferência;
- gerenciador de pacotes — o detectado;
- rota base das docs — `/docs`; outro valor exige mudar a rota **e** o `baseUrl`;
- extras já no gerador: busca (`--search`), OG (`--og-image`), Ask AI (`--ai-chat`), i18n.

Mostre o comando exato e os arquivos que serão criados ou alterados. Execute só após o "sim".
Não passe `--yes` a um gerador sobre projeto existente sem autorização explícita: ele
sobrescreve arquivos sem perguntar.

## 4. Executar

- Gerador: rode o comando confirmado. Se o pnpm 10+ parar com `ERR_PNPM_IGNORED_BUILDS`, as
  dependências já foram gravadas — peça ao usuário `pnpm approve-builds` e siga
  (`<plugin-root>/references/pitfalls.md`).
- Manual: para cada arquivo, leia a página, traduza os blocos ` ```npm ` para o gerenciador
  detectado, remova os marcadores `[!code ...]` e grave. Arquivo existente → mostre o diff antes.
  Use `<plugin-root>/references/frameworks.md` para saber onde cada peça fica.

## 5. Verificar (obrigatório)

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text   # sem achados error
<pm> install
<pm> run types:check    # ou o script de type-check do projeto
<pm> run build
```

Se houver servidor de dev disponível, suba-o e confira `GET <baseUrl>` (200) e
`GET /api/search?query=a` (JSON). Falha → não declare sucesso: mostre a saída e passe para
fumadocs-doctor.

## 6. Relatar

```
FUMADOCS: instalado via {create-fumadocs-app | cli init | manual} · {framework} · {pm}
ROTAS: {baseUrl} · busca {rota} · extras {llms, og, ...}
VERIFICAÇÃO: type-check {ok|falhou} · build {ok|falhou} · dev {ok|não testado}
PRÓXIMO: escrever conteúdo (fumadocs-content) · features (fumadocs-feature)
```

Idioma: responda no idioma do usuário. Caminhos `<plugin-root>/...`, `references/` e
`scripts/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos
dependem do runtime (`<plugin-root>/references/runtime.md`).
