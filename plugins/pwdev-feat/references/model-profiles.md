# Model Profiles (single source of truth)

Only the **executor** and **advisor** resolve a model. Every other skill (planning, map, setup,
quick, status, audit) runs in the main session on the session model — the PWDEVIA planner
interviews the human, and subagents cannot talk to the user.

## Tiers, not model names

| Role | `performance` | `balanced` (default) | `economy` |
|------|:-------------:|:--------------------:|:---------:|
| executor | top | mid | mid |
| advisor  | top | top | mid |

The advisor exists to BE the strong model at the moment of doubt — `top` even in `balanced`.

Read `top` and `mid` as tiers of whatever family the runtime offers:

| Runtime | `top` | `mid` | How it is passed |
|---|---|---|---|
| Claude Code | `opus` | `sonnet` | `model` parameter of `Task`/`Agent` — always explicit |
| Codex | host default | host default | omit `model`/`reasoning_effort` (inherit); pass only an explicit override the host exposes |
| Hermes | host model | host model | not passed (`delegate_task` has no established model parameter) |
| OpenCode | host model | host model | not passed unless an explicit override exists |
| Inline fallback | session model | session model | nothing to pass |

## Resolution order

1. `.planning/config.json` → `model_overrides["feat-executor"]` / `model_overrides["feat-advisor"]`
   (a literal model name; on non-Claude runtimes use it only if the host exposes that model).
2. `model_profile` → table above (default `balanced`).
3. Claude only: the agent frontmatter `model:`.

Record what was used: `scripts/audit-log.sh spawn exec "" <agent> <model|inherited|inline>`.

## Shared config warning

`.planning/config.json` is SHARED with pwdev-code (same `lang`, `model_profile`, `audit`).
pwdev-feat uses the namespaced keys **`feat-executor`** and **`feat-advisor`** — never read or
write the plain `executor` / `advisor` keys (they belong to pwdev-code).

```json
{
  "model_profile": "balanced",
  "model_overrides": { "feat-executor": "opus", "feat-advisor": "opus" }
}
```

## Profile selection prompt (used by `feat-init`)

**PT-BR:**
```
Qual perfil de modelo deseja usar para os subagentes (executor e advisor)?

1. Performance  — nivel mais forte para executor e advisor (maior custo)
2. Balanced     — nivel intermediario no executor, mais forte no advisor (recomendado)
3. Economy      — nivel intermediario em ambos (menor custo)

No Claude Code: forte = Opus, intermediario = Sonnet. Codex, Hermes e OpenCode herdam o modelo do host.
Escolha (1-3, padrao: 2):
```

**EN:**
```
Which model profile would you like to use for the subagents (executor and advisor)?

1. Performance  — strongest tier for executor and advisor (highest cost)
2. Balanced     — mid tier for the executor, strongest for the advisor (recommended)
3. Economy      — mid tier for both (lowest cost)

On Claude Code: strongest = Opus, mid = Sonnet. Codex, Hermes and OpenCode inherit the host model.
Choose (1-3, default: 2):
```
