# khan_trapmind/core/threat_intel.py
import os
import requests
import threading
import time

class ThreatIntelEngine(threading.Thread):
    def __init__(self, rules_dir, log_callback):
        super().__init__()
        self.rules_dir = rules_dir
        self.log_callback = log_callback
        self.daemon = True 
        self.rule_url = "https://raw.githubusercontent.com/Yara-Rules/rules/master/malware/MALW_Crypto.yar"

    def run(self):
        # Wait 5 seconds so the UI fully loads first
        time.sleep(5) 
        
        while True:
            self.log_callback("[☁️ Cloud] Fetching latest global threat intelligence...")
            try:
                # FIXED: Ensure the folder exists before saving
                os.makedirs(self.rules_dir, exist_ok=True)
                
                response = requests.get(self.rule_url, timeout=10)
                if response.status_code == 200:
                    cloud_rule_path = os.path.join(self.rules_dir, "cloud_threats.yar")
                    with open(cloud_rule_path, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    self.log_callback("[☁️ Cloud] Threat signatures updated successfully from Cloud.")
                else:
                    self.log_callback("[!] Cloud API returned an error.")
            except Exception as e:
                self.log_callback(f"[!] Cloud Sync Failed: {e}")
            
            time.sleep(86400) 