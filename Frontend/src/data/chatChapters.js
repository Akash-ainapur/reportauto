// Reading chapter answers students paste back from their own AI chat. The prompts (built by the
// backend from report_types.py) ask for each section inside <key>...</key> tags in one code block.

// Every section a student can paste, in report order, with its label (mirrors report_types.py)
export const CHAT_SECTIONS = [
    ["abstract", "Abstract"],
    ["introduction", "Introduction"],
    ["problem_statement", "Problem Statement"],
    ["literature_survey", "Literature Survey"],
    ["existing_proposed", "Existing and Proposed System"],
    ["requirement_specification", "Requirement Specification"],
    ["implementation", "Implementation"],
    ["results", "Results"],
    ["testing_validation", "Testing and Validation"],
    ["limitations_future", "Limitations and Future Enhancements"],
    ["conclusion", "Conclusion"],
];
const KEYS = CHAT_SECTIONS.map(([k]) => k);
export const sectionLabel = (key) => CHAT_SECTIONS.find(([k]) => k === key)?.[1] || key;

// Returns { found: {key: text}, continued: {key: text} }. "continued" is text that ends with a
// closing tag but has no opening one: the rest of a section after the student typed "continue".
export function parseChapterAnswer(raw) {
    const text = (raw || "").replace(/\r/g, "").replace(/^\s*```[a-z]*\s*$/gim, "");
    const found = {};
    const continued = {};
    const opens = [...text.matchAll(/<([a-z_]+)>/g)].filter(m => KEYS.includes(m[1]));

    opens.forEach((m, i) => {
        const key = m[1];
        const start = m.index + m[0].length;
        const close = text.indexOf(`</${key}>`, start);
        const nextOpen = i + 1 < opens.length ? opens[i + 1].index : text.length;
        // A missing closing tag (answer cut off) still keeps everything up to the next section
        const end = close !== -1 && close < nextOpen ? close : nextOpen;
        const body = text.slice(start, end).trim();
        if (body) found[key] = body;
    });

    const firstOpen = opens.length ? opens[0].index : text.length;
    const head = text.slice(0, firstOpen);
    const closeOnly = head.match(/<\/([a-z_]+)>/);
    if (closeOnly && KEYS.includes(closeOnly[1])) {
        const body = head.slice(0, closeOnly.index).trim();
        if (body) continued[closeOnly[1]] = body;
    }
    return { found, continued };
}
