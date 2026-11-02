// What the report form collects, how it is checked, and where drafts are kept.
// The backend (backend_flask/form_payload.py) turns this form into the full report data.
import departmentData from "../../../backend/data/departments_context.json";
import sampleProject from "./sampleProject.json";

export const SAMPLE_PROJECT = sampleProject;
export const SAMPLE_REPORT_URL = "/samples/sample-major-project-phase-2.docx";

export const REPORT_TYPES = [
    { key: "major_project_phase2", label: "Major Project – Phase II", note: "8th semester final report" },
    { key: "minor_project", label: "Minor Project", note: "Coming soon", disabled: true },
    { key: "open_elective", label: "Open Elective", note: "Coming soon", disabled: true },
];

export const DEPARTMENTS = Object.entries(departmentData).map(([key, d]) => ({
    key,
    label: `${d.name} (${d.short || key})`,
    hod: d.hod?.name,
    dean: d.dean?.name,
}));

// Sections of the Major Project Phase II report (backend: report_types.py)
export const REPORT_SECTIONS = [
    "Front Page", "Certificate", "Declaration",
    "Acknowledgement", "Abstract", "Table of Contents", "List of Figures",
    "Introduction", "Problem Statement", "Literature Survey",
    "Existing and Proposed System", "Requirement Specification", "Implementation",
    "Results", "Testing and Validation", "Limitations and Future Enhancements",
    "Conclusion", "References",
];

export const SEMESTERS = ["V", "VI", "VII", "VIII"];
export const GUIDE_DESIGNATIONS = ["Assistant Professor", "Associate Professor", "Professor", "Professor & Head"];
export const MAX_STUDENTS = 4;

// Academic years run July-June: in Nov 2026 the current one is 2026-27
export function academicYears(today = new Date()) {
    const start = today.getMonth() >= 6 ? today.getFullYear() : today.getFullYear() - 1;
    return [start - 1, start, start + 1].map(y => `${y}-${String(y + 1).slice(-2)}`);
}

export function emptyForm() {
    return {
        reportType: "major_project_phase2",
        department: "",
        academicYear: academicYears()[1],
        semester: "VIII",
        title: "",
        domain: "",
        students: [{ name: "", usn: "" }],
        guide: { name: "", designation: "" },
        about: { summary: "", tech: "", modules: "", results: "", limitations: "" },
        papers: [],
        sections: null,
        // "own": chapters written in the student's own AI chat and pasted back; "server": our AI writes them
        writingMode: "own",
        chapters: {},
    };
}

export const wordCount = (text) => (text || "").trim().split(/\s+/).filter(Boolean).length;

const USN_PATTERN = /^1MJ\d{2}[A-Z]{2,3}\d{3}$/;
export const usnLooksOdd = (usn) => Boolean(usn?.trim()) && !USN_PATTERN.test(usn.trim());

export const STEPS = [
    { key: "project", title: "Project", blurb: "What report you need and what your project is called." },
    { key: "team", title: "Team & guide", blurb: "Printed on the front page, certificate and declaration." },
    { key: "about", title: "About your project", blurb: "The chapters are written from these answers. More detail, better report." },
    { key: "write", title: "Write chapters", blurb: "Have your own AI chat write them (free, instant), or let us." },
    { key: "review", title: "Review", blurb: "Check everything once, then generate." },
];

// Errors that block moving on, keyed by field id (the input with that id gets focus)
export function stepErrors(form, stepKey) {
    const errors = {};
    if (stepKey === "project") {
        if (!form.department) errors.department = "Choose your department.";
        if (!form.title.trim()) errors.title = "Enter your project title, exactly as approved.";
    }
    if (stepKey === "team") {
        form.students.forEach((s, i) => {
            if (!s.name.trim()) errors[`student-name-${i}`] = "Enter the name.";
            if (!s.usn.trim()) errors[`student-usn-${i}`] = "Enter the USN.";
        });
        if (!form.guide.name.trim()) errors["guide-name"] = "Enter your guide's name.";
    }
    if (stepKey === "about") {
        if (wordCount(form.about.summary) < 8) errors["about-summary"] = "Write at least a few sentences about your project.";
        form.papers.forEach((p, i) => {
            const touched = p.authors?.trim() || p.year?.trim() || p.venue?.trim() || p.notes?.trim();
            if (touched && !p.title.trim()) errors[`paper-title-${i}`] = "Add the paper's title, or remove this paper.";
        });
    }
    if (stepKey === "write" && form.writingMode === "own" && !Object.keys(form.chapters || {}).length) {
        errors["write-chapters"] = "Paste at least one part's answer below, or choose \"Let this site's AI write it\".";
    }
    return errors;
}

// Browser storage can be missing (private mode, blocked storage), so every access is guarded
export const storage = {
    get(key) {
        try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
    },
    set(key, value) {
        try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* draft just isn't kept */ }
    },
    remove(key) {
        try { localStorage.removeItem(key); } catch { /* nothing to remove */ }
    },
};

export const DRAFT_KEY = "reportgen.draft.v1";
export const JOB_KEY = "reportgen.job.v1";

export function loadDraft() {
    const saved = storage.get(DRAFT_KEY);
    if (!saved || typeof saved !== "object") return null;
    const base = emptyForm();
    return {
        ...base,
        ...saved,
        guide: { ...base.guide, ...saved.guide },
        about: { ...base.about, ...saved.about },
        students: Array.isArray(saved.students) && saved.students.length ? saved.students : base.students,
        papers: Array.isArray(saved.papers) ? saved.papers : [],
        chapters: saved.chapters && typeof saved.chapters === "object" ? saved.chapters : {},
    };
}
