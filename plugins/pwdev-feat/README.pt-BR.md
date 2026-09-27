# PWDEV-FEAT v3.2.0

*Leia em [English](./README.md)*

> **Desenvolvimento rápido de features assistido por IA para Claude Code, Codex, Hermes Agent e OpenCode**

```
Mapear (evidência) → Planejar (PWDEVIA, com lint) → Executar (IMPLEMENT/REPORT, retomada) → Revisar
```

O PWDEV-FEAT usa a **metodologia PWDEVIA de 7 perguntas** para escrever planos de ação
executáveis, criados inline enquanto entrevista você (no máximo 2 rodadas). Um **executor** com
contexto limpo implementa o plano e verifica cada critério de aceite com evidência real. Sem
cerimônia pesada: descrever, planejar, executar.

---

## Novidades da 3.0

- **Quatro runtimes, um único conjunto de skills.**
  - O workflow vive em 13 skills portáveis (`skills/feat-*`).
  - O Claude Code mantém todos os comandos `/pwdev-feat:*` como wrappers finos; Codex, Hermes e OpenCode carregam as mesmas skills nativamente.
  - Os subagentes usam o mecanismo de cada runtime e rodam **inline** quando o runtime não tem subagente.
- **Mapa do código com evidência.** O `feat-map` faz uma varredura determinística e somente leitura com `scripts/feat_map.py`:
  - cobre stack, frameworks, comandos declarados (nunca executados), testes, CI, migrations, módulos e áreas sensíveis, e ignora paths de segredo;
  - gera quatro documentos de contexto (`architecture`, `conventions`, `testing`, `concerns`), em que cada afirmação cita evidência e confiança;
  - os planners avisam quando o mapa está desatualizado.
- **Planos rastreáveis.**
  - Critérios `AC-nnn` com sua verificação.
  - Cada passo aponta os arquivos e ACs que cobre.
  - O `scripts/plan_lint.py` valida estrutura e rastreio antes de apresentar ou executar o plano.
- **Execução melhor.**
  - Registra o commit base e sinaliza arquivos planejados que já estão sujos.
  - Faz checkpoints por passo em `progress.md`, e `feat-exec <slug> --resume` retoma de onde parou.
  - O `plan.done.md` registra cada AC com comando, exit code e evidência, além de planejado × alterado.
- **Reviews com achados estáveis.** O `feat-review`:
  - fixa um escopo `BASE..TARGET` explícito (`scripts/review_package.sh`);
  - reporta achados `CR-nnn` com severidade (`BLOCKER`…`INFO`), `path:line`, regra citada e evidência;
  - nunca corrige código silenciosamente.
- **Testes de UI em duas trilhas.**
  - Verificação interativa com **`playwright-cli`** numa sessão própria da tarefa.
  - **Cenários E2E declarativos** em JSON, validados por `schemas/e2e-scenario.schema.json` e guardados no diretório de testes do projeto. São exportados para specs do Playwright Test (`scripts/e2e_scenarios.py`) para qualquer QA executar depois.
- **Instruções do projeto para todos os runtimes.** O `feat-setup` gera o `AGENTS.md` e um `CLAUDE.md` que o importa.

Workspaces `.planning/feat/` existentes continuam funcionando: planos 2.x são lidos, passam pelo
lint só com avisos, são executados e aparecem no status. Veja o [CHANGELOG](./CHANGELOG.md).

---

## Instalação

| Runtime | Instalar | Invocar |
|---|---|---|
| Claude Code | `claude plugin install pwdev-feat@pwdev-claude-marketplace` | `/pwdev-feat:feat "…"` |
| Codex | adicionar este repositório como marketplace e habilitar **pwdev-feat** (`.agents/plugins/marketplace.json`) | `$feat-feature …` |
| Hermes Agent | instalar o plugin a partir deste repositório (`.hermes-plugin/`) | `skill_view("pwdev-feat:feat-feature")` ou só pedir |
| OpenCode | `python3 plugins/pwdev-feat/.opencode-plugin/install.py [--project <dir>]` | `/feat-feature …` ou a ferramenta `skill` |

Subagentes no Codex exigem `[features] multi_agent = true` em `~/.codex/config.toml`. Sem isso,
o executor roda inline. Detalhes por runtime em [`references/runtime.md`](./references/runtime.md).

---

## Início rápido

```bash
/pwdev-feat:init                      # idioma, perfil de modelo, auditoria opcional, workspace
/pwdev-feat:map-codebase              # varredura com evidência + documentos de contexto
/pwdev-feat:setup                     # AGENTS.md (+ import no CLAUDE.md)
/pwdev-feat:feat "CRUD de usuários com validação e E2E"
/pwdev-feat:exec crud-de-usuarios     # ou: latest, --resume
/pwdev-feat:review crud-de-usuarios   # base_commit..HEAD da feature
/pwdev-feat:quick "corrigir o formato de data na lista de faturas"
/pwdev-feat:loop "#42"                # issue → plano → exec → review → PR
```

