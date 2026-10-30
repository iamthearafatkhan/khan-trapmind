# scanner/quarantine.py
import os
import shutil
import uuid
from datetime import datetime

QUARANTINE_DIR = os.path.expanduser("~/.khan_trapmind/quarantine")

class QuarantineManager:
    def __init__(self):
        os.makedirs(QUARANTINE_DIR, exist_ok=True)

    def isolate(self, file_path: str, threat_name: str):
        if not os.path.exists(file_path):
            return False
        
        file_name = os.path.basename(file_path)
        q_id = str(uuid.uuid4())[:8]
        safe_name = f"{q_id}_{file_name}.quarantined"
        dest_path = os.path.join(QUARANTINE_DIR, safe_name)
        
        try:
            # Move file
            shutil.move(file_path, dest_path)
            
            # Remove execute permissions (Linux/Mac) and make read-only (Windows)
            os.chmod(dest_path, 0o400)
            
            # Log the event
            print(f"[KHAN TRAPMIND] QUARANTINED: {file_name} | Threat: {threat_name}")
            return True
        except Exception as e:
            print(f"[!] Failed to quarantine {file_name}: {e}")
            return False