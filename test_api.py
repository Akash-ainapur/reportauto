import time
import requests
import sys

import time
import requests
import sys

# Default to localhost, but allow CLI override
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5000'
# Removing trailing slash if present
BASE_URL = BASE_URL.rstrip('/')
def test_health():
    print(f"Testing Health Check at {BASE_URL}/health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health Check Passed!")
        else:
            print(f"❌ Health Check Failed: {response.text}")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        sys.exit(1)

def test_generate():
    print("\nTesting Report Generation Trigger...")
    try:
        response = requests.post(f"{BASE_URL}/api/generate")
        if response.status_code == 202:
            print("✅ Generation Started successfully!")
            return True
        elif response.status_code == 409:
            print("⚠️ Generation already in progress.")
            return True
        else:
            print(f"❌ Failed to start generation: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error triggering generation: {e}")
        return False

def monitor_progress():
    print("\nMonitoring Progress...")
    while True:
        try:
            response = requests.get(f"{BASE_URL}/api/status")
            if response.status_code == 200:
                status = response.json()
                print(f"   Step: {status['current_step']} | Progress: {status['progress']}/14")
                
                if not status['running']:
                    if status['error']:
                        print(f"\n❌ Generation Limit/Error: {status['error']}")
                    else:
                        print("\n✅ Generation Complete!")
                    return
            else:
                print(f"⚠️ Failed to get status: {response.status_code}")
            
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error monitoring status: {e}")
            break

def test_download():
    print("\nTesting File Download...")
    try:
        response = requests.get(f"{BASE_URL}/api/download")
        if response.status_code == 200:
            filename = "test_downloaded_report.docx"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ File downloaded successfully as '{filename}'")
        else:
            print(f"❌ Download failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error downloading: {e}")

if __name__ == '__main__':
    print("🚀 Starting API Verification for Flask Backend")
    print("============================================")
    
    test_health()
    if test_generate():
        monitor_progress()
        test_download()
    
    print("\n============================================")
    print("Test Suite Complete.")
