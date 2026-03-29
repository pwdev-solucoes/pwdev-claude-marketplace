### PRD: [product] [feature]

Version: [version]
Date: [date]
Owner: [prd_owner]

---

### Summary

[context.summary]

---

### Context and Problem

Target Audience
- [audience 1]
- [audience 2]

Key Use Cases
- [use case 1]
- [use case 2]

Where this feature will be deployed
- [deployment_context.description]

Prioritized Problems
- [problem 1 with impact and priority]
- [problem 2 with impact and priority]

---

### Objectives and Metrics

| Objective | Metric | Target |
|-----------|--------|--------|
| [objective 1] | [metric 1] | [target 1] |
| [objective 2] | [metric 2] | [target 2] |

---

### Scope

In Scope
- [in scope item 1]
- [in scope item 2]

Out of Scope
- [out of scope item 1]
- [out of scope item 2]

---

### Functional Requirements

#### [id] [requirement name]
[requirement description]

**Main Flow**
- [step 1]
- [step 2]

**Alternative Flows and Exceptions**
- [variation / exception 1]
- [variation / exception 2]

**Expected Errors**
- [expected error 1]
- [expected error 2]

**Priority:** [high|medium|low]

---

### Non-Functional Requirements

Performance
- [e.g., p95 less than 150ms]

Availability
- [e.g., 99.9% monthly uptime in production]

Security and Authorization
- [e.g., mandatory authentication and audit of sensitive changes]

Observability
- [e.g., structured logs, error metrics per endpoint, end-to-end distributed tracing]

Reliability and Data Integrity
- [e.g., inventory updates must be transactional]

Compatibility and Portability
- [e.g., REST JSON versioned APIs /v1, packaged in OCI container]

Compliance
- [e.g., price and inventory audit trail available for reconciliation]

Frontend Consumer Accessibility
- [e.g., API response includes alt text for images and labels needed for accessibility]

---

### Architecture and Approach

Approach
- [general approach description]

Components
- [component 1]
- [component 2]

Integrations
- [integration 1]
- [integration 2]

### Decisions and Trade-offs

#### Decision: [decision 1]
- **Justification:** [why this decision was made]
- **Trade-off:** [cost or limitation associated]

---

### Dependencies

#### [dependency type]: [title]
[dependency description]

---

### Risks and Mitigation

#### [risk summarized in one sentence]
- **Probability:** [low|medium|high]
- **Impact:** [expected impact]
- **Mitigation:**
  - [mitigation action 1]
  - [mitigation action 2]
- **Contingency Plan:** [plan B if it goes wrong]

---

### Acceptance Criteria
Objective checklist defining if the feature is done.

- [criterion 1]
- [criterion 2]
- [criterion 3]

---

### Testing and Validation

Mandatory Test Types
- [test type 1]
- [test type 2]

Validation Strategy
- [e.g., TDD for critical logic, manual QA guided by script, exploratory validation with real data]
