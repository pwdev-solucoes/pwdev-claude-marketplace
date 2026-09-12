"""Render the allowlisted PWDEV QA report model as static offline HTML."""

from __future__ import annotations

from html import escape
from typing import Any, Dict, Iterable, List, Mapping
from urllib.parse import quote


_STATUS_CLASSES = {
    "PASS": "status-pass",
    "FAIL": "status-fail",
    "BLOCKED": "status-blocked",
    "NOT_RUN": "status-not-run",
    "NOT_APPLICABLE": "status-not-applicable",
}


def _text(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return escape(str(value), quote=True)


def _status(value: Any) -> str:
    raw = str(value)
    css_class = _STATUS_CLASSES.get(raw, "status-unknown")
    return '<span class="status {}">{}</span>'.format(css_class, _text(value))


def _join(values: Iterable[Any]) -> str:
    rendered = [_text(value) for value in values]
    return ", ".join(rendered) if rendered else "—"


def _definition_rows(rows: Iterable[tuple]) -> str:
    return "".join(
        "<div><dt>{}</dt><dd>{}</dd></div>".format(_text(label), value)
        for label, value in rows
    )


def _approved_evidence_refs(
    identifiers: Iterable[Any], evidence_anchors: Mapping[str, str]
) -> str:
    links: List[str] = []
    for identifier in identifiers:
        anchor = evidence_anchors.get(str(identifier))
        if anchor is not None:
            links.append('<a href="#{}">{}</a>'.format(anchor, _text(identifier)))
    return ", ".join(links) if links else "—"


def render_html(report: dict) -> str:
    """Return one UTF-8, self-contained HTML projection of ``build_report`` output.

    The renderer intentionally reads only the public allowlist produced by
    ``qa_verdict.build_report``. It does not execute commands, inspect evidence, or
    recalculate criterion results and the global verdict.
    """

    criteria = report["criteria"]
    criterion_results = {
        item["id"]: item["result"] for item in report["criterion_results"]
    }
    cases = report["cases"]
    defects = report["defects"]
    evidence = report["verified_evidence"]
    diagnostics = report["diagnostics"]
    counts = report["counts"]
    target = report["target"]
    contract = report["contract"]
    review = contract["criteria_review"]

    criterion_anchors = {
        str(item["id"]): "criterion-{}".format(index)
        for index, item in enumerate(criteria, 1)
    }
    case_anchors = {
        str(item["id"]): "case-{}".format(index)
        for index, item in enumerate(cases, 1)
    }
    logical_case_anchors = {
        str(item["case_id"]): "case-{}".format(index)
        for index, item in enumerate(cases, 1)
    }
    evidence_anchors = {
        str(item["id"]): "evidence-{}".format(index)
        for index, item in enumerate(evidence, 1)
    }

    summary = _definition_rows(
        (
            ("Run ID", _text(report["run_id"])),
            ("Project", _text(report["project"])),
            ("Target ID", _text(target["id"])),
            ("Target kind", _text(target["kind"])),
            ("Executed at", _text(report["executed_at"])),
            ("Schema version", _text(report["schema_version"])),
            ("Contract path", _text(contract["path"])),
            ("Contract SHA-256", _text(contract["sha256"])),
            ("Criteria review actor", _text(review["actor"])),
            ("Criteria reviewed at", _text(review["at"])),
            ("Criteria review complete", _text(review["complete"])),
        )
    )
    count_items = "".join(
        "<li><span>{}</span><strong>{}</strong></li>".format(
            _text(label.replace("_", " ")), _text(counts[label])
        )
        for label in (
            "criteria_total",
            "criteria_applicable",
            "criteria_pass",
            "criteria_fail",
            "criteria_blocked",
            "criteria_not_run",
            "criteria_not_applicable",
            "cases_total",
            "cases_terminal",
            "defects_total",
            "defects_current_in_scope",
            "defects_out_of_scope",
            "evidence_verified",
            "evidence_blocked",
        )
    )

    criterion_rows = []
    for index, item in enumerate(criteria, 1):
        assessment = item["assessment"]
        case_links = []
        for identifier in item["case_ids"]:
            anchor = logical_case_anchors.get(str(identifier))
            if anchor is None:
                case_links.append(_text(identifier))
            else:
                case_links.append(
                    '<a href="#{}">{}</a>'.format(anchor, _text(identifier))
                )
        criterion_rows.append(
            """<tr id="criterion-{index}">
<td>{identifier}</td><td>{criterion_text}</td><td>{applicable}</td>
<td>{reason}</td><td>{cases}</td><td>{expected}</td><td>{observed}</td>
<td>{actor}<br><small>{at}</small></td><td>{result}</td></tr>""".format(
                index=index,
                identifier=_text(item["id"]),
                criterion_text=_text(item["text"]),
                applicable=_text(item["applicable"]),
                reason=_text(item["applicability_reason"]),
                cases=", ".join(case_links) if case_links else "—",
                expected=_text(assessment["expected"]),
                observed=_text(assessment["observed"]),
                actor=_text(assessment["actor"]),
                at=_text(assessment["at"]),
                result=_status(criterion_results[item["id"]]),
            )
        )
    criteria_body = "".join(criterion_rows)
    if not criterion_rows:
        criteria_body = '<tr><td colspan="9" class="empty">No criteria.</td></tr>'

    case_cards = []
    for index, item in enumerate(cases, 1):
        criterion_links = []
        for identifier in item["criterion_ids"]:
            anchor = criterion_anchors.get(str(identifier))
            if anchor is None:
                criterion_links.append(_text(identifier))
            else:
                criterion_links.append(
                    '<a href="#{}">{}</a>'.format(anchor, _text(identifier))
                )
        predecessor = item["supersedes"]
        predecessor_anchor = case_anchors.get(str(predecessor))
        if predecessor is not None and predecessor_anchor is not None:
            supersedes = '<a href="#{}">{}</a>'.format(
                predecessor_anchor, _text(predecessor)
            )
        else:
            supersedes = _text(predecessor)
        rows = _definition_rows(
            (
                ("Attempt ID", _text(item["id"])),
                ("Logical case ID", _text(item["case_id"])),
                ("Criterion IDs", ", ".join(criterion_links) if criterion_links else "—"),
                ("Status", _status(item["status"])),
                ("Required", _text(item["required"])),
                ("Expected", _text(item["expected"])),
                ("Observed", _text(item["observed"])),
                ("Command (inert)", '<code>{}</code>'.format(_text(item["command"]))),
                ("Exit code", _text(item["exit_code"])),
                (
                    "Approved evidence IDs",
                    _approved_evidence_refs(item["evidence_ids"], evidence_anchors),
                ),
                ("Attempt", _text(item["attempt"])),
                ("Supersedes", supersedes),
            )
        )
        case_cards.append(
            '<article class="card" id="case-{}"><h3>Case {}</h3><dl>{}</dl></article>'.format(
                index, index, rows
            )
        )
    cases_body = "".join(case_cards) or '<p class="empty">No cases or attempts.</p>'

    defect_cards = []
    for index, item in enumerate(defects, 1):
        retest = item["retest_attempt_id"]
        retest_anchor = case_anchors.get(str(retest))
        retest_value = (
            '<a href="#{}">{}</a>'.format(retest_anchor, _text(retest))
            if retest is not None and retest_anchor is not None
            else _text(retest)
        )
        rows = _definition_rows(
            (
                ("Defect ID", _text(item["id"])),
                ("Summary", _text(item["summary"])),
                ("In scope", _text(item["in_scope"])),
                ("Status", _text(item["status"])),
                ("Severity", _text(item["severity"])),
                ("Criterion IDs", _join(item["criterion_ids"])),
                (
                    "Approved evidence IDs",
                    _approved_evidence_refs(item["evidence_ids"], evidence_anchors),
                ),
                ("Supersedes", _text(item["supersedes"])),
                ("Retest attempt ID", retest_value),
            )
        )
        defect_cards.append(
            '<article class="card" id="defect-{}"><h3>Defect {}</h3><dl>{}</dl></article>'.format(
                index, index, rows
            )
        )
    defects_body = "".join(defect_cards) or '<p class="empty">No defects.</p>'

    evidence_rows = []
    for index, item in enumerate(evidence, 1):
        item_contract = item["contract"]
        local_href = "./" + quote(str(item["path"]), safe="/")
        evidence_rows.append(
            """<tr id="evidence-{index}"><td>{identifier}</td>
<td><a href="{href}">{path}</a></td><td>{media_type}</td><td>{size}</td>
<td><code>{digest}</code></td><td>{target}</td><td>{contract_path}</td>
<td><code>{contract_digest}</code></td><td>{status}</td><td>{copy_allowed}</td>
<td>{revalidation}</td><td>{diagnostic}</td></tr>""".format(
                index=index,
                identifier=_text(item["id"]),
                href=escape(local_href, quote=True),
                path=_text(item["path"]),
                media_type=_text(item["media_type"]),
                size=_text(item["size_bytes"]),
                digest=_text(item["sha256"]),
                target=_text(item["target_id"]),
                contract_path=_text(item_contract["path"]),
                contract_digest=_text(item_contract["sha256"]),
                status=_text(item["status"]),
                copy_allowed=_text(item["copy_allowed"]),
                revalidation=_text(item["requires_copy_revalidation"]),
                diagnostic=_text(item["diagnostic"]),
            )
        )
    evidence_body = "".join(evidence_rows)
    if not evidence_rows:
        evidence_body = '<tr><td colspan="12" class="empty">No approved evidence.</td></tr>'

    diagnostics_body = "".join(
        "<li>{}</li>".format(_text(item)) for item in diagnostics
    ) or '<li class="empty">No diagnostics.</li>'

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PWDEV QA report</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; line-height: 1.45; }}
body {{ margin: 0 auto; max-width: 112rem; padding: 2rem; color: #172033; background: #f7f8fa; }}
h1, h2, h3 {{ line-height: 1.2; }} h2 {{ border-bottom: 2px solid #d8deea; padding-bottom: .4rem; }}
nav ul, .counts {{ display: flex; flex-wrap: wrap; gap: .65rem 1rem; padding: 0; list-style: none; }}
a {{ color: #174ea6; }} section {{ margin-top: 2rem; scroll-margin-top: 1rem; }}
.panel, .card {{ background: white; border: 1px solid #d8deea; border-radius: .45rem; padding: 1rem; }}
.cards {{ display: grid; gap: 1rem; }} dl {{ margin: 0; }} dl div {{ display: grid; grid-template-columns: minmax(10rem, 15rem) 1fr; gap: 1rem; padding: .3rem 0; }}
dt {{ font-weight: 700; }} dd {{ margin: 0; overflow-wrap: anywhere; }}
.table-wrap {{ overflow-x: auto; background: white; border: 1px solid #d8deea; }}
table {{ border-collapse: collapse; width: 100%; }} th, td {{ border-bottom: 1px solid #d8deea; padding: .65rem; text-align: left; vertical-align: top; overflow-wrap: anywhere; }}
th {{ background: #edf1f7; }} code {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
.status {{ border: 1px solid currentColor; border-radius: 1rem; display: inline-block; font-weight: 800; padding: .1rem .55rem; }}
.status-pass {{ color: #176b3a; }} .status-fail {{ color: #a52020; }} .status-blocked {{ color: #8a5600; }}
.status-not-run, .status-not-applicable, .status-unknown {{ color: #4c566a; }}
.counts li {{ background: white; border: 1px solid #d8deea; padding: .5rem .7rem; }}
.counts strong {{ margin-left: .5rem; }} .empty {{ color: #596579; font-style: italic; }}
@media print {{ body {{ background: white; padding: 0; }} nav {{ display: none; }} section {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<header><h1>PWDEV QA report</h1><p>Static offline report. Stored commands are inert text.</p></header>
<nav aria-label="Report sections"><ul>
<li><a href="#section-summary">Summary</a></li><li><a href="#section-criteria">Criteria</a></li>
<li><a href="#section-cases">Cases</a></li><li><a href="#section-defects">Defects</a></li>
<li><a href="#section-evidence">Evidence</a></li><li><a href="#section-diagnostics">Diagnostics</a></li>
<li><a href="#section-verdict">Verdict</a></li></ul></nav>
<main>
<section id="section-summary"><h2>Summary</h2><div class="panel"><dl>{summary}</dl></div><ul class="counts">{counts}</ul></section>
<section id="section-criteria"><h2>Acceptance criteria matrix</h2><div class="table-wrap"><table><thead><tr>
<th>ID</th><th>Text</th><th>Applicable</th><th>Reason</th><th>Cases</th><th>Expected</th><th>Observed</th><th>Assessment</th><th>Result</th>
</tr></thead><tbody>{criteria}</tbody></table></div></section>
<section id="section-cases"><h2>Cases and attempts</h2><div class="cards">{cases}</div></section>
<section id="section-defects"><h2>Defects</h2><div class="cards">{defects}</div></section>
<section id="section-evidence"><h2>Approved evidence</h2><div class="table-wrap"><table><thead><tr>
<th>ID</th><th>Path</th><th>Type</th><th>Bytes</th><th>SHA-256</th><th>Target</th><th>Contract</th><th>Contract SHA-256</th><th>Status</th><th>Copy allowed</th><th>Revalidation required</th><th>Diagnostic</th>
</tr></thead><tbody>{evidence}</tbody></table></div></section>
<section id="section-diagnostics"><h2>Diagnostics</h2><ul class="panel">{diagnostics}</ul></section>
<section id="section-verdict"><h2>Verdict</h2><div class="panel"><p>{verdict}</p></div></section>
</main>
</body>
</html>
""".format(
        summary=summary,
        counts=count_items,
        criteria=criteria_body,
        cases=cases_body,
        defects=defects_body,
        evidence=evidence_body,
        diagnostics=diagnostics_body,
        verdict=_status(report["verdict"]),
    )
