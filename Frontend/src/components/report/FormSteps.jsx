import { useState } from "react";
import { Plus, X, Pencil, AlertTriangle, BookOpen, Info } from "lucide-react";
import { cn } from "../../lib/utils";
import { Field, TextInput, TextArea, Select, Card } from "./Fields";
import AiChatImport from "./AiChatImport";
import {
    REPORT_TYPES, DEPARTMENTS, SEMESTERS, GUIDE_DESIGNATIONS, MAX_STUDENTS, REPORT_SECTIONS,
    academicYears, usnLooksOdd, wordCount,
} from "../../data/reportForm";

// The four wizard steps. Each gets the form, a setter that takes an updater, and the errors to
// show for its fields (only after the student has tried to move on).

const setIn = (setForm, key, value) => setForm(f => ({ ...f, [key]: value }));

export const StepProject = ({ form, setForm, errors }) => {
    const dept = DEPARTMENTS.find(d => d.key === form.department);
    return (
        <div className="space-y-6">
            <fieldset>
                <legend className="block font-bold uppercase text-sm mb-2">Report type</legend>
                <div className="grid sm:grid-cols-3 gap-3">
                    {REPORT_TYPES.map(t => (
                        <label
                            key={t.key}
                            className={cn(
                                "border-3 border-black p-3 flex flex-col gap-1",
                                t.disabled ? "opacity-50 cursor-not-allowed border-dashed" : "cursor-pointer",
                                form.reportType === t.key && "bg-retro-yellow shadow-neo"
                            )}
                        >
                            <span className="flex items-center gap-2 font-bold">
                                <input
                                    type="radio"
                                    name="reportType"
                                    value={t.key}
                                    checked={form.reportType === t.key}
                                    disabled={t.disabled}
                                    onChange={() => setIn(setForm, "reportType", t.key)}
                                    className="w-4 h-4 accent-black"
                                />
                                {t.label}
                            </span>
                            <span className="text-xs text-black/60 pl-6">{t.note}</span>
                        </label>
                    ))}
                </div>
            </fieldset>

            <Field id="department" label="Department" required error={errors.department}
                hint={dept ? `HOD and Dean on your certificate: ${dept.hod} and ${dept.dean}.` : "Sets the HOD and Dean printed on your certificate."}>
                <Select id="department" value={form.department} onChange={v => setIn(setForm, "department", v)}
                    placeholder="Choose your department" error={errors.department}
                    options={DEPARTMENTS.map(d => ({ value: d.key, label: d.label }))} />
            </Field>

            <div className="grid grid-cols-2 gap-4">
                <Field id="academicYear" label="Academic year">
                    <Select id="academicYear" value={form.academicYear} onChange={v => setIn(setForm, "academicYear", v)}
                        options={academicYears()} />
                </Field>
                <Field id="semester" label="Semester">
                    <Select id="semester" value={form.semester} onChange={v => setIn(setForm, "semester", v)}
                        options={SEMESTERS} />
                </Field>
            </div>

            <Field id="title" label="Project title" required error={errors.title}
                hint="Exactly as your guide approved it. It is printed on the front page in capitals.">
                <TextInput id="title" value={form.title} onChange={v => setIn(setForm, "title", v)}
                    error={errors.title} placeholder="e.g. Smart Attendance System Using Face Recognition" maxLength={200} />
            </Field>

            <Field id="domain" label="Domain" hint="Optional. Helps the writing use the right terms.">
                <TextInput id="domain" value={form.domain} onChange={v => setIn(setForm, "domain", v)}
                    placeholder="e.g. Machine Learning, IoT, Web Development" maxLength={100} />
            </Field>
        </div>
    );
};

