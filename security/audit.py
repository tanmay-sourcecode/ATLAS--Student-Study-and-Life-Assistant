import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_data")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.json")

def ensure_audit_file_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "w") as f:
            json.dump([], f)

def log_action(action_type: str, details: str):
    """
    Logs an agent action or tool invocation for transparency and auditability.
    Writes to demo_data/audit_log.json.
    """
    try:
        ensure_audit_file_exists()
        
        with open(AUDIT_FILE, "r") as f:
            logs = json.load(f)
            
        new_log = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": details
        }
        logs.append(new_log)
        
        with open(AUDIT_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to write audit log: {str(e)}")
