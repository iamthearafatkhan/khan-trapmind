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
        self.last_alert_time = 0
        
        # Track network delta
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()

    def run(self):
        while self.is_running:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            
            # Calculate Network Speed (MB/s)
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            time_diff = current_time - self.last_time
            
            if time_diff > 0:
                sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / (1024 * 1024)
                recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / (1024 * 1024)
                net_speed_mb = (sent + recv) / time_diff
            else:
                net_speed_mb = 0.0
                
            self.last_net_io = current_net_io
            self.last_time = current_time
            
            current_data = [cpu, ram, net_speed_mb]
            self.stats_updated.emit({"cpu": cpu, "ram": ram, "net": net_speed_mb})

            if not self.is_trained:
                self.training_data.append(current_data)
                if time.time() - self.start_time > 60:
                    self.model.fit(self.training_data)
                    self.is_trained = True
                    self.anomaly_detected.emit("[✔] AI ML Model Trained. Now monitoring for zero-day anomalies.")
            else:
                prediction = self.model.predict([current_data])
                if prediction[0] == -1:
                    if time.time() - self.last_alert_time > 30:
                        self.anomaly_detected.emit(
                            f"[🚨 AI ANOMALY] Unusual system behavior! CPU: {cpu}%, RAM: {ram}%, Net Speed: {net_speed_mb:.2f} MB/s"
                        )
                        self.last_alert_time = time.time()
            
            time.sleep(5)

    def stop(self):
        self.is_running = False