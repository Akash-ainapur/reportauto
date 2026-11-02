"""
Cut the fixed pages (front page, certificate, declaration, acknowledgement) out of a
department-approved reference report and turn them into token templates.

Every real value in the reference (title, names, USNs, years...) is swapped for a
{{TOKEN}} kept inside a single run, so the generator can fill it without touching the
layout, borders or logos. Run once per reference / report type:

    python extract_reference_templates.py "Project phase 2 Report_updated.docx" major_project_phase2

Each report type keeps its own replacement map in REFERENCE_MAPS below.
"""

import argparse
import copy
import os
import sys

from docx import Document
from docx.oxml.ns import qn

TEMPLATES_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "templates", "report_types"
)

# Per page: (section index in the reference, output file, [(old text, token), ...]).
# Replacements run on every paragraph of the page (body, tables, text boxes) in order.
REFERENCE_MAPS = {
    "major_project_phase2": [
        (0, "front_page.docx", [
            ("PROJECT PHASE II", "{{REPORT_NAME_UPPER}}"),
            ("HAZARD WASTE DETECTION USING AI AND IOT", "{{PROJECT_TITLE}}"),
            ("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", "DEPARTMENT OF {{DEPARTMENT_UPPER}}"),
            ("COMPUTER SCIENCE & ENGINEERING", "{{DEPARTMENT_UPPER}}"),
            ("Mrs. Poshitha M", "{{GUIDE_NAME}}"),
            ("Assistant Professor, Department of CSE", "{{GUIDE_DESIGNATION}}, {{GUIDE_DEPARTMENT}}"),
            ("BANGALORE - 67", "{{CITY_CODE}}"),
            ("2026 - 2027", "{{ACADEMIC_YEAR}}"),
            ("1MJ21CS007", "{{STUDENT_USN}}"),
            ("ADITYA POLICE PATIL", "{{STUDENT_NAME}}"),
        ]),
        (1, "certificate.docx", [
            ("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", "DEPARTMENT OF {{DEPARTMENT_UPPER}}"),
            ("Project Phase II", "{{REPORT_NAME}}"),
            ("HAZARD WASTE DETECTION USING AI AND IOT", "{{PROJECT_TITLE}}"),
            ("Computer science and Engineering", "{{DEPARTMENT}}"),
            ("2026 - 2027", "{{ACADEMIC_YEAR}}"),
            ("major project", "{{REPORT_CATEGORY}}"),
            ("Project Phase II", "{{REPORT_NAME}}"),
            ("major project", "{{REPORT_CATEGORY}}"),
        ]),
        (2, "declaration.docx", [
            ("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", "DEPARTMENT OF {{DEPARTMENT_UPPER}}"),
            ("Eighth", "{{SEMESTER}}"),
            ("Computer science and Engineering", "{{DEPARTMENT}}"),
            ("Computer science and Engineering", "{{DEPARTMENT}}"),
            ("Project Phase II", "{{REPORT_NAME}}"),
            ("HAZARD WASTE DETECTION USING AI AND IOT", "{{PROJECT_TITLE}}"),
            ("2026 - 2027", "{{ACADEMIC_YEAR}}"),
            ("BANGALORE", "{{PLACE}}"),
        ]),
        (3, "acknowledgement.docx", [
            ("Dr. Ajayan K R, Principal of MVJCE ", "{{PRINCIPAL_NAME}}, Principal of MVJCE "),
            ("for his encouragement and support throughout the project work.", "for {{PRINCIPAL_PRONOUN}} encouragement and support throughout the project work."),
            ("Dr. Salim A, Dean, School of CSE, MVJCE ", "{{DEAN_NAME}}, Dean, {{DEAN_SCHOOL}}, MVJCE "),
            ("for his encouragement and support throughout the project work.", "for {{DEAN_PRONOUN}} encouragement and support throughout the project work."),
            ("Dr. Kumar R, Controller Of Examinations ", "{{COE_NAME}}, Controller Of Examinations "),
            ("for his encouragement and support throughout the project work.", "for {{COE_PRONOUN}} encouragement and support throughout the project work."),
            ("Dr. J Maruthu Pandi, HOD, CSE Department ", "{{HOD_NAME}}, HOD, {{DEPARTMENT_ABBR}} Department "),
            ("for his incessant encouragement", "for {{HOD_PRONOUN}} incessant encouragement"),
            ("Mrs. Poshitha M, Assistant Professor, CSE Department ", "{{GUIDE_NAME}}, {{GUIDE_DESIGNATION}}, {{DEPARTMENT_ABBR}} Department "),
            ("for her valuable guidance", "for {{GUIDE_PRONOUN}} valuable guidance"),
        ]),
    ],
}


