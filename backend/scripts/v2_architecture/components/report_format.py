"""
Markdown -> Word renderer matching the department's Phase II reference report.

Measured from the reference PDF:
  CHAPTER N / chapter title ... 18pt bold (number left, title centred)
  ## sub-section ............... 16pt bold, upper case, numbered N.M
  ### sub-sub-section .......... 14pt bold, upper case, numbered N.M.K
  literature survey titles ..... 14pt bold, title case, numbered N.M
  body ......................... 12pt Times New Roman, justified, 1.5 lines
  lists ........................ i. ii. iii. with a bold lead phrase
  references ................... [n] with a hanging indent

Headings and figures are numbered here, never by the model. Every heading also gets a
hidden TC field so the Table of Contents can be built from them.
"""

import re

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Times New Roman"
TOC_ID = "C"  # TC fields with \f C feed the Table of Contents

# name: (size, bold, alignment, line spacing, space before pt, space after pt)
STYLES = {
    "RG Body":           (12, False, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 0, 8),
    "RG Chapter Number": (18, True, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 0, 0),
    "RG Chapter Title":  (18, True, WD_ALIGN_PARAGRAPH.CENTER, 1.0, 10, 18),
    "RG Prelim Title":   (18, True, WD_ALIGN_PARAGRAPH.CENTER, 1.0, 0, 18),
    "RG Heading 2":      (16, True, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 12, 6),
    "RG Heading 3":      (14, True, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 10, 4),
    "RG Lit Title":      (14, True, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 12, 4),
    "RG Lit Meta":       (12, False, WD_ALIGN_PARAGRAPH.LEFT, 1.15, 0, 4),
    "RG List":           (12, False, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 0, 2),
    "RG Reference":      (12, False, WD_ALIGN_PARAGRAPH.JUSTIFY, 1.5, 0, 10),
    "RG Caption":        (12, False, WD_ALIGN_PARAGRAPH.CENTER, 1.0, 6, 12),
    "RG Figure":         (11, False, WD_ALIGN_PARAGRAPH.CENTER, 1.0, 12, 0),
    "RG Table":          (11, False, WD_ALIGN_PARAGRAPH.LEFT, 1.0, 0, 0),
}

ROMAN = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
         (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]


def to_roman(n):
    out = ""
    for value, numeral in ROMAN:
        while n >= value:
            out += numeral
            n -= value
    return out


def _set_run_font(run, size=None, bold=None, italic=None):
    run.font.name = FONT
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def ensure_styles(doc):
    for name, (size, bold, align, spacing, before, after) in STYLES.items():
        if name in [s.name for s in doc.styles]:
            continue
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.bold = bold
        rpr = style.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.insert(0, rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), FONT)
        pf = style.paragraph_format
        pf.alignment = align
        pf.line_spacing = spacing
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.left_indent = Inches(0)
        pf.first_line_indent = Inches(0)
        if name in ("RG Heading 2", "RG Heading 3", "RG Lit Title", "RG Chapter Number",
                    "RG Chapter Title", "RG Figure"):
            pf.keep_with_next = True
    # Start from a clean, A4 body section
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)


def add_field(paragraph, instruction, result_text=None):
    """Append a complex field ({ instruction }) to a paragraph; returns the result run if any."""
    def fld(kind):
        run = paragraph.add_run()
        el = OxmlElement("w:fldChar")
        el.set(qn("w:fldCharType"), kind)
        run._element.append(el)
        return run

    fld("begin")
    instr_run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    instr_run._element.append(instr)
    result = None
    if result_text is not None:
        fld("separate")
        result = paragraph.add_run(result_text)
    fld("end")
    return result


def add_toc_entry(paragraph, text, level):
    """Hidden TC field the Table of Contents field picks up (TOC \\f C)."""
    safe = text.replace('"', "'")
    add_field(paragraph, f'TC "{safe}" \\f {TOC_ID} \\l {level}')


def add_bookmark(paragraph, name, bookmark_id):
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    paragraph._p.insert(1 if paragraph._p.pPr is not None else 0, start)
    paragraph._p.append(end)


INLINE = re.compile(r"(\*\*.+?\*\*|__.+?__|\*[^*\s][^*]*?\*|`[^`]+`)")


