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
# -------------------------------------------------
# Rebuild Signature Block (CORRECT & SAFE)
# -------------------------------------------------
def rebuild_signature_block(doc, cert, meta):
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

    # Helper to apply metadata replacements to signature text
    def clean_text(text):
        if not text: return ""
        # specific replacements
        dept_short = meta.get("department_short", "Department of Universal Logic")
        text = text.replace("Department of CSE", dept_short)
        text = text.replace("Department of Universal Logic", dept_short) # In case JSON has hardcoded old default
        return text

    if signature_row:
        print("✅ Found signature block in table. Updating...")
        
        # We expect 3 cells: Guide, HOD, Dean
        # If the table structure is different, this might need adjustment, 
        # but based on the template (Col 0: Guide, Col 1: HOD, Col 2: Dean)
        
        # Data mapping
        items = [
            ("Signature of Guide", clean_text(cert["guide_name"]), clean_text(cert["guide_designation"])),
            ("Signature of HOD",   clean_text(cert["hod_name"]),   clean_text(cert["hod_designation"])),
            ("Signature of Dean",  clean_text(cert["dean_name"]),  clean_text(cert["dean_designation"]))
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
        clean_text(cert["guide_name"]),
        clean_text(cert["hod_name"]),
        clean_text(cert["dean_name"])
    ]
    designations = [
        clean_text(cert["guide_designation"]),
        clean_text(cert["hod_designation"]),
        clean_text(cert["dean_designation"])
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

    from docx.shared import RGBColor
    import re

    def replace_chunk_with_format(paragraph, old_text, new_text, is_regex=False, 
                               bold=False, size=None, color=None):
        if not paragraph.runs:
            return

        # 1. Capture state of existing runs
        run_data = []
        for r in paragraph.runs:
            run_data.append({
                "text": r.text,
                "bold": r.bold,
                "italic": r.italic,
                "underline": r.underline,
                "font_name": r.font.name,
                "font_size": r.font.size,
                "font_color": r.font.color.rgb,
                "original_run": r
            })
        
        full_text = "".join(d["text"] for d in run_data)
        
        # 2. Find match
        match_start = -1
        match_end = -1
        
        if is_regex:
            match = re.search(old_text, full_text, flags=re.IGNORECASE)
            if match:
                match_start = match.start()
                match_end = match.end()
        else:
            match_start = full_text.find(old_text)
            if match_start != -1:
                match_end = match_start + len(old_text)
                
        if match_start == -1:
            return

        # 3. Clear existing runs
        for r in paragraph.runs:
            r.text = ""
            
        # 4. Rebuild runs
        current_pos = 0
        
        for r_item in run_data:
            r_text = r_item["text"]
            r_len = len(r_text)
            r_end = current_pos + r_len
            
            # Helper to create run with copied props
            def add_run_copy_props(text):
                nr = paragraph.add_run(text)
                nr.bold = r_item["bold"]
                nr.italic = r_item["italic"]
                nr.underline = r_item["underline"]
                if r_item["font_name"]: nr.font.name = r_item["font_name"]
                if r_item["font_size"]: nr.font.size = r_item["font_size"]
                if r_item["font_color"]: nr.font.color.rgb = r_item["font_color"]
                return nr

            # Case A: Run is completely before match
            if r_end <= match_start:
                 add_run_copy_props(r_text)
                 
            # Case B: Run is completely after match
            elif current_pos >= match_end:
                 add_run_copy_props(r_text)
                 
            # Case C: Overlap
            else:
                # Sub-case: Part before match
                if current_pos < match_start:
                    start_offset = 0
                    end_offset = match_start - current_pos
                    text_chunk = r_text[start_offset:end_offset]
                    if text_chunk:
                        add_run_copy_props(text_chunk)
                
                # Sub-case: The Match Itself (Insert ONLY ONCE when we hit the start)
                if current_pos <= match_start < r_end:
                     target_run = paragraph.add_run(new_text)
                     # Apply requested formatting or inherit
                     target_run.bold = True if bold else r_item["bold"]
                     if size: target_run.font.size = Pt(size)
                     if color: target_run.font.color.rgb = color
                
                # Sub-case: Part after match
                if r_end > match_end:
                    start_offset = match_end - current_pos
                    if start_offset < 0: start_offset = 0
                    text_chunk = r_text[start_offset:]
                    if text_chunk:
                        add_run_copy_props(text_chunk)
                        
            current_pos += r_len


    # Replacements with styling
    styled_replacements = [
        # College Name: Bold, Size 18
        ("MVJ COLLEGE OF ENGINEERING", meta["college_name"], False, True, 18, None),
        
        # Dept Name Header: Bold, Size 14
        ("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", meta["department_name"].upper(), False, True, 14, None),
        
        # Body Dept Name: Replace "Computer science and Engineering" with anonymous name
        ("Computer science and Engineering", meta.get("course_name", "Electronics and Communication Engineering "), False, False, None, None),
        
        # Major -> Mini replacement
        (r"Major",meta["project_type"], True, False, None, None),
        
        # Academic Year
        ("2024 - 2025", meta["academic_year"], False, False, None, None),
        
        # Address
        ("Near ITPB, Whitefield, Bangalore – 560067", meta["college_address"], False, False, None, None),

        # Project Title: Red and Bold, with quotes
        # MOVED TO END: To ensure its styling isn't overwritten by other replacements in same paragraph
        (r"[\"“]?\s*MVJ\s*NEXTGEN\s*EDUCLOUD[:\s-]+AI[:\s-]+BASED\s*ACADEMIC\s*RESOURCE\s*MANAGER\s*[\"”]?", f'"{meta["project_title"]}"', True, True, None, RGBColor(255, 0, 0))
    ]

    for p in doc.paragraphs:
        for search, replace, is_re, bold, size, color in styled_replacements:
             replace_chunk_with_format(p, search, replace, is_re, bold, size, color)

    # ✅ Rebuild signature block (FIX)
    rebuild_signature_block(doc, cert, meta)

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
    input_file = os.path.join(project_root, "backend", "templates", "template_indivisual", "certificate.docx")
    
    if os.path.exists(input_file):
        update_certificate_page(input_file)
    else:
        print(f"Error: Template file not found at {input_file}")