export const StepTeam = ({ form, setForm, errors }) => {
    const updateStudent = (i, key, value) =>
        setForm(f => ({ ...f, students: f.students.map((s, j) => (j === i ? { ...s, [key]: value } : s)) }));
    const removeStudent = (i) => setForm(f => ({ ...f, students: f.students.filter((_, j) => j !== i) }));
    const addStudent = () => setForm(f => ({ ...f, students: [...f.students, { name: "", usn: "" }] }));
    const setGuide = (key, value) => setForm(f => ({ ...f, guide: { ...f.guide, [key]: value } }));

    return (
        <div className="space-y-6">
            <div className="space-y-4">
                <h3 className="font-bold uppercase text-sm">Team members <span className="text-black/50 normal-case font-normal">({form.students.length} of {MAX_STUDENTS})</span></h3>
                {form.students.map((s, i) => (
                    <Card key={i} className="relative shadow-brutal-sm">
                        <div className="flex items-center justify-between mb-3">
                            <span className="font-bold text-sm">Member {i + 1}</span>
                            {form.students.length > 1 && (
                                <button type="button" onClick={() => removeStudent(i)}
                                    className="flex items-center gap-1 text-sm font-bold border-2 border-black px-2 py-1 hover:bg-retro-coral"
                                    aria-label={`Remove member ${i + 1}`}>
                                    <X className="w-4 h-4" /> Remove
                                </button>
                            )}
                        </div>
                        <div className="grid sm:grid-cols-2 gap-4">
                            <Field id={`student-name-${i}`} label="Full name" required error={errors[`student-name-${i}`]}>
                                <TextInput id={`student-name-${i}`} value={s.name} onChange={v => updateStudent(i, "name", v)}
                                    error={errors[`student-name-${i}`]} autoComplete="off" maxLength={80} placeholder="As in college records" />
                            </Field>
                            <Field id={`student-usn-${i}`} label="USN" required error={errors[`student-usn-${i}`]}
                                warning={usnLooksOdd(s.usn) ? "Double-check this - USNs usually look like 1MJ22CS001." : null}>
                                <TextInput id={`student-usn-${i}`} value={s.usn} onChange={v => updateStudent(i, "usn", v.toUpperCase().replace(/\s/g, ""))}
                                    error={errors[`student-usn-${i}`]} autoComplete="off" autoCapitalize="characters" maxLength={14} placeholder="1MJ22CS001" />
                            </Field>
                        </div>
                    </Card>
                ))}
                {form.students.length < MAX_STUDENTS && (
                    <button type="button" onClick={addStudent}
                        className="w-full py-3 border-3 border-black border-dashed hover:bg-retro-yellow/30 font-bold uppercase flex items-center justify-center gap-2 disabled:hidden">
                        <Plus className="w-5 h-5" /> Add team member
                    </button>
                )}
            </div>

            <Card className="bg-retro-blue/20 space-y-4">
                <h3 className="font-bold uppercase text-sm">Project guide</h3>
                <Field id="guide-name" label="Guide's name" required error={errors["guide-name"]}
                    hint="Include their title (Dr. / Prof. / Mrs. / Mr.). It is printed exactly like this on the certificate.">
                    <TextInput id="guide-name" value={form.guide.name} onChange={v => setGuide("name", v)}
                        error={errors["guide-name"]} placeholder="e.g. Dr. Priya Sharma" maxLength={80} />
                </Field>
                <Field id="guide-designation" label="Guide's designation" hint="Pick one or type your own.">
                    <TextInput id="guide-designation" list="designations" value={form.guide.designation}
                        onChange={v => setGuide("designation", v)} placeholder="Assistant Professor" maxLength={80} />
                    <datalist id="designations">
                        {GUIDE_DESIGNATIONS.map(d => <option key={d} value={d} />)}
                    </datalist>
                </Field>
            </Card>
        </div>
    );
};

const AboutQuestion = ({ id, label, hint, example, value, onChange, error, required, rows = 4 }) => (
    <Field id={id} label={label} required={required} hint={hint} error={error}>
        <TextArea id={id} value={value} onChange={onChange} error={error} hint={hint} rows={rows}
            placeholder={example} maxLength={3000} />
    </Field>
);

