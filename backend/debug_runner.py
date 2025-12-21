import os
import sys
import json
import subprocess

# Setup paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BACKEND_DIR, "scripts", "v2_architecture")
DATA_DIR = os.path.join(BACKEND_DIR, "data")
TEMP_DIR = os.path.join(BACKEND_DIR, "debug_output")
os.makedirs(TEMP_DIR, exist_ok=True)

# 1. Load the FULL template first (to get structure)
with open(os.path.join(DATA_DIR, "full_report_template.json"), "r") as f:
    template = json.load(f)

# 2. MALFORM / STRIP the data to mimic the crash scenarios
# Case A: Missing specific keys (like department_name) which we already fixed, but let's test.
# Case B: Empty Lists (The current crash: No guides, No students)
# Case C: Missing optional fields

print("--- CREATING STRESS TEST PAYLOAD ---")
stress_payload = template.copy()

# mimic what the frontend might send if user barely touches anything
stress_payload["global_metadata"]["department_name"] = "Computer Science" # Put this back to pass the first check
# BUT remove others
if "college_name" in stress_payload["global_metadata"]:
    del stress_payload["global_metadata"]["college_name"] 

# EMPTY LISTS - The crash cause
stress_payload["people"]["guide"] = [] 
stress_payload["people"]["students"] = []

# Save this payload
json_path = os.path.join(TEMP_DIR, "stress_test.json")
with open(json_path, "w") as f:
    json.dump(stress_payload, f, indent=4)

print(f"Payload saved to {json_path}")

# 3. Run main.py against this payload
main_script = os.path.join(SCRIPTS_DIR, "main.py")
output_docx = os.path.join(TEMP_DIR, "stress_test_report.docx")

print(f"--- RUNNING MAIN.PY ---")
cmd = [sys.executable, main_script, "--data", json_path, "--output", output_docx]

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

try:
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        cwd=os.path.dirname(BACKEND_DIR), # Run from project root logic? No, scripts expect to find data nearby?
        # main.py adds project root to path. 
        env=env
    )
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("✅ SUCCESS: Report generated even with missing data!")
    else:
        print("❌ FAILED: Script crashed.")

except Exception as e:
    print(f"Execution Error: {e}")
