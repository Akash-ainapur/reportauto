import { useEffect, useState } from "react";
import { Check, Download, Loader2, AlertTriangle, Clock, FileText, ArrowRight, RotateCcw } from "lucide-react";
import { cn } from "../../lib/utils";
import { Card } from "./Fields";
import { LOADING_JOKES } from "../../data/loadingJokes";
import { sectionLabel } from "../../data/chatChapters";

// Shown while the server builds the report, and once it is ready. Both screens say what is
// happening in plain words and what the student has to do next.

const STAGES = [
    { key: "queue", label: "Waiting for a free slot" },
    { key: "write", label: "Writing your chapters" },
    { key: "format", label: "Formatting pages, TOC and figures" },
    { key: "done", label: "Ready to download" },
];

function stageOf(status) {
    if (!status) return "queue";
    if (status.completed) return "done";
    if (status.queue_position > 0 || status.current_step === "Queued" || status.current_step?.startsWith("Waiting")) return "queue";
    if (status.current_step?.startsWith("Formatting")) return "format";
    return "write";
}

// A new joke every few seconds, starting from a random one so a refresh isn't a rerun
const JokeTicker = () => {
    const [index, setIndex] = useState(() => Math.floor(Math.random() * LOADING_JOKES.length));
    useEffect(() => {
        const timer = setInterval(() => setIndex(i => (i + 1) % LOADING_JOKES.length), 7000);
        return () => clearInterval(timer);
    }, []);
    return (
        <div className="bg-black text-white border-3 border-black p-5 min-h-[7rem] flex items-center" aria-live="off">
            <p key={index} className="font-['VT323'] text-2xl leading-snug animate-in fade-in duration-500">&gt; {LOADING_JOKES[index]}</p>
        </div>
    );
};

