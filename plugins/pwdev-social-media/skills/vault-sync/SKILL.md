---
name: vault-sync
description: >
  Arquiva briefs, peças e aprendizados no Obsidian (pasta local) e no Notion
  (via MCP). Use quando o usuário disser "salvar no Obsidian", "arquivar",
  "registrar no Notion", "biblioteca de peças", "documentar a campanha",
  "onde ficou aquela peça". Obsidian é filesystem direto — não precisa de MCP.
metadata:
  version: 1.0.0
---

# Arquivo e Sincronização

Você garante que a campanha do mês que vem encontre a do mês passado.

## Princípio central

> Peça que ninguém acha é peça que será refeita. **O arquivo existe para não
> produzir duas vezes a mesma coisa.**

## Obsidian — sem MCP

Um vault do Obsidian é uma **pasta de arquivos markdown no disco**. Leia e
escreva direto com Read, Write e Glob. Não existe motivo para MCP aqui.

Caminho na seção 7 do contexto.

### Estrutura sugerida
```
{{vault}}/
└── Criativos/
    ├── Campanhas/
    │   └── {{ano}}-{{mes}}-{{campanha}}.md
    ├── Pecas/
    │   └── {{campanha}}-{{n}}.md
    └── Aprendizados.md
```

### Nota de campanha
```markdown
---
campanha: {{nome}}
periodo: {{inicio}} — {{fim}}
canais: [{{lista}}]
figma: {{url}}
status: producao | publicado | arquivado
---

# {{campanha}}

## Conceito
## Peças
- [[{{campanha}}-01]]

## Desempenho
## Aprendizados
```

Use `[[links]]` do Obsidian entre notas — é o que faz o vault render.

## Notion — via MCP

Path A com MCP conectado: banco de peças, calendário editorial, fluxo de aprovação.

Path B sem MCP: entregue o markdown para colar. Não simule ter gravado.

### Divisão de responsabilidade
- **Notion** — o que a equipe consulta e aprova: calendário, status, aprovação
- **Obsidian** — o que fica como memória: conceito, aprendizado, referência
- **Figma** *(opcional)* — o arquivo editável, quando existe

Não duplique a peça nos três. Guarde o **link** e o contexto.

## O que arquivar

| Item | Onde | Por quê |
|---|---|---|
| Conceito | Obsidian | reaproveitável |
| **Prompt e seed** | **Obsidian** | **sem seed a peça é irreproduzível** |
| Link do Figma | ambos | fonte editável |
| Peça exportada | pasta de exports | entrega |
| Legenda e alt | Obsidian | reuso |
| Desempenho | Notion | decisão |
| Aprendizado | Obsidian | não repetir erro |

**Não arquive o PNG dentro do vault.** Vault de markdown com centenas de imagens
fica lento e pesado no sync. Guarde o caminho ou o link.

## Aprendizados

O item de maior valor e o mais esquecido. Ao fechar campanha, registre:

```markdown
## {{data}} — {{campanha}}
Funcionou: {{o quê}} — {{evidência}}
Não funcionou: {{o quê}} — {{evidência}}
Faria diferente: {{o quê}}
```

Sem evidência, é opinião. Marque como opinião quando for.

## Limites

- Não analisa desempenho — ver `perf-analyzer` do pwdev-copy
- Não publica
- Não move nem apaga arquivo do usuário sem confirmação
- Não grava no Notion sem MCP — entrega markdown

## Skills relacionadas

- `export-handoff` — origem do que se arquiva
- `creative-concept` — consome o arquivo em campanhas futuras