def add_inline(paragraph, text, size=None, bold=None):
    """Add markdown-ish inline text (**bold**, *italic*, `code`) to a paragraph."""
    for part in INLINE.split(text):
        if not part:
            continue
        if (part.startswith("**") and part.endswith("**")) or (part.startswith("__") and part.endswith("__")):
            run = paragraph.add_run(part[2:-2])
            _set_run_font(run, size, True)
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            _set_run_font(run, size, bold)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            _set_run_font(run, size, bold, True)
        else:
            run = paragraph.add_run(part.replace("**", ""))
            _set_run_font(run, size, bold)


HEADING_NUMBER = re.compile(r"^(chapter\s+\d+[:.\s-]*)?(\d+(\.\d+)*\.?\s+)?", re.IGNORECASE)
LIST_ITEM = re.compile(r"^(?:[-*•▪]\s+|\(?\d{1,3}[.)]\s+|\(?[ivxlc]{1,6}[.)]\s+|\[\d{1,3}\]\s*)(.*)$", re.IGNORECASE)
FIGURE = re.compile(r"^\[\[\s*FIGURE\s*:\s*(.+?)\s*\]\]$", re.IGNORECASE)
TABLE_ROW = re.compile(r"^\|.*\|$")
TABLE_RULE = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")


def clean_heading(text):
    text = text.strip().strip("#").strip().strip("*").strip()
    return HEADING_NUMBER.sub("", text, count=1).strip(" :.-") or text


