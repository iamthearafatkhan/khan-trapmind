# khan_trapmind/rl_engine/process_monitor.py
import psutil
import time
from PyQt6.QtCore import QThread, pyqtSignal

class ProcessMonitorThread(QThread):
    threat_detected = pyqtSignal(str)

    def run(self):
        self.threat_detected.emit("[✔] Process Tree & Cookie Shield Active.")
        
        # Known browsers and shells
        browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe", "opera.exe"]
        shells = ["cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "bash.exe"]
        
        # Keep track of processes we've already killed to avoid spam
        killed_pids = set()

        while True:
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    # 1. DRIVE-BY / MEMORY EXPLOIT DETECTION
                    # If a browser spawns a shell, that is a massive red flag (Drive-by download)
                    if proc.info['name'].lower() in shells:
                        parent = psutil.Process(proc.info['ppid'])
                        if parent.name().lower() in browsers and proc.info['pid'] not in killed_pids:
                            self.threat_detected.emit(
                                f"[🚨 ZERO-DAY PREVENTED] Browser ({parent.name()}) tried to spawn {proc.info['name']}! Killing process."
                            )
                            proc.kill() # Instantly kill the malicious shell
                            killed_pids.add(proc.info['pid'])

                    # 2. COOKIE THEFT DETECTION
                    # Check if a process has files open in browser cookie directories
                    if proc.info['name'].lower() not in browsers and proc.info['name'].lower() not in ["khan_trapmind.exe", "python.exe"]:
                        try:
                            open_files = proc.open_files()
                            for f in open_files:
                                if "Cookies" in f.path or "cookies.sqlite" in f.path:
                                    if proc.info['pid'] not in killed_pids:
                                        self.threat_detected.emit(
                                            f"[🚨 COOKIE THEFT] {proc.info['name']} is trying to steal browser sessions! Killing process."
                                        )
                                        proc.kill()
                                        killed_pids.add(proc.info['pid'])
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass # Normal apps will deny access to open_files

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            time.sleep(1) # Check every second