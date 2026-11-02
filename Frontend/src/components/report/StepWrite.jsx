import { useEffect, useState } from "react";
import { Check, ChevronDown, ChevronUp, ClipboardCopy, Loader2, MessageSquareText, RotateCcw, Server, Zap } from "lucide-react";
import { cn } from "../../lib/utils";
import { API_BASE } from "../../lib/api";
import { Card } from "./Fields";
import { copyText } from "../../lib/clipboard";
import { parseChapterAnswer, sectionLabel } from "../../data/chatChapters";

// Step 4: who writes the chapters. "own" = the student's AI chat, prompt by prompt, pasted back
// here (free, instant, no sign-in); "server" = our AI, from the answers in step 3.

const ModeCard = ({ active, onClick, icon, title, tags, children }) => (
    <button type="button" onClick={onClick} aria-pressed={active}
        className={cn("text-left border-3 border-black p-4 w-full flex flex-col gap-2", active ? "bg-retro-yellow shadow-neo" : "bg-white hover:bg-gray-50")}>
        <span className="flex items-center gap-2 font-bold text-lg">{icon} {title}</span>
        <span className="flex flex-wrap gap-1">
            {tags.map(t => <span key={t} className="text-xs font-bold border-2 border-black bg-white px-1.5 py-0.5">{t}</span>)}
        </span>
        <span className="text-sm">{children}</span>
    </button>
);

const PartCard = ({ index, total, part, chapters, onAdd }) => {
    const [showPrompt, setShowPrompt] = useState(false);
    const [copied, setCopied] = useState(false);
    const [answer, setAnswer] = useState("");
    const [note, setNote] = useState(null); // { ok, text }
    const keys = part.sections.map(s => s.key);
    const done = keys.filter(k => chapters[k]);
    const complete = done.length === keys.length;
    const [open, setOpen] = useState(!complete);

    const copy = async () => {
        const ok = await copyText(part.prompt);
        setCopied(ok);
        if (!ok) setShowPrompt(true);
        setTimeout(() => setCopied(false), 3000);
    };

    const add = () => {
        const { found, continued } = parseChapterAnswer(answer);
        const added = Object.keys(found);
        const extended = Object.keys(continued).filter(k => chapters[k]);
        if (!added.length && !extended.length) {
            setNote({ ok: false, text: "No sections found. Copy the AI's whole answer with the code block's copy button - it must include tags like <introduction>." });
            return;
        }
        onAdd(found, continued);
        setAnswer("");
        const stillMissing = keys.filter(k => !chapters[k] && !found[k]);
        setNote({
            ok: true,
            text: [
                added.length && `Added ${added.map(sectionLabel).join(", ")}.`,
                extended.length && `Continued ${extended.map(sectionLabel).join(", ")}.`,
                stillMissing.length && `Still missing: ${stillMissing.map(sectionLabel).join(", ")} - type "continue" in the chat and paste the rest here.`,
            ].filter(Boolean).join(" "),
        });
        if (!stillMissing.length) setOpen(false);
    };

    return (
        <Card className={cn("space-y-3", complete ? "bg-green-50" : "shadow-brutal-sm")}>
            <button type="button" onClick={() => setOpen(o => !o)} className="w-full flex items-start justify-between gap-3 text-left">
                <span>
                    <span className="block text-xs font-bold uppercase text-black/60">Part {index + 1} of {total}</span>
                    <span className="block font-bold">{part.sections.map(s => s.label).join(", ")}</span>
                </span>
                <span className={cn("shrink-0 text-xs font-bold border-2 border-black px-2 py-1 flex items-center gap-1", complete ? "bg-green-400" : "bg-white")}>
                    {complete ? <><Check className="w-3 h-3" /> Done</> : `${done.length}/${keys.length}`}
                </span>
            </button>

            <div className="flex flex-wrap gap-1">
                {part.sections.map(s => (
                    <span key={s.key} className={cn("text-xs border-2 px-1.5 py-0.5", chapters[s.key] ? "border-green-700 text-green-800 bg-white" : "border-black/30 text-black/50")}>
                        {chapters[s.key] ? "✓ " : ""}{s.label}
                    </span>
                ))}
            </div>

            {open && (
                <div className="space-y-3 pt-1">
                    <div className="flex flex-wrap gap-2">
                        <button type="button" onClick={copy}
                            className="px-4 py-2 bg-black text-white font-bold uppercase border-3 border-black flex items-center gap-2 hover:bg-white hover:text-black">
                            {copied ? <><Check className="w-4 h-4" /> Copied</> : <><ClipboardCopy className="w-4 h-4" /> Copy prompt {index + 1}</>}
                        </button>
                        <button type="button" onClick={() => setShowPrompt(s => !s)} className="px-2 py-2 font-bold text-sm underline underline-offset-4 flex items-center gap-1">
                            {showPrompt ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />} {showPrompt ? "Hide" : "See"} prompt
                        </button>
                    </div>
                    {showPrompt && (
                        <textarea readOnly value={part.prompt} rows={8} onFocus={e => e.target.select()}
                            className="w-full border-2 border-black p-2 font-mono text-xs bg-white" aria-label={`Prompt for part ${index + 1}`} />
                    )}
                    <label htmlFor={`part-answer-${index}`} className="block font-bold text-sm">Paste the chat's answer to part {index + 1}</label>
                    <textarea id={`part-answer-${index}`} value={answer} rows={4}
                        onChange={e => { setAnswer(e.target.value); setNote(null); }}
                        placeholder={`<${keys[0]}>\n...\n</${keys[0]}>`}
                        className="w-full bg-white border-3 border-black px-3 py-2 font-mono text-sm outline-none focus:shadow-neo" />
                    <button type="button" onClick={add} disabled={!answer.trim()}
                        className="w-full sm:w-auto px-4 py-2 bg-retro-yellow font-bold uppercase border-3 border-black shadow-brutal-sm disabled:opacity-50 disabled:shadow-none">
                        Add part {index + 1}
                    </button>
                </div>
            )}
            {note && <p role="status" className={cn("text-sm font-bold", note.ok ? "text-green-800" : "text-red-700")}>{note.text}</p>}
            {complete && !open && (
                <button type="button" onClick={() => setOpen(true)} className="text-sm underline flex items-center gap-1"><RotateCcw className="w-3 h-3" /> Paste again</button>
            )}
        </Card>
    );
};