export const StepAbout = ({ form, setForm, errors }) => {
    const setAbout = (key) => (value) => setForm(f => ({ ...f, about: { ...f.about, [key]: value } }));
    const words = wordCount(form.about.summary);
    const papers = form.papers;
    const setPaper = (i, key, value) =>
        setForm(f => ({ ...f, papers: f.papers.map((p, j) => (j === i ? { ...p, [key]: value } : p)) }));
    const addPaper = () => setForm(f => ({ ...f, papers: [...f.papers, { title: "", authors: "", year: "", venue: "", notes: "" }] }));
    const removePaper = (i) => setForm(f => ({ ...f, papers: f.papers.filter((_, j) => j !== i) }));

    return (
        <div className="space-y-6">
            <AiChatImport form={form} setForm={setForm} />

            <div className="flex gap-3 p-3 border-2 border-black bg-secondary text-sm">
                <Info className="w-5 h-5 shrink-0 mt-0.5" />
                <p><strong>Or type the answers yourself</strong> - the way you'd explain your project to a friend; short notes are fine. The AI turns these facts into formal chapters, and <strong>only uses what you write here</strong>, so anything you leave out won't be in the report.</p>
            </div>

            <AboutQuestion id="about-summary" required label="What is your project and what problem does it solve?"
                hint="The most important answer. 3-6 sentences."
                example="e.g. An app that marks class attendance automatically using face recognition from a classroom camera. Manual roll call wastes 10 minutes per class and allows proxies..."
                value={form.about.summary} onChange={setAbout("summary")} error={errors["about-summary"]} rows={5} />
            <p className={cn("-mt-4 text-xs font-bold", words < 8 ? "text-black/50" : words < 40 ? "text-amber-700" : "text-green-700")}>
                {words} words {words >= 40 ? "- great" : words >= 8 ? "- OK, more detail gives better chapters" : ""}
            </p>

            <AboutQuestion id="about-tech" label="Hardware, software and tools you used"
                hint="Boards, sensors, languages, frameworks, libraries, models, databases."
                example="e.g. Raspberry Pi 4, Pi Camera, Python, OpenCV, face_recognition library, Flask, MySQL, React"
                value={form.about.tech} onChange={setAbout("tech")} rows={3} />
            <AboutQuestion id="about-modules" label="Main parts and how it works"
                hint="Used for the Implementation chapter. List the modules and what each does."
                example="e.g. Capture module takes a photo every 5 min; recognition module matches faces; dashboard shows reports to teachers..."
                value={form.about.modules} onChange={setAbout("modules")} />
            <AboutQuestion id="about-results" label="Results and testing"
                hint="What works, accuracy or numbers you measured, what you tested."
                example="e.g. 94% recognition accuracy on 40 students; works under 2 seconds per photo; tested in low light..."
                value={form.about.results} onChange={setAbout("results")} rows={3} />
            <AboutQuestion id="about-limitations" label="Limitations and future plans"
                example="e.g. Struggles with masks; needs Wi-Fi. Future: mobile app, SMS alerts to parents"
                value={form.about.limitations} onChange={setAbout("limitations")} rows={3} />

            <div className="space-y-4 pt-2">
                <div className="flex items-start gap-3">
                    <BookOpen className="w-6 h-6 shrink-0" />
                    <div>
                        <h3 className="font-bold uppercase text-sm">Research papers you referred to</h3>
                        <p className="text-sm text-black/70">Your Literature Survey and References use <strong>only these papers</strong> - nothing is made up. Skip this and those chapters get spaces for you to fill in later.</p>
                    </div>
                </div>
                {papers.map((p, i) => (
                    <Card key={i} className="shadow-brutal-sm space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="font-bold text-sm">Paper {i + 1}</span>
                            <button type="button" onClick={() => removePaper(i)} aria-label={`Remove paper ${i + 1}`}
                                className="flex items-center gap-1 text-sm font-bold border-2 border-black px-2 py-1 hover:bg-retro-coral">
                                <X className="w-4 h-4" /> Remove
                            </button>
                        </div>
                        <Field id={`paper-title-${i}`} label="Title" required error={errors[`paper-title-${i}`]}>
                            <TextInput id={`paper-title-${i}`} value={p.title} onChange={v => setPaper(i, "title", v)}
                                error={errors[`paper-title-${i}`]} maxLength={250} />
                        </Field>
                        <div className="grid sm:grid-cols-[1fr_7rem] gap-3">
                            <Field id={`paper-authors-${i}`} label="Authors" hint="Separate with semicolons.">
                                <TextInput id={`paper-authors-${i}`} value={p.authors} onChange={v => setPaper(i, "authors", v)}
                                    placeholder="A. Kumar; R. Rao" maxLength={300} />
                            </Field>
                            <Field id={`paper-year-${i}`} label="Year">
                                <TextInput id={`paper-year-${i}`} value={p.year} onChange={v => setPaper(i, "year", v.replace(/\D/g, ""))}
                                    inputMode="numeric" maxLength={4} placeholder="2024" />
                            </Field>
                        </div>
                        <Field id={`paper-venue-${i}`} label="Journal / conference" hint="Optional. Leave blank and the reference says [Add venue] for you to fill.">
                            <TextInput id={`paper-venue-${i}`} value={p.venue} onChange={v => setPaper(i, "venue", v)}
                                placeholder="e.g. IEEE ICCCNT 2024" maxLength={250} />
                        </Field>
                        <Field id={`paper-notes-${i}`} label="What is it about?" hint="One or two lines in your words. Optional, but the summary is better with it.">
                            <TextArea id={`paper-notes-${i}`} value={p.notes} onChange={v => setPaper(i, "notes", v)} rows={2} maxLength={1000} />
                        </Field>
                    </Card>
                ))}
                {papers.length < 15 && (
                    <button type="button" onClick={addPaper}
                        className="w-full py-3 border-3 border-black border-dashed hover:bg-retro-yellow/30 font-bold uppercase flex items-center justify-center gap-2">
                        <Plus className="w-5 h-5" /> Add a paper
                    </button>
                )}
            </div>
        </div>
    );
};

const ReviewBlock = ({ title, onEdit, editable, children }) => (
    <Card className="space-y-2">
        <div className="flex items-center justify-between gap-2">
            <h3 className="font-bold uppercase text-sm">{title}</h3>
            {editable && (
                <button type="button" onClick={onEdit} className="flex items-center gap-1 text-sm font-bold underline underline-offset-4">
                    <Pencil className="w-4 h-4" /> Edit
                </button>
            )}
        </div>
        <div className="text-sm space-y-1">{children}</div>
    </Card>
);

