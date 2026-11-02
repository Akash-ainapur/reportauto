import { useState } from "react";
import { Bot, Check, ClipboardCopy, ChevronDown, ChevronUp, Wand2 } from "lucide-react";
import { Card } from "./Fields";
import { buildAiChatPrompt, parseAiChatAnswer } from "../../data/aiChatPrompt";
import { copyText } from "../../lib/clipboard";

// "Let your AI chat fill this": students copy a prompt into the chat or coding agent that
// already knows their project, then paste its answer back and the About step fills itself.

const StepNumber = ({ n }) => (
    <span className="w-7 h-7 shrink-0 border-2 border-black bg-retro-yellow font-bold flex items-center justify-center">{n}</span>
);

const AiChatImport = ({ form, setForm }) => {
    const [copied, setCopied] = useState(false);
    const [showPrompt, setShowPrompt] = useState(false);
    const [answer, setAnswer] = useState("");
    const [result, setResult] = useState(null); // { ok, text }
    const prompt = buildAiChatPrompt(form.title.trim());

    const copy = async () => {
        const ok = await copyText(prompt);
        setCopied(ok);
        if (!ok) setShowPrompt(true);
        setTimeout(() => setCopied(false), 3000);
    };

    const fill = () => {
        const parsed = parseAiChatAnswer(answer);
        if (!parsed) {
            setResult({ ok: false, text: "Couldn't find the === sections in that text. Paste the AI's whole answer, including the lines like === SUMMARY ===." });
            return;
        }
        const aboutKeys = Object.keys(parsed.about);
        const overwrites = aboutKeys.some(k => form.about[k]?.trim() && form.about[k].trim() !== parsed.about[k])
            || (parsed.papers.length && form.papers.some(p => p.title.trim()));
        if (overwrites && !window.confirm("This replaces answers you've already typed in this step. Continue?")) return;

        setForm(f => ({
            ...f,
            // Title and domain come from step 1; only fill them if the student left them empty
            title: f.title.trim() ? f.title : parsed.title || f.title,
            domain: f.domain.trim() ? f.domain : parsed.domain || f.domain,
            about: { ...f.about, ...parsed.about },
            papers: parsed.papers.length ? parsed.papers : f.papers,
        }));
        const papers = parsed.papers.length;
        setResult({
            ok: true,
            text: `Filled ${aboutKeys.length} of 5 answers${papers ? ` and ${papers} paper${papers > 1 ? "s" : ""}` : ""}. Read them below and fix anything that's wrong - the report is written from exactly this.`,
        });
        setAnswer("");
    };

    return (
        <Card className="bg-retro-blue/30 shadow-brutal space-y-4">
            <div className="flex items-start gap-3">
                <Bot className="w-7 h-7 shrink-0" />
                <div>
                    <h3 className="font-heading text-2xl font-bold uppercase leading-tight">Fastest way: let your AI chat fill this</h3>
                    <p className="text-sm mt-1">Used ChatGPT, Gemini, Claude, Antigravity or Cursor while building your project? That chat already knows it. Ask it, then paste the answer here.</p>
                </div>
            </div>

            <ol className="space-y-4">
                <li className="flex gap-3">
                    <StepNumber n={1} />
                    <div className="flex-1 space-y-2">
                        <p className="font-bold">Copy this prompt</p>
                        <div className="flex flex-wrap gap-2">
                            <button type="button" onClick={copy}
                                className="px-4 py-2 bg-black text-white font-bold uppercase border-3 border-black flex items-center gap-2 hover:bg-white hover:text-black">
                                {copied ? <><Check className="w-4 h-4" /> Copied</> : <><ClipboardCopy className="w-4 h-4" /> Copy prompt</>}
                            </button>
                            <button type="button" onClick={() => setShowPrompt(s => !s)}
                                className="px-3 py-2 font-bold text-sm underline underline-offset-4 flex items-center gap-1">
                                {showPrompt ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />} {showPrompt ? "Hide" : "See"} prompt
                            </button>
                        </div>
                        {showPrompt && (
                            <textarea readOnly value={prompt} rows={10} onFocus={e => e.target.select()}
                                className="w-full border-2 border-black p-2 font-mono text-xs bg-white" aria-label="Prompt to copy" />
                        )}
                    </div>
                </li>
                <li className="flex gap-3">
                    <StepNumber n={2} />
                    <p className="flex-1"><strong>Paste it into the chat where you worked on your project</strong> - the same conversation, or your Antigravity/Cursor workspace so it can read your code. Then copy its whole answer.</p>
                </li>
                <li className="flex gap-3">
                    <StepNumber n={3} />
                    <div className="flex-1 space-y-2">
                        <label htmlFor="ai-answer" className="font-bold block">Paste the answer here</label>
                        <textarea id="ai-answer" value={answer} onChange={e => { setAnswer(e.target.value); setResult(null); }} rows={5}
                            placeholder={"=== TITLE ===\n...\n=== SUMMARY ===\n..."}
                            className="w-full bg-white border-3 border-black px-3 py-3 font-mono text-sm outline-none focus:shadow-neo" />
                        <button type="button" onClick={fill} disabled={!answer.trim()}
                            className="w-full sm:w-auto px-4 py-3 bg-retro-yellow font-bold uppercase border-3 border-black shadow-brutal-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:shadow-none">
                            <Wand2 className="w-5 h-5" /> Fill my answers
                        </button>
                        {result && (
                            <p role="status" className={result.ok ? "text-sm font-bold text-green-800" : "text-sm font-bold text-red-700"}>{result.text}</p>
                        )}
                    </div>
                </li>
            </ol>
        </Card>
    );
};

export default AiChatImport;
