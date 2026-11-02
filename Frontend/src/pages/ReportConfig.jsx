import { useState, useEffect, useRef, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth, useClerk } from "@clerk/clerk-react";
import { ArrowLeft, ArrowRight, Eye, Lock, Sparkles, X } from "lucide-react";
import confetti from "canvas-confetti";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { cn } from "../lib/utils";
import { StepProject, StepTeam, StepAbout, StepReview } from "../components/report/FormSteps";
import StepWrite from "../components/report/StepWrite";
import { API_BASE } from "../lib/api";
import { GeneratingScreen, DoneScreen, SampleDoneScreen } from "../components/report/ResultScreens";
import {
    STEPS, SAMPLE_PROJECT, SAMPLE_REPORT_URL, emptyForm, loadDraft, stepErrors,
    storage, DRAFT_KEY, JOB_KEY,
} from "../data/reportForm";

// Local testing only: lets the generate button work without a Clerk session
const SKIP_SIGN_IN = import.meta.env.VITE_SKIP_SIGN_IN === "true";
const POLL_MS = 3000;
const JOB_MAX_AGE_MS = 60 * 60 * 1000; // the server deletes reports after an hour

const STEP_VIEWS = [StepProject, StepTeam, StepAbout, StepWrite, StepReview];

const ReportConfig = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const { isSignedIn, getToken } = useAuth();
    const { openSignIn } = useClerk();

    // The student's own answers; the sample project is shown instead without touching them
    const [form, setForm] = useState(() => loadDraft() || emptyForm());
    const [sampleMode, setSampleMode] = useState(() => searchParams.get("sample") === "1");
    const shown = sampleMode ? SAMPLE_PROJECT : form;

    const [step, setStep] = useState(0);
    const [showErrors, setShowErrors] = useState(false);
    const [phase, setPhase] = useState("form"); // form | generating | done | sampleDone
    const [job, setJob] = useState(null); // { sessionId, status }
    const [waking, setWaking] = useState(false);
    const [banner, setBanner] = useState(null); // error shown above the form
    const [credits, setCredits] = useState(null);
    const [pendingGenerate, setPendingGenerate] = useState(false);
    const pollTimer = useRef(null);
    const topRef = useRef(null);

    const errors = showErrors && !sampleMode ? stepErrors(shown, STEPS[step].key) : {};
    const signedIn = SKIP_SIGN_IN || isSignedIn;

    useEffect(() => { storage.set(DRAFT_KEY, form); }, [form]);

    // Each screen change starts at the top, where its heading and status are
    useEffect(() => { window.scrollTo({ top: 0 }); }, [phase]);

    // The free server sleeps when idle; wake it while the student is still typing
    useEffect(() => { fetch(`${API_BASE}/health`).catch(() => {}); }, []);

    const scrollTop = () => topRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });

    const authHeaders = useCallback(async () => {
        const token = signedIn && !SKIP_SIGN_IN ? await getToken() : null;
        return token ? { Authorization: `Bearer ${token}` } : {};
    }, [signedIn, getToken]);

    const loadCredits = useCallback(async () => {
        if (!isSignedIn) return;
        try {
            const res = await fetch(`${API_BASE}/api/credits`, { headers: await authHeaders() });
            if (res.ok) setCredits(await res.json());
        } catch { /* credits are informational */ }
    }, [isSignedIn, authHeaders]);

    useEffect(() => { loadCredits(); }, [loadCredits]);

    // --- Polling a running job (also resumes one after a reload or the phone killing the tab) ---
    const poll = useCallback((sessionId) => {
        clearTimeout(pollTimer.current);
        const tick = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/status?session_id=${sessionId}`);
                if (res.status === 404) {
                    storage.remove(JOB_KEY);
                    setPhase("form");
                    setBanner("We lost track of that report (the server restarted). Your details are saved - please generate again.");
                    return;
                }
                if (res.ok) {
                    const status = await res.json();
                    setJob({ sessionId, status });
                    if (status.error) {
                        storage.remove(JOB_KEY);
                        setPhase("form");
                        setStep(STEPS.length - 1);
                        setBanner(status.error);
                        return;
                    }
                    if (status.completed) {
                        setPhase("done");
                        confetti();
                        loadCredits();
                        return;
                    }
                }
            } catch { /* network blip: keep polling */ }
            pollTimer.current = setTimeout(tick, POLL_MS);
        };
        tick();
    }, [loadCredits]);

    useEffect(() => {
        const saved = storage.get(JOB_KEY);
        if (saved?.sessionId && Date.now() - saved.startedAt < JOB_MAX_AGE_MS) {
            setPhase("generating");
            setJob({ sessionId: saved.sessionId, status: null });
            poll(saved.sessionId);
        }
        return () => clearTimeout(pollTimer.current);
    }, [poll]);

    // --- Navigation ---
    const firstInvalidStep = (f) => STEPS.findIndex(s => Object.keys(stepErrors(f, s.key)).length > 0);

    const focusFirstError = (f, stepIndex) => {
        const first = Object.keys(stepErrors(f, STEPS[stepIndex].key))[0];
        setTimeout(() => {
            const el = document.getElementById(first);
            el?.scrollIntoView({ behavior: "smooth", block: "center" });
            el?.focus({ preventScroll: true });
        }, 50);
    };

    const goTo = (index) => {
        // Forward jumps only past finished steps, so nobody reaches Review with gaps
        const blocker = sampleMode ? -1 : firstInvalidStep(shown);
        const target = blocker !== -1 && blocker < index ? blocker : index;
        setStep(target);
        setShowErrors(target !== index);
        if (target !== index) focusFirstError(shown, target); else scrollTop();
    };

    const goNext = () => {
        if (!sampleMode && Object.keys(stepErrors(shown, STEPS[step].key)).length) {
            setShowErrors(true);
            focusFirstError(shown, step);
            return;
        }
        setShowErrors(false);
        setStep(s => s + 1);
        scrollTop();
    };

    const startSample = () => {
        setSampleMode(true);
        setStep(0);
        setShowErrors(false);
        setSearchParams({ sample: "1" }, { replace: true });
        scrollTop();
    };

    const exitSample = () => {
        setSampleMode(false);
        setPhase("form");
        setStep(0);
        setSearchParams({}, { replace: true });
        scrollTop();
    };

    const clearForm = () => {
        if (window.confirm("Clear everything you've typed and start again?")) {
            setForm(emptyForm());
            setStep(0);
            setShowErrors(false);
        }
    };

    // --- Generation ---
    const generate = async () => {
        const invalid = firstInvalidStep(form);
        if (invalid !== -1) {
            setStep(invalid);
            setShowErrors(true);
            focusFirstError(form, invalid);
            return;
        }
        // Chapters from the student's own chat cost us nothing, so only our AI needs a signed-in account
        if (!signedIn && form.writingMode !== "own") {
            setPendingGenerate(true);
            openSignIn();
            return;
        }
        setBanner(null);
        setPhase("generating");
        setJob(null);
        const wakeTimer = setTimeout(() => setWaking(true), 4000);
        try {
            const res = await fetch(`${API_BASE}/api/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json", ...(await authHeaders()) },
                body: JSON.stringify({ form }),
            });
            const body = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(body.error || "Could not start your report. Please try again.");
            storage.set(JOB_KEY, { sessionId: body.session_id, startedAt: Date.now() });
            setJob({ sessionId: body.session_id, status: null });
            poll(body.session_id);
        } catch (e) {
            setPhase("form");
            setBanner(e.message === "Failed to fetch"
                ? "Can't reach the server. Check your internet and try again - your details are saved."
                : e.message);
            scrollTop();
        } finally {
            clearTimeout(wakeTimer);
            setWaking(false);
        }
    };

    // Continue straight to generating once the sign-in window closes signed in
    useEffect(() => {
        if (pendingGenerate && isSignedIn) {
            setPendingGenerate(false);
            generate();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [pendingGenerate, isSignedIn]);

    const editAgain = () => {
        storage.remove(JOB_KEY);
        setPhase("form");
        setStep(STEPS.length - 1);
        scrollTop();
    };

    // --- Render ---
    const StepView = STEP_VIEWS[step];
    const isLast = step === STEPS.length - 1;
    const ownWriting = shown.writingMode === "own";
    const outOfCredits = !ownWriting && credits?.remaining === 0;

    let content;
    if (phase === "generating") {
        content = <GeneratingScreen status={job?.status} waking={waking} ownWriting={form.writingMode === "own"} />;
    } else if (phase === "done") {
        content = <DoneScreen status={job?.status} credits={credits} onEditAgain={editAgain}
            downloadUrl={`${API_BASE}/api/download?session_id=${job?.sessionId}`} />;
    } else if (phase === "sampleDone") {
        content = <SampleDoneScreen sampleUrl={SAMPLE_REPORT_URL} onStartOwn={exitSample} />;
    } else {
        content = (
            <div className="max-w-3xl mx-auto">
                {sampleMode ? (
                    <div className="mb-6 border-3 border-black bg-black text-white p-4 flex flex-col sm:flex-row sm:items-center gap-3">
                        <Eye className="w-6 h-6 shrink-0 text-retro-yellow" />
                        <p className="flex-1 text-sm">
                            <strong className="text-retro-yellow">Sample project.</strong> Every field is filled with made-up details and locked. Click through to see what each step asks, then download the finished report.
                        </p>
                        <div className="flex gap-2">
                            {!isLast && (
                                <button type="button" onClick={() => setStep(STEPS.length - 1)}
                                    className="px-3 py-2 bg-retro-yellow text-black font-bold text-sm border-2 border-white">Skip to the end</button>
                            )}
                            <button type="button" onClick={exitSample}
                                className="px-3 py-2 bg-white text-black font-bold text-sm border-2 border-white flex items-center gap-1"><X className="w-4 h-4" /> Exit</button>
                        </div>
                    </div>
                ) : step === 0 && (
                    <div className="mb-6 border-3 border-black bg-retro-yellow p-4 shadow-brutal flex flex-col sm:flex-row sm:items-center gap-3">
                        <Sparkles className="w-7 h-7 shrink-0" />
                        <div className="flex-1">
                            <p className="font-bold">First time here? See it work before typing anything.</p>
                            <p className="text-sm">Fills every step with a sample project, then gives you its finished report. No sign-in, no waiting, doesn't use your free reports.</p>
                        </div>
                        <button type="button" onClick={startSample}
                            className="px-4 py-3 bg-black text-white font-bold uppercase border-3 border-black whitespace-nowrap hover:bg-white hover:text-black">
                            Try a sample project
                        </button>
                    </div>
                )}

                {banner && (
                    <div role="alert" className="mb-6 border-3 border-red-700 bg-red-50 p-4 flex gap-3">
                        <p className="flex-1 font-bold text-red-800">{banner}</p>
                        <button type="button" onClick={() => setBanner(null)} aria-label="Dismiss"><X className="w-5 h-5" /></button>
                    </div>
                )}

                {/* Where am I */}
                <nav aria-label="Steps" className="mb-6">
                    <ol className="grid grid-cols-5 gap-1 sm:gap-2">
                        {STEPS.map((s, i) => (
                            <li key={s.key}>
                                <button type="button" onClick={() => goTo(i)} aria-current={i === step ? "step" : undefined}
                                    className={cn("w-full text-left border-3 border-black px-2 py-2 h-full",
                                        i === step ? "bg-retro-yellow shadow-neo" : i < step ? "bg-white" : "bg-white text-black/50")}>
                                    <span className="block text-xs font-bold">{i < step ? "✓ " : ""}Step {i + 1}</span>
                                    <span className="hidden sm:block text-sm font-bold leading-tight">{s.title}</span>
                                </button>
                            </li>
                        ))}
                    </ol>
                </nav>

                <div className="bg-white border-3 border-black shadow-brutal-lg">
                    <div className="p-4 md:p-8">
                        <div className="mb-6 flex items-start justify-between gap-4">
                            <div>
                                <h1 className="font-heading text-3xl md:text-4xl font-bold uppercase">{STEPS[step].title}</h1>
                                <p className="text-sm text-black/70 mt-1">{STEPS[step].blurb}</p>
                            </div>
                            {sampleMode && <Lock className="w-6 h-6 shrink-0" aria-label="Locked sample" />}
                            {!sampleMode && step === 0 && form.title && (
                                <button type="button" onClick={clearForm} className="text-sm underline shrink-0">Clear form</button>
                            )}
                        </div>

                        <fieldset disabled={sampleMode} className="min-w-0">
                            <StepView form={shown} setForm={setForm} errors={errors} goTo={goTo} editable={!sampleMode} />
                        </fieldset>

                        {isLast && !sampleMode && ownWriting && (
                            <div className="mt-6 text-sm space-y-1 border-t-2 border-black/10 pt-4">
                                <p>• Your pasted chapters are formatted into the report - usually ready in under a minute.</p>
                                <p>• Free and unlimited: no sign-in, doesn't use your free reports.</p>
                            </div>
                        )}
                        {isLast && !sampleMode && !ownWriting && (
                            <div className="mt-6 text-sm space-y-1 border-t-2 border-black/10 pt-4">
                                <p>• Takes about 2-5 minutes. You'll see live progress.</p>
                                {credits?.remaining != null
                                    ? <p>• Uses 1 of your free reports - <strong>{credits.remaining} of {credits.limit} left</strong>. A report with unwritten chapters isn't counted.</p>
                                    : <p>• Each account gets a limited number of free reports, so check names and USNs first.</p>}
                                {!signedIn && <p>• You'll be asked to sign in (Google works) - your answers stay saved.</p>}
                            </div>
                        )}
                    </div>

                    {/* Always-reachable actions, even on a long mobile form */}
                    <div className="sticky bottom-0 z-10 bg-white border-t-3 border-black p-3 md:p-4 flex gap-3">
                        {step > 0 && (
                            <button type="button" onClick={() => { setStep(s => s - 1); setShowErrors(false); scrollTop(); }}
                                className="px-4 py-3 border-3 border-black font-bold uppercase flex items-center gap-1 hover:bg-gray-100">
                                <ArrowLeft className="w-5 h-5" /> <span className="hidden sm:inline">Back</span>
                            </button>
                        )}
                        {!isLast ? (
                            <button type="button" onClick={goNext}
                                className="flex-1 font-heading text-xl font-bold uppercase py-3 bg-retro-yellow border-3 border-black shadow-brutal-sm hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none flex items-center justify-center gap-2">
                                <span className="sm:hidden">Next</span>
                                <span className="hidden sm:inline">Next: {STEPS[step + 1].title}</span>
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        ) : sampleMode ? (
                            <button type="button" onClick={() => { setPhase("sampleDone"); scrollTop(); }}
                                className="flex-1 font-heading text-xl font-bold uppercase py-3 bg-retro-purple text-white border-3 border-black shadow-brutal-sm hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none">
                                See the finished sample report
                            </button>
                        ) : (
                            <button type="button" onClick={generate} disabled={outOfCredits}
                                className="flex-1 font-heading text-xl font-bold uppercase py-3 bg-retro-purple text-white border-3 border-black shadow-brutal-sm hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none disabled:bg-gray-300 disabled:text-gray-600 disabled:shadow-none disabled:translate-x-0 disabled:translate-y-0">
                                {outOfCredits ? "No free reports left" : ownWriting ? "Build my report" : signedIn ? "Generate my report" : "Sign in & generate"}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white flex flex-col">
            <Navbar />
            <main ref={topRef} className="flex-1 px-4 pt-32 md:pt-28 pb-16 scroll-mt-28">
                {content}
            </main>
            <Footer />
        </div>
    );
};

export default ReportConfig;
