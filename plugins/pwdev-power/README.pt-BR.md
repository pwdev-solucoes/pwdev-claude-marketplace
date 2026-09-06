# PWDEV Power

Desenvolvimento orientado a especificação com disciplina, rodando em **Claude Code, Codex e
Hermes Agent**, com frotas paralelas isoladas no **cmux** — acompanhadas lado a lado num painel, ou
deixadas rodando sem supervisão.

---

## Por que este plugin existe

Agentes de código falham de maneiras previsíveis. Começam a escrever antes de alguém combinar o
que construir. Escrevem o teste depois do código, então o teste valida o que foi feito e não o que
era necessário. Corrigem o sintoma que enxergam em vez da causa que não enxergam. Dizem "pronto"
sem rodar nada. E, quando trabalham em paralelo, sobrescrevem uns aos outros em silêncio.

Cada uma dessas falhas tem uma contramedida conhecida, e nenhuma é complicada. O difícil é aplicar
a contramedida sob pressão, no meio da tarefa, quando pular uma parece produtivo.

O `pwdev-power` codifica essas contramedidas como skills que o agente é obrigado a invocar, e
coloca um humano em cada portão que importa. Ele junta três coisas que costumam viver separadas:

- **Velocidade.** O planejamento acontece na conversa, não atrás de um subagente que não pode
  falar com você. Uma mudança pequena custa um comando.
- **Camada de produto.** Um requisito e, em seguida, um roadmap `Fase → Épico → Feature → Task`
  com rastreabilidade real, para que um esforço grande tenha espinha dorsal.
- **Disciplina de engenharia.** Um portão de brainstorming antes de qualquer código, planos cujos
  valores exatos chegam a quem implementa, execução com registro durável e ciclo de correção
  limitado, e verificação que tenta *refutar* a conclusão em vez de confirmá-la.

### Três regras que sobrevivem a qualquer racionalização

1. **Nenhum código de produção sem um teste falhando antes** — e o vermelho precisa ser
   *observado*, não presumido. Um teste que nunca falhou não prova nada quando passa.
2. **Nenhuma correção sem investigação de causa raiz antes.** Três correções falhas significam que
   a arquitetura virou suspeita, não a linha que você continua editando.
3. **Nenhuma afirmação de sucesso sem rodar o comando e ler a saída.** Evidência e depois
   afirmação — nunca o contrário.

---

## O modelo mental

**As skills são a única fonte de verdade.** Quatorze skills descrevem o trabalho. Cada runtime
recebe só um adaptador fino sobre elas: comandos de barra no Claude Code, `$power-*` no Codex, um
plugin nativo no Hermes. Não existe uma segunda implementação para divergir.

**Os portões pertencem a humanos.** Portão é o ponto em que o agente para, mostra algo e espera. A
aprovação é *registrada* — nunca inferida do silêncio, e nunca concedida pelo agente ao próprio
trabalho. Nada está aprovado só porque o arquivo existe.

**Contratos de status são curtos.** Um subagente escreve o relatório em arquivo e devolve no
máximo dez linhas. O orquestrador lê o status e o caminho — nunca o conteúdo do relatório. Essa
regra sozinha é o que mantém uma feature longa viável, em vez de afogar o contexto principal.

**O registro fica em disco.** O progresso da execução e cada decisão de arbitragem vivem no
`ledger.md`, cuja primeira linha o amarra ao seu plano. Um controlador que perde o lugar lê o
registro em vez de redespachar tasks já concluídas.

---

## Instalação

### Claude Code

```bash
/plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
/plugin install pwdev-power
```

Confira: `/pwdev-power:init` deve oferecer a criação do workspace.

### Codex

O plugin declara `"skills": "./skills/"`, então o Codex descobre as skills sozinho. Invoque com
`$power-<nome>`, por exemplo `$power-plan`.

Subagentes exigem isto em `~/.codex/config.toml`:

```toml
[features]
multi_agent = true
```

### Hermes Agent

```bash
# instalação global
hermes plugins install pwdev-solucoes/pwdev-claude-marketplace --enable

# ou, trabalhando dentro de um checkout, carregue as skills locais do repositório
hermes skills trust .
hermes skills list | grep power-
```

Confira: `hermes plugins doctor plugins/pwdev-power` deve reportar registro OK, e uma sessão nova
já deve conhecer a skill `power` sem que você a mencione.

### Para a frota (opcional)

A frota precisa do **cmux** e de `jq`, `git`, `python3` e `docker` no `PATH`. Todo o resto do
plugin funciona sem cmux.

```bash
cmux ping                    # responde quando o cmux está rodando
```

O cmux não precisa já estar aberto: o lançamento da frota inicia ele e espera o socket, avisando
enquanto faz isso. `POWER_CMUX_NO_AUTOSTART=1` desliga esse comportamento, e
`POWER_CMUX_START_TIMEOUT` (padrão 90 segundos) cobre uma partida fria lenta. O encerramento e o
`--status` nunca iniciam nada — abrir um aplicativo para fechar uma workspace seria absurdo.

Se a CLI não estiver no `PATH` (comum no macOS, onde ela fica dentro do bundle do app):

```bash
export PWDEV_POWER_CMUX_BIN=/Applications/cmux.app/Contents/Resources/bin/cmux
```

