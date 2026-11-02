// The prompt students paste into the AI chat or coding agent that already knows their project
// (ChatGPT, Gemini, Claude, Antigravity, Cursor...), and the parser for the answer they paste back.
// The answer uses fixed "=== HEADING ===" blocks so it can be split without guessing.

const BLOCKS = [
    ["TITLE", "title"],
    ["DOMAIN", "domain"],
    ["SUMMARY", "summary"],
    ["TECH", "tech"],
    ["MODULES", "modules"],
    ["RESULTS", "results"],
    ["LIMITATIONS", "limitations"],
    ["PAPERS", "papers"],
];

export function buildAiChatPrompt(title) {
    return `I'm writing the final report for my engineering project${title ? ` "${title}"` : ""}. You know this project from our conversation or from the project files you can read. Give me the facts about it in the exact format below so I can paste them into a report generator.

Rules:
- Use ONLY what you actually know about MY project from this chat or the code/files. Do not invent features, numbers, results or tools.
- If you can read the project files (code, README, requirements, package.json, datasheets), look through them first.
- If you don't know something, write UNKNOWN for that section.
- Plain sentences, no markdown, no bullet symbols. Each section at most 200 words.
- PAPERS: list only research papers I actually used or mentioned. Never make up a paper, author or year. If there are none, write NONE.
- Put your whole answer inside ONE code block so I can copy it in one go.

Format (keep the === lines exactly):

=== TITLE ===
The project title.
=== DOMAIN ===
The field, e.g. Machine Learning, IoT, Web Development.
=== SUMMARY ===
What the project is, the problem it solves and why it matters (3-6 sentences).
=== TECH ===
All hardware (boards, sensors, components) and software (languages, frameworks, libraries, models, databases, tools) used.
=== MODULES ===
The main modules or parts, what each one does, and how data flows through the system.
=== RESULTS ===
What works, any accuracy/speed/other numbers measured, and how it was tested.
=== LIMITATIONS ===
Current limitations, then future improvements.
=== PAPERS ===
Title: ...
Authors: ... (separate with semicolons)
Year: ...
Venue: ... (journal or conference, or UNKNOWN)
About: one or two lines on what the paper does
---
(repeat for each paper)`;
}

const isUnknown = (text) => /^(unknown|none|n\/a|not (known|available|applicable))\.?$/i.test(text.trim());

function parsePapers(text) {
    if (!text || isUnknown(text)) return [];
    return text
        .split(/\n\s*-{3,}\s*\n|\n\s*\n(?=\s*title\s*:)/i)
        .map(chunk => {
            const field = (name) => {
                const m = chunk.match(new RegExp(`^\\s*${name}\\s*:\\s*(.+)$`, "im"));
                const value = m ? m[1].trim() : "";
                return isUnknown(value) ? "" : value;
            };
            return {
                title: field("title"),
                authors: field("authors?"),
                year: (field("year").match(/\d{4}/) || [""])[0],
                venue: field("venue"),
                notes: field("about"),
            };
        })
        .filter(p => p.title)
        .slice(0, 15);
}

// Returns { title, domain, about: {...}, papers: [...] } with only the parts that were found,
// or null when the text has none of the === blocks.
export function parseAiChatAnswer(raw) {
    const text = (raw || "").replace(/```[a-z]*\n?/gi, "").replace(/\r/g, "");
    const marker = /^\s*={2,}\s*([A-Z ]+?)\s*={2,}\s*$/gim;
    const found = {};
    const matches = [...text.matchAll(marker)];
    matches.forEach((m, i) => {
        const block = BLOCKS.find(([name]) => name === m[1].trim().toUpperCase());
        if (!block) return;
        const end = i + 1 < matches.length ? matches[i + 1].index : text.length;
        found[block[1]] = text.slice(m.index + m[0].length, end).trim();
    });
    if (!Object.keys(found).length) return null;

    const clean = (key, limit = 3000) => {
        const v = (found[key] || "").trim();
        return v && !isUnknown(v) ? v.slice(0, limit) : "";
    };
    const about = {};
    for (const key of ["summary", "tech", "modules", "results", "limitations"]) {
        const v = clean(key);
        if (v) about[key] = v;
    }
    return {
        title: clean("title", 200).replace(/^["']|["']$/g, ""),
        domain: clean("domain", 100),
        about,
        papers: parsePapers(found.papers),
    };
}
