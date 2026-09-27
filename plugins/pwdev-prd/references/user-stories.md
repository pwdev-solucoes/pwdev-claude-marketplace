# User stories, acceptance criteria (CA) and business rules (RN)

The quality bar for every story of a pwdev-prd roadmap. Adapted from the pwdev-code
`skill-user-stories` standard (canonical format, INVEST, acceptance criteria, Definition of
Ready, anti-patterns, review checklist), extended with business rules and with the fields the
`roadmap.json` contract and `scripts/roadmap-check.py` enforce.

## 1. Canonical format

**PT-BR:** `Como {persona}, quero {ação}, para {valor/resultado}.`
**EN:** `As a {persona}, I want {action}, so that {value/outcome}.`

- **Persona** — a real user type named in the PRD (Context → Target Audience). Never "o sistema"
  / "the system"; never a generic "usuário" when the PRD names personas.
- **Ação** — one capability, observable from the user's perspective.
- **Valor** — the reason; if it cannot be stated, it is not a story. The value clause must not
  repeat the action.

Each feature of the roadmap carries **1 to 5 stories**. More than 5 → the feature is too big;
split the feature.

## 2. INVEST — quick test per letter

| Letter | Question | Fails when... |
|--------|----------|---------------|
| **I**ndependent | Can it ship without waiting on another story? | hidden dependency on an unwritten story |
| **N**egotiable | Is it an intent, not a frozen spec? | prescribes UI pixel or implementation detail |
| **V**aluable | Does the persona gain something? | value only for developers ("refactor X") |
| **E**stimable | Can the team size it? | too vague or research-shaped |
| **S**mall | Fits in one iteration? | it is an epic wearing a story costume |
| **T**estable | Can each CA be verified objectively? | "should be fast/easy/intuitive" |

A story that fails 2+ letters is rewritten or split before it can be `ready`.

## 3. Acceptance criteria (CA)

IDs are local to the story: `CA-01`, `CA-02`… (cited as `US-03/CA-02`). Each CA declares its
`path`: `happy`, `error` or `edge`.

**Gherkin** (`type: gherkin`) when behavior has state + trigger + observable result:

```gherkin
# PT-BR                                  # EN
Dado que estou logado como cliente       Given I am logged in as a customer
Quando adiciono um item esgotado         When I add an out-of-stock item
Então vejo a mensagem "indisponível"     Then I see the "unavailable" message
E o item não entra no carrinho           And the item is not added to the cart
```

**Checklist** (`type: check`) for cross-cutting or static criteria ("lista pagina de 20 em 20",
"contraste AA em todos os estados").

Rules: every CA is objectively verifiable (numbers, observable states); a `ready` story has
**3–8 CA** with at least one `happy` and at least one `error` or `edge` (more than 8 → split the
story). A CA that enforces a business rule cites it (`"rules": ["RN-02"]`).

## 4. Business rules (RN)

A business rule is a policy of the domain that holds regardless of screens or technology:
"Pedido só pode ser cancelado antes do envio", "Desconto máximo de 30% sem aprovação do
gerente". Not a requirement ("the system must list orders") and not a design decision.

- **Source of truth: the PRD** (`### Business Rules`, IDs `RN-01`, `RN-02`…, stable, never
  reused). `roadmap.json` carries a copy in `rules[]` for traceability and publishing.
- Each RN states: **name**, **rule** (one sentence, testable), **example** (a concrete case,
  ideally with numbers), and optionally **exceptions**.
- A story lists the RN it applies (`rules`), and at least one of its CA verifies each of them.
- A rule discovered while refining a story is **added to the PRD** (next free `RN-xx`, row in
  the PRD Change Log) and to `roadmap.json` — never kept only inside the story.
- Every RN should be applied by at least one story (the checker warns otherwise).

## 5. Definition of Ready (`status: ready`)

- [ ] Canonical format with a persona named in the PRD
- [ ] Passes all 6 INVEST letters
- [ ] 3–8 verifiable CA, at least one happy and one error/edge path
- [ ] Applicable RN listed, each verified by a CA
- [ ] Priority assigned (MoSCoW)
- [ ] Dependencies declared (`depends_on`, or none)
- [ ] Out-of-scope noted when the title invites scope creep

