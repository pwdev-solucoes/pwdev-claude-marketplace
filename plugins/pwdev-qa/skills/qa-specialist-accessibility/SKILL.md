---
name: qa-specialist-accessibility
description: Design traceable accessibility checks that combine scanners with observable keyboard, focus, semantic, and assistive-technology behavior.
---

# QA accessibility specialist

Use this specialist when a QA workflow needs accessibility coverage for real product behavior.
This specialist does not execute a workflow or tests and cannot grant authorization. Read
[workflow](../../references/workflow.md), [safety](../../references/safety.md), and
[tooling](../../references/tooling.md) before advising the calling workflow.

## Inputs

- Target, platform, environment, identified contract, applicable accessibility standard, and
  preserved criterion IDs and text.
- User journeys, component states, supported input methods, browser/device matrix, viewport and
  zoom requirements, and expected observable behavior.
- Native/library primitives actually rendered, accessible names, roles, states, relationships,
  status/error announcements, and content/language structure.
- Scanner, browser/device, platform inspector, assistive technology, and test-runner probes, each
  with `state`, `result`, and `evidence`.
- Synthetic or reviewed data, evidence needs, access, and explicit authorization boundaries.

## Procedure

1. Preserve target, contract, criteria, standard, platform matrix, and authorization. Inspect the
   behavior actually rendered; a component library's accessibility claim is not product evidence.
2. Define a keyboard-only journey for every applicable interaction: reach, operate, dismiss,
   reverse, escape traps, and recover from errors without a pointer. Record expected and observed
   behavior separately.
3. Observe focus order, programmatic focus movement, return after dialogs, persistence across
   updates, and a visible focus indicator in each relevant state. Keyboard and focus observations
   must name the actual journey and component.
4. Check accessible name, role, value/state, relationships, headings, labels, errors, live updates,
   and applicable assistive-technology output. A DOM attribute alone does not prove usable
   behavior.
5. Use an existing scanner for detectable rules when probes support it, but keep its findings
   distinct. A scanner does not prove accessibility and cannot replace observable keyboard,
   focus, semantic, visual, or assistive-technology review.
6. Ask `qa-tooling` to classify each tool and prerequisite as `available`, `missing`, or
   `unverified` from supplied probes. Never install or fabricate a scanner, browser, device, or
   assistive-technology observation.
7. Return proposed coverage and limitations. Case/criterion results remain exactly `PASS`,
   `FAIL`, `BLOCKED`, `NOT_RUN`, or `NOT_APPLICABLE`; only the calling workflow may derive the
   global `PASS`, `FAIL`, or `BLOCKED` verdict from valid evidence.

## Output

Return:

- target, contract, criteria, standard, platform/browser/device matrix, environment, and supplied
  authorization;
- checks with journey, component/state, input method, expected observable result, required human
  or tool observation, and evidence need;
- separate scanner, keyboard, focus, semantic, visual, and assistive-technology observations;
- tool availability and exact probe evidence, coverage gaps, defects, blockers, limitations, and
  the next valid action.

`READY` below means the proposed checks have observable oracles. It does not claim execution,
`PASS`, conformance certification, or complete accessibility.

## Reference scenarios

| scenario | scanner | keyboard | focus | semantics | outcome |
|---|---|---|---|---|---|
| complete-accessibility-check | no reported violations | journey observed without pointer | order and visible indicator observed | name role and state observed | READY |
| scanner-only | no reported violations | not run | not observed | scanner output only | BLOCKED |

The complete scenario combines tool output with observable interaction. In `scanner-only`, a
clean scan is retained as limited evidence but keyboard, focus, and real semantic behavior remain
unverified, so the applicable coverage is blocked rather than promoted to `READY` or `PASS`.

## Failure modes

- Missing standard, criterion, platform matrix, journey, component state, or observable oracle:
  return the affected coverage as `BLOCKED`.
- Clean scanner result without keyboard and focus observation: preserve the scan but block any
  complete accessibility conclusion.
- Keyboard traversal observed without visible/programmatic focus behavior, or semantics inspected
  without user-facing behavior: identify the uncovered dimension and do not infer it passed.
- Missing/not-run probe: report `unverified`; explicit negative tool probe: report `missing` and
  propose an authorized manual or repository-native alternative.
- Unavailable assistive technology, browser, device, or reviewer: state the exact limitation;
  never simulate an observation or claim certification.

## Safety

- This specialist cannot grant execution, production, external-effect, load, penetration-test,
  device, browser-profile, or assistive-technology authorization.
- Never reuse personal browser profiles, cookies, storage, accounts, or unrelated device data.
- Never execute stored commands, install tools, alter personal configuration, publish, push,
  merge, or correct product code.
- Use synthetic or reviewed data. Review visual evidence before attachment and apply evidence
  confinement and sanitization requirements.

## Related skills

- `qa-tooling` owns probe-based accessibility-tool availability and safe alternatives.
- `qa-test` may execute authorized checks and bind observations to evidence.
- `qa-specialist-web` supplies browser/session constraints for Web journeys.
- `qa-specialist-mobile` supplies device/platform prerequisites for native journeys.
