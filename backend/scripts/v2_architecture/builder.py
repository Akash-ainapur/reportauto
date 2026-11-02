import os
import json
from docx import Document
from docxcompose.composer import Composer
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from report_types import get_report_type, ai_section_specs
from components.report_format import _set_run_font, add_field
from components.front_matter import academic_year
from components.chapters import TOC_MARKER, LOF_MARKER

# Page geometry of the reference report (A4). Front pages keep the geometry of their templates.
PAGE_WIDTH, PAGE_HEIGHT = Inches(8.27), Inches(11.69)
MARGINS = {"top": Inches(0.93), "bottom": Inches(0.85), "left": Inches(1.0), "right": Inches(0.79)}
HEADER_DISTANCE, FOOTER_DISTANCE = Inches(0.5), Inches(0.72)
TEXT_WIDTH = PAGE_WIDTH - MARGINS["left"] - MARGINS["right"]


class ReportContext:
    def __init__(self, project_root, data_file=None):
        self.project_root = project_root
        self.output_dir = os.path.join(project_root, "output")
        self.templates_dir = os.path.join(project_root, "backend", "templates", "template_indivisual")
        self.data_file = data_file
        self.data = self._load_data()
        self.bulk_content = {}  # Stores extracted AI content mapped by section name

        self.report_type = get_report_type(self.data.get("report_type"))
        self.report_templates_dir = os.path.join(
            project_root, "backend", "templates", "report_types", self.report_type["templates"])
        # Filled while sections render; used to pre-fill the TOC and build the List of Figures
        self.toc_entries = []
        self.figures = []
        self.bookmark_seq = 0

        os.makedirs(self.output_dir, exist_ok=True)

    def extract_bulk_content(self, raw_response: str):
        """Extract multi-section content from AI response using tags."""
        import re
        # Pattern to match <section_name>...</section_name>
        pattern = r'<(\w+)>(.*?)</\1>'
        matches = re.findall(pattern, raw_response, re.DOTALL)

        for section_name, content in matches:
            self.bulk_content[section_name.strip()] = content.strip()
            print(f"📥 Extracted bulk content for: {section_name}")

    def _load_data(self):
        # Use provided data path or fallback to default
        if self.data_file:
            json_path = self.data_file
        else:
            json_path = os.path.join(self.project_root, "backend", "data", "full_report_template.json")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Post-processing: Enforce capitalization for key academic fields
        if "global_metadata" in data:
            meta = data["global_metadata"]
            if "project_title" in meta:
                meta["project_title"] = meta["project_title"].upper()

        return data

    def get_template_path(self, filename):
        return os.path.join(self.templates_dir, filename)


