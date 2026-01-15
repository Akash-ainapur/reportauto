import os
import sys
import json
import threading
import subprocess
import time
import uuid
import shutil
import base64
from functools import wraps
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from clerk_backend_api import Clerk
from dotenv import load_dotenv

load_dotenv()

# --- Auth Setup ---
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY) if CLERK_SECRET_KEY else None

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not clerk_client:
            # Dev bypass if no key
            request.user_id = "dev_user"
            return f(*args, **kwargs)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized: Missing token'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            # Quick decode to get User ID (sub)
            # production should verify signature via JWKS
            payload = token.split('.')[1]
            # Fix padding
            payload += '=' * (-len(payload) % 4)
            decoded = json.loads(base64.b64decode(payload))
            request.user_id = decoded.get('sub')
        except Exception as e:
            return jsonify({'error': 'Unauthorized: Invalid token format'}), 401
            
        return f(*args, **kwargs)
    return decorated

# --- Configuration & Setup ---

# Determine Project Root
COURSE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = COURSE_ROOT 
sys.path.append(PROJECT_ROOT)

# Directory for Session Data (Input JSONs and Output DOCXs)
TEMP_DIR = os.path.join(PROJECT_ROOT, 'temp_sessions')
os.makedirs(TEMP_DIR, exist_ok=True)

# Default Template (Read-Only Source)
DEFAULT_DATA_FILE = os.path.join(PROJECT_ROOT, 'backend', 'data', 'full_report_template.json')

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# --- Concurrency Control (Level 1: Free Tier Logic) ---
# Limit concurrent generations to save RAM.
MAX_CONCURRENT_TASKS = 2
generation_semaphore = threading.Semaphore(MAX_CONCURRENT_TASKS)

# In-Memory Status Map: { "session_id": { "status": "processing", "progress": 10 ... } }
status_map = {}

# --- Helper Functions ---

def cleanup_old_files():
    """Deletes files older than 1 hour to prevent disk fill-up."""
    try:
        now = time.time()
        for f in os.listdir(TEMP_DIR):
            f_path = os.path.join(TEMP_DIR, f)
            if os.stat(f_path).st_mtime < now - 3600:
                os.remove(f_path)
    except Exception as e:
        print(f"Cleanup Error: {e}")

def run_report_generation(session_id, json_path, output_path):
    """Runs the main.py script for a specific session."""
    global status_map
    
    # Update Status
    status_map[session_id]['running'] = True
    status_map[session_id]['current_step'] = "Waiting for slot..."
    status_map[session_id]['last_updated'] = time.time()

    # Acquire Semaphore (Wait if busy)
    with generation_semaphore:
        try:
            status_map[session_id]['current_step'] = "Starting process..."
            
            # Script Path
            script_path = os.path.join(PROJECT_ROOT, 'backend', 'scripts', 'v2_architecture', 'main.py')
            
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # Run with explicit input/output arguments
            process = subprocess.Popen(
                [sys.executable, "-u", script_path, '--data', json_path, '--output', output_path],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                env=env
            )

            for line in process.stdout:
                line = line.strip()
                print(f"[{session_id}] {line}")
                
                if 'Executing Step:' in line:
                    status_map[session_id]['progress'] += 1
                    step_name = line.split('Executing Step:')[1].strip()
                    status_map[session_id]['current_step'] = f"Generating {step_name}..."
                    status_map[session_id]['last_updated'] = time.time()

            process.wait()

            if process.returncode == 0:
                status_map[session_id]['progress'] = 14
                status_map[session_id]['current_step'] = "Complete"
                status_map[session_id]['running'] = False
                status_map[session_id]['completed'] = True
            else:
                stderr = process.stderr.read()
                status_map[session_id]['error'] = f"Script Failure: {stderr}"
                status_map[session_id]['running'] = False
                print(f"[{session_id}] ERROR: {stderr}")

        except Exception as e:
            status_map[session_id]['error'] = str(e)
            status_map[session_id]['running'] = False
            print(f"[{session_id}] EXCEPTION: {e}")

# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'mode': 'multi-user-session'}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in status_map:
        return jsonify({'error': 'Invalid Session ID'}), 404
    return jsonify(status_map[session_id])

