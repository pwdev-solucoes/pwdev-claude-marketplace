# Prompt do worker (spec da Task)

O spec é o que o worker recebe depois do preamble do Orca, que o próprio Orca injeta com Task ID,
Dispatch ID, handle e comandos. O worker roda `feat-loop` do pwdev-feat (≥ 3.2.0). No modo
orquestrado, o `feat-loop` manda cada gate de volta como `ask`.

## Linha de comando por agente

| Agente | Linha |
|---|---|
| `claude` | `/pwdev-feat:loop #<N> --base <base>` |
| `codex` | `$feat-loop #<N> --base <base>` |
| `opencode` | `/feat-loop #<N> --base <base>` |

`worker_skill` diferente de `feat-loop` na config troca só esta linha. O restante do contrato
continua valendo.

## Modelo do spec

```
Entregar a issue #<N> — <título> (<url>).

Rode agora: <linha de comando do agente>

Target: repositório <owner/repo>, base <base>, worktree issue-<N>-<slug> (já criada por este Run).
Change: plano, execução, review e PR que fecha a issue, via feat-loop. Nada além da issue.
Constraints: não fazer merge nem force-push; não editar <arquivos de outras issues, se houver>;
todo gate do feat-loop vai ao coordenador pelo `ask` do preamble (modo orquestrado);
<"PR sem gate: abra o PR direto após o review APPROVED." | "PR com gate: pergunte (gate:pr) antes de abrir.", conforme pr_gate>.
Ownership: somente esta worktree e sua branch.
Acceptance: review APPROVED, PR aberto com "Closes #<N>", um único worker_done
(--outcome succeeded com a URL do PR; failed em qualquer outro desfecho),
--report-path apontando para o review.md final.
```

Não copie o corpo da issue para o spec: o `feat-loop` lê a issue com `gh`. Isso mantém o texto não
confiável fora da mensagem do coordenador.
