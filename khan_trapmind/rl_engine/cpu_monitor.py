# khan_trapmind/rl_engine/cpu_monitor.py
import time
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

class CPUMonitorThread(QThread):
    # Signals to update the UI
    cpu_update = pyqtSignal(float, str) # (cpu_percent, top_process_name)
    anomaly_detected = pyqtSignal(str)

    def run(self):
        while True:
            # Get overall CPU usage
            cpu_percent = psutil.cpu_percent(interval=2)
            
            # Find the process using the most CPU
            top_proc = "Unknown"
            max_cpu = 0.0
            
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > max_cpu:
                        max_cpu = proc.info['cpu_percent']
                        top_proc = proc.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

            # Send data to UI
            self.cpu_update.emit(cpu_percent, top_proc)

            # --- THE "RL" ANOMALY DETECTION ---
            # If CPU is over 85% and it's not a known system process, flag it
            if cpu_percent > 85.0 and top_proc not in ["System Idle Process", "System", "svchost.exe", "python.exe"]:
                self.anomaly_detected.emit(f"[⚠️ RL ENGINE] High CPU Anomaly: '{top_proc}' is using {cpu_percent}% CPU. Potential threat!")

            time.sleep(3) # Check every 3 seconds