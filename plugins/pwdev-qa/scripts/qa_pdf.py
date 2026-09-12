"""Render the allowlisted PWDEV QA report model as a paginated PDF."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape


_REPORTLAB_VERSION = "4.4.9"
_STATUS_VALUES = ("PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE")


def _reportlab():
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
        from reportlab.platypus import (
            BaseDocTemplate,
            Frame,
            HRFlowable,
            PageBreak,
            PageTemplate,
            Paragraph,
            Spacer,
        )
        from reportlab.platypus.tableofcontents import TableOfContents
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "reportlab==4.4.9 is required to export PWDEV QA PDF reports"
        ) from error
    if reportlab.Version != _REPORTLAB_VERSION:
        raise RuntimeError(
            "reportlab==4.4.9 is required to export PWDEV QA PDF reports "
            f"(found {reportlab.Version})"
        )
    return locals()


def _value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _markup(value: Any) -> str:
    return escape(_value(value), {'"': "&quot;", "'": "&#x27;"}).replace(
        "\n", "<br/>"
    )


def _joined(values: Iterable[Any]) -> str:
    rendered = [_value(value) for value in values]
    return ", ".join(rendered) if rendered else "—"


def render_pdf(report: dict, destination: Path) -> None:
    """Write the public ``build_report`` projection to ``destination``.

    The renderer never evaluates commands, opens evidence, or recalculates criterion
    results and the global verdict. ReportLab is loaded lazily so its absence produces
    an explicit export error rather than an import-time failure.
    """

    rl = _reportlab()
    reportlab = rl["reportlab"]
    colors = rl["colors"]
    A4 = rl["A4"]
    mm = rl["mm"]
    pdfmetrics = rl["pdfmetrics"]
    TTFont = rl["TTFont"]
    canvas = rl["canvas"]
    BaseDocTemplate = rl["BaseDocTemplate"]
    Frame = rl["Frame"]
    PageTemplate = rl["PageTemplate"]
    Paragraph = rl["Paragraph"]
    ParagraphStyle = rl["ParagraphStyle"]
    getSampleStyleSheet = rl["getSampleStyleSheet"]
    TableOfContents = rl["TableOfContents"]
    PageBreak = rl["PageBreak"]
    Spacer = rl["Spacer"]
    HRFlowable = rl["HRFlowable"]
    TA_CENTER = rl["TA_CENTER"]

    font_dir = Path(reportlab.__file__).resolve().parent / "fonts"
    regular_font = font_dir / "Vera.ttf"
    bold_font = font_dir / "VeraBd.ttf"
    if not regular_font.is_file() or not bold_font.is_file():
        raise RuntimeError("ReportLab embedded Unicode font files are unavailable")
    font_name = "PWDEV-Vera"
    bold_name = "PWDEV-Vera-Bold"
    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, regular_font))
    if bold_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(bold_name, bold_font))
    pdfmetrics.registerFontFamily(
        "PWDEV-Vera-Family", normal=font_name, bold=bold_name
    )

    margin = 18 * mm
    page_width, page_height = A4
    run_id = _value(report["run_id"])

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            page_count = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.setFont(font_name, 7.5)
                self.setFillColor(colors.HexColor("#526078"))
                self.drawString(margin, page_height - 11 * mm, "PWDEV QA report")
                self.drawRightString(
                    page_width - margin, page_height - 11 * mm, run_id
                )
                self.drawString(margin, 9 * mm, "Static offline report")
                self.drawRightString(
                    page_width - margin,
                    9 * mm,
                    f"Page {self._pageNumber} of {page_count}",
                )
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

    class ReportDocument(BaseDocTemplate):
        def __init__(self, filename):
            BaseDocTemplate.__init__(
                self,
                filename,
                pagesize=A4,
                leftMargin=margin,
                rightMargin=margin,
                topMargin=margin,
                bottomMargin=margin,
                title="PWDEV QA report",
                author="PWDEV QA",
            )
            frame = Frame(
                self.leftMargin,
                self.bottomMargin,
                self.width,
                self.height,
                id="content",
                leftPadding=0,
                rightPadding=0,
                topPadding=0,
                bottomPadding=0,
            )
            self.addPageTemplates(PageTemplate(id="report", frames=[frame]))
            self._heading_index = 0

        def beforeDocument(self):
            self._heading_index = 0

        def afterFlowable(self, flowable):
            if isinstance(flowable, Paragraph) and flowable.style.name == "Heading1":
                self._heading_index += 1
                key = f"section-{self._heading_index}"
                text = flowable.getPlainText()
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=0, closed=False)
                self.notify("TOCEntry", (0, text, self.page, key))

    sample = getSampleStyleSheet()
    normal = ParagraphStyle(
        "Body",
        parent=sample["BodyText"],
        fontName=font_name,
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#172033"),
        spaceAfter=3 * mm,
        splitLongWords=True,
    )
    label = ParagraphStyle(
        "Label",
        parent=normal,
        fontName=bold_name,
        spaceAfter=0.7 * mm,
        keepWithNext=True,
    )
    heading1 = ParagraphStyle(
        "Heading1",
        parent=sample["Heading1"],
        fontName=bold_name,
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#173b70"),
        spaceBefore=5 * mm,
        spaceAfter=3 * mm,
        keepWithNext=True,
    )
    heading2 = ParagraphStyle(
        "Heading2",
        parent=sample["Heading2"],
        fontName=bold_name,
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#263b5a"),
        spaceBefore=3 * mm,
        spaceAfter=2 * mm,
        keepWithNext=True,
    )
    title = ParagraphStyle(
        "Title",
        parent=sample["Title"],
        fontName=bold_name,
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#173b70"),
        spaceAfter=5 * mm,
    )
    status = ParagraphStyle(
        "Status",
        parent=normal,
        fontName=bold_name,
        borderColor=colors.HexColor("#70809a"),
        borderWidth=0.6,
        borderPadding=3,
        backColor=colors.HexColor("#edf1f7"),
    )
    toc_level = ParagraphStyle(
        "TOC",
        parent=normal,
        fontSize=9,
        leading=13,
        leftIndent=4 * mm,
        firstLineIndent=-4 * mm,
    )

    story = [
        Spacer(1, 20 * mm),
        Paragraph("PWDEV QA report", title),
        Paragraph(
            "Static offline report. Stored commands are inert text.",
            ParagraphStyle("Subtitle", parent=normal, alignment=TA_CENTER),
        ),
        Spacer(1, 10 * mm),
        Paragraph(f"<b>Run ID:</b> {_markup(report['run_id'])}", normal),
        Paragraph(f"<b>Project:</b> {_markup(report['project'])}", normal),
        Paragraph(f"<b>Verdict:</b> {_markup(report['verdict'])}", status),
        PageBreak(),
        Paragraph("Contents", heading1),
    ]
    toc = TableOfContents()
    toc.levelStyles = [toc_level]
    story.extend(
        [
            toc,
            Spacer(1, 6 * mm),
            Paragraph("Status legend", heading2),
            Paragraph(
                "PASS — approved; FAIL — proven current failure; BLOCKED — pending or "
                "insufficient evidence; NOT_RUN — not executed; NOT_APPLICABLE — explicitly "
                "outside the applicable scope.",
                normal,
            ),
            Paragraph("Textual labels: " + ", ".join(_STATUS_VALUES), status),
            PageBreak(),
        ]
    )

    def section(text: str) -> None:
        story.extend(
            [
                Paragraph(_markup(text), heading1),
                HRFlowable(
                    width="100%", thickness=0.7, color=colors.HexColor("#c5cedc")
                ),
                Spacer(1, 2 * mm),
            ]
        )

    def subsection(text: Any) -> None:
        story.append(Paragraph(_markup(text), heading2))

    def field(name: str, value: Any, *, style=normal) -> None:
        story.append(Paragraph(_markup(name), label))
        story.append(Paragraph(_markup(value), style))

    target = report["target"]
    contract = report["contract"]
    review = contract["criteria_review"]
    section("Summary")
    for name, value in (
        ("Run ID", report["run_id"]),
        ("Project", report["project"]),
        ("Target ID", target["id"]),
        ("Target kind", target["kind"]),
        ("Executed at", report["executed_at"]),
        ("Schema version", report["schema_version"]),
        ("Contract path", contract["path"]),
        ("Contract SHA-256", contract["sha256"]),
        ("Criteria review actor", review["actor"]),
        ("Criteria reviewed at", review["at"]),
        ("Criteria review complete", review["complete"]),
    ):
        field(name, value)
    subsection("Counts")
    for key, value in report["counts"].items():
        field(key.replace("_", " "), value)

    criterion_results = {
        item["id"]: item["result"] for item in report["criterion_results"]
    }
    approved_evidence_ids = {
        item["id"] for item in report["verified_evidence"]
    }

    def approved_references(identifiers: Iterable[Any]) -> str:
        return _joined(
            identifier
            for identifier in identifiers
            if identifier in approved_evidence_ids
        )

    section("Acceptance criteria")
    if not report["criteria"]:
        field("State", "No criteria.")
    for index, item in enumerate(report["criteria"], 1):
        assessment = item["assessment"]
        subsection(f"Criterion {index}: {item['id']}")
        for name, value in (
            ("ID", item["id"]),
            ("Text", item["text"]),
            ("Applicable", item["applicable"]),
            ("Applicability reason", item["applicability_reason"]),
            ("Logical case IDs", _joined(item["case_ids"])),
            ("Expected", assessment["expected"]),
            ("Observed", assessment["observed"]),
            ("Assessment actor", assessment["actor"]),
            ("Assessed at", assessment["at"]),
            ("Result", criterion_results[item["id"]]),
        ):
            field(name, value, style=status if name == "Result" else normal)

    section("Cases and attempts")
    if not report["cases"]:
        field("State", "No cases or attempts.")
    for index, item in enumerate(report["cases"], 1):
        subsection(f"Case {index}: {item['id']}")
        for name, value in (
            ("Attempt ID", item["id"]),
            ("Logical case ID", item["case_id"]),
            ("Criterion IDs", _joined(item["criterion_ids"])),
            ("Status", item["status"]),
            ("Required", item["required"]),
            ("Expected", item["expected"]),
            ("Observed", item["observed"]),
            ("Command (inert)", item["command"]),
            ("Exit code", item["exit_code"]),
            ("Approved evidence IDs", approved_references(item["evidence_ids"])),
            ("Attempt", item["attempt"]),
            ("Supersedes", item["supersedes"]),
        ):
            field(name, value, style=status if name == "Status" else normal)

    section("Defects")
    if not report["defects"]:
        field("State", "No defects.")
    for index, item in enumerate(report["defects"], 1):
        subsection(f"Defect {index}: {item['id']}")
        for name, value in (
            ("Defect ID", item["id"]),
            ("Summary", item["summary"]),
            ("In scope", item["in_scope"]),
            ("Status", item["status"]),
            ("Severity", item["severity"]),
            ("Criterion IDs", _joined(item["criterion_ids"])),
            ("Approved evidence IDs", approved_references(item["evidence_ids"])),
            ("Supersedes", item["supersedes"]),
            ("Retest attempt ID", item["retest_attempt_id"]),
        ):
            field(name, value)

    section("Approved evidence")
    if not report["verified_evidence"]:
        field("State", "No approved evidence.")
    for index, item in enumerate(report["verified_evidence"], 1):
        evidence_contract = item["contract"]
        subsection(f"Evidence {index}: {item['id']}")
        for name, value in (
            ("ID", item["id"]),
            ("Path", item["path"]),
            ("Media type", item["media_type"]),
            ("Size bytes", item["size_bytes"]),
            ("SHA-256", item["sha256"]),
            ("Target ID", item["target_id"]),
            ("Contract path", evidence_contract["path"]),
            ("Contract SHA-256", evidence_contract["sha256"]),
            ("Status", item["status"]),
            ("Copy allowed", item["copy_allowed"]),
            ("Revalidation required", item["requires_copy_revalidation"]),
            ("Diagnostic", item["diagnostic"]),
        ):
            field(name, value)

    section("Diagnostics")
    if not report["diagnostics"]:
        field("State", "No diagnostics.")
    for index, item in enumerate(report["diagnostics"], 1):
        field(f"Diagnostic {index}", item)

    section("Verdict")
    field("Global verdict", report["verdict"], style=status)

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        document = ReportDocument(str(temporary_path))
        document.multiBuild(story, canvasmaker=NumberedCanvas)
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