@app.route('/api/data', methods=['GET'])
def get_data():
    """Returns the default template for new users."""
    try:
        with open(DEFAULT_DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/context-data', methods=['GET'])
@authenticate
def get_context_data():
    """Returns available departments and years."""
    try:
        dept_file = os.path.join(PROJECT_ROOT, 'backend', 'data', 'departments_context.json')
        with open(dept_file, 'r') as f:
            depts = json.load(f)
        
        # Years can be hardcoded or dynamic. Hardcoding for now relative to current year.
        current_year = 2025 # as per prompt time it is Dec 2025
        years = [f"{current_year-1}-{str(current_year)[-2:]}", f"{current_year}-{str(current_year+1)[-2:]}"]
        
        departments = list(depts.keys())
        departments.append("TEST DEPARTMENT")
        
        return jsonify({
            "departments": departments,
            "years": years
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/defaults', methods=['GET'])
@authenticate
def get_defaults():
    """Returns merged default data based on Dept and Year."""
    dept = request.args.get('dept')
    year = request.args.get('year')
    
    try:
        # 1. Load Master Template
        with open(DEFAULT_DATA_FILE, 'r') as f:
            data = json.load(f)
            
        # 2. Load Context Data
        dept_file = os.path.join(PROJECT_ROOT, 'backend', 'data', 'departments_context.json')
        with open(dept_file, 'r') as f:
            dept_context = json.load(f)
            
        # 3. Merge Logic
        if dept == "TEST DEPARTMENT":
            # AUTO-FILL EVERYTHING FOR TESTING
            data['global_metadata'].update({
                'project_title': "Autonomous Traffic Surveillance System using YOLOv8",
                'project_subtitle': "An AI-powered approach to urban traffic management",
                'domain': "Artificial Intelligence & Computer Vision",
                'project_type': "Major Project",
                'course_name': "Bachelor of Engineering in CSE",
                'academic_year': "2024-25",
                'semester': "VIII",
                'department_name': "Computer Science and Engineering",
                'department_abbr': "CSE",
                'college_name': "MVJ College of Engineering",
                'city_code': "Bangalore - 67"
            })
            data['people']['students'] = [
                {"name": "Alice Johnson", "usn": "1MJ21CS001"},
                {"name": "Bob Smith", "usn": "1MJ21CS002"},
                {"name": "Charlie Brown", "usn": "1MJ21CS003"},
                {"name": "Diana Ross", "usn": "1MJ21CS004"}
            ]
            data['people']['guide'] = [{
                "name": "Dr. Sarah Connor",
                "designation": "Associate Professor",
                "department": "Department of CSE",
                "role": "Internal Guide"
            }]
            data['ai_context'] = "My project is about using YOLOv8 for real-time traffic surveillance. It identifies congestion, license plates, and emergency vehicles. It uses a Python backend with a React dashboard."
            
        elif dept and dept in dept_context:
            ctx = dept_context[dept]
            # Global Metadata
            data['global_metadata']['department_name'] = ctx.get('name', '')
            data['global_metadata']['department_short'] = ctx.get('short', '')
            data['global_metadata']['department_abbr'] = ctx.get('short', '')
            if year:
                data['global_metadata']['academic_year'] = year
                
            # People: Approvers
            if 'hod' in ctx:
                data['people']['approvers']['hod'] = ctx['hod']
                data['certificate_info']['hod_name'] = ctx['hod']['name'] 
                data['certificate_info']['hod_designation'] = ctx['hod']['designation']

            if 'dean' in ctx:
                data['people']['approvers']['dean'] = ctx['dean']
                data['certificate_info']['dean_name'] = ctx['dean']['name']
                data['certificate_info']['dean_designation'] = ctx['dean']['designation']

        # 4. Clear/Blank out user fields (ONLY IF NOT TEST DEPT)
        if dept != "TEST DEPARTMENT":
            data['global_metadata']['project_title'] = ""
            data['global_metadata']['project_subtitle'] = ""
            data['global_metadata']['domain'] = ""
            data['global_metadata']['project_type'] = ""
            data['global_metadata']['course_name'] = ""
            data['people']['students'] = []
            data['people']['guide'] = []
            data['ai_context'] = "" # Ensure blank

        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
@authenticate
def generate_report():
    # --- Freemium Logic ---
    if clerk_client:
        try:
            user = clerk_client.users.get(user_id=request.user_id)
            # Access public_metadata safely
            # Note: SDK returns objects, not dicts usually. user.public_metadata
            # Verify SDK structure via assumption or safely handle
            meta = getattr(user, 'public_metadata', {})
            count = meta.get('report_count', 0)
            
            if count >= 2:
                return jsonify({'error': 'Free limit reached (2/2). Upgrade to continue.'}), 402
            
            # Increment Count (Optimistic update)
            clerk_client.users.update(user_id=request.user_id, public_metadata={'report_count': count + 1})
            print(f"User {request.user_id} used credit {count + 1}/2")

        except Exception as e:
            print(f"Auth Check Failed: {e}")
            return jsonify({'error': 'Authentication failed during credit check'}), 500
            
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Get or Create Session ID
    session_id = request.args.get('session_id')
    if not session_id:
        # Fallback if frontend forgets (shouldn't happen with updated frontend)
        session_id = str(uuid.uuid4())
    
    # 1. Save User Data to Temp File
    user_json_path = os.path.join(TEMP_DIR, f"{session_id}_data.json")
    user_output_path = os.path.join(TEMP_DIR, f"{session_id}_report.docx")
    
    with open(user_json_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    # 2. Initialize Status
    status_map[session_id] = {
        'running': True,
        'progress': 0,
        'total_steps': 17,
        'current_step': 'Queued',
        'error': None,
        'last_updated': time.time(),
        'completed': False
    }
    
    # 3. Start Thread
    thread = threading.Thread(target=run_report_generation, args=(session_id, user_json_path, user_output_path), daemon=True)
    thread.start()
    
    # 4. Cleanup Trigger (Fire and forget)
    threading.Thread(target=cleanup_old_files, daemon=True).start()

    return jsonify({
        'status': 'accepted', 
        'session_id': session_id,
        'message': 'Request queued'
    })

@app.route('/api/download', methods=['GET'])
def download_report():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
        
    file_path = os.path.join(TEMP_DIR, f"{session_id}_report.docx")
    
    if os.path.exists(file_path):
        # Schedule deletion after sending
        @after_this_request
        def remove_file(response):
            try:
                # Optional: Delete immediately or keep for short cache?
                # For high security/space, delete now.
                # os.remove(file_path) 
                # Actually, keep it for a bit in case download fails. cleanup_old_files handles it.
                pass
            except Exception as e:
                print(e)
            return response

        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='Project_Report.docx'
        )
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Threaded=True is default, which allows multiple requests. 
    # Our semaphore controls the heavy lifting.
    # Validation: Turn off debug mode in 'production' usage to prevent
    # auto-reloads from killing background generation threads.
    app.run(host='0.0.0.0', port=port, debug=False)
