# PWDEV Power

Desenvolvimento orientado a especificação com disciplina, rodando em **Claude Code, Codex e
Hermes Agent**, com frotas autônomas isoladas no **cmux**.

Rápido como um planejador leve de features, com a camada de produto de um pesado, e com as
disciplinas de engenharia que normalmente nenhum dos dois carrega: um portão de brainstorming
antes de qualquer código, planos cujas restrições viajam literais até quem implementa, execução
com registro durável e ciclo de correção limitado, e verificação que tenta **refutar** a
conclusão em vez de confirmá-la.

## Instalação

```bash
# Claude Code
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-power

# Hermes Agent
hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable
# ou, para skills locais do repositório:
hermes skills trust .
```

O Codex descobre as skills pelo `.codex-plugin/plugin.json`; invoque com `$power-<nome>`.

## O ciclo

```text
/pwdev-power:init                  prepara o workspace e relata o ambiente disponível
/pwdev-power:product prd           entrevista e produz um requisito aprovado
/pwdev-power:product roadmap       Fase → Épico → Feature → Task, com rastreabilidade
/pwdev-power:plan <feature>        brainstorm → spec → plano executável
/pwdev-power:exec <slug>           task a task, com revisão entre elas
/pwdev-power:verify <slug>         verificação adversarial e integração
/pwdev-power:quick <tarefa>        mudança pequena, sem arquivo de plano
/pwdev-power:fleet <slugs>         fases aprovadas em paralelo, sem supervisão
```

Nenhum portão é cruzado sem um humano. Aprovação é **registrada**, nunca inferida.

## Do que é feito

Quatorze skills, quatro subagentes e doze contratos de referência. As skills são a única fonte
de verdade; cada runtime recebe apenas um adaptador fino.

| Skill | Dispara quando |
|---|---|
| `power` | início da sessão — como encontrar e aplicar as demais |
| `power-brainstorm` | qualquer comportamento novo, antes do design |
| `power-plan` | um design que precisa ser decomposto |
| `power-execute` | um plano aprovado que precisa rodar |
| `power-tdd` | escrever qualquer código de implementação |
| `power-debug` | um bug, uma falha ou uma surpresa |
| `power-verify` | qualquer afirmação de que algo funciona |
| `power-review` | pedir ou receber revisão |
| `power-product` | um requisito ou um roadmap |
| `power-quick` | mudança pequena e já compreendida |
| `power-worktree` | começar trabalho isolado |
| `power-finish` | implementação completa e verde |
| `power-fleet` | fases paralelas sem supervisão |
| `power-init` | repositório ainda sem workspace |

## Três regras que sobrevivem a qualquer racionalização

1. **Nenhum código de produção sem um teste falhando antes**, e o vermelho precisa ser observado.
2. **Nenhuma correção sem investigação de causa raiz antes**; três correções falhas significam
   que a arquitetura passou a ser a suspeita.
3. **Nenhuma afirmação de sucesso sem rodar o comando e ler a saída.**

## A frota

Uma fase aprovada, um worktree, um stack Docker, um workspace cmux. As portas vêm do primeiro
slot livre, são publicadas só em loopback, e o arquivo de ambiente gerado é escrito sob
`umask 077` e mantido fora do branch.

O comando privilegiado do provider existe em exatamente um adaptador por runtime, e nada mais
pode construir um. O runtime é fixado pelo launcher escolhido antes de qualquer mutação, gravado
no registro do membro, e um runner cujo adaptador discorda recusa iniciar. A flag perigosa de
cada runtime — `--dangerously-skip-permissions`, `--dangerously-bypass-approvals-and-sandbox`,
`--yolo` — é exibida e precisa ser reconhecida antes do primeiro lançamento.

O ciclo é `plan → execute → review → verify`, com no máximo **dois** ciclos de correção. Uma
terceira rejeição vai para o humano; nunca vira aprovação por cansaço.

O estado aparece na barra lateral do cmux, em vez de um painel que alguém precisa ficar olhando.
A frota nunca rouba o foco, e só fecha workspaces cujo identificador ela mesma registrou.

Exige o cmux em execução. Se o socket não responder, a frota diz isso e para.

## A rota Kanban

Com o Hermes disponível, `--via-kanban` transforma fases aprovadas em cards do Kanban do Hermes e
deixa o dispatcher dele executar, espelhando o estado no cmux. A ponte reaplica o portão de
aprovação por conta própria, porque o board não tem opinião sobre aprovação. A chave de
idempotência carrega o hash da spec: relançar devolve o mesmo card, uma spec editada gera um novo.

O que muda de dono nessa rota está documentado em `references/kanban.md`. Leia antes de usar.

## Limites conhecidos

- **O Hermes não tem hook de pós-compactação.** Uma sessão longa que compacta sobre o primeiro
  turno perde o bootstrap. Se as skills pararem de disparar, comece uma sessão nova — isso não
  tem conserto dentro do plugin. O Claude Code reinjeta no `compact`; o Codex descobre as skills
  nativamente.
- **Seleção de modelo por dispatch no Hermes ainda não está estabelecida.** Até estar, use
  `--model`/`--provider` do card do Kanban, ou execute inline. Veja `references/hermes-tools.md`.
- **A frota precisa do cmux.** Todo o resto funciona sem ele.
- **A auditoria é opt-in e precisa de `sqlite3`.** Criar o banco é o que a liga.

## Testes

```bash
python3 -m unittest tests.test_pwdev_power tests.test_power_hermes
```

`unittest discover` não funciona nesta árvore: uma forma levanta `ImportError` e a outra roda
zero testes em silêncio. Nomeie os módulos.

## Licença

Apache-2.0.
