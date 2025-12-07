# Next Steps: Assembly Line Architecture Refactor
**Date:** 2025-12-07

## Goal
Transition the project from "one script per page" to a modular "Assembly Line" where a single document is passed through multiple generator functions.

## 1. Directory Structure
We will reorganize `backend/` to be modular:

```text
backend/
├── data/
│   └── full_report_template.json  <-- Single Source of Truth
├── scripts/
│   ├── main_generator.py          <-- The Orchestrator (Starts here)
│   ├── utils.py                   <-- Shared tools (replace_text, etc.)
│   └── generators/                <-- Package for page logic
│       ├── __init__.py
│       ├── front_page.py          <-- Logic for Page 1 only
│       ├── certificate.py         <-- Logic for Page 2
│       └── ...
└── templates/
    └── senior_project_template.docx
```

## 2. Component Design

### `utils.py` (The Shared Toolbox)
Will contain the low-level logic currently trapped in `front_page.py`:
*   `def replace_text_runs(paragraph, old, new)`
*   `def replace_text_in_tables(table, replacements)`
*   `def load_json_data(path)`
*   `def add_page_number(paragraph)`

### `generators/front_page.py` (The Worker)
*   **Input**: Accepts `doc` (Document object) and `data` (JSON dict).
*   **Action**: Modifies the **First Section** of `doc` using `data`.
*   **Output**: None (Modifies in-place).
*   **Signature**: `def generate(doc, data):`

### `main_generator.py` (The Manager)
*   Loads the JSON data (`backend/data/full_report_template.json`).
*   Loads the Template (`backend/templates/senior_project_template.docx`).
*   Calls `generators.front_page.generate(doc, data)`.
*   Calls `generators.certificate.generate(doc, data)` (Future).
*   Saves the final `Final_Report.docx`.

## 3. Implementation Steps

1.  **Create `backend/scripts/utils.py`**:
    *   Move `replace_text_runs` and generic table/footer replacement logic here.
    *   Add a helper for `load_data`.

2.  **Create `backend/scripts/generators/` folder**:
    *   Add `__init__.py`.
    *   Create `front_page.py` (Refactored version of current script).
        *   It will **Import** `utils`.
        *   It will **Export** `generate(doc, data)`.

3.  **Create `backend/scripts/main_generator.py`**:
    *   Import `utils`, `generators`.
    *   Run the full pipeline.
