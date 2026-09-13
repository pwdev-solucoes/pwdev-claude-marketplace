# Runtime operacional

Todos os runtimes usam a mesma skill, `.mcp.json`, servidor `glpi` e as variáveis
`GLPI_BASE_URL`, `GLPI_PAT`, `GLPI_APP_TOKEN`, `GLPI_USE_SESSION` e
`GLPI_TIMEOUT_MS`.

## Claude Code

Instale o plugin, configure as variáveis no ambiente da sessão e reinicie-a. Os
comandos slash são atalhos opcionais; a skill compartilhada contém as regras.

## Codex

Instale pelo manifesto Codex, ative `$glpi` e disponibilize o servidor MCP pelo
manifesto portátil. Configure as variáveis no ambiente da sessão e reinicie-a.

## Hermes

O adaptador registra a skill `glpi`. O MCP é registrado manualmente, sem alterar
arquivos pessoais:

```sh
hermes mcp add glpi -- npx -y @soarescbm/mcp-glpi@0.4.0
```

Forneça as variáveis ao processo Hermes e valide chamando `search_tickets`.

## Contrato comum

GLPI 10.x/11.x exige Legacy V1 habilitada e URL terminada em `/apirest.php`.
O servidor mantém exatamente 20 tools, 2 prompts e 3 resources. Nunca imprima
PAT ou App-Token; use presença ou valor mascarado.
