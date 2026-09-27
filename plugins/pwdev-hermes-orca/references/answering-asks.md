# Respondendo aos workers

As perguntas do `feat-loop` chegam como `question` no formato
`[feat-loop #<N>][gate:<kind>] <pergunta>` e são respondidas com
`orca orchestration reply --id <message_id> --body "<resposta>" --json`. A resposta deve ser uma das
opções oferecidas ou texto livre quando o gate pede isso.

## Autonomia

O usuário aprovou o DAG no gate do plano. Dentro desse escopo você decide sozinho; fora dele,
leva ao usuário.

| Gate | Responda sozinho quando | Leve ao usuário quando |
|---|---|---|
| `interview` | a resposta está na issue, nos comentários ou no DAG aprovado; senão, `you-decide` com a escolha mais conservadora | a pergunta é de produto ou negócio que a issue não responde |
| `plan` / `quick` | o plano cobre só a issue, não toca arquivos de outra issue do Run e não traz migração destrutiva → `approve` | escopo maior que a issue, sobreposição com outra issue, migração destrutiva ou dependência nova de peso |
| `exec` | a branch não é a padrão e os arquivos sujos são do próprio worker → `proceed` | branch padrão, ou arquivos sujos alheios |
| `branch` | a branch é `feat/issue-<N>-*` ou a da worktree → `approve` | qualquer outra |
| `advice` | — | sempre (o worker já gastou advisor e retry) |
| `stopped` | — | sempre, com o motivo do worker e a sugestão de `continue` ou `abort` |
| `pr` | `pr_gate` é `false` na config → `open` | `pr_gate` é `true` |

Na dúvida, leve ao usuário. Uma pergunta ao usuário não bloqueia os outros workers: continue o
loop e responda o `reply` quando ele decidir.

## Levando ao usuário

Formato curto, uma issue por vez:

```
❓ #<N> (<agente>) pergunta [gate:<kind>]: <pergunta>
Contexto: <≤5 linhas>
Opções: <a> / <b> / <c>   Minha recomendação: <x>, porque <motivo>
```

Não faça o ack da Delivery que contém a pergunta enquanto o usuário não responder. Ela é
reentregue até o ack. Se precisar processar outras mensagens do mesmo lote, responda às que
puder e deixe a pergunta pendente para o próximo `check`.

## Escalations

`escalation` indica que o worker está bloqueado fora de um gate (por exemplo `gh` sem
autenticação ou branch inesperada). Resolva se estiver ao seu alcance e dentro do escopo, como
reenviar instrução com `send --to dispatch:<id>`. Caso contrário, leve ao usuário. Nunca pare nem
relance o worker por causa de uma escalation sem a prova positiva que o contrato do Orca exige.

## Dependências bloqueadas

Se uma issue termina com `failed` e outras dependem dela, crie um decision gate para cada Task
dependente ainda não despachada:
`orca orchestration gate-create --task <dependente> --question "#<A> falhou: seguir, pular ou cancelar?" --options '["seguir","pular","cancelar"]' --json`.
Leve a decisão ao usuário e registre a resposta com `gate-resolve`.
