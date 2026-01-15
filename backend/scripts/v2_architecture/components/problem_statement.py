"""
Problem Statement Chapter Generator - Chapter 3

Generates the Problem Statement chapter with AI-powered content.
Format: CHAPTER 3 (18pt bold) -> PROBLEM STATEMENT (Heading 1) -> Content
"""

from docx import Document
from components.ai_content_base import AIContentBase


class ProblemStatementGenerator(AIContentBase):
    """
    Generates Chapter 3 - Problem Statement with AI-powered content.
    Single cohesive narrative about gaps in current systems.
    """
    NEEDS_BORDER = False

    def generate(self) -> Document:
        """Generate the Problem Statement chapter with AI content."""
        # Create fresh document
        doc = Document()
        
        # Add "CHAPTER 3: PROBLEM STATEMENT" as Heading 1
        self.add_heading(doc, "CHAPTER 3: PROBLEM STATEMENT", level=1)
        
        # Add spacing
        doc.add_paragraph()
        
        # Generate AI content
        content = self.generate_ai_content("problem_statement")
        
        # Add content
        self.add_body_content(doc, content, justified=True, font_size=12.5)
        
        return doc
