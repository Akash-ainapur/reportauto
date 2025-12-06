from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os
import re

def replace_text_runs(paragraph, old, new):
    """Replace text even if split across runs."""
    full_text = "".join(run.text for run in paragraph.runs)
    if old in full_text:
        new_text = full_text.replace(old, new)
        # clear all runs and write new text to first run
        for run in paragraph.runs:
            run.text = ""
        paragraph.runs[0].text = new_text

def add_page_number(paragraph):
    """Adds dynamic PAGE field to footer paragraph."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')

    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)

def update_project_doc_with_dummies(input_path):
    doc = Document(input_path)
    base, ext = os.path.splitext(input_path)
    output_path = base + "_dummy_fixed.docx"

    # --- DUMMY PLACEHOLDER DATA ---
    dummy_project_title = "ZQX-HAZARDOUS1234-AI-IOT"
    dummy_project_name = "<<<FAKE_PROJECT_XYZ>>>"
    dummy_degree = "FAKE DEGREE OF MAGIC TECHNOLOGY"
    dummy_department = "DEPT-OF-GALACTIC-COMPUTING"
    dummy_college = "INTERPLANETARY MVJ ACADEMY"
    dummy_city = "NEBULA CITY - 999"
    dummy_year = "GALACTIC YEAR 3030 - 3031"
    dummy_guide_name = "Prof. XÆ-12 Quantum"
    dummy_guide_designation = "Chief Mentor, Parallel Universe Division"
    dummy_header = "HEADER_TITLE_$$$__ZQX"
    dummy_footer_text = "FOOTER_LINE__8888__DEPT-TEST   "
    dummy_students = [
        ("ID-XYZ001", "Alpha Centauri"),
        ("ID-XYZ002", "Beta Orion"),
        ("ID-XYZ003", "Gamma Hydra"),
        ("ID-XYZ004", "Delta Lyra")
    ]

    # --- TEXT REPLACEMENTS ---
    replacements = {
        "HAZARD WASTE DETECTION USING AI AND IOT": dummy_project_title,
        "MVJ NEXTGEN EDUCLOUD:AI-BASED ACADEMIC RESOURCE MANAGER": dummy_project_name,
        "BACHELOR OF ENGINEERING": dummy_degree,
        "COMPUTER SCIENCE & ENGINEERING": dummy_department,
        "Mrs. Sumanjali": dummy_guide_name,
        "Sumanjali": dummy_guide_name,  # catches split runs
        "Assistant Professor, Department of CSE": dummy_guide_designation,
        "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING": dummy_department,
        "MVJ COLLEGE OF ENGINEERING": dummy_college,
        "BANGALORE - 67": dummy_city,
        "ACADEMIC YEAR 2024 - 2025": dummy_year
    }

    # --- Replace text in paragraphs (run-safe) ---
    for para in doc.paragraphs:
        for old, new in replacements.items():
            replace_text_runs(para, old, new)

    # --- Replace text inside tables ---
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for old, new in replacements.items():
                    if old in cell.text:
                        cell.text = cell.text.replace(old, new)

    # --- Update student IDs and names ---
    if doc.tables:
        table = doc.tables[0]
        for i, (dummy_id, dummy_name) in enumerate(dummy_students):
            if i < len(table.rows):
                table.cell(i, 0).text = dummy_id
                table.cell(i, 1).text = dummy_name

    # --- HEADER ---
    for section in doc.sections:
        header = section.header
        if header.paragraphs:
            header.paragraphs[0].text = dummy_header
        else:
            header.add_paragraph(dummy_header)

    # --- FOOTER (preserve structure with tabs, replace text in place) ---
    # Handle various dash characters: regular hyphen (-), en dash (–), em dash (—)
    for section in doc.sections:
        footer = section.footer
        for para in footer.paragraphs:
            if not para.runs:
                continue
                
            # Get full text to check what's actually there
            full_text = "".join(run.text for run in para.runs)
            
            # Replace year patterns while preserving tabs and structure
            year_patterns = [
                (r"2024\s*[-–—]\s*2025", dummy_year),  # Matches "2024 - 2025", "2024 – 2025", etc.
                (r"ACADEMIC YEAR\s+2024\s*[-–—]\s*2025", dummy_year),
            ]
            
            text_replaced = False
            for pattern, replacement in year_patterns:
                if re.search(pattern, full_text):
                    # Find which run contains the year text
                    for run in para.runs:
                        if re.search(pattern, run.text):
                            # Replace only the year part, preserve tabs and other text
                            run.text = re.sub(pattern, replacement, run.text)
                            text_replaced = True
                            break
                    if text_replaced:
                        break
            
            # Replace department names if present
            dept_replacements = {
                "COMPUTER SCIENCE & ENGINEERING": dummy_department,
                "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING": dummy_department,
                "CSE": dummy_department.split()[-1] if len(dummy_department.split()) > 0 else "CSE",
                "Computer Science": dummy_department,
            }
            
            for old, new in dept_replacements.items():
                if old in full_text:
                    # Replace in the run that contains the department text
                    for run in para.runs:
                        if old in run.text:
                            run.text = run.text.replace(old, new)
                            break

    # Save updated doc
    doc.save(output_path)
    print(f"Dummy-fixed file saved as: {output_path}")

# --- RUN ---
input_file = r"D:\Model\REPORT1\AutomatedReportGenerator\templates\senior_project_template.docx"
update_project_doc_with_dummies(input_file)
