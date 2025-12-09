from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .base import BaseSectionGenerator

class AbstractGenerator(BaseSectionGenerator):
    NEEDS_BORDER = False

    def generate(self) -> Document:
        # Create fresh document or use template if one existed (stub used fresh doc)
        doc = Document()
        
        # Title
        p = doc.add_paragraph()
        run = p.add_run("ABSTRACT")
        run.bold = True
        run.font.size = Pt(16)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Placeholder Content
        p = doc.add_paragraph()
        p.add_run("\n[Abstract Content Will Be Generated Here]\n")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        return doc
