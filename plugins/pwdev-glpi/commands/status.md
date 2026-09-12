---
description: Estado do plugin — configuração, REST, MCP e contexto do projeto
---

# Status do GLPI

Este comando slash é mantido para Claude Code. Codex e Hermes usam a skill
compartilhada e seus mecanismos nativos de diagnóstico.

## Verificações

1. Execute o verificador operacional distribuído com o plugin: node/npx,
   variáveis de ambiente, PAT mascarado, handshake REST e pacote npm.
2. Faça uma prova viva chamando `search_tickets` com `{"limit": 1}`.
3. Confirme o contexto do projeto (entidade, grupos e categorias).

O servidor pode listar tools sem configuração; isso não prova autenticação.
Nunca exiba credenciais. Reporte URL, PAT e App-Token apenas como
presente/ausente ou mascarados.
