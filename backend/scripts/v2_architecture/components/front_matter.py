"""
Front matter pages filled from the templates cut out of the reference report
(see tools/extract_reference_templates.py). Each template carries {{TOKENS}} inside
single runs, so filling them keeps the reference layout, borders and logos untouched.
"""

import copy
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from .base import BaseSectionGenerator
from .report_format import add_toc_entry, _set_run_font

TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")

SEMESTER_WORDS = {
    "1": "First", "2": "Second", "3": "Third", "4": "Fourth",
    "5": "Fifth", "6": "Sixth", "7": "Seventh", "8": "Eighth",
    "I": "First", "II": "Second", "III": "Third", "IV": "Fourth",
    "V": "Fifth", "VI": "Sixth", "VII": "Seventh", "VIII": "Eighth",
}


def academic_year(value):
    """'2026-27', '2026 - 2027', '2026–2027' -> '2026 - 2027'."""
    m = re.search(r"(\d{4})\s*[-–—/]\s*(\d{2,4})", value or "")
    if not m:
        return (value or "").strip()
    start, end = m.group(1), m.group(2)
    if len(end) == 2:
        end = start[:2] + end
    return f"{start} - {end}"


def semester_word(value):
    v = (value or "").strip()
    return SEMESTER_WORDS.get(v.upper().replace("TH", "").replace("SEM", "").strip(), v.title() or "Eighth")


def pronoun(name):
    """Pronoun for the acknowledgement, only when the honorific states it; otherwise neutral."""
    n = (name or "").strip().lower()
    if re.match(r"^(mrs|ms|miss)\b", n):
        return "her"
    if re.match(r"^mr\b", n):
        return "his"
    return "their"


def strip_department_prefix(name):
    return re.sub(r"^\s*(the\s+)?department\s+of\s+", "", name or "", flags=re.I).strip()


def build_values(context):
    """All token values for the front matter, derived from the request data."""
    data = context.data
    meta = data.get("global_metadata", {})
    cert = data.get("certificate_info", {})
    people = data.get("people", {})
    approvers = people.get("approvers", {})
    report_type = context.report_type

    abbr = (meta.get("department_abbr") or "CSE").strip()
    department = strip_department_prefix(meta.get("department_name")) or "Computer Science and Engineering"

    guides = people.get("guide") or []
    guide = guides[0] if guides else {}
    guide_name = guide.get("name") or cert.get("guide_name") or "[GUIDE NAME]"
    guide_designation = guide.get("designation") or (cert.get("guide_designation") or "").split("\n")[0] or "[DESIGNATION]"
    guide_department = guide.get("department") or f"Department of {abbr}"

    hod = approvers.get("hod", {})
    hod_name = cert.get("hod_name") or hod.get("name") or "[HOD NAME]"
    hod_designation = (cert.get("hod_designation") or hod.get("designation") or "Professor & Head").split("\n")[0]

    dean = approvers.get("dean", {})
    dean_name = cert.get("dean_name") or dean.get("name") or "[DEAN NAME]"
    dean_school = dean.get("school") or f"School of {abbr}"
    dean_lines = [l.strip() for l in (cert.get("dean_designation") or "").split("\n") if l.strip()]
    if not dean_lines or dean_lines == ["Dean"]:
        dean_lines = [f"Dean, {dean_school}", "MVJCE"]

    principal_name = approvers.get("principal", {}).get("name") or "[PRINCIPAL NAME]"
    coe_name = approvers.get("COE", {}).get("name") or "[COE NAME]"

    return {
        "REPORT_NAME": report_type["report_name"],
        "REPORT_NAME_UPPER": report_type["report_name_upper"],
        "REPORT_CATEGORY": report_type["report_category"],
        "PROJECT_TITLE": (meta.get("project_title") or "PROJECT TITLE").upper(),
        "DEPARTMENT": department,
        "DEPARTMENT_UPPER": department.upper(),
        "DEPARTMENT_ABBR": abbr,
        "ACADEMIC_YEAR": academic_year(meta.get("academic_year")),
        "SEMESTER": semester_word(meta.get("semester")),
        "CITY_CODE": (meta.get("city_code") or "BANGALORE - 67").upper(),
        "PLACE": (data.get("submission_info", {}).get("place") or "BANGALORE").upper(),
        "GUIDE_NAME": guide_name,
        "GUIDE_DESIGNATION": guide_designation,
        "GUIDE_DEPARTMENT": guide_department,
        "GUIDE_PRONOUN": pronoun(guide_name),
        "HOD_NAME": hod_name,
        "HOD_PRONOUN": pronoun(hod_name),
        "DEAN_NAME": dean_name,
        "DEAN_SCHOOL": dean_school,
        "DEAN_PRONOUN": pronoun(dean_name),
        "PRINCIPAL_NAME": principal_name,
        "PRINCIPAL_PRONOUN": pronoun(principal_name),
        "COE_NAME": coe_name,
        "COE_PRONOUN": pronoun(coe_name),
        # Signature blocks on the certificate (one line each)
        "_SIG_GUIDE": ["Signature of Guide", guide_name, guide_designation, guide_department],
        "_SIG_HOD": ["Signature of HOD", hod_name, hod_designation, f"Department of {abbr}"],
        "_SIG_DEAN": ["Signature of Dean", dean_name, *dean_lines],
    }


