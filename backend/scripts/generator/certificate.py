from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import json


# -------------------------------------------------
# Add page border
# -------------------------------------------------
def add_page_border(section):
    sectPr = section._sectPr

    # Remove existing borders if present
    for child in list(sectPr):
        if child.tag == qn("w:pgBorders"):
            sectPr.remove(child)

    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")

    for side in ["top", "left", "bottom", "right"]:
        border = OxmlElement(f"w:{side}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "12")
        border.set(qn("w:space"), "24")
        border.set(qn("w:color"), "000000")
        pgBorders.append(border)

    sectPr.append(pgBorders)


# -------------------------------------------------
# Rebuild Signature Block (CORRECT & SAFE)
# -------------------------------------------------
def rebuild_signature_block(doc, cert):
    # Try finding the signature in a table first
    signature_row = None
    for table in doc.tables:
        for row in table.rows:
            # Check all cells in the row for "Signature of Guide"
            for cell in row.cells:
                if "Signature of Guide" in cell.text:
                    signature_row = row
                    break
            if signature_row:
                break
        if signature_row:
            break

    if signature_row:
        print("✅ Found signature block in table. Updating...")
        
        # We expect 3 cells: Guide, HOD, Dean
        # If the table structure is different, this might need adjustment, 
        # but based on the template (Col 0: Guide, Col 1: HOD, Col 2: Dean)
        
        # Data mapping
        items = [
            ("Signature of Guide", cert["guide_name"], cert["guide_designation"]),
            ("Signature of HOD",   cert["hod_name"],   cert["hod_designation"]),
            ("Signature of Dean",  cert["dean_name"],  cert["dean_designation"])
        ]

        # Ensure we have enough cells
        for col_idx, (header, name, designation) in enumerate(items):
            if col_idx >= len(signature_row.cells):
                break
            
            cell = signature_row.cells[col_idx]
            
            # Clear existing content
            cell.text = ""
            
            # Add Header (Bold)
            p = cell.paragraphs[0]
            runner = p.add_run(header)
            runner.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            
            # Add Name (Bold, new paragraph)
            p = cell.add_paragraph()
            runner = p.add_run(name)
            runner.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(0)
            
            # Add Designation (Bold, multiple lines if needed)
            lines = designation.split('\n')
            for line in lines:
                if not line.strip():
                    continue
                p = cell.add_paragraph()
                runner = p.add_run(line.strip())
                runner.bold = True  # Requested by user
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)

        return

    # Fallback: Paragraph based (original logic)
    print("⚠ Signature table not found, attempting paragraph reconstruction...")
    start_para = None
    end_para = None

    # 1️⃣ Identify start & end markers
    for p in doc.paragraphs:
        if p.text.strip() == "Signature of Guide":
            start_para = p
        elif start_para and p.text.strip() == "EXTERNAL EXAMINERS":
            end_para = p
            break

    if not start_para or not end_para:
        print("⚠ Signature section not found in paragraphs either.")
        return

    # 2️⃣ Collect paragraphs to delete (SAFE way)
    paras_to_delete = []
    collecting = False
    for p in doc.paragraphs:
        if p == start_para:
            collecting = True
        if collecting:
            paras_to_delete.append(p)
        if p == end_para:
            break

    # 3️⃣ Remember insertion position (before EXTERNAL EXAMINERS)
    insert_before_el = end_para._element

    # 4️⃣ Delete old signature content
    for p in paras_to_delete:
        p._element.getparent().remove(p._element)

    # 5️⃣ Create new signature table
    table = doc.add_table(rows=3, cols=3)
    table.autofit = True

    headers = ["Signature of Guide", "Signature of HOD", "Signature of Dean"]
    names = [
        cert["guide_name"],
        cert["hod_name"],
        cert["dean_name"]
    ]
    designations = [
        cert["guide_designation"],
        cert["hod_designation"],
        cert["dean_designation"]
    ]

    # Header row (BOLD)
    for col in range(3):
        p = table.rows[0].cells[col].paragraphs[0]
        p.text = headers[col]
        for r in p.runs:
            r.bold = True

    # Name row (BOLD ✅)
    for col in range(3):
        p = table.rows[1].cells[col].paragraphs[0]
        p.text = names[col]
        for r in p.runs:
            r.bold = True

    # Designation row
    for col in range(3):
        table.rows[2].cells[col].paragraphs[0].text = designations[col]

    # Spacing control
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)

    # 6️⃣ Insert table at exact position
    insert_before_el.addprevious(table._element)


# -------------------------------------------------
# Main Generator
# -------------------------------------------------
def update_certificate_page(input_path):
    # Get the directory of the current script
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 3 levels to get to project root (generator -> scripts -> backend -> root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir)))
    
    # Establish output directory
    output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.basename(input_path)
    base, ext = os.path.splitext(filename)
    output_filename = f"{base}_filled{ext}"
    output_path = os.path.join(output_dir, output_filename)

    doc = Document(input_path)

    # Load JSON
    json_path = os.path.join(project_root, "backend", "data", "full_report_template.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["global_metadata"]
    cert = data["certificate_info"]

    # Body replacements (NON-SIGNATURE)
    replacements = {
        "MVJ COLLEGE OF ENGINEERING": meta["college_name"],
        "Near ITPB, Whitefield, Bangalore – 560067": meta["college_address"],
        "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING": meta["department_name"],
        "MVJ NEXTGEN EDUCLOUD:AI-BASED ACADEMIC RESOURCE MANAGER": meta["project_title"],
        "2024 - 2025": meta["academic_year"],
        "Major Project": cert["project_type"],
        "Major project": cert["project_type"]
    }

    for p in doc.paragraphs:
        for old, new in replacements.items():
            if old in p.text:
                p.text = p.text.replace(old, new)

    # ✅ Rebuild signature block (FIX)
    rebuild_signature_block(doc, cert)

    # Add page border
    add_page_border(doc.sections[0])

    doc.save(output_path)
    print(f"✅ Certificate generated correctly: {output_path}")


# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    # Calculate input file path dynamically
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir)))
    input_file = os.path.join(project_root, "backend", "templates", "template_indivisual", "senior_project_template (2).docx")
    
    if os.path.exists(input_file):
        update_certificate_page(input_file)
    else:
        print(f"Error: Template file not found at {input_file}")
