# Anatomia de uma Skill pwdev-devops

Herdado de `pwdev-copy` e `pwdev-social-media`, com o que DevOps exige a mais.

## Estrutura
```
1. Frontmatter        description rica em gatilhos
2. Papel              uma frase
3. Princípio central  a regra que explica as decisões
4. Portão de segurança  classificação leitura/mutação/destrutivo
5. Diagnóstico        tabela sintoma → ordem de verificação
6. Comandos           leitura (livre) e mutação (com portão)
7. Anti-padrões       o que não fazer, e por quê
8. Limites            o que a skill NÃO faz + para onde mandar
9. Relacionadas
```

A seção 5 é o coração de uma skill de DevOps. **Tabela sintoma → ordem de
verificação** vale mais que qualquer explicação conceitual, porque é o que
alguém consulta às 3h da manhã.

## Portão de segurança

Toda skill que toca infraestrutura declara a classificação e aponta para
`references/execucao-segura.md`. O script `scripts/guard.sh` é a segunda
barreira, independente da instrução.

## Regras que nenhuma skill negocia

1. **Leitura livre, mutação sob confirmação, destrutivo sob confirmação reforçada.**
2. **Confirmação é por comando, não por sessão.** "Pode seguir" de três mensagens
   atrás não vale para o comando atual.
3. **Ambiente indeterminado = produção.** Nunca infira por nome de recurso.
4. **Nunca imprimir valor de segredo.**
5. **Preservar evidência antes de mitigar** durante incidente.
6. **Não pular do sintoma para o comando** — hipótese primeiro.
7. **Correlação não é causalidade** — hipótese é rotulada como hipótese.
8. **Declarar o que não foi verificado** ao final de todo diagnóstico.
9. **Não ampliar exposição de segurança**, nem com confirmação.
10. **Ferramenta ausente = modo consultivo**, nunca simulação.

## Confiança

| Nível | Base |
|---|---|
| Confirmado | evidência direta, comando mostrado |
| Provável | consistente com os sintomas, sem prova direta |
| Hipótese | explicação plausível ainda não testada |