def _direct_runs(p):
    runs = []
    for child in p:
        if child.tag == qn("w:r"):
            runs.append(child)
        elif child.tag == qn("w:hyperlink"):
            runs.extend(child.findall(qn("w:r")))
    return runs


def _run_text(r):
    return "".join(t.text or "" for t in r.findall(qn("w:t")))


def _set_run_text(r, text):
    ts = r.findall(qn("w:t"))
    if not ts:
        t = r.makeelement(qn("w:t"), {})
        r.append(t)
        ts = [t]
    ts[0].text = text
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for extra in ts[1:]:
        r.remove(extra)


def replace_once(p, old, new):
    """Replace the first `old` in paragraph `p` (spanning runs) with `new`, placed in the
    run where the match starts so it keeps that run's formatting. Returns True if replaced."""
    runs = [r for r in _direct_runs(p) if r.find(qn("w:t")) is not None]
    texts = [_run_text(r) for r in runs]
    full = "".join(texts)
    start = full.find(old)
    if start == -1:
        return False
    end = start + len(old)
    pos = 0
    placed = False
    for r, t in zip(runs, texts):
        r_start, r_end = pos, pos + len(t)
        pos = r_end
        if r_end <= start or r_start >= end:
            continue
        keep_before = t[: max(0, start - r_start)]
        keep_after = t[end - r_start:] if end < r_end else ""
        if not placed:
            _set_run_text(r, keep_before + new + keep_after)
            placed = True
        else:
            _set_run_text(r, keep_after)
    return True


def _section_ranges(body):
    """Yield lists of body children per section (a section ends at a paragraph carrying sectPr)."""
    current = []
    for el in list(body):
        if el.tag == qn("w:sectPr"):
            continue
        current.append(el)
        if el.tag == qn("w:p") and el.find(qn("w:pPr") + "/" + qn("w:sectPr")) is not None:
            yield current
            current = []
    if current:
        yield current


def extract_section(ref_path, index):
    doc = Document(ref_path)
    body = doc.element.body
    sections = list(_section_ranges(body))
    keep = sections[index]
    keep_ids = set(id(e) for e in keep)
    for el in list(body):
        if el.tag != qn("w:sectPr") and id(el) not in keep_ids:
            body.remove(el)

    # The section's own properties become the document's final sectPr
    last_p = keep[-1]
    inner = last_p.find(qn("w:pPr") + "/" + qn("w:sectPr"))
    final = body.find(qn("w:sectPr"))
    if inner is not None:
        inner.getparent().remove(inner)
        new_final = copy.deepcopy(inner)
        if final is not None:
            body.remove(final)
        body.append(new_final)
        final = new_final
    # Headers/footers/page numbering are applied by the builder
    for tag in ("w:headerReference", "w:footerReference", "w:pgNumType"):
        for ref in final.findall(qn(tag)):
            final.remove(ref)
    return doc


