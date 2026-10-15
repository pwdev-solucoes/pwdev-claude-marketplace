# pwdev-mods

**English** | [Português](./README.pt-BR.md)

A Claude Code **mod**: a management pane that runs inside Claude Code and shows your subagents, token usage, cost and daily history, with buttons to stop or spawn subagents.

Requires Claude Code **v2.1.287 or later** (mods). The pane and the band draw in the terminal and in the Desktop app's Code tab; in VS Code and `claude -p` the command answers with a text summary instead.

## Installation

```bash
claude plugin marketplace add pwdev-solucoes/pwdev-claude-marketplace
claude plugin install pwdev-mods@pwdev-claude-marketplace
```

In a running session, run `/reload-plugins`. Run `/plugin` to confirm the line `… mods active · pwdev-mods`.

To try it from a clone without installing:

```bash
claude --plugin-dir ./plugins/pwdev-mods
```

## Usage

```
/pwdev-mods              # opens the pane on the last tab
/pwdev-mods agents       # opens on a tab: overview | agents | tokens | history
```

Close the pane with `ctrl+x x` or its close mark. Inside the pane, `v`, `s`, `t` and `h` switch tabs.

| Tab | Shows |
|---|---|
| **Overview** | Context window bar and percentage, session cost, today's cost, rate-limit windows (5h / 7d), turns, active subagents |
| **Subagents** | Live list (type, description, status, model, age, tokens), a **Stop** button on each running one, and a **Spawn** form (type picker + prompt) |
| **Tokens** | Input, output, cache read and cache write for the session; totals per model and per agent loop; cache hit rate; the last turns |
| **History** | Tokens and cost per day as sparklines, kept across sessions, plus the last 10 days as a table |

A one-line **band above the prompt** shows `ctx %` · session cost · today's cost · active subagents. Press `ocultar` to hide it for the session.

## Settings

Set them in `/plugin` → Installed → pwdev-mods → configure, or `/plugin configure pwdev-mods@pwdev-claude-marketplace`.

| Option | Default | Effect |
|---|---|---|
| `dailyBudgetUsd` | `0` | Toast at 80% and 100% of the day's spend, once per threshold per day. `0` turns it off. |
| `historyDays` | `30` | Days of history kept; older days are deleted on session start. |
| `showBand` | `true` | Draws the band above the prompt. |
| `autoOpenPane` | `false` | Opens the pane when a session starts (only where it fits as a sidebar). |

## How it works

| Data | Source |
|---|---|
| Tokens per turn, model and subagent | `turn.complete` (`usage`, `agentId`) |
| Context, cost, rate limits | `$.session.usage()` |
| Subagents | `$.agent.list()`, plus model and start time from `agent.spawn` |
| Stop | the `TaskStop` tool with the agent id |
| Spawn | `$.agent.spawn({ subagentType, prompt })` |
| History | `$.store` keys `daily:YYYY-MM-DD` (cost = growth of the session's cost between turns) |

While the pane is shown, or while a subagent runs, it refreshes every 2 seconds. Day boundaries use your local time.

## Security

A mod runs inside Claude Code with your permissions. This one:

- reads only session data through the mods API (usage, cost, agent list); it reads no files, runs no processes and makes no network requests;
- writes only its own `$.store` keys (`daily:*`, `budget:*`);
- **Stop** and **Spawn** act only when you press them. A spawned subagent runs with the session's permissions and spends your usage like any other subagent.

Review it yourself before installing:

```bash
claude plugin validate ./plugins/pwdev-mods
```

## Development

```bash
claude plugin validate ./plugins/pwdev-mods
claude plugin test ./plugins/pwdev-mods
```

`hooks/register.tsx` holds every function that calls the engine (`$`); the engine follows `$` only into functions declared in that file. `hooks/lib/` holds pure helpers. State the pane draws from is declared in `types/index.d.ts`.

## License

Apache-2.0
