import os
import sys
import argparse
from functools import partial

# Add the script directory to path to allow importing from components
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from builder import ReportBuilder, ReportContext
from report_types import LEGACY_SECTION_NAMES
from components.front_matter import (
    FrontPageGenerator, CertificateGenerator, DeclarationGenerator, AcknowledgementGenerator,
)
from components.chapters import (
    AbstractGenerator, TableOfContentsGenerator, ListOfFiguresGenerator,
    ChapterGenerator, ReferencesGenerator,
)

FRONT_MATTER = {
    # kind: (generator, section type)
    "front_page": (FrontPageGenerator, "isolated"),
    "certificate": (CertificateGenerator, "isolated"),
    "declaration": (DeclarationGenerator, "isolated"),
    "acknowledgement": (AcknowledgementGenerator, "preliminary"),
    "abstract": (AbstractGenerator, "preliminary"),
    "table_of_contents": (TableOfContentsGenerator, "preliminary"),
    "list_of_figures": (ListOfFiguresGenerator, "preliminary"),
}


def main():
    parser = argparse.ArgumentParser(description='Generate Project Report')
    parser.add_argument('--data', help='Path to input JSON data file')
    parser.add_argument('--output', help='Path to output DOCX file')
    args = parser.parse_args()

    print("🚀 Starting V2 Report Assembly (Single Object Workflow)...", flush=True)

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    context = ReportContext(project_root, data_file=args.data)
    report_type = context.report_type
    print(f"📘 Report type: {report_type['label']}")

    builder = ReportBuilder(context)

    # None means "everything"; older frontends send legacy chapter names
    custom = context.data.get("custom_sections", None)
    if custom is not None:
        custom = {LEGACY_SECTION_NAMES.get(name, name) for name in custom}

    def wanted(display):
        return custom is None or display in custom

    chapters = [c for c in report_type["chapters"] if wanted(c["display"])]
    has_figures = any(c.get("figures") for c in chapters)

    ai_sections = set()
    for display, kind in report_type["front_matter"]:
        if not wanted(display):
            continue
        if kind == "list_of_figures" and not has_figures:
            continue
        generator, sec_type = FRONT_MATTER[kind]
        builder.add_step(generator, section_type=sec_type, name=display)
        if kind == "abstract":
            ai_sections.add(report_type["abstract"]["key"])

    for number, spec in enumerate(chapters, start=1):
        builder.add_step(partial(ChapterGenerator, spec=spec, number=number),
                         section_type="main", name=spec["display"])
        ai_sections.add(spec["key"])

    references = report_type["references"]
    if wanted(references["display"]):
        builder.add_step(ReferencesGenerator, section_type="main", name=references["display"])
        ai_sections.add(references["key"])

    builder.ai_sections = ai_sections

    # An absolute --output path wins over the output dir inside builder.save
    output_filename = args.output if args.output else "full_report_v2.docx"
    builder.build().save(output_filename)

    print("✨ Process Completed.")


if __name__ == "__main__":
    main()
