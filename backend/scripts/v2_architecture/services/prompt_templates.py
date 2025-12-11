"""
Prompt Templates for AI Content Generation

This module contains all prompt templates for generating different sections
of the report. Templates support variable substitution from project data.
"""

from typing import Dict, Any


class PromptTemplates:
    """Centralized prompt template management."""
    
    # System instructions define the AI's role and behavior
    SYSTEM_INSTRUCTIONS = {
        "abstract": (
            "You are a professional technical writer specializing in academic project reports. "
            "Write in a formal, concise, and objective tone. Focus on clarity and precision. "
            "Use third-person perspective and avoid promotional language. "
            "You may use markdown formatting: **bold**, *italic*, and ### for subsection headings."
        ),
        "introduction": (
            "You are an academic technical writer creating introduction chapters for engineering project reports. "
            "Write in a formal, scholarly tone with proper structure. Include context, motivation, "
            "and objectives. Use technical terminology appropriately and maintain objectivity. "
            "You may use markdown formatting: ### for subsection headings (e.g., ### Motivation), "
            "**bold** for emphasis, and *italic* for technical terms."
        ),
    }
    
    # Prompt templates with {variable} placeholders
    PROMPTS = {
        "abstract": {
            "system": SYSTEM_INSTRUCTIONS["abstract"],
            "template": (
                "Write an abstract for a {project_type} project titled '{project_title}' "
                "in the domain of {domain}.\n\n"
                "The abstract should:\n"
                "- Provide a concise overview of the project\n"
                "- Mention the problem being addressed\n"
                "- Briefly describe the proposed solution or approach\n"
                "- Highlight the key benefits or expected outcomes\n"
                "- Be approximately {word_limit} words\n\n"
                "Write only the abstract content, do not include the heading 'ABSTRACT' or any other titles."
            ),
            "word_limit": 250,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "introduction": {
            "system": (
                "You are a technical writer creating the Introduction chapter for an engineering project report. "
                "Write in a formal, academic tone suitable for a college-level technical report. "
                "Use markdown formatting: ### for subsection headings, **bold** for emphasis, *italic* for terms. "
                "IMPORTANT: Use numbered subsection headings in the format '### 1.1 Subsection Title' for proper TOC integration."
            ),
            "template": (
                "Write a comprehensive introduction for the following project:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "Create an introduction with the following NUMBERED subsections:\n\n"
                "### 1.1 Background\n"
                "Provide context about the problem domain and current state of technology.\n\n"
                "### 1.2 Motivation\n"
                "Explain why this project is important and what gap it addresses.\n\n"
                "### 1.3 Objectives\n"
                "List the main goals and objectives of the project.\n\n"
                "IMPORTANT FORMATTING RULES:\n"
                "- Use '### 1.1 Title' format for subsections (will appear in Table of Contents)\n"
                "- Use **bold** for key terms and emphasis\n"
                "- Use *italic* for technical terms when first introduced\n"
                "- Write clear, concise paragraphs\n"
                "- Target length: approximately {word_limit} words total\n\n"
                "Write only the introduction content with numbered subsections. "
                "Do not include 'CHAPTER 1' or 'INTRODUCTION' headings as those are added automatically."
            ),
            "word_limit": 200,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "literature_survey": {
            "system": (
                "You are an academic researcher compiling a literature survey for an engineering project report. "
                "Write professional research paper summaries in formal academic tone. "
                "Each entry should have: authors, publication year, and a detailed summary. "
                "Use numbered subsections (2.1, 2.2, etc.) for each paper reviewed."
            ),
            "template": (
                "Write a comprehensive literature survey for the following project:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "Generate 10-12 literature survey entries in the following format:\n\n"
                "### 2.1 [Paper Title]\n"
                "**AUTHORS:** [Author Names]\n"
                "**PUBLISHED ON:** [Year]\n"
                "[Detailed summary of the paper, its contributions, methodology, and findings]\n\n"
                "IMPORTANT:\n"
                "- Use numbered subsections: ### 2.1, ### 2.2, ### 2.3, etc.\n"
                "- Each entry should be 150-200 words\n"
                "- Cover diverse aspects: cloud computing, AI/ML, security, databases, web technologies\n"
                "- Include recent papers (2019-2025)\n"
                "- Use **bold** for AUTHORS and PUBLISHED ON\n"
                "- Total length: approximately {word_limit} words\n\n"
                "Do not include 'CHAPTER 2' or 'LITERATURE SURVEY' headings."
            ),
            "word_limit": 500,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "problem_statement": {
            "system": (
                "You are a technical analyst identifying problems in existing systems. "
                "Write in formal academic tone, clearly articulating gaps, challenges, and limitations. "
                "Focus on why current solutions are insufficient and what needs improvement."
            ),
            "template": (
                "Write a detailed problem statement for the following project:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "The problem statement should cover:\n"
                "1. Current state of existing systems and their limitations\n"
                "2. Specific challenges faced by users (students/institutions)\n"
                "3. Technical gaps (scalability, security, accessibility, intelligence)\n"
                "4. User experience issues (manual processes, lack of personalization)\n"
                "5. Why these problems need to be addressed\n\n"
                "Write in clear, flowing paragraphs. Be specific about problems.\n"
                "Use **bold** for key issues.\n"
                "Target length: approximately {word_limit} words.\n\n"
                "Do not include 'CHAPTER 3' or 'PROBLEM STATEMENT' headings."
            ),
            "word_limit": 250,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "existing_proposed": {
            "system": (
                "You are a systems architect comparing existing and proposed solutions. "
                "Write detailed technical comparisons with numbered subsections. "
                "Clearly articulate advantages and disadvantages in formal academic style."
            ),
            "template": (
                "Write a comprehensive comparison of existing and proposed systems:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "Structure the content with these numbered subsections:\n\n"
                "### 4.1 Existing System\n"
                "Describe current approaches, their features, and how they work. "
                "Mention technologies used (cloud storage, LMS, basic platforms).\n\n"
                "### 4.1.1 Disadvantages of Existing System\n"
                "List 5-6 specific disadvantages as:\n"
                "i. [Disadvantage 1]\n"
                "ii. [Disadvantage 2]\n"
                "etc.\n\n"
                "### 4.2 Proposed System\n"
                "Describe your innovative solution, key features, and how it addresses the gaps. "
                "Mention advanced technologies (AI, cloud, real-time processing, etc.).\n\n"
                "### 4.2.1 Advantages of Proposed System\n"
                "List 5-6 specific advantages as:\n"
                "i. [Advantage 1]\n"
                "ii. [Advantage 2]\n"
                "etc.\n\n"
                "IMPORTANT:\n"
                "- Use numbered subsections (### 4.1, ### 4.1.1, ### 4.2, ### 4.2.1)\n"
                "- Use **bold** for key technologies and features\n"
                "- Target length: approximately {word_limit} words\n\n"
                "Do not include 'CHAPTER 4' heading."
            ),
            "word_limit": 400,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "methodology": {
            "system": (
                "You are a technical architect documenting system methodology. "
                "Write detailed technical descriptions of system design, components, and implementation approach. "
                "Use formal engineering language with numbered subsections for clarity."
            ),
            "template": (
                "Write a comprehensive methodology for implementing:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "Start with an overview paragraph explaining the overall approach.\n\n"
                "Then create numbered subsections covering:\n\n"
                "### 5.1 System Design and Components\n"
                "Describe the architecture (cloud platform, web interface, database, AI components).\n\n"
                "### 5.2 Data Processing and AI Integration\n"
                "Explain how data is processed, AI algorithms used, and content management.\n\n"
                "### 5.3 Communication and APIs\n"
                "Describe data transmission protocols (RESTful APIs, real-time communication).\n\n"
                "### 5.4 User Interface and Interaction\n"
                "Explain the web interface, features, and user control mechanisms.\n\n"
                "IMPORTANT:\n"
                "- Use roman numerals (i., ii., iii.) for sub-points\n"
                "- Use **bold** for technical terms\n"
                "- Mention specific technologies (AWS, React, MongoDB, etc.)\n"
                "- Target length: approximately {word_limit} words\n\n"
                "Do not include 'CHAPTER 5' or 'METHODOLOGY' headings."
            ),
            "word_limit": 500,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "requirements": {
            "system": (
                "You are a system requirements analyst documenting technical specifications. "
                "List hardware and software requirements in clear, organized format. "
                "Be specific about versions, specifications, and technical details."
            ),
            "template": (
                "Write detailed hardware and software requirements for:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "Structure with two main subsections:\n\n"
                "### 6.1 Software Requirements\n"
                "List as numbered items:\n"
                "i. **OS:** [Operating systems]\n"
                "ii. **Frontend:** [Technologies like React.js, HTML, CSS, JavaScript]\n"
                "iii. **Backend:** [Spring Boot, Node.js, Python, etc.]\n"
                "iv. **Database:** [MongoDB, MySQL, PostgreSQL, etc.]\n"
                "v. **Cloud Services:** [AWS S3, Cognito, Lambda, etc.]\n"
                "vi. **AI/Chatbot:** [Gemini API, OpenAI, etc.]\n"
                "vii. **Tools:** [VS Code, Git, Docker, etc.]\n"
                "viii. **Other Libraries:** [Specific libraries used]\n\n"
                "### 6.2 Hardware Requirements\n"
                "List as numbered items:\n"
                "i. **Processor:** [CPU specifications]\n"
                "ii. **RAM:** [Memory requirements]\n"
                "iii. **Storage:** [Disk space needed]\n"
                "iv. **Internet:** [Connection requirements]\n"
                "v. **Display:** [Screen resolution]\n\n"
                "IMPORTANT:\n"
                "- Use roman numerals (i., ii., iii.)\n"
                "- Use **bold** for requirement categories\n"
                "- Be specific about versions and specifications\n"
                "- Target length: approximately {word_limit} words\n\n"
                "Do not include 'CHAPTER 6' heading."
            ),
            "word_limit": 200,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "conclusion": {
            "system": (
                "You are writing the conclusion of an engineering project report. "
                "Summarize achievements, impact, and future scope in formal academic tone. "
                "End on a positive, forward-looking note about the project's contribution."
            ),
            "template": (
                "Write a comprehensive conclusion for:\n\n"
                "Project Title: {project_title}\n"
                "Domain: {domain}\n\n"
                "The conclusion should:\n"
                "1. Summarize what the system achieves and its significance\n"
                "2. Highlight key features and innovations (AI, cloud, real-time processing)\n"
                "3. Explain benefits to users (students, faculty, institutions)\n"
                "4. Mention security, scalability, and efficiency improvements\n"
                "5. Discuss the system's potential impact on education/industry\n"
                "6. End with future possibilities and overall contribution\n\n"
                "Write in flowing paragraphs.\n"
                "Use **bold** for key achievements.\n"
                "Maintain optimistic, professional tone.\n"
                "Target length: approximately {word_limit} words.\n\n"
                "Do not include 'CONCLUSION' heading."
            ),
            "word_limit": 200,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "references": {
            "system": (
                "You are a bibliography compiler following IEEE citation format. "
                "Generate properly formatted academic references based on the literature survey papers."
            ),
            "template": (
                "Generate IEEE-formatted references corresponding to the literature survey:\n\n"
                "Project Domain: {domain}\n\n"
                "Create 10-12 numbered references in IEEE format:\n\n"
                "[1] Author1, Author2, et al. \"Paper Title.\" Conference/Journal Name, "
                "vol. X, no. Y, pp. ZZ-ZZ, Year. Publisher, Year.\n\n"
                "IMPORTANT:\n"
                "- Number references as [1], [2], [3], etc.\n"
                "- Follow IEEE citation format strictly\n"
                "- Include: authors, title (in quotes), publication venue, "
                "volume, issue, pages, year, publisher\n"
                "- Match the number of references to literature survey entries\n"
                "- Focus on {domain} related papers from 2019-2025\n\n"
                "Do not include 'REFERENCES' heading."
            ),
            "word_limit": 300,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
    }
    
    @staticmethod
    def get_prompt(section_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Get formatted prompt and system instruction for a section.
        
        Args:
            section_name: Name of the section (e.g., 'abstract', 'introduction')
            context: Dictionary containing variables for template substitution
                    Expected keys: project_title, project_type, domain, word_limit
        
        Returns:
            Tuple of (system_instruction, formatted_prompt)
        
        Raises:
            ValueError: If section_name is not found in templates
        """
        if section_name not in PromptTemplates.PROMPTS:
            raise ValueError(f"No prompt template found for section: {section_name}")
        
        template_config = PromptTemplates.PROMPTS[section_name]
        
        # Merge default context with provided context
        full_context = {**template_config["default_context"], **context}
        
        # Add word limit if not provided
        if "word_limit" not in full_context:
            full_context["word_limit"] = template_config["word_limit"]
        
        # Format the prompt template
        try:
            formatted_prompt = template_config["template"].format(**full_context)
            system_instruction = template_config["system"]
            return system_instruction, formatted_prompt
        except KeyError as e:
            raise ValueError(f"Missing required context variable: {e}")
    
    @staticmethod
    def get_word_limit(section_name: str) -> int:
        """Get the default word limit for a section."""
        if section_name not in PromptTemplates.PROMPTS:
            return 500  # Default fallback
        return PromptTemplates.PROMPTS[section_name]["word_limit"]
    
    @staticmethod
    def list_available_sections() -> list[str]:
        """Get list of all available section templates."""
        return list(PromptTemplates.PROMPTS.keys())
