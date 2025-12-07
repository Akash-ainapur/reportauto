# Project Architecture Feedback and Analysis

## Current Status Analysis
Based on the review of `page_01_front_page.py` and `PROJECT_ROADMAP.md`, the current direction involves building separate scripts for each page and merging them later. This approach presents several significant long-term risks.

### 1. The "Merge" Nightmare (Technical Difficulty)
*   **The Problem:** Merging Word documents is not as simple as concatenating text files. `python-docx` does not natively support merging two separate `Document` objects while preserving their individual headers, footers, margins, and page numbering.
*   **Risk:** If Script 1 produces `front_page.docx` and Script 2 produces `certificate.docx`, joining them will likely result in broken formatting (e.g., Certificate page inheriting Front Page margins, page numbering resetting).

### 2. The "Copy-Paste" Trap (Code Duplication)
*   **The Problem:** Helper functions like `replace_text_runs` and `add_page_number` are currently embedded in the script.
*   **Risk:** Duplicating these functions across 10+ page scripts means that any bug fix or improvement must be applied manually to 10+ files, leading to maintenance issues.

### 3. Data Inconsistency (Split Brain)
*   **The Problem:** Data variables (e.g., `dummy_project_title`) are defined locally within the script.
*   **Risk:** As more scripts are created, these variables will be duplicated. Eventually, data will drift (e.g., "Project A" in one file, "Project B" in another), leading to inconsistent reports.

### 4. Refactoring Debt
*   **The Problem:** The roadmap plans for "Refactoring" in Phase 2 to introduce dynamic data.
*   **Risk:** Writing all scripts with hardcoded strings now means Phase 2 will essentially be a complete rewrite rather than a refactor.

---

## Proposed Solution: The "Assembly Line" Architecture

Instead of merging separate *files*, the system should pass a **single Document object** through multiple **functions**.

### Recommended Structure

1.  **`project_data.json` (Single Source of Truth)**
    *   Store all data (dummy or real) in one external file. All generators read from this source.

2.  **`utils.py` (Shared Toolbox)**
    *   Store generic helpers here: `replace_text_runs`, `add_page_number`, `setup_page_layout`, etc.

3.  **`generators/` (Assembly Stations)**
    *   Each page is a **Function**, not a standalone script.
    *   Example: `page_01.py` accepts a `doc` object and a `data` dictionary, modifies the `doc` in-place, and returns it.

### Pseudocode Visualization

**Current (Problematic) Flow:**
```python
# script_1.py -> loads template, saves page1.docx
# script_2.py -> loads template, saves page2.docx
# main.py -> struggles to merge page1.docx and page2.docx
```

**Recommended (Assembly Line) Flow:**
```python
# main_generator.py
from generators import page_01_front, page_02_cert
from utils import load_data

# 1. Start the Assembly Line
data = load_data("project_data.json")
doc = Document("template.docx")

# 2. Pass the SAME document through stations
# Each function modifies the document in memory
page_01_front.generate(doc, data) 
doc.add_page_break()
page_02_cert.generate(doc, data) 

# 3. Save ONCE at the end
doc.save("Final_Full_Report.docx")
```

### Immediate Action Items
1.  **Extract Helpers:** Move `replace_text_runs` and other helpers to a `utils.py` file.
2.  **Centralize Data:** Create a JSON file or a configuration module for the dummy data.
3.  **Modularize Page 1:** Refactor `page_01_front_page.py` to be a module that exports a generation function, rather than a standalone script that saves a file.
