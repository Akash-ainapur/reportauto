
import sys
import os
from unittest.mock import MagicMock, patch

# Add the script directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from builder import ReportBuilder, ReportContext
from components.abstract import AbstractGenerator
from components.introduction import IntroductionGenerator

def test_bulk_extraction():
    print("Testing Bulk Extraction Logic...")
    
    # Mock data
    mock_data = {
        "global_metadata": {
            "project_title": "Test Project",
            "department_name": "Test Dept",
            "academic_year": "2024-25"
        },
        "ai_content_config": {
            "enabled": True,
            "sections": {
                "abstract": {"generate": True},
                "introduction": {"generate": True}
            }
        },
        "people": {"students": [], "guide": []}
    }
    
    # Mock context
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_file = os.path.join(project_root, "backend", "data", "full_report_template.json")
    context = ReportContext(project_root, data_file=data_file)
    context.data = mock_data
    
    # Raw AI response with tags
    raw_response = """
    <abstract>
    This is the extracted abstract content.
    </abstract>
    <introduction>
    This is the extracted introduction content with ### Subheadings and **bold** text.
    </introduction>
    """
    
    context.extract_bulk_content(raw_response)
    
    assert "abstract" in context.bulk_content
    assert "introduction" in context.bulk_content
    assert "This is the extracted abstract" in context.bulk_content["abstract"]
    
    print("✅ Extraction Logic Verified.")

def test_builder_integration():
    print("Testing Builder Integration...")
    
    with patch('services.gemini_service.GeminiService') as MockGemini, \
         patch('components.ai_content_base.GeminiService') as MockGeminiComp:
        
        mock_instance = MockGemini.return_value
        MockGeminiComp.return_value = mock_instance
        # Mock bulk response
        mock_instance.generate_bulk_content.return_value = "<abstract>Bulk Abstract</abstract><introduction>Bulk Intro</introduction>"
        # Mock individual fallback (should not be called for abstract/intro)
        mock_instance.generate_content.return_value = "Fallback Content"
        
        # Setup Builder
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        data_file = os.path.join(project_root, "backend", "data", "full_report_template.json")
        context = ReportContext(project_root, data_file=data_file)
        context.data = {
            "global_metadata": {"project_title": "Test"},
            "ai_content_config": {"enabled": True},
            "people": {"students": [], "guide": [], "approvers": {}},
            "certificate_info": {}
        }
        builder = ReportBuilder(context)
        builder.add_step(AbstractGenerator)
        builder.add_step(IntroductionGenerator)
        
        # We need to mock _get_bulk_groups to only include what we want to test
        builder._get_bulk_groups = lambda: [["abstract", "introduction"]]
        
        # Run build (mock docx generation parts to avoid file issues)
        with patch('components.ai_content_base.AIContentBase.add_body_content'):
            builder.build()
            
        # Verify calls
        assert mock_instance.generate_bulk_content.call_count == 1
        # generate_content might be called for individual if bulk fails, but in our success case it shouldn't be for these two
        print("✅ Builder Integration Verified (AI calls minimized).")

if __name__ == "__main__":
    try:
        test_bulk_extraction()
        test_builder_integration()
        print("\n✨ ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
