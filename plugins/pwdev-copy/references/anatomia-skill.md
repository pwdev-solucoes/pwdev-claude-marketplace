# Anatomia de uma Skill pwdev-copy

Padrão que toda skill deste plugin segue. Use ao criar ou revisar uma skill.

## Estrutura

```
1. Frontmatter        description rica em gatilhos + metadata.derivado-de
2. Papel              uma frase: quem você é nesta skill
3. Princípio central  a regra que, sozinha, explica as decisões da skill
4. Antes de começar   leitura do contexto + portões + perguntas mínimas
5. Framework          o método — tabelas e passos numerados
6. Processo           a sequência de execução
7. Formato de saída   estrutura fixa, com placeholders
8. Anti-padrões       o que não fazer, com o motivo
9. Limites            o que a skill NÃO faz + para onde mandar
10. Relacionadas      links para skills vizinhas
```

## Path A / Path B

Toda skill que dependa de ferramenta externa declara **os dois caminhos**.
Princípio não basta — precisa ser mecanismo no corpo da skill.

```markdown
### Path A — Com MCP conectado
{{como coletar direto; declarar qual MCP e o intervalo coberto}}

### Path B — Sem MCP (padrão hoje)
{{o que pedir ao usuário, com especificidade}}
```

Regras:
- a skill **funciona** nos dois caminhos; MCP melhora o insumo, não é requisito
- em Path B, sempre declarar o que não pôde ser verificado
- nunca simular o resultado que o MCP daria

## Limites

Seção obrigatória. É o antídoto contra scope creep — sem ela, cada skill começa
a fazer um pouco de tudo e o roteamento entre skills deixa de funcionar.

```markdown
## Limites
- Não {{faz X}} — ver `{{skill}}`
- Não {{faz Y}} — ver `{{skill}}`
- Não acessa plataforma nem API sem MCP conectado
```

## Portões

Skill que depende de insumo anterior **para** em vez de improvisar:

| Portão | Verificar | Se vazio |
|---|---|---|
| Brief | seção 3 do contexto | parar → `/pwdev-copy:brief` |
| Voz | seção 5 | seguir degradado, com aviso |
| VOC | seção 6 | seguir degradado, com aviso |
| Baseline | seção 9 | análise descritiva, não comparativa |
| Volume | nº de peças | recusar análise de padrão |

## Regras que nenhuma skill negocia

1. Nunca inventar número, depoimento, certificação ou verbatim.
   Sem dado → `[PREENCHER: {{o que falta}}]`.
2. Nunca publicar, agendar ou enviar sem confirmação explícita.
3. Sempre declarar o que não pôde ser verificado.
4. Sempre respeitar a lista de proibidos (seção 5) e os vetos jurídicos (seção 7).
5. Correlação não é causalidade — hipótese é rotulada como hipótese.

## Confiança

Onde houver interpretação de dado, rotule:

| Nível | Base |
|---|---|
| Alta | padrão consistente, volume suficiente, mecanismo claro |
| Média | padrão presente, volume limitado ou variável confundida |
| Baixa | princípio geral, sem dado do cliente |
