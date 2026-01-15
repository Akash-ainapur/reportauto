"""
List of Figures Generator

Creates a Word field for List of Figures (TOF).
Format: LIST OF FIGURES (18pt bold, centered) -> Field placeholder
"""

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .base import BaseSectionGenerator


class ListOfFiguresGenerator(BaseSectionGenerator):
    """
    Generates List of Figures using Word TOF field.
    """
    NEEDS_BORDER = True
    
    def generate(self) -> Document:
        """Generate LOF with Word field code."""
        doc = Document()
        
        # Add "LIST OF FIGURES" heading (centered, Heading 1)
        heading = doc.add_heading("LIST OF FIGURES", level=1)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add spacing
        doc.add_paragraph()
        
        # Add TOF field
        p = doc.add_paragraph()
        run = p.add_run()
        
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = 'TOC \\h \\z \\t "Figure" \\c'
        
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'separate')
        
        run._element.append(fldChar1)
        run._element.append(instrText)
        run._element.append(fldChar2)
        
        run_text = p.add_run("Right-click and select 'Update Field' to list figures.")
        run_text.font.italic = True
        
        fldChar3 = OxmlElement('w:fldChar')
        fldChar3.set(qn('w:fldCharType'), 'end')
        run._element.append(fldChar3)
        
        return doc
