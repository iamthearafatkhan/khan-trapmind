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
        
        # NEW: Safe background apps that legitimately read cookies
        safe_apps = [
            "msedgewebview2.exe", "eosoverlayrenderer-win64-shipping.exe", 
            "nvidia overlay.exe", "epicwebhelper.exe", "gamebar.exe", 
            "searchapp.exe", "runtimebroker.exe", "svchost.exe",
            "code.exe", "electron.exe", "discord.exe", "spotify.exe"
        ]
        
        killed_pids = set()

        while True:
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    proc_name = proc.info['name'].lower()

                    # 1. DRIVE-BY / MEMORY EXPLOIT DETECTION
                    if proc_name in shells:
                        parent = psutil.Process(proc.info['ppid'])
                        if parent.name().lower() in browsers and proc.info['pid'] not in killed_pids:
                            self.threat_detected.emit(
                                f"[🚨 ZERO-DAY PREVENTED] Browser ({parent.name()}) tried to spawn {proc.info['name']}! Killing process."
                            )
                            proc.kill()
                            killed_pids.add(proc.info['pid'])

                    # 2. COOKIE THEFT DETECTION
                    # Ignore browsers and our safe apps list
                    if proc_name not in browsers and proc_name not in safe_apps and proc_name not in ["khan_trapmind.exe", "python.exe"]:
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
                            pass
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            time.sleep(5)