def students(context):
    return [s for s in context.data.get("people", {}).get("students", []) if s.get("name") or s.get("usn")]


def fill_tokens(element, values):
    for t in element.iter(qn("w:t")):
        if t.text and "{{" in t.text:
            t.text = TOKEN.sub(lambda m: str(values.get(m.group(1), m.group(0))), t.text)


def paragraph_with(element, marker):
    for p in element.iter(qn("w:p")):
        if marker in "".join(t.text or "" for t in p.iter(qn("w:t"))):
            return p
    return None


class TemplatePageGenerator(BaseSectionGenerator):
    TEMPLATE = None

    def generate(self) -> Document:
        doc = Document(os.path.join(self.context.report_templates_dir, self.TEMPLATE))
        self.values = build_values(self.context)
        self.prepare(doc)
        fill_tokens(doc.element.body, self.values)
        return doc

    def prepare(self, doc):
        pass


class FrontPageGenerator(TemplatePageGenerator):
    TEMPLATE = "front_page.docx"

    def prepare(self, doc):
        proto = next(tr for tr in doc.element.body.iter(qn("w:tr"))
                     if "{{STUDENT_USN}}" in "".join(t.text or "" for t in tr.iter(qn("w:t"))))
        anchor = proto
        for stud in students(self.context) or [{"usn": "[USN]", "name": "[STUDENT NAME]"}]:
            row = copy.deepcopy(proto)
            fill_tokens(row, {"STUDENT_USN": stud.get("usn", "").upper(), "STUDENT_NAME": stud.get("name", "").upper()})
            anchor.addnext(row)
            anchor = row
        proto.getparent().remove(proto)


class CertificateGenerator(TemplatePageGenerator):
    TEMPLATE = "certificate.docx"

    def prepare(self, doc):
        for marker in ("SIG_GUIDE", "SIG_HOD", "SIG_DEAN"):
            p = paragraph_with(doc.element.body, "{{%s}}" % marker)
            if p is None:
                continue
            self._signature_line(p.getparent())
            lines = self.values["_" + marker]
            anchor = p
            for i, line in enumerate(lines):
                new_p = copy.deepcopy(p)
                fill_tokens(new_p, {marker: line})
                pPr = new_p.find(qn("w:pPr"))
                if pPr is not None:
                    spacing = pPr.find(qn("w:spacing"))
                    if spacing is not None and i > 0:
                        spacing.set(qn("w:before"), "0")
                    # The converted reference's indents make the narrow guide cell wrap every word
                    for old in pPr.findall(qn("w:ind")) + pPr.findall(qn("w:jc")):
                        pPr.remove(old)
                    jc = OxmlElement("w:jc")
                    jc.set(qn("w:val"), "center")
                    rpr = pPr.find(qn("w:rPr"))
                    (rpr.addprevious if rpr is not None else pPr.append)(jc)
                anchor.addnext(new_p)
                anchor = new_p
            p.getparent().remove(p)

    @staticmethod
    def _signature_line(tc):
        """Top border on a signature cell (the line the signature goes on)."""
        if tc.tag != qn("w:tc"):
            return
        tcPr = tc.find(qn("w:tcPr"))
        if tcPr is None:
            tcPr = OxmlElement("w:tcPr")
            tc.insert(0, tcPr)
        if tcPr.find(qn("w:tcBorders")) is not None:
            return
        borders = OxmlElement("w:tcBorders")
        top = OxmlElement("w:top")
        for k, v in (("w:val", "single"), ("w:color", "000000"), ("w:sz", "4"), ("w:space", "0")):
            top.set(qn(k), v)
        borders.append(top)
        tcW = tcPr.find(qn("w:tcW"))
        (tcW.addnext if tcW is not None else tcPr.append)(borders)


class DeclarationGenerator(TemplatePageGenerator):
    TEMPLATE = "declaration.docx"

    def prepare(self, doc):
        marker = paragraph_with(doc.element.body, "{{STUDENT_TABLE}}")
        if marker is None:
            return
        rows = students(self.context) or [{"usn": "[USN]", "name": "[STUDENT NAME]"}]
        table = doc.add_table(rows=len(rows), cols=3)
        widths = (Inches(1.75), Inches(2.85), Inches(1.6))
        for i, stud in enumerate(rows):
            for j, text in enumerate((stud.get("usn", "").upper(), stud.get("name", "").upper(), "_" * 22)):
                cell = table.cell(i, j)
                cell.width = widths[j]
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                _set_run_font(p.add_run(text), 12, j < 2)
        tblPr = table._tbl.tblPr
        indent = OxmlElement("w:tblInd")
        indent.set(qn("w:w"), "115")
        indent.set(qn("w:type"), "dxa")
        tblPr.append(indent)
        marker.addprevious(table._tbl)
        marker.getparent().remove(marker)


class AcknowledgementGenerator(TemplatePageGenerator):
    TEMPLATE = "acknowledgement.docx"

    def prepare(self, doc):
        for p in doc.paragraphs:
            if p.text.strip().upper() == "ACKNOWLEDGEMENT":
                add_toc_entry(p, "ACKNOWLEDGEMENT", 1)
                self.context.toc_entries.append(("ACKNOWLEDGEMENT", 1))
                break
