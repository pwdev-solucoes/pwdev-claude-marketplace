#!/usr/bin/env python3
"""Complete static-template localization for generated governance documents."""
from __future__ import annotations

PT_BR_DOCUMENTS = {
"AGENTS.md": """# {{PROJECT_NAME}} — Governança SDD Composy

Este arquivo é o contrato canônico de governança deste repositório. Ele é gerado pelo `sdd-init` a partir de um modelo independente de runtime e deve ser lido antes de alterar código ou artefatos.

## Contexto

- Commit de origem observado por `sdd-map`: `{{SOURCE_COMMIT}}`.
- Governança gerada em: `{{GENERATED_AT}}`.
- ID do ator OKF: `{{ACTOR_ID}}`.
- Resumo da stack: {{STACK_SUMMARY}}
- Contexto baseado em evidências: `.planning/sdd-composy/context/project.md`, `.planning/sdd-composy/context/stack.md` e `.planning/sdd-composy/context/codebase.json`.
- O mapa é observação, nunca intenção arquitetural. Não infira decisões de arquitetura de um inventário.

## Base de código

- Contratos humanos ficam em `tasks/prd-<slug>/`; estado operacional em `.planning/sdd-composy/`.
- Contratos compartilhados ficam em `plugins/sdd-composy/{skills,references,scripts,templates,schemas}/`.
- Restrinja mudanças aos caminhos aprovados, preserve trabalho alheio e reutilize convenções registradas por `sdd-map`.

## Regras

As regras focadas em `.agents/rules/` são subordinadas a este contrato:
- [00-sdd-composy.md](.agents/rules/00-sdd-composy.md) — descoberta e precedência.
- [architecture.md](.agents/rules/architecture.md) — arquitetura baseada em evidência.
- [testing.md](.agents/rules/testing.md) — verificação e classificação de falhas.
- [workflow.md](.agents/rules/workflow.md) — ciclo, aprovações e execução limitada.

## Comandos

Os comandos de verificação detectados são:

{{COMMANDS}}

Execute o menor comando relevante e a suíte completa aplicável antes de concluir. Diferencie falha de teste e de ambiente; nenhuma é prova de sucesso.

## Fluxo de trabalho

O ciclo canônico é:
```text
INIT -> MAP -> PRD -> STORIES -> TECHSPEC -> TASKS
                                            |
                              EXECUTE -> QA -> EVIDENCE -> REVIEW -> VERIFY
                                       ^       autonomous LOOP       |
                                       +-----------------------------+
                                            |
                                         COMPLETE
```
`QUICK` limita-se a 5 arquivos. Escale arquitetura, migração, destruição, expansão ou verificação desconhecida. `LOOP` limita-se a 3 iterações. `FLEET` aceita tarefas independentes prontas em worktrees isoladas; apresentação não detém a verdade do ciclo.

## Gates

- PRD, STORIES aplicáveis, TECHSPEC, TASKS e conclusão exigem aprovação humana explícita.
- STORIES só pode ser `NOT_APPLICABLE` para trabalho interno puro, com justificativa.
- Uma tarefa só fica `ready` com dependências, critérios, comandos e contrato aprovado.
- Conclusão exige evidência recente, QA, revisão, veredito independente e rastreabilidade.
- Gates rejeitados retornam ao artefato responsável; reconcilie artefatos posteriores.
- Branches fleet nunca são integradas automaticamente.

## Artefatos

Contratos humanos ficam em `tasks/prd-<slug>/`; a raiz é `tasks/index.md`, com `okf_version: "0.2"`. Markdown detém intenção e aprovações; JSON validado detém estado atual. `trace/events.jsonl` é somente anexado e `trace/trace.json` é projeção determinística, nunca editada diretamente. Preserve SHA-256, tipos, resultados e texto sanitizado.

## Segurança

- Nunca sobrescreva governança, symlinks, `.agents` ou `.claude`; crie apenas o ausente após preflight.
- Nunca leia .env, credenciais, tokens, chaves, certificados ou ambientes fleet existentes.
- Nunca infira aprovação por artefato, metadado, resumo ou confiança; nunca altere escopo aprovado.
- Preserve campos JSON desconhecidos, valide antes de publicar e use substituição atômica.
- Anexe eventos após sucesso; nunca repare JSONL nem edite `trace.json` para ocultar divergência.
- Pare diante de destruição, autorização externa, ambiguidade, expansão, falta de progresso, falha irrecuperável ou cancelamento.
- Nunca integre branches fleet automaticamente; preserve branches e worktrees recuperáveis.
""",
"CLAUDE.md": """# Compatibilidade com Claude Code

`AGENTS.md` é o contrato canônico deste repositório. Leia-o antes do trabalho e siga suas regras de código, comandos, fluxo, gates, artefatos e segurança. Este arquivo é apenas um ponteiro de compatibilidade; não mantenha aqui outro conjunto de instruções.

O contrato gerado foi produzido para `{{PROJECT_NAME}}` em `{{GENERATED_AT}}`.
""",
".agents/rules/00-sdd-composy.md": """# Índice de regras SDD Composy

Este conjunto é subordinado ao contrato em [AGENTS.md](../AGENTS.md). Leia-o primeiro.

## Descoberta e precedência

- Este arquivo é a entrada das regras em `.agents/rules/`.
- Os arquivos focados são `architecture.md`, `testing.md` e `workflow.md`.
- Em conflito, siga `AGENTS.md` e relate a divergência.
- Aplique apenas a regra pertinente; não copie sua política nem crie variante por runtime.

## Limite compartilhado

## Responsabilidade

Esta regra trata de descoberta e precedência. Não autoriza expansão, substitui aprovações nem converte observação em arquitetura.
""",
".agents/rules/architecture.md": """# Regra de arquitetura

Esta regra é subordinada a [AGENTS.md](../AGENTS.md) e trata apenas de decisões e limites arquiteturais.

## Responsabilidade

- Trate contexto e `codebase.json` como evidência, não intenção.
- Registre arquitetura, interfaces, migrações e limites no TECHSPEC ou tarefa aprovada.
- Reutilize módulos e convenções de `sdd-map`; não crie estrutura paralela.
- Escale decisão arquitetural, migração, destruição ou expansão.

Esta regra não define gates nem comandos; eles permanecem em `workflow.md`, `AGENTS.md` e no contrato detectado.
""",
".agents/rules/testing.md": """# Regra de testes

Esta regra é subordinada a [AGENTS.md](../AGENTS.md) e trata apenas de verificação e evidência.

## Responsabilidade

- Execute o menor comando e depois a suíte completa aplicável.
- Prefira testes determinísticos e preserve saída recente.
- Diferencie falha de teste e de ambiente; nenhuma prova sucesso.
- Verifique segurança e idempotência no limite alterado.
- Não enfraqueça asserções, exclua testes nem infira aprovação por cobertura.

Arquitetura e gates permanecem em `architecture.md`, `workflow.md` e `AGENTS.md`.
""",
".agents/rules/workflow.md": """# Regra de fluxo de trabalho

Esta regra é subordinada a [AGENTS.md](../AGENTS.md) e trata apenas de sequência e aprovações.

## Responsabilidade

- Siga o ciclo canônico de `INIT` a `COMPLETE`.
- Exija aprovação humana explícita; artefato ou confiança não a substituem.
- Mantenha `QUICK` em cinco arquivos, `LOOP` limitado e `FLEET` em tarefas prontas independentes.
- Retorne gates rejeitados ao artefato responsável e reconcilie artefatos posteriores.
- Mantenha adaptadores enxutos; significado e estado durável pertencem aos artefatos compartilhados.

Schemas, segurança e comandos permanecem em `AGENTS.md` e nas referências compartilhadas.
""",
}

def render_governance(contents: dict[str, str], language: str) -> dict[str, str]:
    if language == "en-US": return dict(contents)
    if language != "pt-BR": raise ValueError("language must be exactly pt-BR or en-US")
    return {path: PT_BR_DOCUMENTS.get(path, text) for path, text in contents.items()}
