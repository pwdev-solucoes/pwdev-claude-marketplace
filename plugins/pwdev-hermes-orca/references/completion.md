# Conclusão por issue e do Run

## Ao receber `worker_done`

1. **Validar a autoridade.** Task ID e Dispatch ID precisam ser os do Dispatch ativo esperado.
   Mensagem de um Dispatch antigo ou desconhecido não conclui nada: registre e siga.
2. **Validar a evidência**, sem abrir relatórios longos:
   - `--outcome succeeded`: o corpo traz a URL do PR. Confira com
     `gh pr view <url> --json state,headRefName,body,url` que o PR está aberto e que o corpo
     contém `Closes #<N>`. Leia só a linha `verdict:` do `--report-path`, que deve ser `APPROVED`.
     Se algo não bater, a issue é tratada como `failed (evidência inconsistente)`.
   - `--outcome failed`: guarde o resumo de três frases e o motivo (`STOPPED:*`, `FAILED`,
     `abort`).
3. **Registrar na issue** (um comentário, sem segredos), com `gh issue comment <N> --body-file <tmp>`:
   - sucesso: `PR <url> aberto pelo worker <agente> (review APPROVED). Aguardando revisão humana.`;
   - falha: `Tentativa automática parou: <motivo>. Branch <branch> preservada.`
4. **Status da worktree:** `orca worktree set --worktree name:issue-<N>-<slug> --workspace-status in-review`
   se deu certo; em caso de falha, mantenha `in-progress`.
5. **Destino do terminal**, exatamente um:
   - `worker-release --dispatch <id>`, o padrão após sucesso;
   - `worker-retain --dispatch <id>`, quando o usuário pediu para inspecionar ou após falha que
     ele queira depurar;
   - reuso imediato do mesmo terminal para um follow-up, só com um novo Dispatch.
6. **Próxima onda:** despache as Tasks que dependiam desta e agora estão livres.

Um `worker_done` válido já liquida a Task e o Dispatch. Não rode `task-update --status completed`.

## Retry

Só com decisão explícita do usuário e seguindo a referência de recuperação do Orca
(`--retry-of` exige `--task` e repete placement e agente). No máximo um retry por issue em cada
Run.

## Fim do Run

O turno só termina quando:
- todos os Dispatches esperados estão liquidados;
- `worker-list --run <run_id> --terminal-state reclaimable --json` volta vazio;
- o relatório abaixo foi entregue.

```
✅ Run <run_id> — <objetivo>
| Issue | Agente | Resultado | Evidência | Pendência |
| #12 | codex | PR aberto | <url> · review APPROVED | revisão humana |
| #15 | claude | falhou | STOPPED:review_not_approved · review.md | decisão do usuário |
Workers: 2 liberados, 0 retidos. Nada foi mergeado.
```
