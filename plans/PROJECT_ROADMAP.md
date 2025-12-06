# Project Roadmap: Automated Report Generator

This document outlines the strategic plan for developing the Automated Report Generator, moving from a hardcoded prototype to a full-fledged SaaS platform.

## Phase 1: Hardcoded Prototype (Current Focus)
**Goal:** Validate the feasibility of automating report generation page-by-page using fixed data.

- [ ] **Infrastructure Setup**: Establish directory structure and backup templates.
- [ ] **Page-by-Page Scripting**:
    - Develop individual Python scripts for each section of the report (Front Page, Certificate, Declaration, Acknowledgement, Abstract, etc.).
    - Use `python-docx` to replace placeholders with hardcoded test data.
    - Ensure strict formatting compliance with the college template.
- [ ] **Integration Test**: Combine scripts to generate a full document with dummy data.

## Phase 2: Dynamic Content Integration
**Goal:** Replace hardcoded data with dynamic inputs from users and AI.

- [ ] **Input Mechanism**: Design a data structure (JSON/Dict) to hold user inputs (Name, ID, Project Title, etc.).
- [ ] **AI Content Generation**:
    - Integrate an LLM (e.g., Gemini/OpenAI) to generate content for sections like "Abstract", "Introduction", or "Conclusion" based on brief user prompts.
- [ ] **Refactoring**: Update Phase 1 scripts to accept data as arguments/variables instead of hardcoded strings.

## Phase 3: SaaS Platform Development
**Goal:** Turn the tool into a web-based service for students.

- [ ] **Frontend Development**:
    - Build a modern, responsive web interface (React/Next.js).
    - Create forms for user data collection.
- [ ] **Backend Development**:
    - Expose the Python generation logic via an API (Flask/FastAPI).
    - Implement User Authentication (Login/Signup).
- [ ] **Monetization & Deployment**:
    - Integrate a Payment Gateway.
    - Deploy the application (Cloud hosting).
    - Launch to students.
