"""
Turns the student-facing form the frontend sends into the full report data main.py reads.

The form only asks for what a student knows: the project, the team, the guide, what they
built and the papers they read. College and department details (HOD, Dean, Principal, COE)
come from backend/data, so students cannot get them wrong.
"""

import copy
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend", "scripts", "v2_architecture"))
from report_types import ai_section_specs, get_report_type  # noqa: E402
from services.prompt_templates import PromptTemplates  # noqa: E402
TEMPLATE_FILE = os.path.join(PROJECT_ROOT, "backend", "data", "full_report_template.json")
DEPARTMENTS_FILE = os.path.join(PROJECT_ROOT, "backend", "data", "departments_context.json")

REPORT_TYPES = {"major_project_phase2"}
MAX_STUDENTS = 4
MAX_PAPERS = 15
MAX_CHAPTER_CHARS = 40000

# "own": the students wrote the chapters in their own AI chat and pasted them (no AI on our side);
# "server": our AI writes them from the answers in the form.
WRITING_MODES = {"own", "server"}

# Order and labels of the "About your project" answers in the AI context
ABOUT_FIELDS = [
    ("summary", "What the project is and the problem it solves"),
    ("tech", "Hardware, software and tools used"),
    ("modules", "Main modules and how the system works"),
    ("results", "Results and testing"),
    ("limitations", "Limitations and future plans"),
]


class FormError(ValueError):
    """A problem the student can fix; the message is shown to them as is."""


def _text(value, limit=3000):
    return re.sub(r"[ \t]+", " ", str(value or "")).strip()[:limit]


