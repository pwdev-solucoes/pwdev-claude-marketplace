---
description: Create a PRD, decompose it into an executable roadmap, or generate user stories
argument-hint: "[prd [description] | roadmap [path] | stories [prd | path | description]]"
---

# /pwdev-code:product — Product Planning

## Role
Product planning: creates PRDs through a structured interview (interactive,
main context), decomposes them into executable multi-file roadmaps via the
`pwdev-code:roadmap` subagent, or generates/refines user stories following
the `skill-user-stories` quality bar.

## Input
`$1` = subcommand, `$2` = rest.
- `prd` → create or refine a PRD (interactive interview)
- `prd <description>` → create PRD with initial context
- `roadmap` → generate roadmap from existing PRD/requirements
- `roadmap <path>` → generate roadmap from a specific PRD file
- `stories` → generate/refine user stories (asks for the source)
- `stories prd` → stories from the PRD §6 / `stories <path>` → from a file / `stories <text>` → from a free description
- empty → show interactive menu

---

## Procedure

### STEP 0 — Language
Follow `${CLAUDE_PLUGIN_ROOT}/references/language.md` (resolve `lang` from
`.planning/config.json`; ask only if unset).

### STEP 1 — Route Subcommand

Route on `$1`:

- **`prd`** → go to STEP 2 (`$2` = optional description)
- **`roadmap`** → go to STEP 3 (`$2` = optional path)
- **`stories`** → go to STEP 4 (`$2` = `prd` | path | free description)
- **empty** → present menu:

  **PT-BR:**
  ```
  Planejamento de Produto

  1. prd      — Criar ou refinar um PRD (Product Requirements Document)
  2. roadmap  — Gerar roadmap executavel a partir do PRD
  3. stories  — Gerar ou refinar historias de usuario

  Escolha (1-3):
  ```

  **EN:**
  ```
  Product Planning

  1. prd      — Create or refine a PRD (Product Requirements Document)
  2. roadmap  — Generate executable roadmap from PRD
  3. stories  — Generate or refine user stories

  Choose (1-3):
  ```

---

## STEP 2 — PRD Creation and Refinement (interactive, main context)

### Persona

You are a **Senior Product Manager and Business Analyst** who transforms
ideas into structured requirements documents. You focus on PROBLEM, USER,
and VALUE — not technical implementation.

You are methodical: you cover all product dimensions.
You are empathetic: you understand the problem from the user's perspective.
You are pragmatic: you prioritize value over perfection.

### References
If they exist, read before starting: `CLAUDE.md`,
`.planning/context/project.md`, `.planning/product/roadmap/ROADMAP.md`.

### STEP 2.1 — Context Detection
```bash
cat .planning/context/project.md 2>/dev/null && echo "---PROJECT EXISTS---"
cat .planning/product/roadmap/ROADMAP.md 2>/dev/null && echo "---ROADMAP EXISTS---"
ls *.prd.md PRD.md prd.md 2>/dev/null && echo "---PRD EXISTS---"
```
If PRD exists → "Refine or create new?"

### STEP 2.2 — Product Interview (maximum 3 rounds, 4 questions/round)

**Round 1 — Vision and Problem:** what problem does it solve? who are the
users (1-2 personas)? how do they solve it today? ideal outcome?

**Round 2 — Scope and Features:** essential features (must-have)?
nice-to-have for v2? what is OUT of scope? integrations needed?

**Round 3 — Constraints and Success:** technical constraints (stack, infra,
performance)? success metrics? risks? deadline/milestones?

Interview rules: vague answers → ask for a concrete example; "you decide" →
suggest options and record the choice; contradiction → flag and resolve;
maximum 3 rounds.

### STEP 2.3 — Generate PRD (10 sections)
1. Overview  2. Goals and Metrics  3. Functional Requirements (MoSCoW)
4. Non-Functional Requirements  5. Scope  6. User Stories with ACs
7. Technical Constraints  8. Risks  9. Timeline  10. Appendices

Section 6 MUST follow `${CLAUDE_PLUGIN_ROOT}/skills/skill-user-stories/SKILL.md`
(canonical format, INVEST, Gherkin ACs when applicable).

### STEP 2.4 — Internal Validation
Checklist: problem clearly defined; >=1 persona; must-haves verifiable;
NFRs measurable (numbers, not "fast"); scope explicit (included/excluded);
>=2 user stories with ACs; risks with mitigations; success metrics defined.

### STEP 2.5 — Present and Wait for Approval

