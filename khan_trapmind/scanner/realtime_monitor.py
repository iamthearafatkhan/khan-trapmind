import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .yara_engine import YaraScanner
from .quarantine import QuarantineManager
from ..ai_defense.honeytokens import HoneytokenDeployer

class ThreatInterceptor(FileSystemEventHandler):
    def __init__(self, log_callback, honeytoken_names):
        self.scanner = YaraScanner()
        self.quarantine = QuarantineManager()
        self.log_callback = log_callback
        self.recent_scans = {}
        self.honeytokens = honeytoken_names # Store the names of our traps

    def on_created(self, event):
        if not event.is_directory:
            self._process_file(event.src_path, "Created")

    def on_modified(self, event):
        if not event.is_directory:
            self._process_file(event.src_path, "Modified")

    def on_moved(self, event):
        if not event.is_directory:
            self._process_file(event.dest_path, "Moved/Renamed")

    def _process_file(self, file_path, event_type):
        base_name = os.path.basename(file_path)
        
        # --- AI TRAP DETECTION ---
        # If a honeytoken is modified, read, or moved, ALERT IMMEDIATELY
        if base_name in self.honeytokens and event_type in ["Modified", "Moved/Renamed"]:
            self.log_callback(f"[🚨 CRITICAL] AI AGENT OR HACKER DETECTED! They touched the honeytoken: {base_name}")
            return # Stop processing further so we don't quarantine our own trap

        if base_name.startswith('.') or file_path.endswith(('.tmp', '.crdownload')):
            return

        current_time = time.time()
        if file_path in self.recent_scans and (current_time - self.recent_scans[file_path]) < 3.0:
            return
        
        self.recent_scans[file_path] = current_time

        time.sleep(0.2) 
        is_threat, threat_name = self.scanner.scan_file(file_path)
        
        if is_threat:
            self.log_callback(f"[🚨 ALERT] Malware detected: {base_name} -> {threat_name}")
            success = self.quarantine.isolate(file_path, threat_name)
            if success:
                self.log_callback(f"[✔] {base_name} securely quarantined.")

class RealtimeMonitor:
    def __init__(self, paths_to_watch, log_callback):
        self.paths = paths_to_watch
        self.log_callback = log_callback
        self.observer = Observer()
        
        # Deploy Traps on startup
        self.deployer = HoneytokenDeployer(paths_to_watch[0]) # Deploy to Downloads
        deployed_traps = self.deployer.deploy_traps()
        
        # Pass trap names to the interceptor
        self.event_handler = ThreatInterceptor(self.log_callback, deployed_traps)

    def start(self):
        for path in self.paths:
            if os.path.exists(path):
                self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()
        self.log_callback(f"[Khan TrapMind] Real-time protection active.")
        self.log_callback(f"[🪤] AI Honeytokens deployed: {', '.join(self.event_handler.honeytokens)}")

    def stop(self):
        self.observer.stop()
        self.observer.join()