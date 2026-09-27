---
name: github-issues
description: >
  Cria, atualiza, comenta, fecha e reabre issues do GitHub e gerencia as tarefas de um
  GitHub Project — mover Status, editar campos, sub-issues e dependências "blocked by",
  inclusive em lote. Use quando o usuário disser "criar issue", "abrir uma issue", "fechar a
  issue #12", "reabrir", "comentar na issue", "atribuir para", "mover para Em andamento",
  "marcar como concluída", "bloqueada por", "sub-issue", "o que está bloqueando", "tarefas
  do project", "fechar as tasks da feature", ou citar #123 num repo GitHub. Não use para
  criar um Project novo (skill github-project) nem para publicar um roadmap inteiro
  (skill github-publish).
metadata:
  version: 0.1.0
---

# GitHub Issues e tarefas de Project

Você opera issues e itens de GitHub Projects pelo `gh` CLI, e pelo `ghp.py` onde o `gh` não
cobre (sub-issues, blocked-by, campos do Project por nome). Receitas exatas:
[gh-recipes](../../references/gh-recipes.md) — leia a seção da intenção antes de executar.

`GHP="<plugin-root>/scripts/ghp.py"`

## Contexto
- Repo e Project padrão: `.planning/github.json` (`repo`, `owner`, `project.number`). Sem ele,
  use o repo do diretório (`gh repo view`) e pergunte o Project só se a intenção precisar.
- Issues publicadas de um roadmap: `.planning/github/<slug>.map.json` traduz IDs do roadmap
  (`F01-E02-FT01`) em números (`#14`) — aceite os dois.
- Pré-requisitos: `gh auth status` ok; operações de Project exigem o scope `project`
  (`! gh auth refresh -s project`).

## Mapa de intenção

| Intenção | Como |
|---|---|
| Criar issue | `gh issue create --repo R --title --body-file --label --assignee --milestone`; opcional: adicionar ao Project e setar Status |
| Ver / listar | `gh issue view N --json ...` · `gh issue list --search "..."` |
| Editar | `gh issue edit N` (`--title`, `--body-file`, `--add-label`/`--remove-label`, `--add-assignee`, `--milestone`) |
| Comentar | `gh issue comment N --body-file` |
| Fechar | `gh issue close N --reason completed\|"not planned" --comment "..."` |
| Reabrir | `gh issue reopen N --comment "..."` |
| Sub-issue | `ghp.py link sub\|unsub --repo R --parent P --child C` |
| Dependência | `ghp.py link block\|unblock --repo R --issue N --blocker M` (N fica bloqueada por M) |
| O que bloqueia / o que é bloqueado | `ghp.py deps --repo R --issue N` |
| Mover no Project / editar campo | `ghp.py item set --owner O --number P --url URL --field Status --value "Em andamento"` |
| Adicionar ao Project | `gh project item-add P --owner O --url URL` |
| Arquivar item | `gh project item-archive P --owner O --id ITEM` |
| Marcar task do checklist | editar o corpo da feature trocando `- [ ] T0n` por `- [x] T0n` |
| Marcar critério de aceite atendido | editar o corpo (feature, ou sub-issue da história) trocando `- [ ] **CA-0n` por `- [x] **CA-0n` da história `US-xx` citada; fechar a história só quando todos os CA estiverem marcados |

## Regras

1. **Leitura é livre; escrita tem preview.** Antes de qualquer escrita mostre o que muda
   (issue, campo, de → para, texto do comentário) e espere um "sim". Um pedido explícito e
   inequívoco do usuário para *uma* operação ("fecha a #12 como concluída") conta como
   confirmação dessa operação; lotes sempre pedem confirmação.
2. **Fechar com contexto.** Sempre `--reason` e um comentário curto do porquê (o que foi
   entregue, PR, ou por que não será feito). Antes de fechar, rode `ghp.py deps`:
   - se a issue tem sub-issues abertas, avise e pergunte se fecha mesmo assim;
   - liste as issues que ela **bloqueia** e que ficam desbloqueadas — ofereça movê-las para
     `Pronto` no Project;
   - se todas as irmãs sob o mesmo épico/pai ficaram fechadas, ofereça fechar o pai.
3. **Status acompanha o estado.** Ao fechar como concluída, ofereça mover o item para
   `Concluído`/`Done`; ao reabrir, para `Em andamento`/`Backlog`. Use os nomes de opção que o
   Project realmente tem (`ghp.py project fields`).
4. **Em lote** ("fechar todas as tasks concluídas da FT01", "mover a onda 2 para Pronto"):
   resolva a lista (busca `gh issue list` ou o mapa do roadmap), mostre a tabela
   `# · título · de → para`, peça confirmação uma vez e execute item a item, relatando falhas
   sem abortar o resto.
5. **Nunca apagar.** Nada de `gh issue delete`, `gh project delete` ou `item-delete` sem pedido
   explícito com a palavra "apagar/excluir" — e mesmo assim confirme mostrando o alvo. Prefira
   fechar ou arquivar.
6. **Corpo por arquivo.** Textos com várias linhas vão por `--body-file` (arquivo temporário
   no scratchpad), nunca interpolados na linha de comando.
7. **Issue gerada por roadmap.** Título e corpo são sobrescritos no próximo publish. Para
   mudanças duráveis, diga que o lugar é o roadmap; comentários, labels extras, assignees e
   Status são seguros.

## Resposta
Curta: o que foi feito, com links (`#N` + URL) e o que mudou no Project. Em lotes, uma tabela
com resultado por item.

Idioma: responda no idioma de `.planning/config.json` (`lang`); sem config, no idioma do usuário. Caminhos `<plugin-root>/...`, `references/`, `scripts/` e `templates/` são relativos à raiz do plugin; nomes de ferramentas e a forma de citar comandos dependem do runtime (`references/runtime.md`).
