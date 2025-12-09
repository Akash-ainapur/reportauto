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

def main():
    print("🚀 Starting V2 Report Assembly (Single Object Workflow)...")
    
    # 1. Initialize Context
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    context = ReportContext(project_root)
    
    # 2. Initialize Builder
    builder = ReportBuilder(context)
    
    # 3. Add Steps
    builder.add_step(FrontPageGenerator)
    builder.add_step(CertificateGenerator)
    builder.add_step(DeclarationGenerator)
    builder.add_step(AbstractGenerator)
    builder.add_step(AcknowledgementGenerator)
    
    # 4. Build & Save
    builder.build().save("full_report_v2.docx")
    
    print("✨ Process Completed.")

if __name__ == "__main__":
    main()