No Codex, use `$feat-init`, `$feat-map`, `$feat-setup`, `$feat-feature`, `$feat-exec`, com os
mesmos nomes das skills.

---

## Comandos e skills

| Comando Claude | Skill | O que faz |
|---|---|---|
| `/pwdev-feat:init` | `feat-init` | Idioma, perfil de modelo, auditoria, `.planning/feat/` |
| `/pwdev-feat:map-codebase` | `feat-map` | Varredura com evidência + `codebase.md` + 4 documentos de contexto |
| `/pwdev-feat:setup` | `feat-setup` | Arquivo de instruções do projeto para todos os runtimes |
| `/pwdev-feat:feat` | `feat-feature` | Plano de feature completa (backend + UI + testes) |
| `/pwdev-feat:backend` | `feat-backend` | Plano de backend: API, serviços, modelos, migrations |
| `/pwdev-feat:frontend` | `feat-frontend` | Plano de UI com cenários E2E e verificações `playwright-cli` |
| `/pwdev-feat:test` | `feat-test` | Plano de testes (IMPLEMENT) ou auditoria de testes (REPORT) |
| `/pwdev-feat:review` | `feat-review` | Plano de review de um intervalo explícito (REPORT) |
| `/pwdev-feat:exec` | `feat-exec` | Executa um plano: executor, advisor, nova tentativa, retomada |
| `/pwdev-feat:quick` | `feat-quick` | ≤5 arquivos, mini-plano, sem arquivo de plano |
| `/pwdev-feat:loop` | `feat-loop` | Issue do GitHub → plano → exec → review → ≤2 ciclos de correção → PR (nunca faz merge) |
| `/pwdev-feat:status` | `feat-status` | Pendentes, concluídos, com ressalvas, falhos, retomáveis; frescor do mapa |
| `/pwdev-feat:audit` | `feat-audit` | Resumo, eventos, estatísticas, exportação e consulta somente leitura |

---

## O método

**As 7 perguntas PWDEVIA:**
1. Persona e escopo
2. Objetivo direto
3. Entradas mínimas
4. Formato de saída
5. Critérios de qualidade (`AC-nnn` + verificação)
6. Tratamento de ambiguidade
7. Proibições

O planner roda na sessão principal porque entrevista você, e subagentes não falam com o usuário.
Referência: [`references/pwdevia-method.md`](./references/pwdevia-method.md); template:
[`templates/plan.md`](./templates/plan.md).

**Modos de execução.**
- Planos de review e planos só de relatório rodam em **REPORT**: achados em `review.md` ou `test-audit.md`, sem mudar código e sem commit. Todo o resto roda em **IMPLEMENT**.
- O contrato do executor está em [`references/executor-contract.md`](./references/executor-contract.md).
- Diante de uma decisão real, o executor retorna `NEEDS_ADVICE` e o **advisor** (nível mais forte, somente leitura) escolhe uma direção: [`references/advisor-contract.md`](./references/advisor-contract.md).

Os cenários E2E ficam no diretório de testes do projeto:
- cenários: `<tests-dir>/e2e/scenarios/*.scenario.json`;
- specs gerados: `<tests-dir>/e2e/generated/`.

Detalhes em [`references/testing.md`](./references/testing.md).

```bash
python3 <plugin>/scripts/e2e_scenarios.py validate tests/e2e/scenarios --plan .planning/feat/features/<slug>/plan.md
python3 <plugin>/scripts/e2e_scenarios.py export --to playwright tests/e2e/scenarios --out tests/e2e/generated
APP_BASE_URL=http://localhost:8000 npx playwright test tests/e2e/generated   # ou abra no UI mode
```

---

## Configuração

O `.planning/config.json` é compartilhado com o pwdev-code: sempre mesclar, nunca sobrescrever.
Chaves de override: `feat-executor` e `feat-advisor`. Perfis por nível:

| Papel | performance | balanced | economy |
|---|---|---|---|
| executor | top | mid | mid |
| advisor | top | top | mid |

No Claude Code, `top` = Opus e `mid` = Sonnet. Codex, Hermes e OpenCode herdam o modelo do host,
a menos que um override explícito nomeie um modelo que o host oferece. Detalhes em
[`references/model-profiles.md`](./references/model-profiles.md).

## Auditoria e segurança

- **Auditoria:** a trilha SQLite é opcional. O `feat-init` a cria (`scripts/audit.py init`) e o `feat-audit` a lê em modo somente leitura, aceitando só um `SELECT` por consulta.
- **O que é registrado:** no Claude Code, hooks gravam sessões, duração dos subagentes e escritas em `.planning/`. Em qualquer runtime, as skills registram marcos, despachos e mudanças de configuração.
- **Segredos:** `.env*`, chaves e certificados nunca são lidos. No Claude Code, o hook `guard-secrets.sh` garante isso; nos demais runtimes, a regra vem das próprias skills ([`references/safety.md`](./references/safety.md)).

## Licença

Apache-2.0 — veja [LICENSE](./LICENSE).
