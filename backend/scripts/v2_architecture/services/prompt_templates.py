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
                "INFER the core problem and a modern 3-node tech stack suitable for this title.\n\n"
                "The abstract should:\n"
                "- Provide a concise overview of the project\n"
                "- Mention the problem being addressed (Infer based on title)\n"
                "- Briefly describe the proposed solution or approach\n"
                "- Highlight the key benefits or expected outcomes\n"
                "- Be approximately {word_limit} words\n\n"
                "Write only the abstract content, do not include the heading 'ABSTRACT' or any other titles."
            ),
            "template_director": (
                "Write an abstract for a {project_type} project titled '{project_title}'.\n\n"
                "CONTEXT:\n"
                "The core problem is: {problem_desc}\n"
                "Our proposed solution uses: {tech_stack}\n"
                "To achieve: {solution_desc}\n"
                "Key features: {key_features}\n\n"
                "The abstract should:\n"
                "- Seamlessly weave these specific details into a professional narrative\n"
                "- Highlight the key benefits or expected outcomes\n"
                "- Be approximately {word_limit} words\n\n"
                "Write only the abstract content."
            ),
            "word_limit": 250,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology",
                "problem_desc": "manual and inefficient systems",
                "tech_stack": "modern technologies",
                "solution_desc": "automate the process",
                "key_features": "efficiency and accuracy"
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
                "INFER the Motivation and Objectives suitable for this specific title.\n\n"
                "Create an introduction with the following NUMBERED subsections:\n\n"
                "### 1.1 Background\n"
                "Provide context about the problem domain and standard technologies used.\n\n"
                "### 1.2 Motivation\n"
                "Explain why this project is important and what gap it addresses (Infer from title).\n\n"
                "### 1.3 Objectives\n"
                "List 4-5 specific goals and objectives of the project.\n\n"
                "IMPORTANT FORMATTING RULES:\n"
                "- Use '### 1.1 Title' format for subsections\n"
                "- Use **bold** for key terms\n"
                "- Write clear, concise paragraphs\n"
                "- Target length: approximately {word_limit} words total\n\n"
                "Write only the introduction content with numbered subsections."
            ),
            "template_director": (
                "Write a comprehensive introduction for:\n"
                "Project Title: {project_title}\n\n"
                "Use this SPECIFIC context:\n"
                "Problem: {problem_desc}\n"
                "Proposed Solution: {solution_desc}\n"
                "Key Objectives: {key_features}\n\n"
                "Create numbered subsections:\n"
                "### 1.1 Background\n"
                "Contextualize the specific problem: {problem_desc}\n\n"
                "### 1.2 Motivation\n"
                "Why is {solution_desc} necessary?\n\n"
                "### 1.3 Objectives\n"
                "List specific objectives including: {key_features}\n\n"
                "Target length: {word_limit} words."
            ),
            "word_limit": 200,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology",
                "problem_desc": "inefficiency in current methods",
                "solution_desc": "automation",
                "key_features": "better performance"
            }
        },
        
        "literature_survey": {
            "system": (
                "You are an academic researcher compiling a literature survey for an engineering project report. "
                "Write professional research paper summaries. "
                "Each entry should have: authors, publication year, and a detailed summary. "
                "Use numbered subsections (2.1, 2.2, etc.)."
            ),
            "template": (
                "Write a literature survey for: '{project_title}' ({domain}).\n"
                "Generate 10-12 generic but relevant papers for this domain from 2019-2025.\n"
                "Format: ### 2.1 [Title]\n**AUTHORS:** ...\n**PUBLISHED ON:** ...\n[Summary]\n"
                "Total length: {word_limit} words."
            ),
            "word_limit": 500,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology"
            }
        },
        
        "problem_statement": {
            "system": (
                "You are a technical analyst identifying problems. "
                "Write in formal academic tone."
            ),
            "template": (
                "Write a problem statement for: '{project_title}' ({domain}).\n"
                "INFER common problems faced in this domain.\n"
                "Cover: Limitations of existing systems, technical gaps, and user pain points.\n"
                "Target length: {word_limit} words."
            ),
            "template_director": (
                "Write a specific problem statement for: '{project_title}'.\n\n"
                "ELABORATE on this specific problem description:\n"
                "'{problem_desc}'\n\n"
                "Discuss technical gaps related to not having '{solution_desc}'.\n"
                "Target length: {word_limit} words."
            ),
            "word_limit": 250,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology",
                "problem_desc": "manual systems",
                "solution_desc": "automated systems"
            }
        },
        
        "existing_proposed": {
            "system": (
                "You are a systems architect comparing solutions. "
                "Write detailed technical comparisons."
            ),
            "template": (
                "Compare Existing and Proposed Systems for: '{project_title}'.\n"
                "INFER a standard existing system and propose a modern solution.\n"
                "Subsections:\n### 4.1 Existing System\n### 4.1.1 Disadvantages\n### 4.2 Proposed System\n### 4.2.1 Advantages\n"
                "Target length: {word_limit} words."
            ),
            "template_director": (
                "Compare Existing and Proposed Systems for: '{project_title}'.\n\n"
                "### 4.1 Existing System\n"
                "Discuss systems that suffer from: {problem_desc}\n\n"
                "### 4.2 Proposed System\n"
                "Describe the proposed solution: {solution_desc}\n"
                "Using technology: {tech_stack}\n\n"
                "Highlight these advantages: {key_features}\n"
                "Target length: {word_limit} words."
            ),
            "word_limit": 400,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology",
                "problem_desc": "manual errors",
                "solution_desc": "automation",
                "tech_stack": "Modern AI/ML",
                "key_features": "accuracy and speed"
            }
        },
        
        "methodology": {
            "system": (
                "You are a technical architect documenting system methodology. "
                "Write detailed technical descriptions. "
                "Use formal engineering language."
            ),
            "template": (
                "Write a methodology for: '{project_title}'.\n"
                "INFER a suitable 3-tier architecture using standard modern tools.\n"
                "Subsections:\n"
                "### 5.1 System Design\n"
                "### 5.2 Data Processing\n"
                "### 5.3 Communication\n"
                "### 5.4 User Interface\n"
                "Target length: {word_limit} words."
            ),
            "template_director": (
                "Write a System Methodology for: '{project_title}'.\n\n"
                "Base the architecture strictly on this TECH STACK: {tech_stack}\n"
                "To implement this SOLUTION: {solution_desc}\n\n"
                "Subsections:\n"
                "### 5.1 System Design\n"
                "Describe how {tech_stack} components interact.\n\n"
                "### 5.2 Implementation Modules\n"
                "Explain the implementation of {key_features}.\n\n"
                "Target length: {word_limit} words."
            ),
            "word_limit": 500,
            "default_context": {
                "project_type": "engineering",
                "domain": "technology",
                "tech_stack": "Cloud, AI, DB",
                "solution_desc": "integrated system",
                "key_features": "core modules"
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
        
        # Determine Mode: Autopilot vs Director
        # Logic: If 'tech_stack' is present and not generic, use Director Mode
        is_director_mode = (
            "tech_stack" in full_context and 
            full_context["tech_stack"] != template_config["default_context"].get("tech_stack", "") and
            "template_director" in template_config
        )
        
        selected_template = template_config["template_director"] if is_director_mode else template_config["template"]
        
        # Format the prompt template
        try:
            formatted_prompt = selected_template.format(**full_context)
            system_instruction = template_config["system"]
            
            if is_director_mode:
                print(f"🎬 Director Mode Prompt: {section_name}")
            else:
                print(f"✈️ Autopilot Prompt: {section_name}")
                
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
