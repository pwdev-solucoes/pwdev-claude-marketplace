# PWDEV-FUMADOCS v0.1.0

*Leia em [English](./README.md)*

> **Sites de documentação [Fumadocs](https://www.fumadocs.dev) construídos a partir da documentação oficial ao vivo — instalação, conteúdo, features e diagnóstico, verificados por type-check e build, no Claude Code, Codex, Hermes Agent e OpenCode.**

```
fdscan (fatos do projeto) → página oficial (MCP / .mdx) → @fumadocs/cli ou edição manual → scan + type-check + build
```

O Fumadocs muda rápido (Macro API, `proxy.ts` do Next.js 16, Tailwind 4, Base UI por padrão). O
plugin nunca escreve código de API do Fumadocs de memória: toda mudança segue a página oficial
lida na mesma sessão, pelo servidor MCP oficial do Fumadocs ou pelo Markdown `.mdx` de cada página.

## O que faz

| Peça | O que faz |
|---|---|
| `/pwdev-fumadocs:setup` | Site novo com `create-fumadocs-app`, Fumadocs num app Next.js / React Router / TanStack Start / Waku existente com `@fumadocs/cli init`, ou instalação manual (Astro, outras fontes de conteúdo) página a página |
| `/pwdev-fumadocs:content` | Páginas, frontmatter, `meta.json`, grupos de pasta, pastas raiz (abas), versões, arquivos de i18n, componentes MDX; migração de Docusaurus / Nextra / Mintlify |
| `/pwdev-fumadocs:feature` | Provedores de busca, `llms.txt` + Markdown por página, servidor MCP das docs, Ask AI, OG images, OpenAPI / AsyncAPI / GraphQL, i18n, export estático, tema, layout customizado, componentes — `@fumadocs/cli feature` primeiro, a página oficial nos demais casos |
| `/pwdev-fumadocs:doctor` | Diagnóstico somente leitura (scanner, versões, type-check, build, catálogo de armadilhas, docs oficiais) e correção aplicada só após aprovação; também estado e atualização |
| `scripts/fdscan.py` | Varredura determinística e somente leitura: framework, gerenciador de pacotes, pacotes Fumadocs, fonte de conteúdo (Macro / Config API), `baseUrl`, diretórios de conteúdo, features ligadas e armadilhas conhecidas (`FD001`–`FD013`). JSON ou texto |
| MCP `fumadocs` | Servidor oficial em `https://www.fumadocs.dev/api/mcp` (`search`, `get_page`, `list_pages`, `ask-ai`) — sem autenticação |

## Instalação

1. Node.js 22+ e um gerenciador de pacotes (npm, pnpm, yarn ou bun) no projeto Fumadocs.
2. Python 3 (só biblioteca padrão) para `scripts/fdscan.py`.
3. Acesso de rede a `www.fumadocs.dev` (docs) e ao registro npm (`npx`).
4. Instale o plugin no seu runtime:

| Runtime | Instalar | Invocar | MCP do Fumadocs |
|---|---|---|---|
| Claude Code | `claude plugin install pwdev-fumadocs@pwdev-claude-marketplace` | `/pwdev-fumadocs:setup`, `:content`, `:feature`, `:doctor` | automático (`.mcp.json`) |
| Codex | adicione este repositório como marketplace e habilite **pwdev-fumadocs** (`.agents/plugins/marketplace.json`) | `$fumadocs-setup`… | `codex mcp add fumadocs --url https://www.fumadocs.dev/api/mcp` |
| Hermes Agent | `hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable` (entrada `.hermes-plugin/`) | `skill_view("pwdev-fumadocs:fumadocs-setup")` ou só pedir | `mcp_servers: { fumadocs: { url: "https://www.fumadocs.dev/api/mcp" } }` em `~/.hermes/config.yaml` |
| OpenCode | `python3 plugins/pwdev-fumadocs/.opencode-plugin/install.py [--project <dir>]` | `/fumadocs-setup`… ou a ferramenta `skill` | `"mcp": { "fumadocs": { "type": "remote", "url": "https://www.fumadocs.dev/api/mcp" } }` no `opencode.json` |

Sem o servidor MCP, as skills leem as mesmas páginas por HTTP
(`https://www.fumadocs.dev/docs/<caminho>.mdx`, índice em `/llms.txt`). Quatro skills portáveis
(`skills/fumadocs-*`) são a fonte única, cada uma com um comando Claude como wrapper. Sem
subagentes, sem hooks. Detalhes: [references/runtime.md](./references/runtime.md).

## Referências

- [docs-access.md](./references/docs-access.md) — como ler a documentação viva; mapa de páginas por assunto.
- [frameworks.md](./references/frameworks.md) — onde cada peça fica em cada framework.
- [features.md](./references/features.md) — feature → comando do CLI → página.
- [pitfalls.md](./references/pitfalls.md) — achados do scanner e sintomas em execução, com correção.

Verificado em 2026-09-28 contra os templates do `create-fumadocs-app` (fumadocs-core 16.15,
fumadocs-mdx 15.4, `@fumadocs/cli` 1.7): o template Next.js compilou e o `feature mcp` criou um
`/api/mcp` funcional.

## Segurança

- Instalar pacotes, rodar gerador (`create-fumadocs-app`, `@fumadocs/cli`) e sobrescrever
  arquivos exigem um "sim" explícito; o comando e os arquivos afetados aparecem antes. Geradores
  nunca recebem `--yes` em projeto existente sem autorização.
- `fdscan.py` só lê arquivos (ignora `node_modules`, saída de build e diretórios ocultos) e roda
  `node --version`; não grava nada.
- Chaves de provedores de busca ou IA vão para arquivos de ambiente fora do git (`.env.local`),
  nunca para arquivos versionados.
- O servidor MCP do Fumadocs é um serviço público de documentação, somente leitura; nenhuma
  credencial é enviada.

## Licença

Apache-2.0 — veja [LICENSE](./LICENSE)