---

## Referência de comandos

| Comando | Argumentos | O que faz |
|---|---|---|
| `/pwdev-power:init` | `[--map \| --check]` | Cria `.planning/power/`, mapeia o codebase, relata o ambiente disponível |
| `/pwdev-power:product` | `prd [descrição] \| roadmap [caminho]` | Entrevista para um requisito, ou decompõe um já aprovado |
| `/pwdev-power:plan` | `<descrição da feature>` | Faz brainstorm, projeta e decompõe em tasks |
| `/pwdev-power:exec` | `<slug-da-feature>` | Executa um plano aprovado, task a task |
| `/pwdev-power:verify` | `<slug-da-feature> [--strict]` | Verificação adversarial e integração |
| `/pwdev-power:quick` | `<tarefa delimitada>` | Mudança pequena e compreendida, sem arquivo de plano |
| `/pwdev-power:fleet` | `<slug...> [--auto] [--via-kanban] \| --status \| --teardown <slug> [--merge]` | Fases aprovadas em paralelo — painel visual no cmux de 1 a 4, ou sem supervisão |

As skills também disparam sozinhas — você não precisa citar `power-tdd` para que ela valha quando
código está sendo escrito.

---

# Cenários

Cada cenário abaixo é um caminho completo: o que você digita, o que acontece e onde você para.

---

## Cenário A — Um produto novo, do zero

O caminho completo. Use quando estiver começando algo substancial e ninguém escreveu o requisito
ainda.

### A1. Preparar

```
/pwdev-power:init
```

Ele detecta antes de perguntar: se é repositório git, se é greenfield ou brownfield, qual a stack
(lida de `package.json`, `pyproject.toml`, `go.mod` e afins — inclusive os comandos *reais* de
teste e lint) e quais de cmux, Hermes, `jq` e `sqlite3` estão disponíveis.

Depois, no máximo três perguntas: idioma, perfil de modelo (`economy` / `balanced` /
`performance`) e se a trilha de auditoria fica ligada.

