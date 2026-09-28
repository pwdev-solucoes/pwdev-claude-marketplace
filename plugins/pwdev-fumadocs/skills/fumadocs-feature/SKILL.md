---
name: fumadocs-feature
description: >
  Use quando o usuário quiser adicionar ou configurar uma feature num projeto que já usa
  Fumadocs — busca (Algolia, Orama Cloud, Typesense...), llms.txt e Markdown para LLMs, servidor
  MCP das docs, Ask AI, OG images, OpenAPI/AsyncAPI/GraphQL, i18n, export estático, versões,
  tema/cores, layout customizado, componentes (@fumadocs/cli add), feedback, Twoslash, Mermaid.
  Prefere o @fumadocs/cli feature quando cobre o caso, senão segue a página oficial; executa após
  confirmação e verifica a rota criada e o build. Não use sem Fumadocs instalado
  (fumadocs-setup), para escrever páginas (fumadocs-content) ou para diagnosticar erros
  (fumadocs-doctor).
metadata:
  version: 0.1.0
---

# Adicionar uma feature ao Fumadocs

## 1. Detectar

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text
```

Sem Fumadocs instalado → fumadocs-setup. Feature já em `features` → mostre onde está e
pergunte se é para ajustar, não para reinstalar. Achados `error` do scanner → resolva antes
(fumadocs-doctor), senão a verificação final não prova nada.

## 2. Escolher o caminho

Consulte `<plugin-root>/references/features.md`:

- **CLI** (`npx @fumadocs/cli@latest feature <id>` / `add` / `customize`) quando a linha da
  feature tem comando e a fonte é Fumadocs MDX. Rode antes `npx @fumadocs/cli@latest feature -h`
  e confira flags e provedores atuais.
- **Manual** pela página oficial quando não há comando, a fonte é outra, ou o usuário quer
  controle arquivo a arquivo. Leia a página (`<plugin-root>/references/docs-access.md`) e as
  subpáginas do framework detectado.

Com o working tree sujo, sugira commitar antes: o CLI escreve vários arquivos e o `git diff`
é a forma mais simples de revisar e desfazer.

## 3. Confirmar (uma rodada)

Mostre: comando exato ou lista de arquivos a criar/alterar, dependências novas, variáveis de
ambiente exigidas (chaves de Algolia, provedor de IA...) e o que muda para o usuário final.
Pergunte só as escolhas abertas (provedor, engine, idiomas), com recomendação. Execute após o
"sim". Nunca grave chaves ou tokens em arquivos versionados: use `.env.local` (fora do git) e
documente o nome da variável.

## 4. Executar

- CLI: rode o comando confirmado. `ERR_PNPM_IGNORED_BUILDS` → dependências já gravadas; peça
  ao usuário `pnpm approve-builds` + `pnpm install`. Depois, `git status` e resuma o que o CLI
  criou (inclusive `cli.json`, na primeira execução).
- Manual: um arquivo por vez, forma da página, marcadores `[!code ...]` removidos, gerenciador
  de pacotes do projeto. Mudança em arquivo existente → diff antes.

## 5. Verificar (obrigatório)

```bash
python3 <plugin-root>/scripts/fdscan.py <dir-do-app> --format text   # a feature aparece em FEATURES
<pm> run types:check
<pm> run build
```

Com dev ou start rodando, prove a rota da feature: `/api/search?query=...`, `/llms.txt`,
`<baseUrl>/<página>.md`, `/og/...`, `POST /api/mcp` com `tools/list`, página traduzida em
`/<locale><baseUrl>`, saída estática no diretório de export. Falhou → mostre a saída e siga
fumadocs-doctor; não declare sucesso sem evidência.

## 6. Relatar

```
FEATURE: {nome} via {cli feature <id> | manual (<página>)}
ARQUIVOS: {criados} · {alterados} · deps {novas}
AMBIENTE: {variáveis a definir | nenhuma}
VERIFICAÇÃO: rota {url → status} · type-check {ok|falhou} · build {ok|falhou}
```

Idioma: responda no idioma do usuário. Caminhos `<plugin-root>/...`, `references/` e
`scripts/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos
dependem do runtime (`<plugin-root>/references/runtime.md`).
