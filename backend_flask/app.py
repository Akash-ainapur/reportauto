import os
import sys
import json
import threading
import subprocess
import time
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# --- Configuration & Setup ---

# Determine Project Root (Assuming app.py is in backend_flask/)
# backend_flask/ -> AutomatedReportGenerator/
COURSE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = COURSE_ROOT 
# Fix python path to allow imports from backend/scripts
sys.path.append(PROJECT_ROOT)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'full_report_v2.docx')
DATA_FILE = os.path.join(PROJECT_ROOT, 'backend', 'data', 'full_report_template.json')

# Initialize Flask App
app = Flask(__name__)
# Enable CORS for all domains (allows frontend on Vercel to talk to backend on Render)
CORS(app)

# Global Status Tracking (In-memory for MVP, use Redis for scaling later)
generation_status = {
    'running': False,
    'progress': 0,
    'total_steps': 14,
    'current_step': 'Idle',
    'error': None,
    'last_updated': 0
}

# --- Helper Functions ---

def reset_status():
    global generation_status
    generation_status = {
        'running': False,
        'progress': 0,
        'total_steps': 14,
        'current_step': 'Idle',
        'error': None,
        'last_updated': time.time()
    }

def run_report_generation():
    """Runs the main.py script in a subprocess and parses output for progress."""
    global generation_status
    
    generation_status['running'] = True
    generation_status['progress'] = 0
    generation_status['error'] = None
    generation_status['current_step'] = "Starting process..."
    generation_status['last_updated'] = time.time()

    try:
        # Path to the main generation script
        script_path = os.path.join(PROJECT_ROOT, 'backend', 'scripts', 'v2_architecture', 'main.py')
        
        # Prepare Environment
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        # Start Subprocess
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            env=env
        )

        # Monitor Output for Progress
        for line in process.stdout:
            line = line.strip()
            print(f"GENERATOR: {line}") # Log to console for Render logs
            
            if 'Executing Step:' in line:
                generation_status['progress'] += 1
                step_name = line.split('Executing Step:')[1].strip()
                generation_status['current_step'] = f"Generating {step_name}..."
                generation_status['last_updated'] = time.time()

        process.wait()

        if process.returncode == 0:
            generation_status['progress'] = 14
            generation_status['current_step'] = "Complete"
            generation_status['running'] = False
        else:
            stderr = process.stderr.read()
            generation_status['error'] = f"Script Failure: {stderr}"
            generation_status['running'] = False
            print(f"ERROR: {stderr}")

    except Exception as e:
        generation_status['error'] = str(e)
        generation_status['running'] = False
        print(f"EXCEPTION: {e}")

# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check for Render."""
    return jsonify({'status': 'healthy', 'service': 'report-generator-backend'}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current generation status."""
    return jsonify(generation_status)

@app.route('/api/generate', methods=['POST'])
def generate_report():
    """Starts the report generation process."""
    global generation_status
    
    if generation_status['running']:
        return jsonify({
            'status': 'error',
            'message': 'Generation already in progress'
        }), 409

    # Reset status
    reset_status()

    # Start generation in background thread
    thread = threading.Thread(target=run_report_generation, daemon=True)
    thread.start()

    return jsonify({
        'status': 'accepted',
        'message': 'Report generation started'
    }), 202

@app.route('/api/download', methods=['GET'])
def download_report():
    """Downloads the generated report."""
    if os.path.exists(OUTPUT_FILE):
        return send_file(
            OUTPUT_FILE,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='Project_Report.docx'
        )
    else:
        return jsonify({'error': 'Report not found. Please generate it first.'}), 404

# --- Data Management Endpoints (for Configuration) ---

@app.route('/api/data', methods=['GET'])
def get_data():
    """Reads the configuration JSON."""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['POST'])
def update_data():
    """Updates the configuration JSON."""
    try:
        data = request.json
        if not data:
             return jsonify({'error': 'No JSON data provided'}), 400
             
        # Save to file
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
        return jsonify({'status': 'success', 'message': 'Configuration saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For local testing
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
