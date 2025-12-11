import os
import sys

# Add the script directory to path to allow importing from components
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from builder import ReportBuilder, ReportContext
from components.front_page import FrontPageGenerator
from components.certificate import CertificateGenerator
from components.declaration import DeclarationGenerator
from components.abstract import AbstractGenerator
from components.acknowledgement import AcknowledgementGenerator
from components.table_of_contents import TableOfContentsGenerator
from components.introduction import IntroductionGenerator
from components.literature_survey import LiteratureSurveyGenerator
from components.problem_statement import ProblemStatementGenerator
from components.existing_proposed import ExistingProposedGenerator
from components.methodology import MethodologyGenerator
from components.requirements import RequirementsGenerator
from components.conclusion import ConclusionGenerator
from components.references import ReferencesGenerator

def main():
    print("🚀 Starting V2 Report Assembly (Single Object Workflow)...")
    
    # 1. Initialize Context
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    context = ReportContext(project_root)
    
    # 2. Initialize Builder
    builder = ReportBuilder(context)
    
    # 3. Add Steps (in order)
    builder.add_step(FrontPageGenerator)              # Section 0
    builder.add_step(CertificateGenerator)            # Section 1
    builder.add_step(DeclarationGenerator)            # Section 2
    builder.add_step(AbstractGenerator)               # Section 3
    builder.add_step(AcknowledgementGenerator)        # Section 4
    builder.add_step(TableOfContentsGenerator)        # Section 5 - TOC
    builder.add_step(IntroductionGenerator)           # Section 6 - Chapter 1
    builder.add_step(LiteratureSurveyGenerator)       # Section 7 - Chapter 2
    builder.add_step(ProblemStatementGenerator)       # Section 8 - Chapter 3
    builder.add_step(ExistingProposedGenerator)       # Section 9 - Chapter 4
    builder.add_step(MethodologyGenerator)            # Section 10 - Chapter 5
    builder.add_step(RequirementsGenerator)           # Section 11 - Chapter 6
    builder.add_step(ConclusionGenerator)             # Section 12 - Conclusion
    builder.add_step(ReferencesGenerator)             # Section 13 - References
    
    # 4. Build & Save
    builder.build().save("full_report_v2.docx")
    
    print("✨ Process Completed.")

if __name__ == "__main__":
    main()
