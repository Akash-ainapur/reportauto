"""
Conclusion Chapter Generator

Generates the Conclusion section (no chapter number in reference).
Format: CONCLUSION (Heading 1) -> Summary content
"""

from docx import Document
from components.ai_content_base import AIContentBase


class ConclusionGenerator(AIContentBase):
    """
    Generates Conclusion section.
    Summarizes project achievements and future scope.
    """
    NEEDS_BORDER = False

    def generate(self) -> Document:
        """Generate the Conclusion section."""
        # Create fresh document
        doc = Document()
        
        # Add "CHAPTER 7: CONCLUSION" as Heading 1
        self.add_heading(doc, "CHAPTER 7: CONCLUSION", level=1)
        
        # Add spacing
        doc.add_paragraph()
        
        # Generate AI content
        content = self.generate_ai_content("conclusion")
        
        # Add content
        self.add_body_content(doc, content, justified=True, font_size=12.5)
        
        return doc
