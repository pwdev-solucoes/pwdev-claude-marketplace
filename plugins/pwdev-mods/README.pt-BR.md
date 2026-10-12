# pwdev-mods

[English](./README.md) | **Português**

Um **mod** do Claude Code: um painel de gestão que roda dentro do Claude Code e mostra seus subagentes, consumo de tokens, custo e histórico diário, com botões para parar ou disparar subagentes.

Requer Claude Code **v2.1.287 ou posterior** (mods). O painel e a faixa aparecem no terminal e na aba Code do app Desktop; no VS Code e no `claude -p` o comando responde com um resumo em texto.

## Instalação

```bash
claude plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
claude plugin install pwdev-mods@pwdev-claude-marketplace
```

Numa sessão aberta, rode `/reload-plugins`. Rode `/plugin` e confira a linha `… mods active · pwdev-mods`.

Para testar a partir de um clone, sem instalar:

```bash
claude --plugin-dir ./plugins/pwdev-mods
```

## Uso

```
/pwdev-mods              # abre o painel na última aba
/pwdev-mods agents       # abre numa aba: overview | agents | tokens | history
```

Feche o painel com `ctrl+x x` ou pela marca de fechar. Dentro do painel, `v`, `s`, `t` e `h` trocam de aba.

| Aba | Mostra |
|---|---|
| **Visão geral** | Barra e percentual da janela de contexto, custo da sessão, custo do dia, janelas de rate limit (5h / 7d), turnos, subagentes ativos |
| **Subagentes** | Lista ao vivo (tipo, descrição, status, modelo, duração, tokens), botão **Parar** em cada um em execução e formulário **Disparar** (tipo + prompt) |
| **Tokens** | Entrada, saída, cache lido e cache escrito da sessão; totais por modelo e por loop de agente; taxa de cache hit; últimos turnos |
| **Histórico** | Tokens e custo por dia em sparklines, mantidos entre sessões, e os últimos 10 dias em tabela |

Uma **faixa acima do prompt** mostra `ctx %` · custo da sessão · custo do dia · subagentes ativos. O botão `ocultar` esconde a faixa na sessão.

## Configuração

Ajuste em `/plugin` → Installed → pwdev-mods → configure, ou `/plugin configure pwdev-mods@pwdev-claude-marketplace`.

| Opção | Padrão | Efeito |
|---|---|---|
| `dailyBudgetUsd` | `0` | Toast ao atingir 80% e 100% do gasto do dia, uma vez por limiar por dia. `0` desliga. |
| `historyDays` | `30` | Dias de histórico mantidos; os mais antigos são apagados no início da sessão. |
| `showBand` | `true` | Desenha a faixa acima do prompt. |
| `autoOpenPane` | `false` | Abre o painel quando a sessão começa (só onde cabe como barra lateral). |

## Como funciona

| Dado | Fonte |
|---|---|
| Tokens por turno, modelo e subagente | `turn.complete` (`usage`, `agentId`) |
| Contexto, custo, rate limits | `$.session.usage()` |
| Subagentes | `$.agent.list()`, mais modelo e início vindos de `agent.spawn` |
| Parar | a ferramenta `TaskStop` com o id do agente |
| Disparar | `$.agent.spawn({ subagentType, prompt })` |
| Histórico | chaves `daily:AAAA-MM-DD` em `$.store` (custo = crescimento do custo da sessão entre turnos) |

Enquanto o painel está visível, ou enquanto algum subagente roda, os dados se atualizam a cada 2 segundos. A virada do dia usa o horário local.

## Segurança

Um mod roda dentro do Claude Code com as suas permissões. Este:

- lê apenas dados da sessão pela API de mods (uso, custo, lista de agentes); não lê arquivos, não executa processos e não faz requisições de rede;
- grava só as próprias chaves em `$.store` (`daily:*`, `budget:*`);
- **Parar** e **Disparar** só agem quando você pressiona. Um subagente disparado roda com as permissões da sessão e consome seu uso como qualquer outro subagente.

Revise antes de instalar:

```bash
claude plugin validate ./plugins/pwdev-mods
```

## Desenvolvimento

```bash
claude plugin validate ./plugins/pwdev-mods
claude plugin test ./plugins/pwdev-mods
```

`hooks/register.tsx` concentra todas as funções que chamam o motor (`$`); o motor só segue `$` para funções declaradas nesse arquivo. `hooks/lib/` tem os helpers puros. O estado que o painel desenha está declarado em `types/index.d.ts`.

## Licença

Apache-2.0