class ReportWriter:
    """Writes one chapter (or preliminary page) into a python-docx Document."""

    def __init__(self, doc, context, chapter_no=None, style="standard"):
        self.doc = doc
        self.context = context
        self.chapter_no = chapter_no
        self.style = style
        self.h2 = 0
        self.h3 = 0
        self.list_counter = 0
        self.fig_counts = {}
        ensure_styles(doc)
        # Drop the empty paragraph a fresh Document() starts with
        body = doc.element.body
        for p in body.findall(qn("w:p")):
            if not "".join(t.text or "" for t in p.iter(qn("w:t"))):
                body.remove(p)

    # ---- headings -------------------------------------------------------------------

    def chapter_heading(self, title):
        p = self.doc.add_paragraph(style="RG Chapter Number")
        run = p.add_run(f"CHAPTER {self.chapter_no}")
        _set_run_font(run, 18, True)
        add_toc_entry(p, f"CHAPTER {self.chapter_no} {title.upper()}", 1)
        self._toc(f"CHAPTER {self.chapter_no} {title.upper()}", 1)
        p = self.doc.add_paragraph(style="RG Chapter Title")
        _set_run_font(p.add_run(title.upper()), 18, True)

    def prelim_heading(self, title):
        p = self.doc.add_paragraph(style="RG Prelim Title")
        _set_run_font(p.add_run(title.upper()), 18, True)
        add_toc_entry(p, title.upper(), 1)
        self._toc(title.upper(), 1)

    def heading(self, text, level):
        text = clean_heading(text)
        self.list_counter = 0
        if level <= 2:
            self.h2 += 1
            self.h3 = 0
            number = f"{self.chapter_no}.{self.h2}"
            if self.style == "literature":
                style, label, toc_level = "RG Lit Title", text, 2
            else:
                style, label, toc_level = "RG Heading 2", text.upper(), 2
        else:
            if self.h2 == 0:
                self.h2 = 1
            self.h3 += 1
            number = f"{self.chapter_no}.{self.h2}.{self.h3}"
            style, label, toc_level = "RG Heading 3", text.upper(), 3
        p = self.doc.add_paragraph(style=style)
        size = STYLES[style][0]
        _set_run_font(p.add_run(f"{number} {label}"), size, True)
        add_toc_entry(p, f"{number} {label}", toc_level)
        self._toc(f"{number} {label}", toc_level)

    def _toc(self, text, level):
        self.context.toc_entries.append((text, level))

    # ---- blocks ---------------------------------------------------------------------

    def paragraph(self, text, style="RG Body"):
        self.list_counter = 0
        p = self.doc.add_paragraph(style=style)
        add_inline(p, text, STYLES[style][0])
        return p

    def list_item(self, text):
        self.list_counter += 1
        long_item = len(text) > 110
        p = self.doc.add_paragraph(style="RG List")
        pf = p.paragraph_format
        pf.left_indent = Inches(0.5)
        pf.first_line_indent = Inches(-0.35)
        pf.tab_stops.add_tab_stop(Inches(0.5))
        pf.line_spacing = 1.5 if long_item else 1.15
        pf.space_after = Pt(2 if long_item else 5)
        _set_run_font(p.add_run(f"{to_roman(self.list_counter)}.\t"), 12, True)
        add_inline(p, text, 12)

    def reference_item(self, text):
        self.list_counter += 1
        p = self.doc.add_paragraph(style="RG Reference")
        pf = p.paragraph_format
        pf.left_indent = Inches(0.4)
        pf.first_line_indent = Inches(-0.4)
        pf.tab_stops.add_tab_stop(Inches(0.4))
        _set_run_font(p.add_run(f"[{self.list_counter}]\t"), 12)
        add_inline(p, text, 12)

    def lit_meta(self, text):
        p = self.doc.add_paragraph(style="RG Lit Meta")
        add_inline(p, text, 12)

    def figure(self, caption):
        self.list_counter = 0
        caption = caption.strip().rstrip(".")
        number = self._figure_number()
        box = self.doc.add_paragraph(style="RG Figure")
        self._box(box)
        run = box.add_run(f"[ Paste image here: {caption} ]")
        _set_run_font(run, 11, False, True)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

        p = self.doc.add_paragraph(style="RG Caption")
        _set_run_font(p.add_run(f"Fig {number} {caption}"), 12)
        self.context.bookmark_seq += 1
        name = f"_RGFig{self.context.bookmark_seq}"
        add_bookmark(p, name, 9000 + self.context.bookmark_seq)
        self.context.figures.append({"number": number, "caption": caption, "bookmark": name})

    def _figure_number(self):
        if self.h3:
            base = f"{self.chapter_no}.{self.h2}.{self.h3}"
        elif self.h2:
            base = f"{self.chapter_no}.{self.h2}"
        else:
            base = f"{self.chapter_no}"
        count = self.fig_counts.get(base, 0) + 1
        self.fig_counts[base] = count
        # Under a sub-sub-section the first figure takes its number (Fig 6.2.1), as in the reference
        if self.h3 and count == 1:
            return base
        return f"{base}.{count}"

    def _box(self, paragraph):
        pPr = paragraph._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        for side in ("top", "left", "bottom", "right"):
            b = OxmlElement(f"w:{side}")
            b.set(qn("w:val"), "dashed")
            b.set(qn("w:sz"), "6")
            b.set(qn("w:space"), "24")
            b.set(qn("w:color"), "999999")
            borders.append(b)
        pPr.append(borders)
        paragraph.paragraph_format.left_indent = Inches(1.2)
        paragraph.paragraph_format.right_indent = Inches(1.2)

    def table(self, rows):
        self.list_counter = 0
        cols = max(len(r) for r in rows)
        table = self.doc.add_table(rows=len(rows), cols=cols)
        table.style = self.doc.styles["Table Grid"] if "Table Grid" in [s.name for s in self.doc.styles] else None
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, row in enumerate(rows):
            for j in range(cols):
                cell = table.cell(i, j)
                cell.text = ""
                p = cell.paragraphs[0]
                p.style = self.doc.styles["RG Table"]
                add_inline(p, row[j] if j < len(row) else "", 11, True if i == 0 else None)
        self.doc.add_paragraph(style="RG Body")

    # ---- markdown -------------------------------------------------------------------

    def render_markdown(self, text):
        lines = (text or "").replace("\r\n", "\n").split("\n")
        buffer = []
        table_rows = []

        def flush():
            if buffer:
                self.paragraph(" ".join(buffer))
                buffer.clear()

        def flush_table():
            if table_rows:
                self.table(table_rows[:])
                table_rows.clear()

        for raw in lines:
            line = raw.strip()
            if TABLE_ROW.match(line):
                flush()
                if not TABLE_RULE.match(line):
                    table_rows.append([c.strip() for c in line.strip("|").split("|")])
                continue
            flush_table()

            if not line or re.fullmatch(r"[-*_]{3,}", line):
                flush()
                continue
            fig = FIGURE.match(line)
            if fig:
                flush()
                self.figure(fig.group(1))
                continue
            if line.startswith("#"):
                flush()
                level = len(line) - len(line.lstrip("#"))
                self.heading(line, 2 if level <= 2 else 3)
                continue
            if self.style == "literature" and re.match(r"^\*{0,2}(AUTHORS?|PUBLISHED ON|PUBLISHED|YEAR)\b", line, re.I):
                flush()
                self.lit_meta(line)
                continue
            item = LIST_ITEM.match(line)
            if item and (self.style == "references" or not re.match(r"^\d+\.\d", line)):
                flush()
                if self.style == "references":
                    self.reference_item(item.group(1))
                else:
                    self.list_item(item.group(1))
                continue
            if self.style == "references":
                flush()
                self.reference_item(line)
                continue
            buffer.append(line)
        flush()
        flush_table()
