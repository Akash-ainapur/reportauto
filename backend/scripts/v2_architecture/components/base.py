from docx import Document

class BaseSectionGenerator:
    NEEDS_BORDER = False

    def __init__(self, context):
        self.context = context
        self.data = context.data
        self.meta = self.data["global_metadata"]

    def generate(self) -> Document:
        raise NotImplementedError
