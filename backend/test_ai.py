import os
import sys
from pathlib import Path

# Add the correct paths to sys.path so we can import the service
backend_dir = Path(__file__).resolve().parent
v2_dir = backend_dir / "scripts" / "v2_architecture"
sys.path.append(str(v2_dir))

from services.gemini_service import GeminiService

def test_ai():
    print("🚀 Starting AI Service Test...")
    
    # Initialize Service
    try:
        service = GeminiService()
        
        if not service.is_available():
            print("❌ AI Service not available. Check your GEMINI_API_KEY in the .env file.")
            return

        print(f"✅ AI Service available using model: {service.model.model_name if hasattr(service.model, 'model_name') else 'Unknown'}")
        
        # Test Generation with System Instruction (Matches user's failing path)
        prompt = "Write a one-sentence requirement for a report generator."
        system_instruction = "You are a professional technical writer."
        print(f"📡 Sending prompt: '{prompt}' with system instruction")
        
        # We disable cache for the test to ensure a real API call
        response = service.generate_content(prompt, system_instruction=system_instruction, use_cache=False)
        
        with open("ai_test_result.txt", "w", encoding="utf-8") as rf:
            rf.write(f"PROMPT: {prompt}\nRESPONSE: {response}")

        print("\n--- AI RESPONSE ---")
        print(response)
        print("-------------------\n")
        
        if "[AI-Generated Content Placeholder]" in response:
            print("❌ Test Failed: Received fallback/placeholder content. API might be blocked or misconfigured.")
        else:
            print("🎉 Test Successful! AI is responding correctly.")

    except Exception as e:
        print(f"💥 Critical Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai()