Num repositório que já tem código, ele também despacha o subagente `mapper` para escrever o mapa
do codebase — veja [O mapa do codebase](#o-mapa-do-codebase) adiante. Num repositório greenfield
ele pula essa etapa e avisa: um mapa de diretório vazio é ruído que as fases seguintes leriam como
fato.

**Produz:** `.planning/power/config.json`, `.planning/power/state.md` e — em brownfield —
`.planning/power/context/`.

### A2. Escrever o requisito

```
/pwdev-power:product prd "sistema de agendamento para clínicas municipais de saúde"
```

Três rodadas, no máximo quatro perguntas por rodada, **feitas uma de cada vez** — uma lista
numerada de seis perguntas é respondida como formulário, e formulário se responde por cima.

1. Visão e problema — quem tem, o que faz hoje, quanto isso custa.
2. Escopo e capacidade — o que precisa existir, o que seria bom, o que fica de fora.
3. Restrições e sucesso — prazos, conformidade, integrações, números-alvo.

Depois ele escreve um requisito de dez seções e revisa o próprio trabalho antes de mostrar: todo
requisito não-funcional é *mensurável* (um número, não "rápido")? Todo item obrigatório tem
critério de aceite? Algo em "requisitos funcionais" é na verdade decisão de design, que pertence a
uma spec?

🚦 **PORTÃO.** Ele mostra o requisito e espera. Na aprovação, marca `Status: APPROVED`.

**Produz:** `.planning/power/product/prd.md`

### A3. Decompor em roadmap

```
/pwdev-power:product roadmap
```

Primeiro ele valida o requisito. Se faltam objetivos, requisitos funcionais, critérios de aceite
ou fronteiras de escopo, ele te manda de volta — três ou mais faltando significa que o roadmap
seria ficção.

Então despacha o subagente `roadmap`, que escreve arquivos e devolve dez linhas. A ordenação é por
dependência técnica primeiro, depois valor de negócio, depois risco — trabalho arriscado cedo,
enquanto errar ainda é barato.

🚦 **PORTÃO.** Você vê as contagens e o caminho raiz. Peça ajustes e ele redespacha; não remenda a
saída na mão.

**Produz:**

```text
.planning/power/product/roadmap/
├── ROADMAP.md          índice
├── TRACEABILITY.md     requisito ↔ roadmap, nos dois sentidos — obrigatório
├── RISKS.md · METRICS.md · ROLLOUT.md
└── F01-<slug>/
    ├── PHASE.md · CHECKLIST-F01.md
    └── F01-E01-<slug>/
        ├── EPIC.md
        └── F01-E01-FT01-<slug>.md
```

Um roadmap sem `TRACEABILITY.md` é recusado. É o arquivo que prova que todo requisito foi parar em
algum lugar e que toda fase remete a um requisito.

### A4. Planejar a primeira fase

```
/pwdev-power:plan "F01-E01 — cadastro de clínicas e salas"
```

**Ele classifica em voz alta antes de perguntar qualquer coisa** — spike, delimitado ou
arquitetural — porque a classificação decide quanto processo vem depois, e esconder isso esconde a
decisão.

Para um subsistema novo, é *arquitetural*: ele explora o código, pergunta uma coisa de cada vez,
oferece duas ou três abordagens com trade-offs reais **e uma recomendação**, e depois percorre o
design seção por seção, para que uma discordância custe uma seção em vez do documento inteiro.

🚦 **PORTÃO 1.** A spec. Na aprovação, exatamente um campo `Status: APPROVED`.

Aí ele decompõe. O plano é escrito para um engenheiro que chega em uma task, não tem nada do seu
contexto e nunca verá as outras tasks:

```markdown
## Global Constraints
- Timeout de requisição: 2500ms
- Tamanho de página: no máximo 50 itens

## File Structure
...

## Task 01 — modelo de clínica e migração
Complexity: low
Files: src/models/clinic.ts, migrations/001_clinics.sql
Interfaces:
  Produces: `findClinic(id: string): Promise<Clinic | null>`
Steps:
- [ ] Escrever um teste falhando para buscar clínica por id
- [ ] Rodar e ver falhar pela função ausente
- [ ] Implementar findClinic
- [ ] Rodar e ver passar
- [ ] Commit
```

O `Global Constraints` é copiado **literalmente** da spec, nunca resumido — o revisor confere
contra esse bloco, então uma paráfrase aqui vira um veredito errado lá. O bloco `Interfaces:` é
como um implementador que vê uma task descobre o que os vizinhos esperam.

🚦 **PORTÃO 2.** O mapa de tasks — id, nome, complexidade, arquivos.

**Produz:** `spec.md` e `plan.md` em `.planning/power/features/<slug>/`

### A5. Executar

```
/pwdev-power:exec cadastro-clinicas
```

O que acontece, por task:

1. **Varredura preliminar** (uma vez, antes da Task 01) — uma tabela com uma linha por par de
   tasks que compartilha arquivo ou interface, e uma linha por task confirmando que o texto dela
   concorda consigo mesmo.
2. **Despacho** — um implementador novo recebe o caminho do brief, as interfaces que consome e o
   caminho do relatório. Nunca o plano inteiro, nunca a conversa acumulada.
3. **Relatório** — `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT` ou `BLOCKED`.
4. **Revisão** — um revisor novo recebe o brief, o relatório, o diff e as restrições literais, e
   devolve dois vereditos independentes: conformidade com a spec *e* qualidade da task.
5. **Ciclo de correção, se preciso** — no máximo **cinco rodadas**. As rodadas 1–3 retomam o
   implementador original, que ainda tem o contexto; as 4–5 usam um novo, um tier de modelo acima.
   Achados menores vão para o registro e nunca entram no ciclo.
6. **Conclusão** — `Task NN: complete (commits abc1234..def5678, review clean)`.

No fim você recebe cada linha `Ruling:` do registro, em ordem, com o custo caso a decisão esteja
errada. Uma decisão que morre junto com o workspace foi uma decisão tomada em segredo.

### A6. Verificar e integrar

```
/pwdev-power:verify cadastro-clinicas
```

A instrução do verificador não é "conferir se está completo" — é **"tentar refutar que está
completo"**. Para cada verdade declarada, ele desenha um comando que *falharia* se a verdade não
valesse, roda e registra a saída real.

Ele presta atenção especial nas proibições (as menos testadas e as mais violadas, porque nada
falha quando você quebra uma) e em testes que não conseguem falhar (reverta a implementação; o
teste tem que ficar vermelho).

Use `--strict` para duas lentes em paralelo — funcional e conformidade — em que o veredito é o
pior dos dois. Algo que funciona mas viola uma proibição declarada não está aprovado.

| Veredito | Próximo passo |
|---|---|
| `APPROVED` | integrar |
| `CAVEATS` | integrar, com os achados expostos |
| `REJECTED` | plano de correção delimitado e nova verificação — no máximo duas vezes |

Depois o `power-finish` roda a suíte completa e, só com ela verde, mostra o menu: merge local,
push com pull request, ou deixar como está. Descartar exige que você digite a palavra `discard`.

---

## Cenário B — Uma feature em código que já existe

Pule a camada de produto inteira.

```
/pwdev-power:init                              # uma vez por repositório — também mapeia o codebase
/pwdev-power:plan "adicionar exportação CSV na lista de pacientes"
```

É aqui que o mapa se paga: o brainstorm parte da arquitetura e do vocabulário já registrados em
vez de redescobri-los, e o plano nomeia caminhos que existem.

Aqui o brainstorm provavelmente vai classificar como **delimitado**: uma mudança bem escopada em
um fluxo que já existe e pode ser lido. Delimitado significa um design curto *na conversa*, sem
arquivo de spec e sem plano — e então ele para e espera um sim explícito antes de implementar.

Se ficar claro que a mudança precisa de uma interface nova, a classificação **sobe** para
arquitetural no meio da conversa, e ele diz isso. A catraca só gira num sentido: complexidade
escondida eleva o caminho, nada nunca o rebaixa.

Para arquitetural, siga exatamente de A4 a A6.

---

## Cenário C — Uma mudança de um a três arquivos

```
/pwdev-power:quick "o teto de retentativas deve ser 5, não 3"
```

Ele lê os arquivos de verdade (mudança pequena proposta de memória do código é chute), mostra um
mini-plano de três linhas, espera um sim, implementa, verifica e commita.

**Ele escala em vez de derivar** assim que qualquer destas for verdade: mais de três arquivos;
você não sabe nomear o modo de falha; adiciona interface ou migração; toca em autenticação,
pagamento, permissão ou remoção de dados; ou você está prestes a escrever "já que estou aqui".

Mesmo aqui vale TDD. "É só uma linha" é a forma mais comum de um teste que faltava nunca ser
escrito.

**Produz:** `.planning/power/quick/<data>-<slug>/{contract,report}.md` — dois arquivos curtos, para
que um padrão de mudanças rápidas na mesma área vire evidência visível de que aquela área precisa
de um plano de verdade.

---

## Cenário D — Alguma coisa quebrou

Você não precisa de comando. Descrever um bug dispara o `power-debug`, que se recusa a propor
correção antes de ter uma causa.

```
O endpoint de agendamento retorna 500 para clínicas criadas hoje.
```

1. **Causa raiz** — ler o erro *inteiro*; reproduzir de forma consistente; ver o que mudou
   recentemente. Em sistema com vários componentes, **instrumentar cada fronteira antes de propor
   qualquer coisa** e rodar uma vez para descobrir *onde* quebra. Rastrear o dado de trás para
   frente, do errado até o certo.
2. **Análise de padrão** — achar algo neste mesmo código que funciona da mesma forma, ler por
   inteiro e listar todas as diferenças. A que parece irrelevante costuma ser a resposta.
3. **Uma hipótese por vez**, escrita, com o menor teste que a derrubaria. Se estava errada,
   formule uma *nova* — não empilhe outra correção sobre a tentativa anterior.
4. **Correção** — teste falhando primeiro, causa raiz uma vez, sem "já que estou aqui", e depois
   verificar.

**Depois de três correções falhas ele para** e traz a arquitetura para você. Continuar custa mais
do que perguntar.

---

## Cenário E — Chegou uma revisão

```
Segue a revisão do PR: <cole aqui>
```

O `power-review` roda LER → ENTENDER → VERIFICAR → AVALIAR → RESPONDER → IMPLEMENTAR.

Ele confere cada achado contra o código antes de agir — revisores às vezes erram sobre o que o
código faz, principalmente os externos — e, se **qualquer** achado estiver obscuro, ele para e
pergunta antes de implementar **qualquer um**, porque achados interagem entre si.

Não há concordância performática. Nada de "Você está certíssimo!", nada de agradecimento.
Discordar com razão técnica é um desfecho normal e esperado.

Para pedir revisão do seu próprio trabalho, ele monta o contexto do revisor de propósito —
requisitos, diff, restrições — em vez de entregar o histórico da sessão, e nunca diz ao revisor o
que deixar de apontar.

---

## Cenário F — Várias fases ao mesmo tempo

Para fases aprovadas que não se sobrepõem. Cada membro ganha worktree e stack Docker próprios. Como
você acompanha é a escolha: um **painel visual**, com as sessões lado a lado e você conduzindo
qualquer uma, ou uma **frota sem supervisão**, que roda a máquina de estágios sozinha.

### F1. Pré-condições

- cmux instalado (o lançamento inicia ele se não estiver rodando)
- Cada slug tem `spec.md` com **exatamente um** campo `Status: APPROVED`, mais `plan.md`
- Um branch atual nomeado — nada de HEAD destacado

### F2. Lançar

```
/pwdev-power:fleet cadastro-clinicas regras-agendamento
```

Por padrão isso abre um **painel visual**: uma workspace do cmux com uma pane por fase, cada pane
uma sessão Claude interativa no seu próprio worktree, já lendo o spec e o plan daquela fase. Você
vê todas ao mesmo tempo e conduz qualquer uma. O painel comporta **1 a 4 membros**, e só um painel
roda por vez.

Use `--auto` para a frota sem supervisão: uma workspace por membro, resultado estruturado, ciclos
de correção, ninguém olhando.

Ele mostra o formato exato do comando do seu runtime e do modo, e **exige que você reconheça a
flag perigosa** antes de lançar qualquer coisa:

| Runtime | Vetor visual | Vetor sem supervisão |
|---|---|---|
| Claude Code | `claude --dangerously-skip-permissions <brief>` | `claude -p --dangerously-skip-permissions --no-session-persistence --output-format json` |
| Codex | não implementado | `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral --cd <worktree> --output-schema <schema> --output-last-message <arquivo>` |
| Hermes | não implementado | `hermes -z <prompt> --in <worktree> --yolo --accept-hooks` |

**Olhar não é aprovar.** A sessão visual continua rodando com as permissões contornadas e continua
agindo entre uma olhada e outra, então o reconhecimento é exigido ali igual ao `--auto`.

Se dois slugs mencionam os mesmos caminhos do repositório, você recebe um aviso consultivo
nomeando-os. Ele não bloqueia — sobreposição plausível é comum e só você sabe se importa ali.

Com `--auto`, cada membro então roda `plan → execute → review → verify` por conta própria,
commitando por estágio. No painel não há máquina de estágios: o laço é você.

### F3. Acompanhar

No **painel**, você acompanha as panes. Cada aba se renomeia com o nome da própria sessão, então o
grid se lê de relance, sem nenhuma instrumentação.

Com **`--auto`** não há pane para olhar, e o estado vive na **barra lateral do cmux** — âmbar
rodando, verde concluído, vermelho quando um membro precisa de você, mais uma notificação.

```
/pwdev-power:fleet --status
```

dá uma tabela única para os dois modos: slug, runtime, modo, estágio, status, portas e uma mensagem
curta. Membro de painel aparece como `visual` e *driven by a human in a panel pane* — esse é o
estado normal dele, não um runner faltando. Nunca imprime caminhos de worktree, logs ou prompts.

As portas vêm do primeiro slot livre, e um slot só conta como livre quando nada mais o segura: o
índice está desocupado, as portas não colidem com as de outro membro, e nenhuma das duas responde a
uma sonda ao vivo. Ou seja, o seu próprio Postgres na `5432` não trava o lançamento — a frota pega
o próximo slot e segue. Publicadas só em loopback.

### F4. Quando um membro é rejeitado — só no `--auto`

Um `verify` com `REJECTED` inicia um ciclo de correção: `execute-fix → review-fix → verify`. No
máximo **dois** ciclos, ou seja, dez invocações de provider no pior caso. Uma terceira rejeição
vira `NEEDS_HUMAN` — nunca vira aprovação por cansaço.

### F5. Encerrar

```
/pwdev-power:fleet --teardown cadastro-clinicas
```

Para o stack, remove o registro do membro e **preserva o branch e o worktree** — um membro que
falhou é evidência. O volume do banco é mantido e reportado junto com o comando para removê-lo.

No painel ele fecha **a pane daquele membro** e deixa as irmãs rodando; a workspace vai embora com
o último membro. Com `--auto` ele fecha a workspace própria do membro.

```
/pwdev-power:fleet --teardown cadastro-clinicas --merge
```

Faz o merge no branch base. Recusado para qualquer membro que não esteja `DONE`, e o status
terminal é revalidado antes.

---

## Cenário G — Deixar o Hermes orquestrar a frota

Requer a CLI `hermes`. Fases aprovadas viram cards no Kanban do Hermes e o dispatcher dele executa.

```
/pwdev-power:fleet cadastro-clinicas regras-agendamento --via-kanban
```

Por baixo, e sempre com preview antes:

```bash
scripts/kanban-bridge.sh preview cadastro-clinicas   # imprime os comandos exatos; não cria nada
scripts/kanban-bridge.sh create  cadastro-clinicas   # cria os cards e grava os ids
hermes kanban dispatch --dry-run --json              # mostra o que seria disparado
hermes kanban daemon --interval 60                   # ou dispare de verdade
scripts/kanban-bridge.sh mirror                      # estado do board → barra lateral do cmux
```

O mapeamento:

| pwdev-power | `hermes kanban` |
|---|---|
| Fase aprovada | `create --workspace worktree:<caminho>` |
| Limite de correção | `--max-retries 2` |
| Tempo máximo do membro | `--max-runtime 2h` (SIGTERM → SIGKILL → refila) |
| Dependências | `--parent <id>`, `kanban link` |
| Portão humano | `request-review` / `request-changes` |

**A chave de idempotência carrega o hash da spec.** Relançar a mesma fase aprovada devolve o
*mesmo* card em vez de duplicar; uma spec editada gera uma chave diferente e, portanto, um card
genuinamente novo.

**Leia `references/kanban.md` antes de usar esta rota.** Nela, o limite de correção passa a ser o
`--max-retries` do dispatcher, e o portão humano passa a ser o `request-review` no card. O que
*não* muda de dono são os hashes de contrato — o board não sabe distinguir uma spec editada de uma
aprovada, então este plugin continua conferindo.

---

## Cenário H — Trabalhando no Codex

As mesmas skills, outra forma de invocar.

```
$power-plan adicionar exportação CSV na lista de pacientes
$power-execute cadastro-clinicas
```

Comportamentos do Codex que as skills já levam em conta:

- Use `fork_turns: "none"` somente quando um contexto novo e isolado for um requisito deliberado
  do fluxo; nos demais casos, preserve o contexto adequado à tarefa.
- Spawns herdam os padrões do host para modelo e esforço de raciocínio, salvo override explícito
  do usuário, governança, configuração ou perfil aprovado. O override precisa ser uma combinação
  suportada e exposta pelo host.
- Inspecione a superfície real de ferramentas do Codex. Hosts atuais normalmente expõem
  `exec_command` para leitura, busca e comandos e `apply_patch` para edições, mas as skills não
  devem inventar nomes indisponíveis.
- Rodadas de correção 1–3 usam `followup_task` para falar com o implementador que já tem o
  contexto, em vez de criar um novo.
- `wait_agent` é assinatura de evento, não poll: uma espera com timeout de 5–10 minutos, não oito
  esperas curtas.

Para rodar uma frota do Codex, use `codex-fleet-up.sh`. Seu runtime é fixado no lançamento e um
runner com adaptador diferente se recusa a iniciar. O painel visual é só do Claude por enquanto; no
Codex a frota roda sem supervisão.

---

## Cenário I — Trabalhando no Hermes

O bootstrap carrega no primeiro turno da sessão, então o agente já sabe que as skills existem.

```
skill_view("pwdev-power:power-plan")
skill_view("pwdev-power:power-tdd")
```

Se uma busca com namespace devolver "not found", o bootstrap imprime o diretório absoluto das
skills para uso com `read_file`.

Sem interface, para scripts e CI:

```bash
hermes -z "carregue pwdev-power:power-quick e suba o teto de retentativas para 5" --in .
```

Duas particularidades do Hermes que vale conhecer:

- **O contexto do subagente é explícito** em `delegate_task(goal=…, context=…, toolsets=[…])`. Não
  há transcript para suprimir, o que combina com a regra deste plugin de entregar ao filho o brief
  dele e não o histórico acumulado.
- **Não existe hook de pós-compactação.** Veja *Limites conhecidos*.

---

## Cenário J — Ligar a trilha de auditoria

Desligada por padrão. Exige três coisas, e criar o banco é o que efetivamente a liga:

```bash
# 1. optar por ligar
jq '.audit = true' .planning/power/config.json > tmp && mv tmp .planning/power/config.json

# 2. sqlite3 precisa estar instalado
command -v sqlite3

# 3. criar o banco — nada é registrado até ele existir
mkdir -p .planning/power/audit
sqlite3 .planning/power/audit/pwdev-audit.db "SELECT 1;"
```

Consulte direto:

```bash
sqlite3 -header -column .planning/power/audit/pwdev-audit.db \
  "SELECT timestamp, phase, action, target FROM events ORDER BY id DESC LIMIT 20;"

# todos os resultados de portão
sqlite3 .planning/power/audit/pwdev-audit.db \
  "SELECT timestamp, phase, action FROM events WHERE action LIKE 'gate_%';"
```

**Nomes de modelo e prompts nunca entram na trilha.** Qualquer chave contendo `model` ou `prompt` é
rejeitada antes da escrita, então um despacho registra um *tier* (`tier=mid`), não o nome do
modelo. Os alvos são gravados relativos à raiz do repositório; caminhos absolutos são rejeitados.
A auditoria é best-effort por construção e sempre sai com 0 — um registro que falha jamais pode
alterar o resultado do ciclo que ele estava descrevendo.

---

## O mapa do codebase

Escrito pelo `/pwdev-power:init` num repositório que já tem código, e atualizado com
`/pwdev-power:init --map`. Quatro documentos curtos em `.planning/power/context/`:

| Arquivo | Contém |
|---|---|
| `project.md` | propósito, arquitetura, estrutura, convenções, os comandos **reais**, fronteiras |
| `stack.md` | linguagens, frameworks, bancos e as versões observadas, lidas dos lockfiles |
| `domain.md` | o vocabulário que o código usa e os invariantes que ele assume |
| `pitfalls.md` | riscos e modos de falha, **cada um com evidência** — arquivo, commit, comando |

Quatro arquivos em vez de um para que cada leitor carregue só o que precisa: um implementador quer
convenções e versões, quem depura quer as armadilhas.

É **observação, nunca decisão.** Nada ali escolhe uma abordagem ou propõe refatoração — isso
pertence a uma spec, atrás de um portão. Os comandos são lidos dos manifestos em vez de presumidos,
então um passo do plano nunca roda `npm test` contra um projeto `pytest`.

Quem lê o quê:

- `power-brainstorm` — `project.md` e `domain.md`, para o design usar as palavras que o código já
  usa. Propor `Patient` onde o código diz `Beneficiary` produz um design que ninguém consegue
  mapear no repositório.
- `power-plan` — `project.md` e `stack.md`, para o `File Structure` nomear caminhos reais.
- `power-execute` — passa os **caminhos** para cada implementador, nunca o conteúdo. Colar o mapa
  em cada brief custa exatamente o contexto que o mapa foi escrito para economizar.
- `power-debug` — lê `pitfalls.md` *primeiro*. A investigação mais barata é descobrir que alguém já
  fez.
- `power-verify` — os comandos reais de teste e lint.
- `power-quick` — as convenções, numa mudança pequena demais para justificar exploração.

**Mapa é um retrato e envelhece.** O `project.md` registra o commit em que foi tirado, então a
defasagem é mensurável e não uma sensação. Quando o mapa e o código discordam, **o código está
certo** — o agente diz isso e oferece remapear, em vez de raciocinar a partir de um documento que
acabou de ver contradito.

```bash
/pwdev-power:init --map      # a stack mudou, ou uma refatoração moveu fronteiras
/pwdev-power:init --check    # relata defasagem e ambiente; não escreve nada
```

---

## O que fica em disco

```text
.planning/power/
├── config.json                     idioma, perfil de modelo, auditoria, frota, kanban
├── state.md                        status, último portão, ciclos de correção, próxima ação válida
├── context/                        o mapa do codebase — só em brownfield
│   ├── project.md                  arquitetura, convenções, comandos reais, fronteiras
│   ├── stack.md                    tecnologias e versões observadas
│   ├── domain.md                   vocabulário e invariantes
│   └── pitfalls.md                 riscos e modos de falha, com evidência
├── product/
│   ├── prd.md
│   └── roadmap/                    ROADMAP, TRACEABILITY, RISKS, METRICS, ROLLOUT + fases
├── features/<slug>/
│   ├── spec.md                     o design aprovado
│   ├── plan.md                     restrições globais + interfaces por task
│   ├── ledger.md                   progresso + cada Ruling:
│   ├── task-01-brief.md            o que o implementador realmente lê
│   ├── task-01-report.md           o que ele fez, com saída real dos comandos
│   ├── task-01-review.md           dois vereditos e os achados
│   ├── verdict.md                  evidências da verificação
│   └── fix-01.md                   tasks de correção delimitadas, em caso de rejeição
├── quick/<data>-<slug>/            contrato + relatório
├── fleet/<slug>.json               runtime, modo, worktree, portas, hashes de contrato, ids cmux
├── fleet/<slug>.pane.sh            o que a pane do membro executa
├── fleet/<slug>.surface            o relato da própria pane sobre qual surface do cmux ela é
├── fleet-status.json               por worktree: estágio, status, veredito, ciclos de correção
└── audit/pwdev-audit.db            opcional
```

Markdown é contrato legível por humanos; JSON é configuração e controle operacional. IDs de task
têm dois dígitos e permanecem estáveis do plano à execução e à correção — uma correção da task 03
é sempre sobre a task 03.

---

## Todos os portões, em uma tabela

| Portão | Quem decide | Registrado em |
|---|---|---|
| Requisito aprovado | você | `state.md` + `Status:` no `prd.md` |
| Roadmap aceito | você | `state.md` |
| Design aprovado | você | `state.md` + exatamente um `Status: APPROVED` no `spec.md` |
| Plano aprovado | você | `state.md` |
| Revisão de task | o subagente revisor | `task-NN-review.md` |
| Veredito de verificação | o verificador e, em `REJECTED`, você | `verdict.md` |
| Lançamento de frota | você, ao reconhecer o vetor | o registro do membro |
| Integração do branch | você, num menu de três opções | — |

"Exatamente um `Status: APPROVED`" é proposital. Um documento com um segundo campo dentro de um
bloco de exemplo é ambíguo, e ambiguidade aqui significa lançar trabalho não aprovado.

---

## Como a frota se mantém segura

- **O comando privilegiado existe em exatamente um adaptador por runtime.** Nada mais no plugin
  pode montar um comando de provider ou acrescentar flag de permissão. Os testes executam os três
  adaptadores e comparam o argv real: `claude` nunca leva `--yolo`, `hermes` nunca leva flag
  `--dangerously`.
- **O runtime é fixado antes de qualquer mutação.** Ele é escolhido pelo launcher, gravado no
  registro do membro, e um runner cujo adaptador discorda se recusa a iniciar. Nenhum valor de
  configuração, variável de ambiente ou argumento transforma um vetor em outro.
- **Os contratos são hasheados no lançamento** — os bytes exatos aprovados na working tree, não os
  bytes do `HEAD`, porque uma spec aprovada frequentemente ainda não foi commitada. Os hashes são
  reconferidos antes e depois de cada estágio, então editar uma spec no meio do caminho para o
  membro em vez de mudar silenciosamente o que está sendo construído.
- **O provider lidera o próprio grupo de processos.** Colher um provider bem-sucedido não libera a
  posse: o grupo inteiro de descendentes precisa ser comprovadamente encerrado antes de validar
  resultado, commitar ou avançar — ele pode ter deixado servidores de desenvolvimento ou
  contêineres filhos vivos.
- **Um estágio precisa produzir trabalho.** JSON bem formado descrevendo trabalho que ninguém fez é
  pego perguntando ao git se o HEAD andou ou se o diretório da feature está sujo.
- **Arquivos gerados nunca chegam ao branch.** O arquivo de ambiente é escrito sob `umask 077`
  *antes* do conteúdo existir, e um `.gitignore` gerado mantém ele e a saída bruta do provider fora
  do que o `git add -A` levaria para o seu branch base no merge.
- **Comando privilegiado nunca é digitado em shell vivo.** A sessão de todo membro — autônoma ou
  interativa — é alcançada por arquivo shell-quotado. O painel é montado numa única chamada
  `new-workspace --layout` por isso, já que cada surface do layout carrega o próprio comando;
  crescer um painel vivo dividindo dentro dele e mandando teclas abriria mão disso, e é por isso
  que um segundo painel é recusado.
- **As panes se identificam sozinhas.** Cada uma registra o próprio id de surface do cmux antes de
  iniciar o provider, então o encerramento fecha a pane daquele membro e não uma pane deduzida por
  posição.
- **A frota nunca rouba o foco** e só fecha workspaces e surfaces do cmux cujo identificador ela
  registrou. E nunca monta essa lista por diferença contra um baseline: "tudo que não estava aqui
  antes é meu" também captura o que você abriu no meio do caminho.

---

## Solução de problemas

| O que aparece | O que significa | O que fazer |
|---|---|---|
| `cmux: no socket at …` | cmux não está rodando | Abra o cmux. Só a frota precisa dele. |
| `a visual fleet panel is already active` | Um painel por vez | Desmonte o painel atual, ou lance com `--auto` |
| `a panel holds at most 4 members` | Mais de quatro slugs num painel | Divida em duas rodadas, ou rode os extras com `--auto` |
| `visual mode is not implemented for the … runtime` | Só o Claude tem vetor interativo aqui | Lance esse runtime com `--auto` |
| `cmux: could not start cmux within …` | O app não respondeu dentro do timeout de início | Abra o cmux você mesmo; aumente `POWER_CMUX_START_TIMEOUT` em máquina lenta |
| `no free fleet port slot below 64` | Os 64 slots estão tomados ou com portas em uso | Desmonte membros concluídos, ou mova `fleet.port_base_app` / `fleet.port_base_db` |
| `cmux: CLI not found` | Não está no `PATH` | `export PWDEV_POWER_CMUX_BIN=/Applications/cmux.app/Contents/Resources/bin/cmux` |
| `spec must carry exactly one 'Status: APPROVED' field (found 2)` | Uma segunda linha de aprovação, muitas vezes num bloco de exemplo | Deixe apenas um campo de aprovação real |
| `no .planning/power/config.json; run init first` | Sem workspace | `/pwdev-power:init` |
| `detached HEAD; check out a named branch first` | Toda fase se amarra a um branch | Faça checkout de um branch |
| `registered fleet member does not match canonical Git worktree registration` | Você é o runtime errado para esse membro, ou o worktree mudou de lugar | Use o launcher correspondente ao campo `runtime` do membro |
| `approved fleet contracts do not match the bound member` | Alguém editou a spec ou o plano depois do lançamento | Restaure os bytes aprovados, ou encerre e relance |
| `invalid structured result for <estágio>` | O provider respondeu em prosa | A resposta bruta fica como `<estágio>-<hora>.invalid.json` em `fleet-results/` |
| `fleet member is already running` | Há um lock de runner ativo | Verifique se existe runner vivo antes de remover qualquer coisa |
| `provider ownership is unresolved; retaining runner lock` | Não foi possível provar que o grupo de processos encerrou | **Proposital.** Procure processos órfãos antes de relançar |
| `verification rejected after two correction cycles` | O limite funcionou | Leia o `verdict.md`; o ciclo não vai tentar uma terceira vez |
| `fleet allocation is already locked` | Lançamento concorrente | Espere terminar, ou remova `.planning/power/fleet/.lock` se nenhum lançamento estiver rodando |
| Skills param de disparar no Hermes | A sessão compactou por cima do primeiro turno | Comece uma sessão nova — veja *Limites conhecidos* |

Um membro que falhou mantém branch e worktree. Investigue ali; não relance por cima.

---

## Limites conhecidos

- **O Hermes não tem hook de pós-compactação.** Uma sessão longa que compacta por cima do primeiro
  turno perde o bootstrap. Comece uma sessão nova se as skills pararem de disparar — isso não tem
  conserto de dentro do plugin. O Claude Code reinjeta em `startup|clear|compact`; o Codex
  descobre as skills nativamente e não precisa de injeção.
- **Seleção de modelo por dispatch no Hermes ainda não está estabelecida.** O `delegate_task` não
  está documentado como recebendo modelo. Até estar, use `--model`/`--provider` do card do Kanban,
  ou execute inline — nunca invente um parâmetro para satisfazer a regra de modelos explícitos.
  Veja `references/hermes-tools.md`.
- **A frota exige o cmux.** Não há fallback para tmux, por decisão de projeto. O lançamento inicia
  o cmux para você, mas não consegue instalá-lo.
- **O painel visual é só para o Claude.** `codex` e `hermes` o recusam com uma frase e devem rodar
  com `--auto`; nenhum dos dois tem vetor interativo verificado aqui.
- **Um painel comporta quatro membros, e há um painel por vez.** Quatro panes é onde um grid deixa
  de ser legível. Um segundo painel teria que crescer para dentro do primeiro dividindo e mandando
  teclas, então é recusado em vez de mesclado.
- **Worktree novo abre no trust prompt do Claude Code.** Uma tecla por pane. Pré-confiar exigiria
  escrever na sua configuração do Claude Code para pular um checkpoint de segurança, coisa que o
  plugin não faz por você.
- **A auditoria exige `sqlite3`** e permanece desligada até o arquivo de banco existir.
- **O template de compose assume Postgres.** Sem um `Dockerfile`, só o banco sobe, o que é
  intencional — o serviço `app` não teria como ser construído.
- **`unittest discover` não funciona nesta árvore.** Uma forma levanta `ImportError` e a outra roda
  zero testes em silêncio. Nomeie os módulos.

---

## Contribuindo

```bash
python3 -m unittest tests.test_pwdev_power tests.test_power_hermes    # 67 testes
claude plugin validate plugins/pwdev-power
hermes plugins doctor --ci plugins/pwdev-power
```

Os contratos em `references/` são a especificação; as skills os leem em vez de repeti-los. Se você
mudar comportamento, mude a referência e o teste junto.

Duas convenções que vale conhecer antes de editar uma skill:

- **A `description` de uma skill diz apenas quando disparar, nunca o que a skill faz.** Uma
  descrição que resume o fluxo passa a ser seguida *no lugar* da leitura da skill.
- **Nada de links `@` entre skills.** Eles forçam carregamento imediato e queimam contexto que
  ninguém escolheu gastar. Use o nome com namespace e links markdown relativos.

---

## Licença

Apache-2.0. Veja [LICENSE](./LICENSE).
