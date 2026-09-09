# PWDEV Marketplace

*Leia em [Português Brasileiro](./README.pt-BR.md).*

Marketplace of plugins for Claude Code, Codex and compatible PWDEV runtimes.

## Install

```bash
claude plugin marketplace add /path/to/pwdev-claude-marketplace
claude plugin install <plugin>@pwdev-claude-marketplace
```

Restart the runtime after installation. Read each plugin README for its setup and permissions.

## Choose by goal

| Goal | Plugins |
|---|---|
| Spec-driven development | [pwdev-power](./plugins/pwdev-power/), [pwdev-flow](./plugins/pwdev-flow/), [sdd-composy](./plugins/sdd-composy/) |
| Coding and delegation | [pwdev-code](./plugins/pwdev-code/), [pwdev-feat](./plugins/pwdev-feat/) |
| Requirements and UI/UX | [pwdev-prd](./plugins/pwdev-prd/), [pwdev-uiux](./plugins/pwdev-uiux/) |
| Copy and social content | [pwdev-copy](./plugins/pwdev-copy/), [pwdev-social-media](./plugins/pwdev-social-media/) |
| DevOps and operations | [pwdev-devops](./plugins/pwdev-devops/) |
| Knowledge and integrations | [pwdev-brain](./plugins/pwdev-brain/), [pwdev-glpi](./plugins/pwdev-glpi/), [pwdev-obsidian](./plugins/pwdev-obsidian/), [pwdev-postgres](./plugins/pwdev-postgres/), [pwdev-youtrack](./plugins/pwdev-youtrack/) |
| Terminal support | [pwdev-statusline](./plugins/pwdev-statusline/) |

## Plugin catalog

| Plugin | Version | Description |
|---|:---:|---|
| [pwdev-brain](./plugins/pwdev-brain/) | 1.1.0 | Second brain and cited LLM Wiki |
| [pwdev-code](./plugins/pwdev-code/) | 2.4.0 | Spec-driven coding and delegation |
| [pwdev-copy](./plugins/pwdev-copy/) | 1.1.0 | Trainable copywriting |
| [pwdev-devops](./plugins/pwdev-devops/) | 1.0.0 | Platform, operations and incidents |
| [pwdev-feat](./plugins/pwdev-feat/) | 2.1.1 | Fast feature planning |
| [pwdev-flow](./plugins/pwdev-flow/) | 0.6.0 | Portable development workflow |
| [pwdev-glpi](./plugins/pwdev-glpi/) | 1.0.5 | GLPI ITSM |
| [pwdev-obsidian](./plugins/pwdev-obsidian/) | 1.0.0 | Obsidian vault operations |
| [pwdev-postgres](./plugins/pwdev-postgres/) | 1.0.0 | Safe PostgreSQL operations |
| [pwdev-power](./plugins/pwdev-power/) | 0.1.0 | Approval-gated development and cmux fleets |
| [pwdev-prd](./plugins/pwdev-prd/) | 2.0.1 | Interview-driven requirements |
| [pwdev-social-media](./plugins/pwdev-social-media/) | 2.0.1 | AI social creative production |
| [pwdev-statusline](./plugins/pwdev-statusline/) | 1.1.0 | Configurable terminal status |
| [pwdev-uiux](./plugins/pwdev-uiux/) | 2.0.1 | UI/UX and accessibility |
| [pwdev-youtrack](./plugins/pwdev-youtrack/) | 1.0.0 | YouTrack management |
| [sdd-composy](./plugins/sdd-composy/) | 0.1.0 | Portable SDD with OKF and traceability |

## First use

Workflow plugins generally follow:

```text
init → discover/map → product/specify → plan/tasks → execute → QA/evidence → review → verify
```

For `sdd-composy`, start with `/sdd-composy:init` and choose `pt-BR` or `en-US`.

## Updates and safety

```bash
claude plugin marketplace update pwdev-claude-marketplace
claude plugin update <plugin>@pwdev-claude-marketplace
```

Review permissions before enabling external providers, MCP integrations or autonomous fleets.

## Contributing

Keep manifests, skills, commands, references, tests and both READMEs synchronized. Run
`python3 scripts/validate_readme_plugins.py` before submitting changes.

License: Apache-2.0.
