# PWDEV-PRD v1.0.0

> **Interview-Driven PRD Creation for Claude Code**

```
Structured interview → Consistent PRD → Markdown + JSON export
```

PWDEV-PRD guides you through a **12-step structured interview** to create complete, consistent, technology-agnostic Product Requirements Documents for features or entire systems.

---

## Methodology

### The Problem

PRDs are often incomplete, inconsistent, or biased toward a specific technology. Teams start building without clear objectives, metrics, acceptance criteria, or risk assessment. The result: scope creep, missed requirements, and features that don't solve the actual problem.

### The Solution

A specialized interviewer agent that:
- Asks **one question at a time** and waits for your answer
- Offers **2-3 options** when you don't know the answer
- Summarizes and confirms at the end of each stage
- Marks unknowns as **hypotheses** (never invents)
- Runs **consistency checks** before generating the final PRD
- Produces a **structured document** ready for execution

### Technology-Agnostic

PRDs created by this plugin describe **what** needs to be built and **why**, not **how**. Architecture sections capture decisions at a system level (monolith vs microservice, sync vs async) without specifying frameworks, libraries, or languages.

This makes PRDs compatible with any downstream workflow:
- `/pwdev-feat:feat` for simplified feature development
- `/pwdev-code:discover` for rigorous spec-driven development
- Manual handoff to engineering teams

---

## 12-Step Interview Process

| Step | Topic | What is captured |
|:----:|-------|-----------------|
| 1 | **Context & Overview** | Product, audience, deployment context, business objective |
| 2 | **Problem & Opportunity** | Current pain, real examples with numbers, failed attempts |
| 3 | **Objectives & Metrics** | Measurable goals with metric and target |
| 4 | **Scope** | What's in, what's explicitly out |
| 5 | **Functional Requirements** | Name, description, main flow, alternatives, errors, priority |
| 6 | **Non-Functional Requirements** | Performance, availability, security, observability, compliance |
| 7 | **Architecture & Approach** | Components, integrations, communication patterns |
| 8 | **Decisions & Trade-offs** | What's decided, why, what's the cost |
| 9 | **Dependencies** | Technical, organizational, external |
| 10 | **Risks & Mitigation** | Probability, impact, mitigation (multiple items), contingency |
| 11 | **Acceptance Criteria** | Objective, verifiable checklist |
| 12 | **Testing & Validation** | Test types, validation strategy |

### Consistency Checks

Before generating the final PRD, the agent validates:
- Every objective has a metric and target
- Every functional requirement has name, flow, and priority
- NFRs include at least performance and availability
- Out of scope doesn't contradict in scope
- Architecture supports declared NFRs
- Every decision has justification and trade-off
- Every risk has probability, impact, mitigation, and contingency
- Acceptance criteria are objective and verifiable

---

## Agent

| Agent | Role | What it does |
|-------|------|-------------|
| **agent-interviewer** | PRD Interview Specialist | Conducts the 12-step interview, validates consistency, generates PRD.md + prd.json |

### Agent Boundaries
- Never chooses specific technologies
- Never invents requirements (marks unknowns as hypotheses)
- Never asks double questions
- Always confirms understanding before moving on

---

## Commands

### Setup

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:init` | Create `.planning/prds/` workspace |

### PRD Creation

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:create "desc"` | Start structured interview → generate PRD.md + optional prd.json |
| `/pwdev-prd:refine {slug}` | Update specific sections of an existing PRD |

### Management

| Command | What it does |
|---------|-------------|
| `/pwdev-prd:list` | List all PRDs with status |
| `/pwdev-prd:export {slug}` | Export as JSON or GitHub issue |
| `/pwdev-prd:export {slug} --json` | Regenerate prd.json |
| `/pwdev-prd:export {slug} --github` | Create GitHub issue from PRD |

---

## Output Formats

### Markdown (PRD.md)

Structured document with standardized sections:

```
PRD: [product] [feature]
├── Summary
├── Context and Problem
├── Objectives and Metrics (table)
├── Scope (in / out)
├── Functional Requirements (per requirement)
├── Non-Functional Requirements (by category)
├── Architecture and Approach
├── Decisions and Trade-offs
├── Dependencies
├── Risks and Mitigation
├── Acceptance Criteria (checklist)
└── Testing and Validation
```

### JSON (prd.json) — Optional

Structured data with English keys, content in original language:

```json
{
  "meta": { "product", "feature", "version", "date" },
  "context": { "summary", "target_audience", "problems" },
  "goals": [{ "goal", "metric", "target" }],
  "scope": { "in_scope", "out_of_scope" },
  "functional_requirements": [{ "id", "name", "main_flow", "priority" }],
  "non_functional_requirements": [{ "category", "specifications" }],
  "architecture": { "approach", "components", "integrations" },
  "decisions_tradeoffs": [{ "decision", "justification", "trade_off" }],
  "dependencies": [{ "type", "title", "description" }],
  "risks": [{ "risk", "probability", "impact", "mitigation", "contingency_plan" }],
  "acceptance_criteria": [],
  "testing_validation": { "test_types", "strategy" }
}
```

---

## Workspace

```
.planning/prds/
├── user-authentication/
│   ├── PRD.md              # Structured PRD document
│   └── prd.json            # Optional JSON export
├── inventory-management/
│   ├── PRD.md
│   └── prd.json
└── ...
```

---

## Smart Defaults

When the user doesn't know, the agent offers these as **hypotheses** (explicitly marked):

| Aspect | Default |
|--------|---------|
| API latency | p95 < 150ms |
| Availability (external) | 99.9% |
| Availability (internal) | 99.5% |
| Observability | Structured logs + error metrics + distributed tracing |
| Security | Auth + RBAC + sensitive change audit |
| Critical updates | Transactional |

---

## License

Apache-2.0 — See [LICENSE](./LICENSE)

*PWDEV-PRD v1.0.0 — Clear requirements, consistent documents, better features.*
*Maintained by [Paulo Soares](https://github.com/pwdev-solucoes)*
