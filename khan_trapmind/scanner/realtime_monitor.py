# khan_trapmind/scanner/realtime_monitor.py
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .yara_engine import YaraScanner
from .quarantine import QuarantineManager

class ThreatInterceptor(FileSystemEventHandler):
    def __init__(self, log_callback):
        self.scanner = YaraScanner()
        self.quarantine = QuarantineManager()
        self.log_callback = log_callback
        self.recent_scans = {}

    def on_created(self, event):
        if not event.is_directory: self._process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory: self._process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory: self._process_file(event.dest_path)

    def _process_file(self, file_path):
        base_name = os.path.basename(file_path)
        
        # 1. IGNORE NOISY FOLDERS (Crucial for performance)
        # Ignore AppData, Temporary folders, and browser cache to prevent CPU spikes
        ignore_paths = ["\\AppData\\", "/AppData/", "\\Windows\\", "/Windows/", "\\Temp\\", "/Temp/", "node_modules", ".git"]
        if any(p in file_path for p in ignore_paths):
            return

        # 2. IGNORE TRAPMIND'S OWN FILES
        if base_name.startswith('.') or file_path.endswith(('.tmp', '.crdownload', '.part')):
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
        self.event_handler = ThreatInterceptor(self.log_callback)

    def start(self):
        for path in self.paths:
            if os.path.exists(path):
                # recursive=True allows it to watch all subfolders
                self.observer.schedule(self.event_handler, path, recursive=True)
        self.observer.start()
        self.log_callback(f"[Khan TrapMind] Real-time protection active across User Profile.")

    def stop(self):
        self.observer.stop()
        self.observer.join()