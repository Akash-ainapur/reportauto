"""
Quick test to verify markdown parsing in AI content
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'backend' / 'scripts' / 'v2_architecture'))

from docx import Document
from components.ai_content_base import AIContentBase
from builder import ReportContext

# Test markdown content
markdown_text = """
This is a paragraph with **bold text** and *italic text* mixed together.

### Motivation for the Project
This is a subsection that should appear as Heading 3.

Some more text with **emphasis** on important points.

### Another Subsection
More content here.
"""

print("=" * 60)
print("Testing Markdown Parsing")
print("=" * 60)

# Create a test document
doc = Document()

# Create a mock context
context = ReportContext(str(project_root))

# Create AI content base instance
class TestGenerator(AIContentBase):
    NEEDS_BORDER = False
    
    def generate(self):
        doc = Document()
        self.add_body_content(doc, markdown_text, justified=True, font_size=12)
        return doc

generator = TestGenerator(context)
test_doc = generator.generate()

# Save test document
output_path = project_root / 'output' / 'markdown_test.docx'
test_doc.save(str(output_path))

print(f"\n✅ Test document created: {output_path}")
print("\nExpected formatting:")
print("- Regular paragraphs with bold and italic")
print("- '### Motivation for the Project' as Heading 3")
print("- '### Another Subsection' as Heading 3")
print("\nPlease open the document to verify formatting!")
