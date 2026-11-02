import os
import sys
import json
import threading
import subprocess
import time
import uuid
import shutil
import base64
import re
from functools import wraps
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
from clerk_backend_api import Clerk
from dotenv import load_dotenv

load_dotenv()

# --- Auth Setup ---
CLERK_SECRET_KEY = os.environ.get("CLERK_SECRET_KEY")
clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY) if CLERK_SECRET_KEY else None

def token_user_id():
    """User id (sub) from the request's Bearer token, or None when there is no usable token."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        # Quick decode to get User ID (sub)
        # production should verify signature via JWKS
        payload = token.split('.')[1]
        # Fix padding
        payload += '=' * (-len(payload) % 4)
        return json.loads(base64.b64decode(payload)).get('sub')
    except Exception:
        return None


def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not clerk_client:
            # Dev bypass if no key
            request.user_id = "dev_user"
            return f(*args, **kwargs)

        request.user_id = token_user_id()
        if not request.user_id:
            return jsonify({'error': 'Unauthorized: Missing or invalid token'}), 401
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_payload import FormError, chat_prompt_parts, report_data_from_form, unwritten_sections, writing_mode

# Reports each signed-in student can generate (a run that left chapters unwritten is not counted)
FREE_REPORTS = int(os.environ.get("FREE_REPORTS_PER_USER", "2"))

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# --- Concurrency Control (Level 1: Free Tier Logic) ---
# Limit concurrent generations to save RAM.
MAX_CONCURRENT_TASKS = 2
generation_semaphore = threading.Semaphore(MAX_CONCURRENT_TASKS)

# In-Memory Status Map: { "session_id": { "status": "processing", "progress": 10 ... } }
status_map = {}
# Sessions waiting for a free slot, oldest first (for "N reports ahead of you")
waiting_sessions = []
# user_id -> session_id of the report they are generating (one at a time per student)
active_jobs = {}

# --- Helper Functions ---

def cleanup_old_files():
    """Deletes files older than 1 hour to prevent disk fill-up."""
    try:
        now = time.time()
        for f in os.listdir(TEMP_DIR):
            f_path = os.path.join(TEMP_DIR, f)
            if os.stat(f_path).st_mtime < now - 3600:
                os.remove(f_path)
        for session_id, status in list(status_map.items()):
            if not status.get('running') and status.get('last_updated', now) < now - 3600:
                status_map.pop(session_id, None)
    except Exception as e:
        print(f"Cleanup Error: {e}")

def reports_used(user_id):
    user = clerk_client.users.get(user_id=user_id)
    meta = getattr(user, 'public_metadata', None) or {}
    return int(meta.get('report_count', 0))


def charge_report(user_id):
    """Counts a finished report against the student's free reports."""
    if not clerk_client or not user_id:
        return
    try:
        clerk_client.users.update(user_id=user_id, public_metadata={'report_count': reports_used(user_id) + 1})
    except Exception as e:
        print(f"Credit update failed for {user_id}: {e}")


def report_file_name(data):
    title = data.get('global_metadata', {}).get('project_title') or 'Project'
    title = re.sub(r'[^A-Za-z0-9 _-]+', '', title).strip()[:80] or 'Project'
    return f"{title} - Report.docx"


def step_label(line):
    """Student-facing progress text for a line of main.py output."""
    if 'Request ' in line and ': Generating' in line:
        counter = line.split('Request ', 1)[1].split(':', 1)[0]
        return f"Writing your chapters ({counter})"
    if 'Executing Step:' in line:
        step = line.split('Executing Step:', 1)[1].strip()
        if step.startswith('BulkAIGeneration'):
            return None
        return f"Formatting {step.replace('_', ' ')}"
    return None


def run_report_generation(session_id, json_path, output_path, user_id=None):
    """Runs the main.py script for a specific session."""
    global status_map
    status = status_map[session_id]

    status['running'] = True
    status['current_step'] = "Waiting for a free slot"
    status['last_updated'] = time.time()
    waiting_sessions.append(session_id)

    try:
        # Acquire Semaphore (Wait if busy)
        with generation_semaphore:
            waiting_sessions.remove(session_id)
            _run_main(session_id, json_path, output_path, user_id)
    finally:
        if session_id in waiting_sessions:
            waiting_sessions.remove(session_id)
        if user_id and active_jobs.get(user_id) == session_id:
            del active_jobs[user_id]