def load_departments():
    with open(DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compile_ai_context(form):
    """The students' answers as one block of project facts for the AI prompt."""
    about = form.get("about") or {}
    parts = []
    for key, label in ABOUT_FIELDS:
        answer = _text(about.get(key))
        if answer:
            parts.append(f"{label}:\n{answer}")

    papers = [p for p in (form.get("papers") or [])[:MAX_PAPERS] if _text((p or {}).get("title"))]
    if papers:
        lines = ["Research papers the students referred to (the literature survey and references use only these):"]
        for i, paper in enumerate(papers, start=1):
            lines.append(f"{i}. Title: {_text(paper.get('title'), 300)}")
            lines.append(f"   Authors: {_text(paper.get('authors'), 400) or 'not given'}")
            lines.append(f"   Year: {_text(paper.get('year'), 10) or 'not given'}")
            lines.append(f"   Venue: {_text(paper.get('venue'), 300) or 'not given'}")
            notes = _text(paper.get("notes"), 1200)
            if notes:
                lines.append(f"   What it is about: {notes}")
        parts.append("\n".join(lines))
    else:
        parts.append("Research papers: none supplied.")
    return "\n\n".join(parts)


def writing_mode(form):
    return form.get("writingMode") if form.get("writingMode") in WRITING_MODES else "server"


def _wanted(form, display):
    sections = form.get("sections")
    return not (isinstance(sections, list) and sections) or display in sections


def chat_sections(form):
    """(key, display name) of every section the students write in their own chat, in report order."""
    report_type = get_report_type(form.get("reportType"))
    names = {"abstract": "Abstract", **{c["key"]: c["display"] for c in report_type["chapters"]}}
    keys = [k for part in report_type["chat_parts"] for k in part["sections"]]
    return [(k, names[k]) for k in keys if _wanted(form, names[k])]


def pasted_chapters(form):
    chapters = form.get("chapters") if isinstance(form.get("chapters"), dict) else {}
    known = {k for k, _ in chat_sections(form)}
    return {k: str(v).strip()[:MAX_CHAPTER_CHARS] for k, v in chapters.items() if k in known and str(v or "").strip()}


def unwritten_sections(form):
    """Sections the students chose to write themselves but did not paste."""
    if writing_mode(form) != "own":
        return []
    pasted = pasted_chapters(form)
    return [k for k, _ in chat_sections(form) if k not in pasted]


def references_from_papers(form):
    """The references list, built from the papers the students entered (never by an AI)."""
    papers = [p for p in (form.get("papers") or [])[:MAX_PAPERS] if _text((p or {}).get("title"))]
    if not papers:
        return "1. [Add reference]"
    lines = []
    for i, p in enumerate(papers, start=1):
        authors = _text(p.get("authors"), 400) or "[Add authors]"
        venue = _text(p.get("venue"), 300) or "[Add venue]"
        year = _text(p.get("year"), 10) or "[Year]"
        lines.append(f'{i}. {authors}. "{_text(p.get("title"), 300).rstrip(".")}." {venue}, {year}.')
    return "\n".join(lines)


def chat_prompt_parts(form):
    """The prompts students paste into their own AI chat, one per part of the report."""
    report_type = get_report_type(form.get("reportType"))
    specs = ai_section_specs(report_type)
    wanted = {k for k, _ in chat_sections(form)}
    context = {
        "project_title": _text(form.get("title"), 300) or "Untitled Project",
        "domain": _text(form.get("domain"), 120) or "technology",
        "report_label": report_type["label"],
        "ai_context": compile_ai_context(form),
    }
    parts = [[k for k in part["sections"] if k in wanted] for part in report_type["chat_parts"]]
    parts = [keys for keys in parts if keys]
    names = dict(chat_sections(form))
    return [{
        "sections": [{"key": k, "label": names[k]} for k in keys],
        "prompt": PromptTemplates.get_chat_prompt([specs[k] for k in keys], context, i, len(parts)),
    } for i, keys in enumerate(parts, start=1)]


def validate_form(form, departments):
    if not isinstance(form, dict):
        raise FormError("The form data is missing. Refresh the page and try again.")
    if (form.get("reportType") or "major_project_phase2") not in REPORT_TYPES:
        raise FormError("This report type is not available yet.")
    if form.get("department") not in departments:
        raise FormError("Choose your department.")
    if not _text(form.get("title")):
        raise FormError("Enter your project title.")
    students = [s for s in form.get("students") or [] if _text((s or {}).get("name")) or _text((s or {}).get("usn"))]
    if not students:
        raise FormError("Add at least one team member.")
    if len(students) > MAX_STUDENTS:
        raise FormError(f"A team can have at most {MAX_STUDENTS} members.")
    for s in students:
        if not _text(s.get("name")) or not _text(s.get("usn")):
            raise FormError("Every team member needs both a name and a USN.")
    if not _text((form.get("guide") or {}).get("name")):
        raise FormError("Enter your guide's name.")
    if len(_text((form.get("about") or {}).get("summary"))) < 40:
        raise FormError("Describe your project in a few sentences so the chapters are about your work.")
    return students


def report_data_from_form(form):
    departments = load_departments()
    students = validate_form(form, departments)
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        data = copy.deepcopy(json.load(f))

    dept_key = form["department"]
    dept = departments[dept_key]
    abbr = dept.get("short") or dept_key
    guide = form.get("guide") or {}
    guide_name = _text(guide.get("name"), 120)
    guide_designation = _text(guide.get("designation"), 120) or "Assistant Professor"

    meta = data["global_metadata"]
    meta.update({
        "project_title": _text(form.get("title"), 300),
        "project_subtitle": "",
        "domain": _text(form.get("domain"), 120),
        "project_type": "Major Project",
        "academic_year": _text(form.get("academicYear"), 20),
        "semester": _text(form.get("semester"), 10) or "VIII",
        "department_name": dept.get("name", ""),
        "department_abbr": abbr,
        "department_short": abbr,
        "city_code": "Bangalore - 67",
    })

    people = data["people"]
    people["students"] = [{"name": _text(s["name"], 120), "usn": _text(s["usn"], 20).upper()} for s in students]
    people["guide"] = [{
        "name": guide_name,
        "designation": guide_designation,
        "department": f"Department of {abbr}",
        "role": "Internal Guide",
    }]
    people["approvers"]["hod"] = dept.get("hod", {})
    people["approvers"]["dean"] = dept.get("dean", {})

    cert = data["certificate_info"]
    cert.update({
        "guide_name": guide_name,
        "guide_designation": guide_designation,
        "hod_name": dept.get("hod", {}).get("name", ""),
        "hod_designation": dept.get("hod", {}).get("designation", ""),
        "dean_name": dept.get("dean", {}).get("name", ""),
        "dean_designation": dept.get("dean", {}).get("designation", ""),
        "project_type": "Major Project",
    })

    # The template's sample texts must never reach a student's report
    data["report_content"] = {}
    data["report_type"] = form.get("reportType") or "major_project_phase2"
    data["ai_context"] = compile_ai_context(form)
    if writing_mode(form) == "own":
        # Chapters come from the students' own AI chat; the builder only formats them
        data["report_content"] = {k: {"text": v} for k, v in pasted_chapters(form).items()}
        data["report_content"]["references"] = {"text": references_from_papers(form)}
        data["ai_context"] = ""
        data["ai_content_config"]["enabled"] = False
    sections = form.get("sections")
    data["custom_sections"] = [str(s) for s in sections] if isinstance(sections, list) and sections else None
    return data
