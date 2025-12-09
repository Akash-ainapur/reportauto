import os
import sys
from docxcompose.composer import Composer
from docx import Document

# Add the generator directory to path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
generator_dir = os.path.join(current_dir, "generator")
sys.path.append(generator_dir)

# Import generator scripts
import page_01_front_page
import certificate
import declaration
import page_04_abstract
import acknowledgement
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION

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

def main():

    print("🚀 Starting Report Assembly Line...")
    project_root = os.path.dirname(os.path.dirname(current_dir))
    output_dir = os.path.join(project_root, "output")
    templates_dir = os.path.join(project_root, "backend", "templates", "template_indivisual")
    
    # 1. GENERATE INDIVIDUAL PAGES
    # We need to call the specific functions or run logic from each script
    # Based on my analysis, each script has a main function that takes an input path.
    
    # Front Page
    print("\n--- Generating Front Page ---")
    fp_in = os.path.join(templates_dir, "front_page.docx")
    page_01_front_page.update_project_doc_with_dummies(fp_in)
    fp_out = os.path.join(output_dir, "front_page_filled.docx")
    
    # Certificate
    print("\n--- Generating Certificate ---")
    cert_in = os.path.join(templates_dir, "certificate.docx")
    certificate.update_certificate_page(cert_in)
    cert_out = os.path.join(output_dir, "certificate_filled.docx")
    
    # Declaration
    print("\n--- Generating Declaration ---")
    decl_in = os.path.join(templates_dir, "declaration.docx")
    declaration.update_declaration_page(decl_in)
    decl_out = os.path.join(output_dir, "declaration_filled_v3.docx") # Filename from script
    
    # Abstract
    print("\n--- Generating Abstract ---")
    page_04_abstract.generate_abstract_page()
    abs_out = os.path.join(output_dir, "abstract_filled.docx")
    
    # Acknowledgement
    print("\n--- Generating Acknowledgement ---")
    ack_in = os.path.join(templates_dir, "Aknowledgement.docx")
    acknowledgement.update_acknowledgement_page(ack_in)
    ack_out = os.path.join(output_dir, "Aknowledgement_filled_new.docx") # Filename from script

    # 2. MERGE DOCUMENTS
    print("\n--- Merging Documents ---")
    
    # Order: Front Page -> Certificate -> Declaration -> Abstract -> Acknowledgement
    files_to_merge = [fp_out, cert_out, decl_out, abs_out, ack_out]
    
    # Verify all exist
    missing = [f for f in files_to_merge if not os.path.exists(f)]
    if missing:
        print(f"❌ Error: Missing generated files: {missing}")
        return

    # Master document (start with Front Page)
    master_doc = Document(files_to_merge[0])
    composer = Composer(master_doc)
    
    # Define which files need borders (Basenames)
    # Front Page: No
    # Certificate: Yes
    # Declaration: Yes (v3)
    # Abstract: No (User said blank page, usually no border on abstract unless specified, but to be safe lets leave it off unless requested. "borders for the pages whcih present when made indivisually" -> Abstract was made just now, default stub has no border. But Certificate and Dec have borders.)
    # Acknowledgement: Yes
    
    files_needing_borders = [
        "certificate_filled.docx", 
        "declaration_filled_v3.docx", 
        "Aknowledgement_filled_new.docx"
    ]
    
    for file_path in files_to_merge[1:]:
        filename = os.path.basename(file_path)
        print(f"Appending: {filename}")
        
        sub_doc = Document(file_path)
        
        # 1. Add new section for the new document to ensure page break + independent styling
        master_doc.add_section(WD_SECTION.NEW_PAGE)
        
        # 2. Append content
        composer.append(sub_doc)
        
        # 3. Apply border if needed to the *last* section (which we just added/appended to)
        # Note: composer.append appends elements. The elements go into the last section.
        # So we target the last section of master_doc.
        if filename in files_needing_borders:
            print(f"  -> Applying border to section for {filename}")
            # Target the last section
            # However, docxcompose might have added more sections if sub_doc had them?
            # We assume 1-to-1.
            last_section = master_doc.sections[-1]
            add_page_border(last_section)


        
    final_output = os.path.join(output_dir, "full_report.docx")
    composer.save(final_output)
    
    print(f"\n✅ Full Report Generated Successfully: {final_output}")

if __name__ == "__main__":
    main()
