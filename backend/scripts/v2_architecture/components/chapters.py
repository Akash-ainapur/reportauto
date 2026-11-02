"""
Generated (non-template) sections: abstract, table of contents, list of figures,
numbered chapters and references. Content comes from the bulk AI step
(context.bulk_content) or, without AI, from report_content in the request data.
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .base import BaseSectionGenerator
from .report_format import ReportWriter, _set_run_font, TOC_ID

TOC_MARKER = "{{TOC_ENTRIES}}"
LOF_MARKER = "{{LOF_TABLE}}"


def section_text(context, key):
    if key in context.bulk_content:
        return context.bulk_content[key]
    manual = context.data.get("report_content", {}).get(key)
    if isinstance(manual, dict) and manual.get("text"):
        return manual["text"]
    if isinstance(manual, str) and manual.strip():
        return manual
    return (f"[Write the {key.replace('_', ' ').title()} here - it was empty when this report was generated. "
            f"Write it in your own words, or generate the report again with this part filled in.]")


class AbstractGenerator(BaseSectionGenerator):
    def generate(self) -> Document:
        doc = Document()
        writer = ReportWriter(doc, self.context)
        writer.prelim_heading("ABSTRACT")
        writer.render_markdown(section_text(self.context, "abstract"))
        return doc


class TableOfContentsGenerator(BaseSectionGenerator):
    """TOC field built from the TC entries every heading carries. The builder pre-fills the
    field result with the entry list; Word adds page numbers when fields are updated."""

    def generate(self) -> Document:
        doc = Document()
        writer = ReportWriter(doc, self.context)
        writer.prelim_heading("TABLE OF CONTENT")
        p = doc.add_paragraph()
        add_field_start(p, f"TOC \\f {TOC_ID} \\l 1-3 \\h \\z")
        _set_run_font(p.add_run(TOC_MARKER), 12)
        end = doc.add_paragraph()
        add_field_end(end)
        return doc


class ListOfFiguresGenerator(BaseSectionGenerator):
    """Heading only; the builder swaps the marker for the FIGURE NO. / NAME / PAGE NO. table
    once every chapter has numbered its figures."""

    def generate(self) -> Document:
        doc = Document()
        writer = ReportWriter(doc, self.context)
        writer.prelim_heading("LIST OF FIGURES")
        p = doc.add_paragraph()
        _set_run_font(p.add_run(LOF_MARKER), 12)
        return doc


class ChapterGenerator(BaseSectionGenerator):
    def __init__(self, context, spec, number):
        super().__init__(context)
        self.spec = spec
        self.number = number

    def generate(self) -> Document:
        doc = Document()
        writer = ReportWriter(doc, self.context, chapter_no=self.number, style=self.spec.get("style", "standard"))
        writer.chapter_heading(self.spec["title"])
        writer.render_markdown(section_text(self.context, self.spec["key"]))
        return doc


class ReferencesGenerator(BaseSectionGenerator):
    def generate(self) -> Document:
        doc = Document()
        writer = ReportWriter(doc, self.context, style="references")
        writer.prelim_heading("REFERENCES")
        writer.render_markdown(section_text(self.context, "references"))
        return doc


def add_field_start(paragraph, instruction):
    """begin + instruction + separate; the result and the end mark follow in later paragraphs."""
    for kind, text in (("begin", None), (None, instruction), ("separate", None)):
        run = paragraph.add_run()
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = f" {text} "
        run._element.append(el)


def add_field_end(paragraph):
    run = paragraph.add_run()
    el = OxmlElement("w:fldChar")
    el.set(qn("w:fldCharType"), "end")
    run._element.append(el)