`draft` stories may be incomplete (at least 1 CA). Only the human moves a story to `ready`, in
`prd-stories`.

## 6. Anti-patterns

| Never write | Why | Instead |
|-------------|-----|---------|
| "Como sistema, quero..." | systems don't want things | name the persona who benefits |
| Technical story ("Como dev, quero migrar o banco") | no user value | attach it to the user outcome, or make it a task |
| CA "deve ser rápido/fácil/intuitivo" | not testable | number it ("responde em < 500 ms", "máx. 2 cliques") |
| Story-epic ("Como cliente, quero gerenciar meu pedido") | not Small | split per capability (ver, cancelar, alterar) |
| Hidden dependency ("...igual à tela de admin") | not Independent | declare the dependency or inline the requirement |
| UI prescription ("quero um dropdown azul") | not Negotiable | state the need; design decides the control |
| Business rule buried in a CA only | invisible to other stories | promote it to an `RN-xx` in the PRD |

## 7. Review checklist (per story)

1. Persona named and real (exists in the PRD)?
2. One capability per story?
3. Value clause non-circular?
4. INVEST: all 6 pass?
5. CA: happy path covered?
6. CA: at least one error/edge path?
7. CA: all objectively verifiable?
8. RN: every applicable rule listed and verified by a CA?
9. Priority MoSCoW assigned; dependencies explicit?
10. Language consistent with the project `lang` (technical terms in English)?

## 8. Examples

### ✅ Good (PT-BR)
> **US-03 — Cancelar pedido não enviado** · Como **cliente**, quero **cancelar um pedido que
> ainda não foi enviado**, para **não pagar por algo que não quero mais**. · RN: RN-04
> - CA-01 (happy) Dado pedido "processando" / Quando clico Cancelar e confirmo / Então o status
>   vira "cancelado" E o estorno é criado E recebo e-mail.
> - CA-02 (error, RN-04) Dado pedido "enviado" / Quando abro o pedido / Então Cancelar não é exibido.
> - CA-03 (edge) Dado pedido pago com cupom / Quando cancelo / Então o cupom volta a ficar disponível.
>
> **RN-04 — Cancelamento só antes do envio** · Um pedido só pode ser cancelado pelo cliente
> enquanto o status for anterior a "enviado". Ex.: pedido 1023 "processando" → pode; pedido
> 1024 "enviado" → não pode (vira devolução).

### ✅ Good (EN)
> **US-07 — Export report as CSV** · As an **operations analyst**, I want **to export the
> monthly report as CSV**, so that **I can cross it with the ERP spreadsheet**.
> - CA-01 (happy) Given a report with data / When I click Export / Then a CSV downloads with the
>   visible columns and filters applied.
> - CA-02 (edge) Given an empty report / Then Export is disabled with a tooltip.
> - CA-03 (error, RN-02) Given more than 100,000 rows / When I click Export / Then I am asked to
>   narrow the period.

### ❌ Bad → fixed
> ~~"Como usuário, quero uma tela de pedidos melhor."~~ — persona genérica, não testável.
> → "Como **cliente recorrente**, quero **filtrar meus pedidos por status e período**, para
> **encontrar uma compra antiga sem rolar a lista inteira**."

## 9. `roadmap.json` shape (see `roadmap-format.md`)

```json
"rules": [ { "id": "RN-04", "title": "Cancelamento só antes do envio",
             "rule": "…", "example": "…" } ],
"stories": [ {
  "id": "US-03", "feature": "F01-E02-FT01", "title": "Cancelar pedido não enviado",
  "persona": "cliente", "action": "cancelar um pedido que ainda não foi enviado",
  "value": "não pagar por algo que não quero mais",
  "priority": "must", "status": "ready", "rules": ["RN-04"], "depends_on": [],
  "out_of_scope": "",
  "acceptance": [
    { "id": "CA-01", "path": "happy", "type": "gherkin",
      "text": "Dado pedido \"processando\"\nQuando clico Cancelar e confirmo\nEntão o status vira \"cancelado\"" },
    { "id": "CA-02", "path": "error", "type": "gherkin", "rules": ["RN-04"],
      "text": "Dado pedido \"enviado\"\nQuando abro o pedido\nEntão Cancelar não é exibido" }
  ]
} ]
```