const StepWrite = ({ form, setForm, errors, editable }) => {
    const [parts, setParts] = useState(null);
    const [loadError, setLoadError] = useState(null);
    const [attempt, setAttempt] = useState(0);
    const own = form.writingMode === "own";
    const chapters = form.chapters || {};

    // Prompts carry the project facts from steps 1-3, so they are built when this step opens
    useEffect(() => {
        if (!own) return;
        let cancelled = false;
        setLoadError(null);
        fetch(`${API_BASE}/api/chat-prompts`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ form: { ...form, chapters: undefined } }),
        })
            .then(r => (r.ok ? r.json() : Promise.reject(new Error())))
            .then(body => { if (!cancelled) setParts(body.parts); })
            .catch(() => { if (!cancelled) setLoadError(true); });
        return () => { cancelled = true; };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [own, attempt]);

    const setMode = (mode) => setForm(f => ({ ...f, writingMode: mode }));
    const addChapters = (found, continued) => setForm(f => {
        const next = { ...(f.chapters || {}), ...found };
        // A reply cut off mid-sentence continues the same paragraph; otherwise start a new one
        Object.entries(continued).forEach(([k, v]) => {
            if (next[k]) next[k] = /[.!?:)\]"']\s*$/.test(next[k]) ? `${next[k]}\n\n${v}` : `${next[k]} ${v}`;
        });
        return { ...f, chapters: next };
    });
    const pastedCount = Object.keys(chapters).length;

    return (
        <div className="space-y-6">
            <div className="grid sm:grid-cols-2 gap-3">
                <ModeCard active={own} onClick={() => setMode("own")} icon={<MessageSquareText className="w-5 h-5" />} title="Write it with my own AI chat"
                    tags={["Recommended", "Free", "Ready in seconds", "No sign-in"]}>
                    Best if ChatGPT, Gemini, Claude or Antigravity already knows your project. Copy 5 prompts, paste the answers back.
                </ModeCard>
                <ModeCard active={!own} onClick={() => setMode("server")} icon={<Server className="w-5 h-5" />} title="Let this site's AI write it"
                    tags={["Sign-in", "Uses 1 of 2 free reports", "2-5 minutes"]}>
                    Written from your answers in the last step. Good if no chat knows your project.
                </ModeCard>
            </div>

            {!own ? (
                <div className="flex gap-3 p-3 border-2 border-black bg-secondary text-sm">
                    <Zap className="w-5 h-5 shrink-0" />
                    <p>Our AI writes every chapter from your answers in "About your project" when you generate. The more detail you gave there, the better the chapters.</p>
                </div>
            ) : (
                <>
                    <div className="p-3 border-2 border-black bg-secondary text-sm space-y-1">
                        <p className="font-bold">How it works</p>
                        <p>1. Open the chat where you worked on your project (same conversation is best - it remembers your work).</p>
                        <p>2. Copy prompt 1, send it, then copy the answer with the <strong>copy button on its code block</strong> and paste it below. Repeat for each part, in the same chat.</p>
                        <p>3. If an answer stops halfway, type <strong>continue</strong> in the chat and paste the rest into the same box.</p>
                        <p className="text-black/70">References are made from the papers you listed - the chat never writes them.</p>
                    </div>

                    {errors["write-chapters"] && (
                        <p id="write-chapters" tabIndex={-1} className="font-bold text-red-700">{errors["write-chapters"]}</p>
                    )}

                    <p className="font-bold">{pastedCount} of 11 sections pasted</p>

                    {loadError ? (
                        <Card className="space-y-2">
                            <p className="font-bold">Couldn't load the prompts. The server may be waking up.</p>
                            <button type="button" onClick={() => setAttempt(a => a + 1)} className="px-3 py-2 border-3 border-black font-bold">Try again</button>
                        </Card>
                    ) : !parts ? (
                        <p className="flex items-center gap-2 text-sm"><Loader2 className="w-4 h-4 animate-spin" /> Preparing your prompts (the first load can take up to a minute while the server wakes up)…</p>
                    ) : (
                        <div className="space-y-3">
                            {parts.map((part, i) => (
                                <PartCard key={i} index={i} total={parts.length} part={part} chapters={chapters} onAdd={editable ? addChapters : () => {}} />
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default StepWrite;