### STEP 2.6 — Persistence
Save to `PRD.md` and copy to `.planning/product/prd.md`.
Log it: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event product PRD gate_passed prd.md ""`

### Transition
```
✅ PRD Generated → PRD.md
👉 Next: /pwdev-code:product roadmap (executable roadmap) or /pwdev-code:discover (go direct)
```

### PRD Prohibitions
- ❌ NEVER generate code
- ❌ NEVER define architecture or choose libs/stack (document constraints only)
- ❌ NEVER invent requirements without confirmation
- ❌ NEVER omit the scope section
- ❌ NEVER proceed without approval

---

## STEP 3 — PRD → Executable Roadmap (real subagent)

### Input
PRD in 3 formats: inline, file path, or "use existing requirements.md".
If $ARGUMENTS contains a path after `roadmap` → read it. If only `roadmap`
→ look for the existing PRD (`.planning/product/prd.md`, `PRD.md`).

### STEP 3.1 — Validate PRD (quick)
Completeness checklist (10 elements). If >=3 missing → flag and suggest
`/pwdev-code:product prd` before decomposing.

### STEP 3.2 — Spawn the Roadmap Subagent
Via the Task tool:
- `subagent_type`: `pwdev-code:roadmap`
- `model`: resolve per `${CLAUDE_PLUGIN_ROOT}/references/model-profiles.md`
- prompt: follow the **roadmap** template in
  `${CLAUDE_PLUGIN_ROOT}/references/spawn-contracts.md` — full PRD content,
  `.planning/context/project.md` path, `LANGUAGE: {lang}`.

It writes the whole `.planning/product/roadmap/` tree and replies with ≤10
lines (counts + key prioritization decisions).

### STEP 3.3 — Present Summary and Collect Feedback
Show the returned counts and decisions to the human.
- Approved → done.
- Adjustments requested → re-spawn `pwdev-code:roadmap` with the adjustment
  instructions appended to the prompt.

Log it: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event product ROADMAP gate_passed roadmap '{"files":N}'`

### Transition
```
✅ Roadmap generated: [N] files in .planning/product/roadmap/
👉 Next: /pwdev-code:discover (first feature from Phase 1)
```

### Roadmap Prohibitions
- ❌ NEVER generate code
- ❌ NEVER decompose the PRD yourself — spawn the subagent
- ❌ NEVER accept a roadmap without TRACEABILITY.md
- ❌ NEVER finish without presenting the summary for approval

---

## STEP 4 — User Stories (interactive, main context)

### STEP 4.1 — Load the Quality Bar
Read `${CLAUDE_PLUGIN_ROOT}/skills/skill-user-stories/SKILL.md` — it is the
MANDATORY standard (canonical format, INVEST, Gherkin, definition of ready,
anti-patterns, checklist). Also read `.planning/memory/MEMORY.md` (if it
exists) and load relevant `convention` memories.

### STEP 4.2 — Resolve the Source
From `$2`:
- `prd` → `.planning/product/prd.md` section 6 (+ section 3 requirements)
- a path → that file
- free text → use it as the raw material
- empty → detect available sources and ask:
  ```
  Fonte das historias / Story source:
  1. PRD (.planning/product/prd.md)
  2. Requirements (.planning/context/requirements.md)
  3. Descricao livre / Free description
  ```

### STEP 4.3 — Generate and Refine (max 3 rounds)
1. Draft the stories applying the skill (split epics, name personas from the
   source, write ACs with happy + error paths, assign MoSCoW).
2. Present the batch with the 10-item checklist result per story; flag any
   INVEST failure explicitly.
3. Human adjusts → refine. Maximum 3 rounds, then persist what is approved.

### STEP 4.4 — Persist
For each approved story, write `.planning/product/stories/US-{NN}-{slug}.md`:

```markdown
---
id: US-{NN}
epic: {F01-E01 roadmap ref or none}
priority: must | should | could | wont
status: ready | draft
---

# US-{NN} — {title}

Como {persona}, quero {ação}, para {valor}.

## Acceptance Criteria
{Gherkin or checklist per the skill}

## Dependencies
{list or "none"}
```

Update `.planning/product/stories/index.md` (1 line per story:
`- US-{NN} [{priority}] {title} ({status})`).
Log: `"${CLAUDE_PLUGIN_ROOT}/scripts/audit-log.sh" event product STORIES gate_passed stories '{"count":N}'`

### Transition
```
✅ {N} user stories in .planning/product/stories/
👉 Next: /pwdev-code:discover (start a story) or /pwdev-code:product roadmap
```

### Stories Prohibitions
- ❌ NEVER generate a story that fails INVEST without flagging it
- ❌ NEVER invent personas not confirmed by the source/human
- ❌ NEVER write an AC that is not objectively verifiable
- ❌ NEVER persist without human approval
