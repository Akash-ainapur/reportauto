"""
Report type registry.

Each report type (Major Project Phase II, Minor Project, Open Elective, ...) describes:
  - the wording that changes between types (front page heading, certificate text)
  - its template folder under backend/templates/report_types/<templates>
    (cut from the department's reference report with tools/extract_reference_templates.py)
  - the ordered front matter and chapters, with the AI instructions for each chapter

To add a new type: drop its reference report through the extraction tool, then add an
entry here. The builder, front matter fillers and chapter renderer are shared.
"""

DEFAULT_REPORT_TYPE = "major_project_phase2"

# Formatting rules every chapter prompt shares. The renderer numbers headings and
# figures itself, so the model must not.
MARKDOWN_RULES = (
    "FORMAT RULES (follow exactly):\n"
    "- Plain paragraphs separated by a blank line. Formal, third-person academic English.\n"
    "- '## Heading' for a sub-section and '### Heading' for a sub-sub-section. "
    "Do NOT number headings and do NOT repeat the chapter title; numbering is added automatically.\n"
    "- Lists: one item per line as '- **Lead phrase:** explanation' (or '- **Item** – purpose' for short items).\n"
    "- Use **bold** only for key terms and list lead phrases.\n"
    "- No tables unless asked, no code blocks, no emojis.\n"
)

FIGURE_RULE = (
    "- Where a diagram, photo or screenshot belongs, put a line '[[FIGURE: caption]]' right after the "
    "paragraph that discusses it; the student pastes the real image there. Captions are 2-6 words in "
    "Title Case naming the thing shown, e.g. 'System Architecture Flowchart', 'ESP32 Microcontroller', "
    "'Web Interface Dashboard' - never a sentence.\n"
)

# Fabricated citations in a submitted report are an academic-integrity problem, so the
# literature survey and references only use papers the students supplied.
NO_PAPERS_ENTRY = (
    "## [Add paper title]\n**AUTHORS:** [Add authors]\n**PUBLISHED ON:** [Year]\n"
    "[Add a 110-150 word summary of the paper and its relevance to this project.]"
)

MAJOR_PROJECT_PHASE2_CHAPTERS = [
    {
        "key": "introduction",
        "title": "INTRODUCTION",
        "display": "Introduction",
        "words": 650,
        "instructions": (
            "Write the INTRODUCTION chapter as 4-5 substantial paragraphs with NO sub-headings: "
            "the real-world context and why the problem matters, what the project builds, "
            "the vision/approach and core technologies, and a closing paragraph outlining what this report covers."
        ),
    },
    {
        "key": "problem_statement",
        "title": "PROBLEM STATEMENT",
        "display": "Problem Statement",
        "words": 450,
        "instructions": (
            "Write the PROBLEM STATEMENT chapter as 3-4 paragraphs with NO sub-headings: the concrete problem, "
            "why existing approaches fall short, and what an effective solution must achieve."
        ),
    },
    {
        "key": "literature_survey",
        "title": "LITERATURE SURVEY",
        "display": "Literature Survey",
        "words": None,  # one entry per supplied paper; a word target would push the model to pad with invented papers
        "style": "literature",
        "instructions": (
            "Write the LITERATURE SURVEY chapter with one entry for EACH research paper listed in the project "
            "context and NO other papers. Keep titles, authors and years exactly as given; order newest first. "
            "Each entry is exactly:\n"
            "## <Paper title>\n"
            "**AUTHORS:** <Author One; Author Two; Author Three>\n"
            "**PUBLISHED ON:** <year>\n"
            "<one paragraph of 110-150 words: what the paper proposes, its method and results, and its relevance "
            "to this project, based on what the context says about it>\n\n"
            "If the context lists no papers, output only this placeholder entry:\n" + NO_PAPERS_ENTRY
        ),
    },
    {
        "key": "existing_proposed",
        "title": "EXISTING AND PROPOSED SYSTEM",
        "display": "Existing and Proposed System",
        "words": 900,
        "instructions": (
            "Write the EXISTING AND PROPOSED SYSTEM chapter with exactly this structure:\n"
            "## Existing System\n<2 paragraphs on how the problem is handled today>\n"
            "### Disadvantages of Existing System\n<4-5 list items '- **Lead:** explanation'>\n"
            "## Proposed System\n<2 paragraphs describing the proposed solution and how it works>\n"
            "### Advantages of Proposed System\n<4-5 list items '- **Lead:** explanation'>"
        ),
    },
    {
        "key": "requirement_specification",
        "title": "REQUIREMENT SPECIFICATION",
        "display": "Requirement Specification",
        "words": 800,
        "instructions": (
            "Write the REQUIREMENT SPECIFICATION chapter with exactly these sections:\n"
            "## Functional Requirements\n<1-2 paragraphs>\n"
            "## Non-Functional Requirements\n<1-2 paragraphs covering performance, reliability, usability, security>\n"
            "## Hardware Requirements\n<list of short items '- **Component** – purpose'>\n"
            "## Software Requirements\n<list of short items '- **Tool / library** – purpose'>"
        ),
    },
    {
        "key": "implementation",
        "title": "IMPLEMENTATION",
        "display": "Implementation",
        "words": 1800,
        "figures": True,
        "instructions": (
            "Write the IMPLEMENTATION chapter:\n"
            "## System Design\n<2-3 paragraphs on the overall architecture and data flow>, a system architecture figure, "
            "then a short paragraph and a list of the main modules as '- **Module name:** what it does'.\n"
            "Then one '## <Module name>' section per module (3-5 modules), each with an intro paragraph and "
            "'### <Component>' sub-sections (2-4 per module) explaining each key component, library or algorithm. "
            "Add a figure for important components."
        ),
    },
    {
        "key": "results",
        "title": "RESULTS",
        "display": "Results",
        "words": 700,
        "figures": True,
        "instructions": (
            "Write the RESULTS chapter as 3-4 '## <Result area>' sections (e.g. the built system, the user interface, "
            "model / system performance). Each section: a short paragraph explaining what is shown and what it means, "
            "followed by 1-3 figures for screenshots, photos or graphs."
        ),
    },
    {
        "key": "testing_validation",
        "title": "TESTING AND VALIDATION",
        "display": "Testing and Validation",
        "words": 1100,
        "figures": True,
        "instructions": (
            "Write the TESTING AND VALIDATION chapter: an opening paragraph on the testing approach, then\n"
            "## Unit Testing\n<paragraph> followed by one '### <Module> Testing' sub-section per main module, "
            "written as 1-2 paragraphs (no lists) covering what was tested, how, and the observed result; "
            "add a figure where a test output belongs\n"
            "## Integration Testing\n<paragraph>\n"
            "## Error Rates and Troubleshooting\n<2 paragraphs on issues found, their impact and fixes>"
        ),
    },
    {
        "key": "limitations_future",
        "title": "LIMITATIONS AND FUTURE ENHANCEMENTS",
        "display": "Limitations and Future Enhancements",
        "words": 800,
        "instructions": (
            "Write the LIMITATIONS AND FUTURE ENHANCEMENTS chapter: one opening paragraph, then\n"
            "## Limitations\n<4-5 list items '- **Lead:** explanation'>\n"
            "## Future Enhancements\n<5-7 list items '- **Lead:** explanation'>"
        ),
    },
    {
        "key": "conclusion",
        "title": "CONCLUSION",
        "display": "Conclusion",
        "words": 350,
        "instructions": (
            "Write the CONCLUSION chapter as 2 paragraphs with NO sub-headings: what was built and achieved, "
            "and its impact and outlook."
        ),
    },
]

