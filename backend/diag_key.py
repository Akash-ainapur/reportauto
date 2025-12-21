import os
from pathlib import Path
from dotenv import load_dotenv

def diagnostic():
    current_file = Path(__file__).resolve()
    # Path logic from gemini_service.py
    project_root = current_file.parent.parent
    env_path = project_root / '.env'
    
    print(f"Checking .env at: {env_path}")
    print(f"File exists: {env_path.exists()}")
    
    load_dotenv(dotenv_path=env_path)
    
    key = os.getenv('GEMINI_API_KEY')
    
    if not key:
        print("❌ GEMINI_API_KEY is NOT set in environment.")
        return

    print(f"Key length: {len(key)}")
    if len(key) > 4:
        print(f"Key starts with: {key[:4]}...")
    else:
        print(f"Key value: {key}")

    # Check if it looks like a Gemini key (usually starts with AIza)
    if key.startswith("AIza"):
        print("✅ Key format looks like a Google API key (AIza...).")
    else:
        print("⚠️  Key format does NOT start with AIza. It might be invalid or an error message.")

if __name__ == "__main__":
    diagnostic()
