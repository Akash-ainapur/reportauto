"""
Table of Contents Generator

Creates a proper Word TOC field that auto-populates from Heading 1-3 styles.
Uses Word field codes for professional auto-updating TOC.
"""

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


class TableOfContentsGenerator:
    """
    Generates Table of Contents using Word TOC field.
    The TOC will auto-populate when:
    1. User opens document and updates field (right-click → Update Field)
    2. pywin32 automation triggers update (optional, see builder.py)
    """
    NEEDS_BORDER = False
    
    def __init__(self, context):
        self.context = context

    def generate(self) -> Document:
        """Generate TOC with Word field code."""
        # Create fresh document
        doc = Document()
        
        # Add "TABLE OF CONTENTS" heading (centered)
        heading = doc.add_paragraph("TABLE OF CONTENTS")
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading_run = heading.runs[0]
        heading_run.font.size = Pt(18)
        heading_run.font.bold = True
        
        # Add spacing
        doc.add_paragraph()
        
        # Add TOC field
        toc_para = doc.add_paragraph()
        self._add_toc_field(toc_para)
        
        return doc
    
    def _add_toc_field(self, paragraph):
        """
        Insert Word TOC field code into paragraph.
        
        The field code: { TOC \\o "1-3" \\h \\z \\u }
        
        Switches:
        - \\o "1-3": Include Heading 1, 2, and 3 styles
        - \\h: Make TOC entries hyperlinks
        - \\z: Hide page numbers in web view
        - \\u: Use outline levels instead of styles
        """
        run = paragraph.add_run()
        
        # 1. Begin field character
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        
        # 2. Field instruction (the TOC command)
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
        
        # 3. Separator (marks end of instruction, start of result)
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        
        # 4. Field result placeholder (shows until updated)
        # Add helpful instruction text
        run_text = paragraph.add_run(
            "Right-click here and select 'Update Field' to populate the Table of Contents.\n\n"
            "Or: Select all (Ctrl+A) → Press F9 to update all fields."
        )
        run_text.font.italic = True
        run_text.font.size = Pt(11)
        
        # 5. End field character
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        
        # Append all field elements to the run
        run._element.append(fldChar1)
        run._element.append(instrText)
        run._element.append(fldChar2)
        # run_text already added to paragraph
        run._element.append(fldChar3)
