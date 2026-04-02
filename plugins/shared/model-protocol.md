# Model Selection Protocol (LLM)

> **INTERNAL REFERENCE** — This file is the canonical specification for model selection behavior.
> It is NOT shipped with individual plugins. Each plugin has self-contained inline instructions
> derived from this spec. Edit this file to update the spec, then sync to each plugin's commands/agents.

This protocol defines how agents resolve which Claude model to use.
It is configured during `init` and consulted by every command that spawns agents.

---

## Available Models

| Model | ID | Best for | Cost |
|-------|----|----------|------|
| **Opus** | `opus` | Complex reasoning, architecture, orchestration | Highest |
| **Sonnet** | `sonnet` | General coding, planning, reviews | Medium |
| **Haiku** | `haiku` | Fast tasks, scanning, linting, simple checks | Lowest |

---

## Profiles

Three predefined profiles control how models are assigned to agent roles:

| Role Category | `performance` | `balanced` | `economy` |
|---------------|:------------:|:----------:|:---------:|
| **orchestrator** — coordination, multi-agent delegation | opus | opus | sonnet |
| **planner** — architecture, planning, design decisions | opus | sonnet | sonnet |
| **executor** — code implementation, file creation | opus | sonnet | sonnet |
| **builder** — component building, theme creation | opus | sonnet | sonnet |
| **reviewer** — code review, QA, accessibility audit | sonnet | sonnet | haiku |
| **scanner** — codebase analysis, dependency checks | sonnet | haiku | haiku |
| **researcher** — documentation lookup, stack analysis | sonnet | sonnet | haiku |
| **interviewer** — requirements gathering, PRD creation | opus | sonnet | sonnet |

### Agent-to-Role Mapping

Each agent maps to a role category:

**pwdev-prd:**
| Agent | Role Category |
|-------|---------------|
| agent-interviewer | interviewer |

**pwdev-feat:**
| Agent | Role Category |
|-------|---------------|
| agent-planner | planner |
| agent-executor | executor |

**pwdev-uiux:**
| Agent | Role Category |
|-------|---------------|
| orchestrator | orchestrator |
| ux-analyst | planner |
| ui-builder | builder |
| theme-builder | builder |
| design-bridge | builder |
| a11y-reviewer | reviewer |
| ux-critic | reviewer |
| ui-scanner | scanner |

**pwdev-code:**
| Agent | Role Category |
|-------|---------------|
| agent-architect | planner |
| agent-planner | planner |
| agent-researcher | researcher |
| agent-interviewer | interviewer |
| agent-prd | interviewer |
| agent-roadmap | planner |
| agent-executor | executor |
| agent-quick | executor |
| agent-code-reviewer | reviewer |
| agent-qa | reviewer |
| agent-verifier | scanner |

---

## Configuration in `.planning/config.json`

```json
{
  "lang": "pt-BR",
  "model_profile": "balanced",
  "model_overrides": {}
}
```

### Fields

- **`model_profile`**: One of `performance`, `balanced`, `economy`. Default: `balanced`.
- **`model_overrides`**: Optional object mapping agent names to specific models. Overrides the profile for that agent only.

### Example with overrides

```json
{
  "lang": "pt-BR",
  "model_profile": "economy",
  "model_overrides": {
    "agent-architect": "opus",
    "orchestrator": "opus"
  }
}
```

This runs most agents on economy settings but uses Opus for architecture and orchestration.

---

## Resolution Order

When a command needs to spawn an agent, resolve the model in this order:

1. **`model_overrides[agent-name]`** — if the agent has a specific override → use it.
2. **Profile lookup** — map agent name → role category → profile table → model.
3. **Frontmatter default** — if no config exists at all, use the `model:` field in the agent's frontmatter.
4. **Inherit** — if no frontmatter `model:` either, inherit from the parent session.

---

## How Commands Apply the Model

Commands that spawn agents must include a model resolution step.
Insert this instruction in the command, before agent invocation:

```markdown
### Model Resolution
Read `.planning/config.json` for `model_profile` and `model_overrides`.
Resolve the model for each agent using the resolution order from `shared/model-protocol.md`.
When invoking the Agent tool, pass the resolved model via the `model` parameter.
```

---

## Special Behavior: `init` Commands

The `init` command of each plugin asks the user to choose a model profile as part of initialization:

1. If `.planning/config.json` already has `model_profile`, show it and ask to confirm or change.
2. If no config, present the three profiles with a clear comparison.
3. Optionally ask about overrides for critical agents (e.g., "Want Opus for the architect even in economy mode?").
4. Save to `.planning/config.json`.

---

## Profile Selection Prompt (for `init` commands)

Use this prompt when asking the user:

**PT-BR:**
```
Qual perfil de modelo deseja usar para os agentes?

1. Performance  — Opus para maioria dos agentes (melhor qualidade, maior custo)
2. Balanced     — Opus para orquestracao, Sonnet para execucao, Haiku para scans (recomendado)
3. Economy      — Sonnet para maioria, Haiku para scans (menor custo)

Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for agents?

1. Performance  — Opus for most agents (best quality, highest cost)
2. Balanced     — Opus for orchestration, Sonnet for execution, Haiku for scans (recommended)
3. Economy      — Sonnet for most, Haiku for scans (lowest cost)

Choose (1-3, default: 2):
```

After selection, optionally ask:

**PT-BR:**
```
Deseja configurar overrides para agentes especificos? (s/n, padrao: n)
```

**EN:**
```
Would you like to configure overrides for specific agents? (y/n, default: n)
```

If yes, list the agents in the current plugin with their profile-assigned model and let the user change individual ones.