class ReportBuilder:
    def __init__(self, context):
        self.context = context
        self.steps = []
        self.master_doc = None
        self.composer = None

    def add_step(self, generator_factory, section_type="main", name=None):
        """generator_factory(context) -> generator with .generate(); a generator class works too.
        section_type: 'isolated' (front pages), 'preliminary' (roman numbered) or 'main'."""
        name = name or getattr(generator_factory, "__name__", "Section")
        self.steps.append({'generator': generator_factory, 'type': section_type, 'name': name})
        return self

    def build(self):
        print("🏗 Starting Build Process...")

        # Pre-process: Trigger bulk AI requests to minimize API calls
        self._perform_bulk_ai_generation()

        # We need to save the type for each section added to master_doc
        self.section_types = []

        for step_info in self.steps:
            factory, sec_type = step_info['generator'], step_info['type']
            print(f"  -> Executing Step: {step_info['name']}", flush=True)
            doc = factory(self.context).generate()

            num_sections_before = len(self.master_doc.sections) if self.master_doc else 0
            self._append_document(doc)
            num_sections_after = len(self.master_doc.sections)
            for _ in range(num_sections_after - num_sections_before):
                self.section_types.append(sec_type)

        self._fill_table_of_contents()
        self._fill_list_of_figures()
        self._apply_page_setup()
        self._apply_headers_footers()
        self._configure_page_numbering()
        self._request_field_update()
        return self

    def _append_document(self, doc):
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

    def _section_type(self, idx):
        return self.section_types[idx] if idx < len(self.section_types) else "main"

    # ========================================
    # PAGE SETUP, BORDERS, HEADERS & FOOTERS
    # ========================================

    def _apply_page_setup(self):
        for idx, section in enumerate(self.master_doc.sections):
            sec_type = self._section_type(idx)
            if sec_type == "isolated":
                continue  # front pages keep the reference geometry and drawn borders
            section.page_width, section.page_height = PAGE_WIDTH, PAGE_HEIGHT
            section.top_margin, section.bottom_margin = MARGINS["top"], MARGINS["bottom"]
            section.left_margin, section.right_margin = MARGINS["left"], MARGINS["right"]
            section.header_distance, section.footer_distance = HEADER_DISTANCE, FOOTER_DISTANCE
            # Preliminary pages carry a thin page border; chapters have none
            self._set_page_border(section, sec_type == "preliminary")

    def _set_page_border(self, section, enabled):
        sectPr = section._sectPr
        for child in sectPr.findall(qn("w:pgBorders")):
            sectPr.remove(child)
        if not enabled:
            return
        pgBorders = OxmlElement("w:pgBorders")
        pgBorders.set(qn("w:offsetFrom"), "page")
        for side in ["top", "left", "bottom", "right"]:
            border = OxmlElement(f"w:{side}")
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "4")
            border.set(qn("w:space"), "24")
            border.set(qn("w:color"), "000000")
            pgBorders.append(border)
        # pgBorders must come before pgNumType/cols etc. in sectPr; insert after pgMar
        pgMar = sectPr.find(qn("w:pgMar"))
        if pgMar is not None:
            pgMar.addnext(pgBorders)
        else:
            sectPr.append(pgBorders)

    def _clear(self, header_or_footer):
        header_or_footer.is_linked_to_previous = False
        for para in list(header_or_footer.paragraphs):
            para._element.getparent().remove(para._element)
        for tbl in list(header_or_footer.tables):
            tbl._element.getparent().remove(tbl._element)

    def _rule(self, paragraph, side):
        """Full-width line above or below a paragraph (the reference's header/footer rule)."""
        pPr = paragraph._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "12")
        b.set(qn("w:space"), "1")
        b.set(qn("w:color"), "000000")
        pBdr.append(b)
        pPr.append(pBdr)

    def _format_header(self, header, project_title):
        """Chapter pages: project title, left, 12pt, with a rule underneath."""
        self._clear(header)
        p = header.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(0)
        _set_run_font(p.add_run(project_title.upper()), 12)
        self._rule(p, "bottom")

    def _format_footer(self, footer, department_label, year):
        """Chapter pages: rule, then 'DEPT. OF CSE, MVJCE' | year | page number."""
        self._clear(footer)
        p = footer.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        tabs = p.paragraph_format.tab_stops
        tabs.add_tab_stop(Inches(3.4), WD_TAB_ALIGNMENT.CENTER)
        tabs.add_tab_stop(TEXT_WIDTH, WD_TAB_ALIGNMENT.RIGHT)
        self._rule(p, "top")
        _set_run_font(p.add_run(f"{department_label}\t{year}\t"), 12)
        add_field(p, "PAGE", "1")
        for run in p.runs:
            _set_run_font(run, 12)

    def _format_footer_simple(self, footer):
        """Preliminary pages: centred page number (I, II, III...)."""
        self._clear(footer)
        p = footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_field(p, "PAGE", "I")
        for run in p.runs:
            _set_run_font(run, 12)

    def _apply_headers_footers(self):
        if not self.master_doc:
            return

        print("  📄 Applying headers and footers...")
        meta = self.context.data.get("global_metadata", {})
        project_title = meta.get("project_title", "")
        abbr = (meta.get("department_abbr") or "CSE").strip().upper()
        department_label = f"DEPT. OF {abbr}, MVJCE"
        year = academic_year(meta.get("academic_year", ""))

        for idx, section in enumerate(self.master_doc.sections):
            sec_type = self._section_type(idx)
            section.different_first_page_header_footer = False
            if sec_type == "isolated":
                self._clear(section.header)
                self._clear(section.footer)
            elif sec_type == "preliminary":
                self._clear(section.header)
                self._format_footer_simple(section.footer)
            else:
                self._format_header(section.header, project_title)
                self._format_footer(section.footer, department_label, year)

    def _configure_page_numbering(self):
        """Upper-case Roman numerals for preliminary pages, Arabic from Chapter 1."""
        if not self.master_doc:
            return

        print("  📊 Configuring page numbering...")
        first_prelim, first_main = True, True
        for idx, section in enumerate(self.master_doc.sections):
            sectPr = section._sectPr
            for old in sectPr.findall(qn('w:pgNumType')):
                sectPr.remove(old)
            sec_type = self._section_type(idx)
            if sec_type == "isolated":
                continue
            pgNumType = OxmlElement('w:pgNumType')
            if sec_type == "preliminary":
                pgNumType.set(qn('w:fmt'), 'upperRoman')
                if first_prelim:
                    pgNumType.set(qn('w:start'), '1')
                    first_prelim = False
            else:
                pgNumType.set(qn('w:fmt'), 'decimal')
                if first_main:
                    pgNumType.set(qn('w:start'), '1')
                    first_main = False
            # pgNumType goes before cols/docGrid in the schema order
            anchor = sectPr.find(qn('w:cols'))
            if anchor is not None:
                anchor.addprevious(pgNumType)
            else:
                sectPr.append(pgNumType)

    # ========================================
    # TABLE OF CONTENTS & LIST OF FIGURES
    # ========================================

    def _marker_paragraph(self, marker):
        for p in self.master_doc.element.body.iter(qn("w:p")):
            if marker in "".join(t.text or "" for t in p.iter(qn("w:t"))):
                return p
        return None

    def _fill_table_of_contents(self):
        """Pre-fill the TOC field result with the entry list so it reads correctly even before
        Word updates it; updating the field adds the page numbers."""
        p = self._marker_paragraph(TOC_MARKER)
        if p is None:
            return
        for r in p.findall(qn("w:r")):
            if TOC_MARKER in "".join(t.text or "" for t in r.findall(qn("w:t"))):
                p.remove(r)
        style_names = {s.name for s in self.master_doc.styles}
        anchor = p
        for text, level in self.context.toc_entries:
            para = self.master_doc.add_paragraph()
            if f"toc {level}" in style_names:
                para.style = self.master_doc.styles[f"toc {level}"]
            _set_run_font(para.add_run(text), 12, level == 1)
            para.paragraph_format.space_after = Pt(4)
            anchor.addnext(para._p)
            anchor = para._p

    def _fill_list_of_figures(self):
        p = self._marker_paragraph(LOF_MARKER)
        if p is None:
            return
        figures = self.context.figures
        table = self.master_doc.add_table(rows=1 + max(1, len(figures)), cols=3)
        table.style = self.master_doc.styles["Table Grid"] if "Table Grid" in [s.name for s in self.master_doc.styles] else None
        widths = (Inches(1.3), Inches(3.9), Inches(1.1))
        for j, head in enumerate(("FIGURE NO.", "FIGURE NAME", "PAGE NO.")):
            cell = table.cell(0, j)
            cell.width = widths[j]
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _set_run_font(para.add_run(head), 12, True)
        if not figures:
            _set_run_font(table.cell(1, 1).paragraphs[0].add_run("No figures"), 12)
        for i, fig in enumerate(figures, start=1):
            cells = table.rows[i].cells
            for j, cell in enumerate(cells):
                cell.width = widths[j]
            c0 = cells[0].paragraphs[0]
            c0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _set_run_font(c0.add_run(fig["number"]), 12)
            _set_run_font(cells[1].paragraphs[0].add_run(fig["caption"]), 12)
            c2 = cells[2].paragraphs[0]
            c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_field(c2, f"PAGEREF {fig['bookmark']} \\h", "")
            for run in c2.runs:
                _set_run_font(run, 12)
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.space_before = Pt(3)
                    para.paragraph_format.space_after = Pt(3)
        p.addprevious(table._tbl)
        p.getparent().remove(p)
        print(f"  🖼 List of Figures: {len(figures)} figure(s)")

    def _request_field_update(self):
        """Ask Word to refresh fields (TOC page numbers, figure pages) when the file is opened."""
        settings = self.master_doc.settings.element
        for old in settings.findall(qn("w:updateFields")):
            settings.remove(old)
        el = OxmlElement("w:updateFields")
        el.set(qn("w:val"), "true")
        settings.append(el)

    def save(self, filename="full_report.docx"):
        output_path = os.path.join(self.context.output_dir, filename)
        if self.composer:
            self.composer.save(output_path)
            print(f"✅ Report Saved: {output_path}")
            # Where Word is available (local Windows runs) fill page numbers now
            if os.environ.get("REPORT_SKIP_WORD_UPDATE") != "1":
                self._auto_update_toc_with_word(output_path)
        else:
            print("⚠ Warning: No content to save.")

    # ========================================
    # AI CONTENT
    # ========================================

    def _perform_bulk_ai_generation(self):
        """Execute bulk AI requests to minimize API calls."""
        from services.gemini_service import GeminiService
        from services.prompt_templates import PromptTemplates

        # Check if AI is enabled globally or if ai_context is provided
        ai_config = self.context.data.get("ai_content_config", {})
        ai_context = self.context.data.get("ai_context", "").strip()

        # Auto-enable AI if ai_context is present (Frontend integration)
        ai_enabled = ai_config.get("enabled", False) or len(ai_context) > 10

        if not ai_enabled:
            print("⏭ AI content generation disabled. Skipping bulk requests.")
            return

        print("🤖 Triggering Bulk AI Content Generation...")
        ai_service = GeminiService()

        specs = ai_section_specs(self.context.report_type)
        wanted = getattr(self, "ai_sections", None)
        groups = [[k for k in batch if wanted is None or k in wanted]
                  for batch in self.context.report_type["ai_batches"]]
        groups = [g for g in groups if g]

        global_meta = self.context.data.get("global_metadata", {})
        prompt_context = {
            "project_title": global_meta.get("project_title", "Untitled Project"),
            "domain": global_meta.get("domain", "technology"),
            "report_label": self.context.report_type["label"],
            "ai_context": ai_context,
            "chapter_numbers": getattr(self, "chapter_numbers", {}),
        }

        for i, group in enumerate(groups):
            print(f"  -> Executing Step: BulkAIGeneration_{i+1}", flush=True)  # Caught by app.py for progress
            print(f"   Request {i+1}/{len(groups)}: Generating {', '.join(group)}...", flush=True)
            bulk_prompt = PromptTemplates.get_spec_bulk_prompt([specs[k] for k in group], prompt_context)
            raw_response = ai_service.generate_bulk_content(bulk_prompt)
            self.context.extract_bulk_content(raw_response)

        # app.py reads this line to tell the student which chapters are placeholders
        missing = [k for group in groups for k in group if k not in self.context.bulk_content]
        print(f"AI_MISSING_SECTIONS: {','.join(missing)}", flush=True)
        print("✅ Bulk AI generation completed.")

    def _auto_update_toc_with_word(self, output_path):
        """
        Use Word (Windows + pywin32) to update the TOC and figure page numbers.
        Skipped silently where Word is not available (e.g. the Linux server); the file
        then asks Word to update fields when the student opens it.
        """
        try:
            import win32com.client
            import pythoncom
        except ImportError:
            return

        word = None
        try:
            print("  🔄 Updating TOC page numbers with Microsoft Word...")
            pythoncom.CoInitialize()
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            doc = word.Documents.Open(os.path.abspath(output_path))
            for toc in doc.TablesOfContents:
                toc.Update()
            doc.Fields.Update()
            doc.Save()
            doc.Close()
            print("     ✅ TOC updated")
        except Exception as e:
            print(f"     ⚠️  Could not update TOC with Word: {e}")
        finally:
            if word is not None:
                try:
                    word.Quit()
                except Exception:
                    pass
