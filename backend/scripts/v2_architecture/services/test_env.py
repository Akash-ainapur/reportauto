import os
from pathlib import Path
from dotenv import load_dotenv

# Test script to verify .env file loading
print("=" * 60)
print("Testing .env file detection")
print("=" * 60)

# Method 1: Load from current directory
current_dir = Path.cwd()
env_file_current = current_dir / '.env'
print(f"\n1. Current working directory: {current_dir}")
print(f"   Looking for .env at: {env_file_current}")
print(f"   .env exists here: {env_file_current.exists()}")

# Method 2: Load from script location
script_location = Path(__file__).resolve().parent
env_file_script = script_location / '.env'
print(f"\n2. Script location: {script_location}")
print(f"   Looking for .env at: {env_file_script}")
print(f"   .env exists here: {env_file_script.exists()}")

# Method 3: Load from project root (5 levels up)
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent.parent
env_file_root = project_root / '.env'
print(f"\n3. Project root (5 up): {project_root}")
print(f"   Looking for .env at: {env_file_root}")
print(f"   .env exists here: {env_file_root.exists()}")

# Try loading
print("\n" + "=" * 60)
print("Attempting to load .env from project root...")
print("=" * 60)
load_dotenv(dotenv_path=env_file_root)

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✅ SUCCESS! GEMINI_API_KEY found: {api_key[:20]}...")
else:
    print("❌ FAILED! GEMINI_API_KEY not found")
    print("\nPlease create .env file at:")
    print(f"   {project_root / '.env'}")
    print("\nWith content:")
    print("   GEMINI_API_KEY=your-api-key-here")
