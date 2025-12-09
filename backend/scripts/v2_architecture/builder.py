import os
import json
from docx import Document
from docxcompose.composer import Composer
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

class ReportContext:
    def __init__(self, project_root):
        self.project_root = project_root
        self.output_dir = os.path.join(project_root, "output")
        self.templates_dir = os.path.join(project_root, "backend", "templates", "template_indivisual")
        self.data = self._load_data()
        
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_data(self):
        json_path = os.path.join(self.project_root, "backend", "data", "full_report_template.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_template_path(self, filename):
        return os.path.join(self.templates_dir, filename)

class ReportBuilder:
    def __init__(self, context):
        self.context = context
        self.steps = []
        self.master_doc = None
        self.composer = None

    def add_step(self, generator_class):
        self.steps.append(generator_class)
        return self

    def build(self):
        print("🏗 Starting Build Process...")
        
        for i, StepClass in enumerate(self.steps):
            print(f"  -> Executing Step: {StepClass.__name__}")
            generator = StepClass(self.context)
            doc = generator.generate()
            
            self._append_document(doc, StepClass)
            
        return self

    def _append_document(self, doc, step_class):
        # If it's the very first document, initialize master
        if self.master_doc is None:
            self.master_doc = doc
            self.composer = Composer(self.master_doc)
            print("     (Initialized Master Document)")
        else:
            # Append as new section
            self.master_doc.add_section(WD_SECTION.NEW_PAGE)
            self.composer.append(doc)
            print("     (Appended to Master)")

        # Post-processing: Borders
        # We check if the step requests borders
        if getattr(step_class, "NEEDS_BORDER", False):
            self._apply_border_to_last_section()

    def _apply_border_to_last_section(self):
        print("     (Applying Page Border)")
        section = self.master_doc.sections[-1]
        sectPr = section._sectPr
        
        # Remove existing
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

    def save(self, filename="full_report.docx"):
        output_path = os.path.join(self.context.output_dir, filename)
        if self.composer:
            self.composer.save(output_path)
            print(f"✅ Report Saved: {output_path}")
        else:
            print("⚠ Warning: No content to save.")
