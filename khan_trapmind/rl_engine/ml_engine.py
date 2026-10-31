# khan_trapmind/rl_engine/ml_engine.py
import time
import psutil
from PyQt6.QtCore import QThread, pyqtSignal
from sklearn.ensemble import IsolationForest

class MLAnomalyEngine(QThread):
    anomaly_detected = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        self.is_trained = False
        self.training_data = []
        self.start_time = time.time()
        self.last_alert_time = 0 # NEW: Cooldown timer

    def run(self):
        while self.is_running:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            net_io = psutil.net_io_counters()
            net_mb = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
            
            current_data = [cpu, ram, net_mb]
            self.stats_updated.emit({"cpu": cpu, "ram": ram, "net": net_mb})

            if not self.is_trained:
                self.training_data.append(current_data)
                if time.time() - self.start_time > 60:
                    self.model.fit(self.training_data)
                    self.is_trained = True
                    self.anomaly_detected.emit("[✔] AI ML Model Trained. Now monitoring for zero-day anomalies.")
            else:
                prediction = self.model.predict([current_data])
                if prediction[0] == -1:
                    # NEW: Only alert if 30 seconds have passed since the last alert
                    if time.time() - self.last_alert_time > 30:
                        self.anomaly_detected.emit(
                            f"[🚨 AI ANOMALY] Unusual system behavior detected! CPU: {cpu}%, RAM: {ram}%, Net: {net_mb:.2f}MB"
                        )
                        self.last_alert_time = time.time() # Reset timer
            
            time.sleep(2)

    def stop(self):
        self.is_running = False