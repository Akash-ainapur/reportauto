# Neo-Brutalism Frontend Redesign Plan

## Goal
Transform the "Automated Report Generator" frontend from a Dark/Glassmorphism style to a **Neo-Brutalism / Retro-Pop** aesthetic. This design style (high contrast, bold borders, vibrant colors) is chosen to appeal to the student demographic by making the report generation process feel fun, easy, and culturally relevant ("Retro 90s").

## User Review Required
> [!IMPORTANT]
> **Design Shift**: This is a radical departure from the current "Professional/Sci-Fi" look. The new design is "loud," colorful, and playful.
> **Fonts**: We will add `Oswald` (Headings) and `Roboto Mono` (Body) from Google Fonts.
> **Content**: The JSON provided contained placeholder text for a "Collaboration App". I will adapt the layout to the "Report Generator" context (e.g., "Ready to Rock Your Report?" instead of "Meeting").

## Proposed Changes

### Configuration & Base Styles
#### [MODIFY] [tailwind.config.js](file:///d:/Model/REPORT1/AutomatedReportGenerator/Frontend/tailwind.config.js)
- Add the Neo-Brutalism color palette:
  - `primary-yellow`: `#F4D73B`
  - `primary-coral`: `#F27870`
  - `primary-purple`: `#635BFF`
  - `secondary-lavender`: `#E6E1F9`
  - `retro-beige`: `#E8E6D9`
- Define new `boxShadow` utilities for the hard drop shadows (`4px 4px 0px #000`).
- Define new `borderWidth` utilities if needed.

#### [MODIFY] [index.css](file:///d:/Model/REPORT1/AutomatedReportGenerator/Frontend/src/index.css)
- Remove dark mode variables and glassmorphism classes.
- Add global base styles:
  - `body`: Background color `retro-beige` (or white), default font `Roboto Mono`.
  - `h1, h2, h3`: Font `Oswald`, uppercase, text-stroke effect.
  - `.neo-card`: Helper class for `bg-white border-2 border-black shadow-neo`.
  - `.neo-button`: Helper class for `hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all`.

#### [MODIFY] [index.html](file:///d:/Model/REPORT1/AutomatedReportGenerator/Frontend/index.html)
- Add `<link>` tags for Google Fonts: `Oswald` and `Roboto Mono`.

### Components & Pages
#### [MODIFY] [LandingPage.jsx](file:///d:/Model/REPORT1/AutomatedReportGenerator/Frontend/src/pages/LandingPage.jsx)
- **Hero Section**:
  - Background: `primary-yellow`.
  - Content: "REPORT GENERATOR FOR PROCRASTINATORS" (or similar fun headline).
  - Style: Sticker-style text, retro computer image (if available or generated css art).
- **Marquee Section**:
  - Scrolling text bands ("MVJ Format Supported", "Fast Generation", "No More Word Formatting").
- **Features Section**:
  - Cards with retro OS window frames.
- **Testimonials**:
  - Masonry layout with "Handshake" badges.
- **Footer**:
  - Simple black bar with "Chuck Norris approves" placeholder replaced by "Your HOD approves".

#### [MODIFY] [ReportConfig.jsx](file:///d:/Model/REPORT1/AutomatedReportGenerator/Frontend/src/pages/ReportConfig.jsx)
- Update form inputs to have white backgrounds, thick black borders, and hard shadows.
- Update buttons to use the Neo-Brutalism interactive states.

#### [MODIFY] [Navbar.jsx] & [Footer.jsx]
- Update to match the new color scheme (likely high contrast black/white or primary yellow).

## Verification Plan

### Manual Verification
1.  **Visual Check**:
    - Verify the "Hard Shadow" effect works (no blur).
    - Checks fonts are loaded (Oswald/Roboto).
    - Check colors match the JSON palette.
2.  **Responsiveness**:
    - Ensure the "Column (mobile) / Split (desktop)" layout generally works.
3.  **Flow**:
    - "Get Started" button should still flow to Auth -> Dashboard.
