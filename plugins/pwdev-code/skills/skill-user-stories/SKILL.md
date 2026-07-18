---
name: skill-user-stories
description: >
  Write and refine high-quality user stories — INVEST criteria, "As a X, I want Y,
  so that Z" format, Gherkin acceptance criteria when applicable, definition of
  ready, anti-patterns, and a review checklist. Use when creating or reviewing
  user stories, PRD section 6, backlog items, or acceptance criteria.
  Do NOT use for technical specs, architecture decisions, or task decomposition.
paths:
  - "**/PRD.md"
  - "**/prd.md"
  - ".planning/product/stories/**"
metadata:
  version: 1.0.0
  author: Pwdev
  updated: 2026-07-18
---

# User Stories Skill

Standard of quality for every user story produced by the PWDEV-CODE framework
(`/pwdev-code:product prd` §6, `/pwdev-code:product stories`) and for
reviewing stories brought by the human.

---

## 1. Canonical Format

**PT-BR:** `Como {persona}, quero {ação}, para {valor/resultado}.`
**EN:** `As a {persona}, I want {action}, so that {value/outcome}.`

- **Persona** — a real user type with a name from the PRD/requirements
  (never "o sistema"/"the system"; never "usuário" genérico if personas exist).
- **Ação** — one capability, observable from the user's perspective.
- **Valor** — the reason; if you can't state it, the story probably isn't one.

## 2. INVEST — quick test per letter

| Letter | Question | Fails when... |
|--------|----------|---------------|
| **I**ndependent | Can it ship without waiting on another story? | hidden dependency on an unwritten story |
| **N**egotiable | Is it an intent, not a frozen spec? | prescribes UI pixel/implementation detail |
| **V**aluable | Does the persona gain something? | value only for developers ("refactor X") |
| **E**stimable | Can the team size it? | too vague or research-shaped |
| **S**mall | Fits in one iteration? | it's an epic wearing a story costume |
| **T**estable | Can each AC be verified objectively? | "should be fast/easy/intuitive" |

A story that fails 2+ letters must be rewritten or split before entering
`.planning/product/stories/`.

## 3. Acceptance Criteria

**Use Gherkin** when behavior has state + trigger + observable result:

```gherkin
# PT-BR                                  # EN
Dado que estou logado como cliente       Given I am logged in as a customer
Quando adiciono um item esgotado         When I add an out-of-stock item
Então vejo a mensagem "indisponível"     Then I see the "unavailable" message
E o item não entra no carrinho           And the item is not added to the cart
```

**Use a simple checklist** for cross-cutting or static criteria
(e.g. "- [ ] lista pagina de 20 em 20", "- [ ] AA contrast on all states").

Rules: every AC is objectively verifiable; cover the happy path AND at least
one error/edge path; 3-8 ACs per story (more → split the story).

## 4. Definition of Ready

A story is `status: ready` only when:

- [ ] Canonical format with a named persona
- [ ] Passes all 6 INVEST letters
- [ ] 3-8 verifiable ACs (happy + error path)
- [ ] Priority assigned (MoSCoW)
- [ ] Dependencies declared (or "none")
- [ ] Out-of-scope noted when the title invites scope creep

## 5. Anti-Patterns

| Never write | Why | Instead |
|-------------|-----|---------|
| "Como sistema, quero..." | systems don't want things | name the persona who benefits |
| Technical story disguised ("Como dev, quero migrar o banco") | no user value stated | attach it to the user outcome, or make it a task in a plan |
| AC "deve ser rápido/fácil/intuitivo" | not testable | number it ("responde em <500ms", "máx 2 cliques") |
| Story-epic ("Como cliente, quero gerenciar meu pedido") | not Small | split per capability (ver, cancelar, alterar) |
| Hidden dependency ("...igual à tela de admin") | not Independent | declare the dependency or inline the requirement |
| UI prescription ("quero um dropdown azul...") | not Negotiable | state the need; design decides the control |

## 6. Review Checklist (10 items)

1. Persona named and real (exists in PRD/requirements)?
2. One capability per story?
3. Value clause non-circular ("para que eu possa fazer X" ≠ repetir a ação)?
4. INVEST: all 6 pass?
5. ACs: happy path covered?
6. ACs: at least one error/edge path?
7. ACs: all objectively verifiable (numbers, observable states)?
8. Priority MoSCoW assigned?
9. Dependencies explicit?
10. Language consistent with project `lang` (terms técnicos em inglês)?

## 7. Examples

### ✅ Good (PT-BR)
> **US-03 — Cancelar pedido não enviado**
> Como **cliente**, quero **cancelar um pedido que ainda não foi enviado**,
> para **não pagar por algo que não quero mais**.
> ACs: Dado pedido "processando" / Quando clico Cancelar e confirmo / Então
> status vira "cancelado" E estorno é criado E recebo e-mail. + Dado pedido
> "enviado" / Quando abro o pedido / Então Cancelar não é exibido.

### ✅ Good (EN)
> **US-07 — Export report as CSV**
> As an **operations analyst**, I want **to export the monthly report as CSV**,
> so that **I can cross it with the ERP spreadsheet**.
> ACs: Given a report with data / When I click Export / Then a CSV downloads
> with the visible columns and filters applied. Given an empty report / Then
> Export is disabled with a tooltip.

### ❌ Bad → fixed
> ~~"Como usuário, quero uma tela de pedidos melhor."~~ — persona genérica,
> não testável, não estimável.
> → "Como **cliente recorrente**, quero **filtrar meus pedidos por status e
> período**, para **encontrar uma compra antiga sem rolar a lista inteira**."

> ~~"As a system, I want to validate tokens."~~ — system persona, technical.
> → "As a **logged-in user**, I want **my session to stay valid while I work**,
> so that **I don't lose a form to a silent logout**." (token validation
> becomes a task under this story's plan)

## 8. Integration with PWDEV-CODE

- `/pwdev-code:product prd` §6 (User Stories with ACs) MUST follow this skill.
- `/pwdev-code:product stories` uses this skill as the quality bar and
  persists stories to `.planning/product/stories/US-{NN}-{slug}.md`.
- `discover`/`design` consult existing stories as requirement sources.
- Story files carry frontmatter: `id`, `epic` (roadmap ref, if any),
  `priority` (MoSCoW), `status: draft|ready`.
