#!/usr/bin/env python3
"""Static-block localization for generated governance documents.

Only literals owned by the plugin are translated.  Runtime values, identifiers,
paths, code spans, and user-provided evidence are never passed through a general
purpose translator or a word-by-word replacement.
"""
from __future__ import annotations


def render_governance(contents: dict[str, str], language: str) -> dict[str, str]:
    """Return governance contents in the requested supported language."""
    if language == "en-US":
        return dict(contents)
    if language != "pt-BR":
        raise ValueError("language must be exactly pt-BR or en-US")
    translations = {
        "AGENTS.md": {
            "SDD Composy Governance": "Governança SDD Composy",
            "## Context": "## Contexto",
            "## Codebase": "## Base de código",
            "## Rules": "## Regras",
            "## Commands": "## Comandos",
            "## Workflow": "## Fluxo de trabalho",
            "## Gates": "## Gates",
            "## Artifacts": "## Artefatos",
            "## Safety": "## Segurança",
            "This file is the canonical governance contract for this repository.":
                "Este arquivo é o contrato canônico de governança deste repositório.",
            "Source commit observed by": "Commit de origem observado por",
            "Governance generated at:": "Governança gerada em:",
            "Stack summary:": "Resumo da stack:",
            "Evidence-based context:": "Contexto baseado em evidências:",
            "The canonical lifecycle is:": "O ciclo de vida canônico é:",
            "Operational artifacts live under": "Os artefatos operacionais ficam em",
            "Human contracts live under": "Os contratos humanos ficam em",
            "Run the smallest relevant command after each change":
                "Execute o menor comando relevante após cada alteração",
            "Never overwrite existing governance files":
                "Nunca sobrescreva arquivos de governança existentes",
            "Never read .env": "Nunca leia .env",
            "Never infer human approval": "Nunca infira aprovação humana",
            "Never change approved requirements": "Nunca altere requisitos aprovados",
            "Always preserve unknown JSON fields": "Sempre preserve campos JSON desconhecidos",
            "Never merge fleet branches automatically": "Nunca faça merge automático de branches fleet",
            "project artifacts.": "artefatos do projeto.",
            "Human contracts are under": "Os contratos humanos ficam em",
            "Operational state is under": "O estado operacional fica em",
            "Shared plugin contracts are under": "Os contratos compartilhados do plugin ficam em",
            "The detected verification commands are:": "Os comandos de verificação detectados são:",
            "neither is evidence of success.": "nenhum deles é evidência de sucesso.",
            "The index uses": "O índice usa",
            "Markdown owns intent, decisions, narrative acceptance contracts, and approvals.":
                "Markdown detém intenção, decisões, contratos narrativos de aceitação e aprovações.",
            "Validated JSON owns current operational state": "JSON validado detém o estado operacional atual",
            "Initialization creates only missing files and diagnoses conflicts.":
                "A inicialização cria apenas arquivos ausentes e diagnostica conflitos.",
            "Do not display, migrate, reuse, adopt, or audit their contents.":
                "Não exiba, migre, reutilize, adote nem audite seus conteúdos.",
            "Validate before publication": "Valide antes da publicação",
            "Stop for destructive work": "Pare diante de trabalho destrutivo",
        },
        "CLAUDE.md": {
            "# Claude Code compatibility": "# Compatibilidade com Claude Code",
            "The generated contract was produced for": "O contrato gerado foi produzido para",
            "is the canonical governance contract for this repository. Read it before":
                "é o contrato canônico de governança deste repositório. Leia-o antes de",
            "starting work and follow its codebase, commands, workflow, gates, artifacts, and safety":
                "iniciar o trabalho e siga sua base de código, comandos, fluxo, gates, artefatos e segurança",
            "rules. This file exists only as a short compatibility pointer for Claude Code; do not":
                "regras. Este arquivo existe apenas como um ponteiro curto de compatibilidade para Claude Code; não",
            "maintain a second set of project instructions here.":
                "mantenha aqui um segundo conjunto de instruções do projeto.",
        },
        ".agents/rules/00-sdd-composy.md": {
            "# SDD Composy rule index": "# Índice de regras SDD Composy",
            "## Discovery and precedence": "## Descoberta e precedência",
            "## Shared boundary": "## Limite compartilhado",
            "## Responsibility": "## Responsabilidade",
            "This rule set is subordinate to the canonical contract in":
                "Este conjunto de regras é subordinado ao contrato canônico em",
            "Read that file first; it owns repository-wide governance, safety, artifacts, gates,":
                "Leia esse arquivo primeiro; ele detém governança, segurança, artefatos e gates do repositório,",
            "and commands.": "e comandos.",
            "This file is the entry point for the rules installed in":
                "Este arquivo é o ponto de entrada para as regras instaladas em",
            "The concern-specific files are": "Os arquivos específicos por assunto são",
            "When a rule conflicts with": "Quando uma regra conflitar com",
            "follow": "siga",
            "and report the conflict.": "e reporte o conflito.",
            "This rule's responsibility is rule discovery and precedence across the focused files.":
                "A responsabilidade desta regra é a descoberta e precedência entre os arquivos focados.",
        },
        ".agents/rules/architecture.md": {
            "# Architecture rule": "# Regra de arquitetura",
            "## Responsibility": "## Responsabilidade",
            "This focused rule is subordinate to the canonical contract in":
                "Esta regra focada é subordinada ao contrato canônico em",
            "and is concerned only with architecture decisions and boundaries.":
                "e trata somente de decisões e limites de arquitetura.",
            "Treat": "Trate",
            "evidence about the repository, not as architectural intent.":
                "como evidência sobre o repositório, não como intenção arquitetural.",
            "Record architecture, interfaces, migrations, and boundary changes in the approved":
                "Registre arquitetura, interfaces, migrações e mudanças de limite na",
            "Reuse established modules and conventions identified by":
                "Reutilize módulos e convenções estabelecidos identificados por",
            "Escalate when a change requires an architectural decision":
                "Escale quando uma alteração exigir uma decisão arquitetural",
        },
        ".agents/rules/testing.md": {
            "# Testing rule": "# Regra de testes",
            "## Responsibility": "## Responsabilidade",
            "This focused rule is subordinate to the canonical contract in":
                "Esta regra focada é subordinada ao contrato canônico em",
            "and is concerned only with verification and evidence.":
                "e trata somente de verificação e evidências.",
            "Run the smallest relevant command after a change, then the complete applicable suite":
                "Execute o menor comando relevante após uma alteração e depois a suíte aplicável completa",
            "before claiming completion.": "antes de declarar conclusão.",
            "Prefer deterministic, repository-native tests and preserve fresh output as evidence":
                "Prefira testes determinísticos nativos do repositório e preserve a saída recente como evidência",
            "Distinguish a test failure from an environment failure":
                "Diferencie falha de teste de falha de ambiente",
            "Verify the behavior at the boundary it changes": "Verifique o comportamento no limite alterado",
            "Do not weaken an assertion, delete a failing test, or infer approval from coverage":
                "Não enfraqueça uma asserção, exclua um teste falhando nem infira aprovação por cobertura",
        },
        ".agents/rules/workflow.md": {
            "# Workflow rule": "# Regra de fluxo de trabalho",
            "## Responsibility": "## Responsabilidade",
            "This focused rule is subordinate to the canonical contract in":
                "Esta regra focada é subordinada ao contrato canônico em",
            "and is concerned only with lifecycle sequencing and approvals.":
                "e trata somente do sequenciamento do ciclo de vida e aprovações.",
            "Follow the canonical lifecycle from": "Siga o ciclo de vida canônico de",
            "Require explicit human approval for the gates named by":
                "Exija aprovação humana explícita para os gates definidos por",
            "Keep runtime adapters thin": "Mantenha os adaptadores de runtime enxutos",
        },
    }
    rendered = dict(contents)
    for path, replacements in translations.items():
        if path not in rendered:
            continue
        text = rendered[path]
        for source, target in replacements.items():
            text = text.replace(source, target)
        rendered[path] = text
    return rendered
