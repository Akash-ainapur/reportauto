# Design Brief: Automatic Report Generator (Neo-Brutalism Redesign)

**To:** Frontend Designer  
**From:** Dev Team  
**Goal:** Redesign the current "Dark Sci-Fi" interface into a **"Neo-Brutalism / Retro-Pop"** experience that removes friction and makes writing project reports feel fun (or at least less painful).

---

## 1. The Vibe Strategy
**Current State:** Dark mode, neon gradients, glassmorphism. Feels like a developer tool or a SaaS dashboard.  
**Target State:** "Neo-Brutalism". High contrast, thick black borders (3px+), pastel/vibrant colors (Yellow #F4D73B, Coral #F27870), retro computer aesthetics (Windows 95 meets 2025).
*   **Why?** Our users are students. They are stressed. The UI should be loud, simple, and self-aware. It should feel like a "hack" or a "magic button," not a serious form filling exercise.

---

## 2. User Journey & Design Needs

### Screen 1: The Landing Page ("The Hook")
**Goal:** Convince the user in 3 seconds that this tool saves them 5 hours of work.
*   **Friction to Remove:** ambiguity. Don't say "Collaboration Tool". Say "We Write Your Report For You."
*   **Layout:**
    *   **Hero Section:** Split screen. Left side: Giant text. Right side: A retro CRT monitor or a mess of papers turning into a neat stack.
    *   **Headline:** "REPORT GENERATOR FOR PROCRASTINATORS." (Font: Impact or Oswald, Text Stroke).
    *   **Subtext:** "Auto-generate Major & Mini Project reports that tick every MVJ checkbox. 100% formatted. 0% headache."
    *   **Primary CTA Button:** Giant, rectangular, yellow button with a hard shadow. Text: **"START NOW ->"**. Hover effect: Button moves down and to the right (simulating a physical press).
    *   **Social Proof (Marquee):** A scrolling banner saying things like: *"Your HOD will love this"* // *"No more alignment issues"* // *"Format Verified"*.

### Screen 2: Authentication
**Goal:** Get them in.
*   **Design:** Keep it simple. A centered "Card" on a patterned background (dots or grid).
*   **Content:** "Login to save your future."

### Screen 3: The Dashboard / Form ("The Machine")
**Critical Friction Point:** This is where users currently drop off. It looks like a tax form.
*   **The Fix:** Make it look like a **Launchpad**.
*   **Layout:**
    *   **Container:** A large white panel with a heavy black border.
    *   **Progress:** If we split it into steps, use a giant progress bar that looks like a retro game health bar.
    *   **Inputs:**
        *   **Project Title:** Not just a line. A big box. Placeholder: *"E.g. AI-Powered Cat Feeder"*
        *   **Student Names:** Cards where you can "Add Teammate".
        *   **Guide Name:** A distinct section. "Who is grading this?"
    *   **"The Magic Button" (Generate):** This needs to be the centerpiece.
        *   **Design:** Huge. Red or Purple.
        *   **Copy:** **"GENERATE REPORT 🚀"**
        *   **Interaction:** When clicked, it should feel satisfying.
*   **Micro-copy:**
    *   Instead of "Upload Images", say **"Drop Evidence Here"**.
    *   Instead of "Submit", say **"Let's Cook"**.

### Screen 4: Loading Screen ("The Entertainment")
**Goal:** The generation takes 30-60 seconds. Don't let them get bored.
*   **Concept:** A "Gamified" loading screen.
*   **Design:**
    *   A pixel-art progress bar filling up.
    *   **Loading Messages:** We cycle through funny text. The designer needs to style these text prompts to look like retro system notifications.
    *   *Examples: "Feeding coffee to the AI...", "Aligning margins pixel by pixel...", "Bribing external examiner..."*

### Screen 5: Success ("The Reward")
**Goal:** Instant gratification.
*   **Visual:** Confetti (pixelated style).
*   **Layout:**
    *   Big distinct card: "REPORT READY."
    *   **Download Button:** The biggest button on the screen. "DOWNLOAD .DOCX".
    *   **Secondary Action:** "Make Another One" (Smaller, outline style).

---

## 3. Specific Components to Design
1.  **Buttons:**
    *   **Primary:** Solid color (Yellow/Coral), Black Border (3px), Hard Shadow (4px). Capitals.
    *   **Secondary:** White fill, Black Border, No Shadow.
2.  **Inputs:**
    *   White background, 2px Black Border. Focus state: Yellow background or thicker border.
3.  **Typography:**
    *   **Headings:** Oswald or similar condensed heavy font. Uppercase.
    *   **Body:** Roboto Mono or similar monospace font (gives the "technical/code" vibe).
4.  **Decorations:**
    *   Please design 3-5 "Stickers" to place randomly:
        *   A pixelated "Thumbs Up" cursor.
        *   A "Verified" stamp.
        *   A jagged "New!" starburst.
        *   Abstract geometric shapes (squiggles, triangles) to fill whitespace.

---

## 4. Friction Analysis Summary
| Current Friction | Proposed Design Solution |
| :--- | :--- |
| "Is this tool for me?" | **Hero Copy:** specific to "MVJ College Projects". Bold aesthetic. |
| "This form is long." | **Chunking:** Group inputs into "Project Info", "Team", "Guide". Use visual "Cards". |
| "Is it stuck?" (Loading) | **Entertainment:** Value-added loading screen with humor. |
| "Did it work?" | **Success State:** Over-the-top celebration visuals. |