def drop_unused_parts(doc):
    # PDF-to-Word conversions leave empty <v:imagedata/> stubs that make docxcompose fail
    vml_imagedata = "{urn:schemas-microsoft-com:vml}imagedata"
    rel_id = qn("r:id")
    for el in list(doc.element.body.iter(vml_imagedata)):
        if not el.get(rel_id):
            el.getparent().remove(el)

    xml = doc.element.xml
    part = doc.part
    for rId, rel in list(part.rels.items()):
        if rel.is_external:
            continue
        if any(k in rel.reltype for k in ("/image", "/header", "/footer")) and f'"{rId}"' not in xml:
            part.rels.pop(rId)


def tokenize(doc, replacements):
    paragraphs = list(doc.element.body.iter(qn("w:p")))
    missing = []
    for old, new in replacements:
        hit = False
        for p in paragraphs:
            if replace_once(p, old, new):
                hit = True
                break
        if not hit:
            missing.append(old)
    return missing


def first_cell_paragraph(tc):
    return tc.find(qn("w:p"))


def set_marker_paragraph(p, marker):
    runs = [r for r in _direct_runs(p) if r.find(qn("w:t")) is not None]
    if not runs:
        r = p.makeelement(qn("w:r"), {})
        p.append(r)
        runs = [r]
    _set_run_text(runs[0], marker)
    for r in runs[1:]:
        p.remove(r) if r.getparent() is p else r.getparent().remove(r)
    for r in _direct_runs(p):
        for br in r.findall(qn("w:br")):
            r.remove(br)


def postprocess_front_page(doc):
    # Keep one student row as the prototype the generator clones per student
    table = doc.tables[0]
    for row in table.rows[1:]:
        table._tbl.remove(row._tr)


def postprocess_certificate(doc):
    sig_table = next(t for t in doc.tables if "Signature of" in "".join(c.text for c in t.rows[0].cells))
    for tc, marker in ((sig_table.rows[0].cells[0]._tc, "{{SIG_GUIDE}}"),
                       (sig_table.rows[0].cells[2]._tc, "{{SIG_HOD}}"),
                       (sig_table.rows[0].cells[3]._tc, "{{SIG_DEAN}}")):
        paragraphs = tc.findall(qn("w:p"))
        target = next((p for p in paragraphs if "Signature" in "".join(_run_text(r) for r in _direct_runs(p))), paragraphs[0])
        set_marker_paragraph(target, marker)
        for p in paragraphs:
            if p is not target:
                tc.remove(p)


def postprocess_declaration(doc):
    # The student list is a floating text box plus three signature-line paragraphs;
    # replace the block with a marker the generator turns into a table.
    body = doc.element.body
    children = [c for c in body if c.tag == qn("w:p")]
    start = next(i for i, p in enumerate(children) if p.find(".//" + qn("w:txbxContent")) is not None)
    block = children[start:start + 4]
    for p in block[1:]:
        body.remove(p)
    marker = block[0]
    for r in list(marker):
        if r.tag != qn("w:pPr"):
            marker.remove(r)
    r = marker.makeelement(qn("w:r"), {})
    t = r.makeelement(qn("w:t"), {})
    t.text = "{{STUDENT_TABLE}}"
    r.append(t)
    marker.append(r)


POSTPROCESS = {
    "front_page.docx": postprocess_front_page,
    "certificate.docx": postprocess_certificate,
    "declaration.docx": postprocess_declaration,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("reference", help="Path to the reference .docx")
    parser.add_argument("report_type", choices=sorted(REFERENCE_MAPS))
    args = parser.parse_args()

    out_dir = os.path.abspath(os.path.join(TEMPLATES_ROOT, args.report_type))
    os.makedirs(out_dir, exist_ok=True)

    ok = True
    for index, filename, replacements in REFERENCE_MAPS[args.report_type]:
        doc = extract_section(args.reference, index)
        missing = tokenize(doc, replacements)
        if filename in POSTPROCESS:
            POSTPROCESS[filename](doc)
        drop_unused_parts(doc)
        path = os.path.join(out_dir, filename)
        doc.save(path)
        print(f"wrote {path} ({os.path.getsize(path) // 1024} KB)")
        if missing:
            ok = False
            print(f"  !! not found in reference: {missing}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
