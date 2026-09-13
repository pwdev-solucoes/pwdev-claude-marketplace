# PWDEV QA

> [Versão em Português](./README.pt-BR.md)

Portable quality-assurance workflows for **Claude Code, Codex, and Hermes Agent**. The plugin
routes QA requests, recommends tools from observed context, guides bounded execution, preserves
auditable evidence, validates acceptance criteria, and exports equivalent offline HTML and PDF
reports. It ships 29 skills, 10 commands, and 0 mandatory MCP servers.

## Manual, portable setup

Clone this marketplace and work from its root. The examples below load the checked-out plugin;
they are instructions for a user to run deliberately. The plugin does not install automatically,
does not publish anything, and does not change personal configuration.

### Claude Code

Load the local directory for the current session:

```bash
claude --plugin-dir ./plugins/pwdev-qa
```

Claude exposes the ten wrappers as `/pwdev-qa:<command>`. A successful listing is only discovery,
not a verified runtime: Task 24 must run a real smoke that discovers `qa-tooling`, handles a
missing-tool scenario, and produces a fixture report before Claude Code may be called verified.

### Codex

Open this checkout as the workspace and load the local `plugins/pwdev-qa` package through the
Codex local-plugin mechanism. Its `.codex-plugin/plugin.json` declares `"skills": "./skills/"`;
invoke a discovered skill by name, such as `$qa-tooling` or `$qa-strategy`. Do not copy it into a
personal skills directory unless you explicitly choose to maintain that separate installation.

Manifest discovery alone is not a smoke. Until a real Codex session performs discovery,
missing-tool handling, and report generation, record Codex as `unverified`.

### Hermes Agent

Use the repository-local plugin and inspect it before enabling or trusting anything globally:

```bash
hermes plugins doctor plugins/pwdev-qa
```

The adapter registers the same 29 `SKILL.md` files with `pathlib.Path` and no intrusive hook. If
you later authorize a repo-local trust operation, follow the installed Hermes version's help.
Doctor output proves packaging only; a real Hermes smoke is still required before the runtime is
verified. Missing executable, authentication, discovery, or invocation stays `unverified` and
must be reported as a limitation rather than simulated.

No runtime requires an MCP server. Capabilities may differ by runtime, and each difference must
remain explicit.

## Exact inventory

The 29 skills are one router, one tool recommender, ten workflows, and seventeen specialists.

| Kind | Skills |
|---|---|
| Router | `qa` |
| Tool recommender | `qa-tooling` |
| Workflows | `qa-init`, `qa-strategy`, `qa-test`, `qa-explore`, `qa-bug`, `qa-regression`, `qa-review`, `qa-release`, `qa-report`, `qa-status` |
| Specialists | `qa-specialist-accessibility`, `qa-specialist-api`, `qa-specialist-automation`, `qa-specialist-cicd`, `qa-specialist-data`, `qa-specialist-defects`, `qa-specialist-functional`, `qa-specialist-metrics`, `qa-specialist-mobile`, `qa-specialist-performance`, `qa-specialist-production`, `qa-specialist-readiness`, `qa-specialist-regression`, `qa-specialist-requirements`, `qa-specialist-security`, `qa-specialist-strategy`, `qa-specialist-web` |

Claude Code supplies these 10 commands:

| Command | Purpose |
|---|---|
| `/pwdev-qa:init` | Inspect context and establish a bounded QA workspace. |
| `/pwdev-qa:strategy` | Define scope, risks, acceptance coverage, and approach. |
| `/pwdev-qa:test` | Execute an authorized test contract and preserve results. |
| `/pwdev-qa:explore` | Conduct bounded exploratory testing. |
| `/pwdev-qa:bug` | Reproduce and document a defect; product fixes require a separate request. |
| `/pwdev-qa:regression` | Select and execute risk-based regression coverage. |
| `/pwdev-qa:review` | Review QA evidence and readiness without inventing execution. |
| `/pwdev-qa:release` | Assess release readiness against explicit gates. |
| `/pwdev-qa:report` | Export the already-recorded normalized run. |
| `/pwdev-qa:status` | Summarize recorded state without discarding or mutating it. |

## Tool recommendations

`qa-tooling` is a recommendation skill, not an installer. Given the observed stack, surface,
runtime/OS, installed tools, CI, budget, license, and data constraints, it reports each option's
purpose, availability (`available`, `missing`, or `unverified`), detection evidence,
prerequisites, verified cost/license, an alternative, and the reason for the recommendation. A
missing tool never becomes a fictitious run and never triggers auto-install. Current commands,
compatibility, licensing, and cost require dated official sources.

For exploratory Web/UI work, `playwright-cli` is an explicit option. The official local
resolution is:

```bash
npx --no-install playwright --version
npx playwright cli
```

The first command detects a local Playwright without downloading it; the presence of `npx` alone
is not evidence. An already installed global alternative is `playwright-cli` (for example,
`playwright-cli --version`). Use an isolated QA session, observed refs, and reviewed screenshots;
do not reuse personal profiles or export cookies/storage. Prefer Playwright Test for repeatable CI
suites. Traces and videos are outside the v1 attachment allowlist.

## Execution and export are separate

Execution runs only an explicitly authorized test contract and records results. Export consumes
that normalized manifest afterward; reporting does not execute stored commands or repair the
product. The export exit code represents publication, while automation reads the QA verdict from
the JSON model.

Case and criterion results are `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or `NOT_APPLICABLE`; the
global verdict is `PASS`, `FAIL`, or `BLOCKED`. A current proven in-scope failure means `FAIL`.
Any pending item—or zero applicable criteria—means `BLOCKED`. `PASS` requires every applicable
criterion to pass and no current in-scope defect.

Both formats derive from the same normalized manifest and contain the same criterion IDs and
texts, expected/observed values, evidence references, defects, and verdict:

- HTML is static offline UTF-8 with no JavaScript or remote resources.
- PDF is A4 with 18 mm margins, pagination, and textual status labels.
- Output is published under `.planning/pwdev-qa/reports/<run-id>/`; an existing run directory is
  never overwritten.

Runtime requirement is Python >=3.9. PDF export requires `reportlab==4.4.9`. Development and PDF
verification use Python 3.12 with `pypdf==6.10.0` and `pdfplumber==0.11.9`; those two packages are
verification dependencies, not runtime export dependencies. Install dependencies only through an
explicitly approved environment-management step.

## Evidence, sanitization, and authorization limits

Evidence attachments must be regular local files, relative and confined to the run root, never
symlinks. Each attachment binds a SHA-256 digest, target, media type, size, and sanitization
review. Accepted v1 media are plain text, JSON treated as inert text, PNG, and JPEG. Pending,
missing, changed, or unsafe evidence is diagnosed, not copied, and prevents `PASS`; invalid schema
or unsafe evidence refuses export.

Sanitization cannot guarantee universal secret or personal-data detection. Known credential
patterns are rejected, but semantic review remains mandatory; images require recorded visual
review. Synthetic or reviewed status records an actor and timestamp. Never attach personal
profiles, cookies, storage, or unsanitized production material.

Limits are explicit errors, never silent truncation: 5 MiB manifest, 1000 criteria, 1000 evidence
items, 10 MiB per evidence item, 100 MiB total evidence, and 20 megapixels per image.

Load, pentest, production access, and any external effect require explicit authorization naming
the target, environment, methods, limits, window, stop conditions, and responsible actor as
applicable. Product correction happens only when separately requested. If authority, tooling, or
real-runtime access is absent, keep the action `NOT_RUN` and the result/verdict `BLOCKED` where the
contract requires it; never claim a smoke that was not performed.