export const GeneratingScreen = ({ status, waking, ownWriting }) => {
    const stage = stageOf(status);
    const stageIndex = STAGES.findIndex(s => s.key === stage);
    const pct = status ? Math.min(99, Math.round((status.progress / (status.total_steps || 24)) * 100)) : 0;
    const line = waking
        ? "Waking up the server - the first report after a quiet spell takes up to a minute to start."
        : status?.queue_position > 0
            ? `${status.queue_position} report${status.queue_position > 1 ? "s" : ""} ahead of you. Yours starts automatically.`
            : status?.current_step || "Starting";

    return (
        <div className="max-w-2xl mx-auto space-y-6" role="status" aria-live="polite">
            <div>
                <h1 className="font-heading text-4xl md:text-5xl font-bold uppercase">Building your report</h1>
                <p className="mt-2 font-bold">{line}</p>
            </div>

            <div className="bg-white border-3 border-black h-10 relative overflow-hidden" aria-label={`${pct}% done`}>
                <div className="h-full bg-retro-yellow border-r-3 border-black transition-all duration-700" style={{ width: `${Math.max(pct, 3)}%` }} />
                <span className="absolute inset-0 flex items-center justify-center font-heading text-xl font-bold">{pct}%</span>
            </div>

            <Card>
                <ol className="space-y-3">
                    {STAGES.map((s, i) => (
                        <li key={s.key} className={cn("flex items-center gap-3", i > stageIndex && "text-black/40")}>
                            <span className={cn("w-7 h-7 border-2 border-black flex items-center justify-center shrink-0",
                                i < stageIndex && "bg-green-400", i === stageIndex && "bg-retro-yellow")}>
                                {i < stageIndex ? <Check className="w-4 h-4" /> : i === stageIndex ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                            </span>
                            <span className={cn(i === stageIndex && "font-bold")}>{s.label}</span>
                        </li>
                    ))}
                </ol>
            </Card>

            <JokeTicker />

            <div className="flex gap-3 text-sm bg-secondary border-2 border-black p-3">
                <Clock className="w-5 h-5 shrink-0" />
                <p>{ownWriting ? "Usually under a minute - your chapters only need formatting." : "Usually 2-5 minutes, longer when many students generate at once."} You can switch apps or lock your phone - when you come back to this page it picks up where it left off.</p>
            </div>
        </div>
    );
};

const BEFORE_YOU_SUBMIT = [
    <>Open the file in <strong>Microsoft Word on a laptop</strong>. When Word asks to <strong>update fields</strong>, click <strong>Yes</strong> - that fills in the page numbers of the Table of Contents and List of Figures. (No prompt? Right-click the table of contents → Update Field → Update entire table.)</>,
    <>Replace every dashed <strong>[ Paste image here ]</strong> box with your real photo, screenshot or diagram. The figure captions and numbers are already done.</>,
    <><strong>Read every chapter.</strong> AI-written text can get details wrong. Fix anything that isn't true about your project - your guide will ask about it.</>,
    <>Fill in anything marked <strong>[Add …]</strong> (for example a paper's journal or conference in References).</>,
    <>Check names, USNs and your guide's name on the front page, certificate and declaration. Small fixes are easier in Word than generating again.</>,
];

export const Checklist = () => (
    <Card className="space-y-3">
        <h2 className="font-heading text-2xl font-bold uppercase">Before you submit</h2>
        <ol className="space-y-3">
            {BEFORE_YOU_SUBMIT.map((item, i) => (
                <li key={i} className="flex gap-3 text-sm leading-relaxed">
                    <span className="w-7 h-7 shrink-0 border-2 border-black bg-retro-yellow font-bold flex items-center justify-center">{i + 1}</span>
                    <span>{item}</span>
                </li>
            ))}
        </ol>
    </Card>
);

const DownloadButton = ({ href, label, fileName }) => (
    <a href={href} download={fileName}
        className="w-full sm:w-auto inline-flex items-center justify-center gap-3 font-heading text-2xl font-bold uppercase px-6 py-4 bg-retro-yellow border-3 border-black shadow-brutal-lg hover:shadow-brutal-sm hover:translate-x-1 hover:translate-y-1 transition-all">
        <Download className="w-7 h-7" /> {label}
    </a>
);

export const DoneScreen = ({ status, downloadUrl, credits, onEditAgain }) => {
    const missing = status?.missing_sections || [];
    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div>
                <h1 className="font-heading text-4xl md:text-5xl font-bold uppercase">Your report is ready</h1>
                <p className="mt-2 flex items-center gap-2"><FileText className="w-5 h-5" /> {status?.file_name || "Project_Report.docx"} · Word document</p>
            </div>
            <DownloadButton href={downloadUrl} label="Download report" fileName={status?.file_name} />
            <p className="text-sm text-black/70">Download it now - for privacy, reports are deleted from the server after one hour.</p>

            {missing.length > 0 && (
                <div className="flex gap-3 bg-amber-50 border-3 border-amber-600 p-4 text-sm">
                    <AlertTriangle className="w-6 h-6 shrink-0 text-amber-700" />
                    <div>
                        {status?.writing_mode === "own" ? (
                            <>
                                <p className="font-bold">These parts were not pasted, so they are empty: {missing.map(sectionLabel).join(", ")}.</p>
                                <p className="mt-1">They are marked in the report for you to write. Or go back, paste them, and build again - it's free.</p>
                            </>
                        ) : (
                            <>
                                <p className="font-bold">The AI service was busy, so these parts could not be written: {missing.map(sectionLabel).join(", ")}.</p>
                                <p className="mt-1">They are marked in the report for you to write. This attempt <strong>did not use</strong> one of your free reports, so you can also try again in a little while.</p>
                            </>
                        )}
                    </div>
                </div>
            )}
            {credits?.remaining != null && (
                <p className="text-sm font-bold">Free reports left on your account: {credits.remaining} of {credits.limit}</p>
            )}

            <Checklist />

            <button type="button" onClick={onEditAgain} className="flex items-center gap-2 font-bold underline underline-offset-4">
                <RotateCcw className="w-4 h-4" /> Change details and generate again
            </button>
        </div>
    );
};

export const SampleDoneScreen = ({ sampleUrl, onStartOwn }) => (
    <div className="max-w-2xl mx-auto space-y-6">
        <div>
            <p className="inline-block bg-black text-white font-bold uppercase text-xs px-2 py-1 mb-3">Sample project</p>
            <h1 className="font-heading text-4xl md:text-5xl font-bold uppercase">Here's what you get</h1>
            <p className="mt-2">This is the report for the sample project you just clicked through - made-up students, generated once in advance. Yours comes out in the same format, written from your own details.</p>
        </div>
        <DownloadButton href={sampleUrl} label="Download sample" fileName="Sample - Major Project Phase II Report.docx" />

        <Card className="space-y-2 text-sm">
            <h2 className="font-heading text-2xl font-bold uppercase">What's inside</h2>
            <ul className="list-disc pl-5 space-y-1">
                <li>Front page, certificate, declaration and acknowledgement filled with the team, guide, HOD and Dean</li>
                <li>Abstract, Table of Contents and List of Figures</li>
                <li>10 chapters, Introduction to Conclusion, numbered like your department's format (about 35 pages)</li>
                <li>A literature survey and references built only from the 3 papers entered</li>
                <li>Boxes marking where each photo or diagram goes, already captioned and numbered</li>
            </ul>
        </Card>

        <button type="button" onClick={onStartOwn}
            className="w-full inline-flex items-center justify-center gap-3 font-heading text-2xl font-bold uppercase px-6 py-4 bg-retro-purple text-white border-3 border-black shadow-brutal hover:shadow-brutal-sm hover:translate-x-1 hover:translate-y-1 transition-all">
            Start my own report <ArrowRight className="w-6 h-6" />
        </button>

        <Checklist />
    </div>
);
