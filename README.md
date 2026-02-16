# PWDEV Claude Marketplace

Marketplace de plugins para [Claude Code](https://docs.anthropic.com/en/docs/claude-code) com agentes especializados, workflows estruturados e skills de desenvolvimento.

## Plugins Disponveis

| Plugin | Descrio | Verso |
|--------|-----------|--------|
| [gsd-pwdevia](./gsd-pwdevia/) | Framework spec-driven com 9 agentes, 5 fases e skills versionadas | 1.0.0 |

## Instalao

### Pr-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Node.js 18+ (para MCP servers via npx)

### Instalar um plugin do marketplace

```bash
# Clone o marketplace
git clone https://github.com/pwdev/pwdev-claude-marketplace.git

# Instale o plugin desejado globalmente
claude plugins add ./pwdev-claude-marketplace/plugins/gsd-pwdevia
```

### Instalar por projeto

Crie `.claude/settings.json` na raiz do seu projeto:

```json
{
  "plugins": [
    { "path": "/caminho/para/pwdev-claude-marketplace/plugins/gsd-pwdevia" }
  ]
}
```

## Uso Rpido

Aps instalar o plugin GSD-PWDEVIA:

```bash
# Inicializar o framework no seu projeto
/gsd-pwdevia:gsd-init

# Task rpida (bugfix, config)
/gsd-pwdevia:gsd-quick "Fix validao de email"

# Feature completa (5 fases)
/gsd-pwdevia:gsd-discover "CRUD de usurios"
/gsd-pwdevia:gsd-design
/gsd-pwdevia:gsd-plan
/gsd-pwdevia:gsd-execute
/gsd-pwdevia:gsd-verify
```

## Estrutura do Repositrio

```
pwdev-claude-marketplace/
 .claude-plugin/
    marketplace.json       # Manifesto do marketplace
 plugins/
    gsd-pwdevia/           # Plugin GSD-PWDEVIA
        commands/          # 19 slash commands
        agents/            # 9 agentes especializados
        skills/            # Skills de conhecimento
        templates/         # Templates para projetos
        mcp.json           # MCP servers sugeridos
        INSTALL.md         # Guia de instalao
        README.md          # Documentao do plugin
        CLAUDE.md          # Referncia tcnica
 README.md                # Este arquivo
```

## Plugins em Detalhe

### GSD-PWDEVIA

> Get Stuff Done + Prompt Writer for Development with Iterative Agents

Framework que orquestra **9 agentes especializados** em **5 fases** para garantir que cada linha de cdigo seja planejada, rastrevel e verificada.

**Workflow:**

```
DISCOVER  DESIGN  PLAN  EXECUTE  VERIFY
```

**Skills includas:** Laravel 12+, Vue 3 + PrimeVue, React + Chakra UI v3, Frontend Design

Consulte o [README do plugin](./plugins/gsd-pwdevia/README.md) para documentao completa.

## Contribuio

1. Fork o repositrio
2. Crie sua branch (`git checkout -b meu-plugin`)
3. Adicione seu plugin em `plugins/seu-plugin/`
4. Atualize o `marketplace.json` com a referncia
5. Abra um Pull Request

### Estrutura mnima de um plugin

```
seu-plugin/
 .claude-plugin/
    plugin.json            # Manifesto (obrigatrio)
 commands/                # Pelo menos 1 command
    meu-command.md
 README.md
```

## Licena

MIT

---

*Mantido por [Paulo Soares](https://github.com/pwdev)*