REPORT_TYPES = {
    "major_project_phase2": {
        "label": "Major Project - Phase II",
        # Wording filled into the cut reference pages
        "report_name": "Project Phase II",          # certificate / declaration body
        "report_name_upper": "PROJECT PHASE II",    # front page: "A PROJECT PHASE II / REPORT ON"
        "report_category": "major project",         # "...incorporated in the major project report..."
        "templates": "major_project_phase2",
        "front_matter": [
            # (display name used by the frontend's custom_sections, kind)
            ("Front Page", "front_page"),
            ("Certificate", "certificate"),
            ("Declaration", "declaration"),
            ("Acknowledgement", "acknowledgement"),
            ("Abstract", "abstract"),
            ("Table of Contents", "table_of_contents"),
            ("List of Figures", "list_of_figures"),
        ],
        "abstract": {
            "key": "abstract",
            "words": 280,
            "instructions": (
                "Write the ABSTRACT as one paragraph (no heading, no lists): the problem, the system that was built "
                "and its key technologies, how it works, and the outcome / impact."
            ),
        },
        "chapters": MAJOR_PROJECT_PHASE2_CHAPTERS,
        "references": {
            "key": "references",
            "display": "References",
            "words": None,
            "instructions": (
                "Write the REFERENCES as a numbered list, one per line: '1. Surname, First, et al. \"Title.\" "
                "Conference or journal name. Publisher, Year.' Include exactly the papers listed in the project "
                "context, in the same order as the literature survey, and no others. Use only venue and publisher "
                "details the context gives; where missing write '[Add venue], Year.' instead of guessing. "
                "If the context lists no papers, output only: 1. [Add reference]"
            ),
        },
        # Prompts a student pastes into their own AI chat, one part per answer. Each part stays
        # around 2,000 words, which free chat apps return without cutting it short. References
        # are not here: they are built from the papers the students listed.
        "chat_parts": [
            {"title": "Abstract, Introduction, Problem Statement, Literature Survey",
             "sections": ["abstract", "introduction", "problem_statement", "literature_survey"]},
            {"title": "Existing and Proposed System, Requirement Specification",
             "sections": ["existing_proposed", "requirement_specification"]},
            {"title": "Implementation", "sections": ["implementation"]},
            {"title": "Results, Testing and Validation", "sections": ["results", "testing_validation"]},
            {"title": "Limitations and Future Enhancements, Conclusion",
             "sections": ["limitations_future", "conclusion"]},
        ],
        # Sections sent to the model together in one request
        "ai_batches": [
            ["abstract", "introduction", "problem_statement"],
            ["literature_survey", "references"],
            ["existing_proposed", "requirement_specification"],
            ["implementation"],
            ["results", "testing_validation"],
            ["limitations_future", "conclusion"],
        ],
    },
}

# Names the frontend used before chapters were renamed to match the Phase II format
LEGACY_SECTION_NAMES = {
    "Existing System & Proposed System": "Existing and Proposed System",
    "Methodology": "Implementation",
    "Requirements": "Requirement Specification",
}


def get_report_type(name):
    return REPORT_TYPES.get(name or DEFAULT_REPORT_TYPE, REPORT_TYPES[DEFAULT_REPORT_TYPE])


def ai_section_specs(report_type):
    """All AI-written sections of a report type, keyed by their tag name."""
    specs = {report_type["abstract"]["key"]: report_type["abstract"],
             report_type["references"]["key"]: report_type["references"]}
    for chapter in report_type["chapters"]:
        specs[chapter["key"]] = chapter
    return specs
