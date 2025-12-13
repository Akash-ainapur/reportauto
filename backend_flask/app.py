import os
import sys
import json
import threading
import subprocess
import time
import uuid
import shutil
from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS

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
                [sys.executable, script_path, '--data', json_path, '--output', output_path],
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

@app.route('/api/generate', methods=['POST'])
def generate_report():
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
        'total_steps': 14,
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
    app.run(host='0.0.0.0', port=port, debug=True)