const Row = ({ label, children }) => (
    <p className="grid grid-cols-[7.5rem_1fr] gap-2"><span className="text-black/60">{label}</span><span className="font-bold break-words">{children || "-"}</span></p>
);

export const StepReview = ({ form, setForm, goTo, editable }) => {
    const [showSections, setShowSections] = useState(Boolean(form.sections));
    const dept = DEPARTMENTS.find(d => d.key === form.department);
    const type = REPORT_TYPES.find(t => t.key === form.reportType);
    const papers = form.papers.filter(p => p.title.trim());
    const answered = Object.values(form.about).filter(v => v.trim()).length;
    const sections = form.sections || REPORT_SECTIONS;
    const toggleSection = (name) => setForm(f => {
        const current = f.sections || REPORT_SECTIONS;
        const next = current.includes(name) ? current.filter(s => s !== name) : REPORT_SECTIONS.filter(s => s === name || current.includes(s));
        return { ...f, sections: next.length === REPORT_SECTIONS.length ? null : next };
    });

    return (
        <div className="space-y-4">
            <ReviewBlock title="Project" editable={editable} onEdit={() => goTo(0)}>
                <Row label="Report">{type?.label}</Row>
                <Row label="Title">{form.title}</Row>
                <Row label="Department">{dept?.label}</Row>
                <Row label="Year / Sem">{form.academicYear} · Semester {form.semester}</Row>
                <Row label="Domain">{form.domain}</Row>
            </ReviewBlock>

            <ReviewBlock title="Team & guide" editable={editable} onEdit={() => goTo(1)}>
                {form.students.map((s, i) => <Row key={i} label={s.usn || `Member ${i + 1}`}>{s.name}</Row>)}
                <Row label="Guide">{[form.guide.name, form.guide.designation].filter(Boolean).join(", ")}</Row>
                <Row label="Certificate">{dept ? `HOD ${dept.hod} · Dean ${dept.dean}` : null}</Row>
            </ReviewBlock>

            <ReviewBlock title="About your project" editable={editable} onEdit={() => goTo(2)}>
                <Row label="Answers">{answered} of 5 questions · {wordCount(Object.values(form.about).join(" "))} words</Row>
                <Row label="Papers">{papers.length ? `${papers.length} paper${papers.length > 1 ? "s" : ""}` : "None"}</Row>
                {!papers.length && (
                    <p className="flex gap-2 text-amber-800 bg-amber-50 border-2 border-amber-600 p-2 mt-2">
                        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                        No papers added. Your Literature Survey and References will have spaces to fill in yourself.
                    </p>
                )}
                {answered < 3 && form.writingMode !== "own" && (
                    <p className="flex gap-2 text-amber-800 bg-amber-50 border-2 border-amber-600 p-2 mt-2">
                        <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                        Few answers means more generic chapters. Adding your tools and modules makes a big difference.
                    </p>
                )}
            </ReviewBlock>

            <ReviewBlock title="Chapters" editable={editable} onEdit={() => goTo(3)}>
                {form.writingMode === "own" ? (
                    <>
                        <Row label="Written by">Your own AI chat</Row>
                        <Row label="Pasted">{Object.keys(form.chapters || {}).length} of 11 sections</Row>
                        {Object.keys(form.chapters || {}).length < 11 && (
                            <p className="flex gap-2 text-amber-800 bg-amber-50 border-2 border-amber-600 p-2 mt-2">
                                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                                Sections you haven't pasted will be left empty for you to write.
                            </p>
                        )}
                    </>
                ) : (
                    <Row label="Written by">This site's AI (uses 1 free report)</Row>
                )}
            </ReviewBlock>

            <ReviewBlock title="Sections">
                <p>{form.sections ? `${sections.length} of ${REPORT_SECTIONS.length} sections` : `All ${REPORT_SECTIONS.length} sections, in your department's Phase II format`}</p>
                {editable && (
                    <button type="button" onClick={() => setShowSections(s => !s)} className="text-sm font-bold underline underline-offset-4">
                        {showSections ? "Hide section list" : "Leave out some sections"}
                    </button>
                )}
                {showSections && (
                    <div className="grid sm:grid-cols-2 gap-1 pt-2">
                        {REPORT_SECTIONS.map(name => (
                            <label key={name} className="flex items-center gap-2 py-1 cursor-pointer">
                                <input type="checkbox" className="w-4 h-4 accent-black" checked={sections.includes(name)}
                                    disabled={!editable} onChange={() => toggleSection(name)} />
                                <span>{name}</span>
                            </label>
                        ))}
                    </div>
                )}
            </ReviewBlock>
        </div>
    );
};