def _run_main(session_id, json_path, output_path, user_id):
    status = status_map[session_id]
    try:
        status['current_step'] = "Starting"
        
        # Script Path
        script_path = os.path.join(PROJECT_ROOT, 'backend', 'scripts', 'v2_architecture', 'main.py')
        
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Run with explicit input/output arguments
        process = subprocess.Popen(
            [sys.executable, "-u", script_path, '--data', json_path, '--output', output_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # one pipe, so a chatty stderr cannot block the process
            text=True,
            encoding='utf-8',
            env=env
        )

        for line in process.stdout:
            line = line.strip()
            print(f"[{session_id}] {line}")

            if 'Executing Step:' in line:
                status['progress'] += 1
                status['last_updated'] = time.time()
            if line.startswith('AI_MISSING_SECTIONS:'):
                missing = line.split(':', 1)[1].strip()
                status['missing_sections'] = [s for s in missing.split(',') if s]
            label = step_label(line)
            if label:
                status['current_step'] = label

        process.wait()

        if process.returncode == 0:
            status['progress'] = status['total_steps']
            status['current_step'] = "Complete"
            status['running'] = False
            status['completed'] = True
            # A report with unwritten chapters does not use up one of the student's free reports
            if status['writing_mode'] == 'server' and not status['missing_sections']:
                charge_report(user_id)
                status['credit_used'] = True
        else:
            status['error'] = "Something went wrong while building your report. It did not use one of your free reports - please try again in a few minutes."
            status['running'] = False
            print(f"[{session_id}] ERROR: main.py exited with {process.returncode}")

    except Exception as e:
        status['error'] = "Something went wrong while building your report. Please try again in a few minutes."
        status['running'] = False
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
    status = dict(status_map[session_id])
    status['queue_position'] = waiting_sessions.index(session_id) + 1 if session_id in waiting_sessions else 0
    return jsonify(status)

@app.route('/api/credits', methods=['GET'])
@authenticate
def get_credits():
    """How many free reports the signed-in student has left."""
    if not clerk_client:
        return jsonify({'limit': None, 'remaining': None})
    try:
        return jsonify({'limit': FREE_REPORTS, 'remaining': max(0, FREE_REPORTS - reports_used(request.user_id))})
    except Exception as e:
        print(f"Credit lookup failed: {e}")
        return jsonify({'limit': FREE_REPORTS, 'remaining': None})

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

@app.route('/api/chat-prompts', methods=['POST'])
def chat_prompts():
    """Prompts students paste into their own AI chat to write the chapters (no AI used here)."""
    form = (request.json or {}).get('form')
    if not isinstance(form, dict):
        return jsonify({'error': 'No form data'}), 400
    try:
        return jsonify({'parts': chat_prompt_parts(form)})
    except Exception as e:
        print(f"Chat prompt build failed: {e}")
        return jsonify({'error': 'Could not prepare the prompts. Please try again.'}), 500


@app.route('/api/generate', methods=['POST'])
def generate_report():
    body = request.json
    if not body:
        return jsonify({'error': 'No data provided'}), 400
    form = body.get('form') if isinstance(body.get('form'), dict) else None
    # Chapters written in the student's own AI chat cost us nothing, so they need no sign-in or credit
    own_writing = form is not None and writing_mode(form) == 'own'
    user_id = token_user_id() if clerk_client else None
    if clerk_client and not user_id and not own_writing:
        return jsonify({'error': 'Please sign in so we can write your report.'}), 401

    # One report at a time per student; a second click resumes the running one
    running = active_jobs.get(user_id) if user_id else None
    if running and status_map.get(running, {}).get('running'):
        return jsonify({'status': 'accepted', 'session_id': running, 'message': 'Already generating'})

    # --- Freemium Logic --- (counted when a report finishes, see run_report_generation)
    if clerk_client and not own_writing:
        try:
            if reports_used(user_id) >= FREE_REPORTS:
                return jsonify({'error': f'You have used your {FREE_REPORTS} free reports.'}), 402
        except Exception as e:
            print(f"Auth Check Failed: {e}")
            return jsonify({'error': 'Could not check your account. Please sign in again and retry.'}), 500

    # The current frontend sends the student form; older clients send the full report data
    if 'form' in body:
        try:
            data = report_data_from_form(body['form'])
        except FormError as e:
            return jsonify({'error': str(e)}), 400
    else:
        data = body

    # Always a server-made id: it becomes part of file paths
    session_id = str(uuid.uuid4())

    # 1. Save User Data to Temp File
    user_json_path = os.path.join(TEMP_DIR, f"{session_id}_data.json")
    user_output_path = os.path.join(TEMP_DIR, f"{session_id}_report.docx")

    with open(user_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # 2. Initialize Status
    status_map[session_id] = {
        'running': True,
        'progress': 0,
        'total_steps': 24,  # 6 AI batches + 18 sections of a full Phase II report
        'current_step': 'Queued',
        'error': None,
        'last_updated': time.time(),
        'completed': False,
        'missing_sections': unwritten_sections(form) if form else [],
        'writing_mode': 'own' if own_writing else 'server',
        'credit_used': False,
        'file_name': report_file_name(data),
    }
    if user_id:
        active_jobs[user_id] = session_id

    # 3. Start Thread
    thread = threading.Thread(target=run_report_generation,
                              args=(session_id, user_json_path, user_output_path, user_id), daemon=True)
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
    session_id = request.args.get('session_id', '')
    try:
        session_id = str(uuid.UUID(session_id))  # also keeps the id from reaching outside TEMP_DIR
    except ValueError:
        return jsonify({'error': 'Invalid session_id'}), 400

    file_path = os.path.join(TEMP_DIR, f"{session_id}_report.docx")
    if not os.path.exists(file_path):
        return jsonify({'error': 'This report has expired. Reports are kept for one hour - please generate it again.'}), 404

    # Kept for an hour so a failed download can be retried; cleanup_old_files removes it
    return send_file(
        file_path,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name=status_map.get(session_id, {}).get('file_name') or 'Project_Report.docx'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Threaded=True is default, which allows multiple requests. 
    # Our semaphore controls the heavy lifting.
    # Validation: Turn off debug mode in 'production' usage to prevent
    # auto-reloads from killing background generation threads.
    app.run(host='0.0.0.0', port=port, debug=False)
