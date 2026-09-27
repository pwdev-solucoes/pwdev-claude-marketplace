# Hermes como coordenador do Orca

## Ferramentas

| Ação | Ferramenta do Hermes |
|---|---|
| Rodar `orca`, `gh`, `git`, `python3` | `terminal` (foreground) |
| Ler arquivo do projeto ou do plugin | `read_file` |
| Criar arquivo temporário (spec longo, corpo de reply) | `write_file` no diretório temporário da sessão, nunca no projeto |
| Perguntar ao usuário | terminar o turno com a pergunta e esperar |
| Carregar esta skill | `skill_view("pwdev-hermes-orca:hermes-orca")` |

`delegate_task` **não** é usado. Workers são sempre do Orca, porque só eles têm Dispatch,
supervisão e worktree próprias.

## Esperas longas

- O `terminal` em foreground tem teto de 600 s (`TERMINAL_MAX_FOREGROUND_TIMEOUT`) e padrão de
  180 s (`terminal.timeout`). Em todo `check --wait`, passe `timeout=600` ao `terminal` e
  `--timeout-ms 540000` ao Orca. A margem garante que o Orca devolva o controle antes do Hermes
  matar o comando.
- Um `check --wait` que expira é checkpoint: escreva ao usuário uma linha de status
  (`⏳ 2/3 issues em andamento; #15 em review`) e chame de novo.
- Nunca mande um `check --wait` para background (`background=true`). A Delivery precisa ser lida e
  confirmada nesta sessão.
- Nunca use `sleep` em loop. Quem espera é o `check --wait`.

## Argumentos longos

Spec de Task e corpo de reply podem ter várias linhas. Para não quebrar o quoting do shell, grave
o texto num arquivo temporário e passe `--spec "$(cat <arquivo>)"`. Nunca coloque segredos nesses
arquivos.

## Identidade do terminal

O coordenador roda num terminal gerenciado pelo Orca (`ORCA_TERMINAL_HANDLE` definido). Dentro
dele, `check` e `reply` não precisam de `--terminal`/`--from`: o Orca infere o chamador. Fora do
Orca, o preflight bloqueia a orquestração.

## Compactação

O Hermes não tem hook pós-compactação. Se a sessão compactar no meio de um Run:
1. Recarregue esta skill e rode `orca orchestration run-current --json` para recuperar o Run.
2. Rode `worker-list --json` para reconstruir o estado de cada Dispatch.
3. Continue o loop com `check --wait`. As Deliveries não confirmadas são reentregues, então nada
   se perde.
