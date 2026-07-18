# Anatomia de uma Skill pwdev-social-media

Herdado de `pwdev-copy`, com os acréscimos da produção visual.

## Estrutura
```
1. Frontmatter        description rica em gatilhos + metadata.derivado-de
2. Papel              uma frase
3. Princípio central  a regra que explica as decisões da skill
4. Antes de começar   contexto + portões + perguntas mínimas
5. Framework          método, em tabelas e passos
6. Processo           sequência de execução
7. Formato de saída   estrutura fixa
8. Anti-padrões       o que não fazer, e por quê
9. Limites            o que a skill NÃO faz + para onde mandar
10. Relacionadas
```

## Portões deste plugin

| Portão | Verificar | Se ausente |
|---|---|---|
| **`/figma-use`** | carregada antes de `use_figma` | **parar** — exigência do MCP |
| Contexto | `.claude/pwdev-social-context.md` | parar → `/pwdev-social:init` |
| Brand kit | seção 3 do contexto | parar → `/pwdev-social:init --brand` |
| Copy aprovada | texto validado | parar → `/pwdev-copy:copy` |
| Chave de API | variável de ambiente | Path C → entregar prompt, não gerar |
| MCP Figma | conexão ativa | Path B → entregar especificação |

## Path A / B / C

```markdown
### Path A — Figma conectado
{{montar de fato; declarar o arquivo e os frames criados}}

### Path B — Sem Figma
{{entregar especificação completa; declarar que não montou}}

### Path C — Gerador de imagem sem chave
{{entregar prompt otimizado; declarar que não gerou}}
```

Nunca descrever artefato que não foi criado.

## Regras que nenhuma skill negocia

1. **Não descrever peça que não existe.** Sem Figma, é especificação — e diz isso.
2. **Não gastar crédito sem confirmação.** Toda chamada paga é confirmada antes,
   com estimativa.
3. **Não publicar.** Publicar é ato externo e irreversível — exige confirmação
   explícita, sempre.
4. **Token, nunca valor solto.** Cor e tipo vêm do design system.
5. **Acessibilidade não é opcional.** Contraste e texto alternativo são portão
   de aprovação, não sugestão.
6. **Não inventar dado em peça.** Número sem fonte vira `[PREENCHER: fonte]`.
7. **Nunca escrever chave de API em arquivo do projeto.**
