from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
import re
import json


# ----------------------------
# Shared helper (same style)
# ----------------------------
def replace_text_runs(paragraph, old, new):
    """Replace text even if split across runs."""
    full_text = "".join(run.text for run in paragraph.runs)
    if old in full_text:
        new_text = full_text.replace(old, new)
        for run in paragraph.runs:
            run.text = ""
        paragraph.runs[0].text = new_text


# ----------------------------
# Certificate generator
# ----------------------------
def update_certificate_page(input_path):
    doc = Document(input_path)

    base, ext = os.path.splitext(input_path)
    output_path = base.replace(
        "senior_project_template",
        "senior_project_certificate_filled"
    ) + ext

    # ----------------------------
    # Load JSON (Single Source)
    # ----------------------------
    json_path = r"C:\\Users\\sumam\\OneDrive\\Documents\\ReportMaker\\reportauto\\backend\\data\\full_report_template.json"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON not found at: {json_path}")
        return

    meta = data["global_metadata"]
    guides = data["people"]["guides"][0]
    approvers = data["people"]["approvers"]

    hod = approvers["hod"]
    dean = approvers["dean"]

    # ----------------------------
    # Certificate text mapping
    # ----------------------------
    replacements = {
        # College details
        "MVJ COLLEGE OF ENGINEERING": meta["college_name"],
        "Near ITPB, Whitefield, Bangalore – 560067":
            f"Near ITPB, Whitefield, Bangalore – {meta['pincode']}",

        # Department
        "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING":
            meta["department_name"],

        # Project title
        "MVJ NEXTGEN EDUCLOUD:AI-BASED ACADEMIC RESOURCE MANAGER":
            meta["project_title"],

        # Academic year (handles various dash styles)
        "2024 - 2025": meta["academic_year"],

        # Project type
        "Major Project": "Mini Project",

        # Guide
        "Mrs. Sumanjali": guides["name"],

        # HOD
        "Dr. Kiran Babu T S": hod["name"],
        "Professor & Head": hod["designation"],

        # Dean
        "Dr. I Hameem Shanavas": dean["name"],
        "Dean": dean["designation"],
    }

    # ----------------------------
    # Replace paragraphs
    # ----------------------------
    for para in doc.paragraphs:

        # Stop when next section starts (safety)
        if "DECLARATION" in para.text.upper():
            break

        for old, new in replacements.items():
            replace_text_runs(para, old, new)

    # ----------------------------
    # Replace inside tables (if any)
    # ----------------------------
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for old, new in replacements.items():
                    if old in cell.text:
                        cell.text = cell.text.replace(old, new)

    # ----------------------------
    # Footer academic year safety
    # ----------------------------
    section = doc.sections[1] if len(doc.sections) > 1 else doc.sections[0]
    footer = section.footer

    year_pattern = r"\b\d{4}\s*[-–—]\s*\d{4}\b"

    for para in footer.paragraphs:
        for run in para.runs:
            if re.search(year_pattern, run.text):
                run.text = re.sub(year_pattern, meta["academic_year"], run.text)

    # ----------------------------
    # Save output
    # ----------------------------
    doc.save(output_path)
    print(f"Certificate page generated: {output_path}")


# ----------------------------
# Run standalone (dev mode)
# ----------------------------
if __name__ == "__main__":
    input_file = r"C:\\Users\\sumam\\OneDrive\\Documents\\senior_project_template (2).docx"
    update_certificate_page(input_file)
