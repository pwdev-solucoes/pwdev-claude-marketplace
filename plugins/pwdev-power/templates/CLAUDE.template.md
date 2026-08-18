# {{PROJECT_NAME}}

{{ONE_LINE_PURPOSE}}

## Stack

{{STACK_TABLE}}

## Commands

| Purpose | Command |
|---|---|
| Install | `{{INSTALL_CMD}}` |
| Run | `{{RUN_CMD}}` |
| Test | `{{TEST_CMD}}` |
| Lint | `{{LINT_CMD}}` |
| Build | `{{BUILD_CMD}}` |

These are the real commands, read from this repository's manifests. If one is wrong, fix it
here rather than working around it.

## Architecture

{{ARCHITECTURE}}

## Conventions

{{CONVENTIONS}}

## Testing

{{TESTING}}

Tests are code: they are committed, reviewed, and held to the same standard as what they test.

## Security

- Never read, print, or commit secrets. `.env` and its variants, `*.pem`, `*.key`, `id_rsa*`
  are off limits; `.env.example` is documentation.
- {{SECURITY_NOTES}}

## Golden rules

1. No production code without a failing test first.
2. No fix without root cause investigation first.
3. No success claim without running the command and reading its output.
4. Never commit on the default branch without explicit consent.
5. {{PROJECT_RULE}}
