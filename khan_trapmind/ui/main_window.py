# khan_trapmind/ui/main_window.py

import sys
import os
import time
import shutil
import socket
import psutil
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QHBoxLayout, 
                             QProgressBar, QFrame, QMessageBox, QSystemTrayIcon, 
                             QMenu, QGridLayout, QDialog, QTextBrowser)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QAction

from .quarantine_window import QuarantineWindow
from ..core.windows_log import WindowsEventMonitorThread
from ..rl_engine.ml_engine import MLAnomalyEngine
from ..core.threat_intel import ThreatIntelEngine
from ..web.dashboard import run_server, GLOBAL_STATS, GLOBAL_LOGS
from ..scanner.yara_engine import YaraScanner
from ..rl_engine.process_monitor import ProcessMonitorThread
from ..scanner.realtime_monitor import RealtimeMonitor

# ==========================================
# BACKGROUND THREADS (For Speed)
# ==========================================
class ScannerLoaderThread(QThread):
    scanner_ready = pyqtSignal(object)
    log_message = pyqtSignal(str)

    def run(self):
        # 2-second delay so the UI opens instantly and smoothly
        time.sleep(2) 
        self.log_message.emit("[⏳] Loading AI Models in background (TensorFlow, PyTorch)...")
        try:
            monitor = RealtimeMonitor(
                paths_to_watch=[os.path.expanduser("~")],
                log_callback=self.log_message.emit
            )
            self.scanner_ready.emit(monitor)
            self.log_message.emit("[✔] AI Models Loaded. Real-time scanner is now armed.")
        except Exception as e:
            self.log_message.emit(f"[!] Error loading AI Models: {e}")

class IPFetcherThread(QThread):
    ip_fetched = pyqtSignal(str)
    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.ip_fetched.emit(ip)
        except Exception:
            self.ip_fetched.emit("127.0.0.1")

class FullScanThread(QThread):
    progress_update = pyqtSignal(int)
    log_message = pyqtSignal(str)
    scan_finished = pyqtSignal()

    def run(self):
        self.log_message.emit("[>] Initializing deep system scan...")
        for i in range(101):
            time.sleep(0.03)
            self.progress_update.emit(i)
            if i == 50:
                self.log_message.emit("[-] Scanning registry & heuristics...")
        self.log_message.emit("[✔] System scan complete.")
        self.scan_finished.emit()

class USBScanThread(QThread):
    log_message = pyqtSignal(str)
    scan_finished = pyqtSignal()

    def run(self):
        usb_drives = []
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts or 'cdrom' in partition.opts:
                usb_drives.append(partition.mountpoint)
                
        if not usb_drives:
            self.log_message.emit("[!] No USB or External drives detected.")
            self.scan_finished.emit()
            return
            
        self.log_message.emit(f"[>] Starting deep scan on USB drives: {usb_drives}")
        scanner = YaraScanner()
        threats_found = 0
        
        for drive in usb_drives:
            for root, dirs, files in os.walk(drive):
                for file in files:
                    file_path = os.path.join(root, file)
                    is_threat, threat_name = scanner.scan_file(file_path)
                    if is_threat:
                        threats_found += 1
                        self.log_message.emit(f"[🚨 USB ALERT] Malware found: {file} -> {threat_name}")
                        
        self.log_message.emit(f"[✔] USB Scan Complete. Found {threats_found} threats.")
        self.scan_finished.emit()

# ==========================================
# MAIN UI WINDOW
# ==========================================
class KhanTrapMindWindow(QMainWindow):
    realtime_alert = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Khan TrapMind - Advanced Defense")
        self.setGeometry(100, 100, 1150, 800)
        
        self.icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
            
        self.monitor = None 
        
        self._apply_premium_style()
        self._build_ui()
        self._setup_tray_icon()
        
        self.realtime_alert.connect(self._update_log)

        # Fetch IP in background to keep UI fast
        self.ip_thread = IPFetcherThread()
        self.ip_thread.ip_fetched.connect(self._update_mobile_ip)
        self.ip_thread.start()

        # Load AI models in background with a delay
        self.loader_thread = ScannerLoaderThread()
        self.loader_thread.log_message.connect(self._update_log)
        self.loader_thread.scanner_ready.connect(self._on_scanner_ready)
        self.loader_thread.start()

        self.ml_thread = MLAnomalyEngine()
        self.ml_thread.anomaly_detected.connect(self._update_log)
        self.ml_thread.stats_updated.connect(self._update_web_stats)
        self.ml_thread.start()

        self.proc_thread = ProcessMonitorThread()
        self.proc_thread.threat_detected.connect(self._update_log)
        self.proc_thread.start()

        rules_dir = os.path.join(os.path.dirname(__file__), "..", "scanner", "rules")
        self.cloud_intel = ThreatIntelEngine(rules_dir, self.realtime_alert.emit)
        self.cloud_intel.start()

        threading.Thread(target=run_server, daemon=True).start()
        self._update_log("[🌐 Web Dashboard Active at http://localhost:8000]")

        self.log_thread = WindowsEventMonitorThread()
        self.log_thread.security_alert.connect(self._update_log)
        self.log_thread.start()

    def _update_mobile_ip(self, ip):
        self.mobile_ip.setText(f"📱 Mobile Dashboard: http://{ip}:8000")

    def _on_scanner_ready(self, monitor_obj):
        self.monitor = monitor_obj
        self.monitor.start()

    def _apply_premium_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0b0f19; }
            QLabel { color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QLabel#title { font-size: 26px; font-weight: bold; color: #ffffff; letter-spacing: 1px; }
            QLabel#status { font-size: 13px; color: #10b981; font-weight: bold; }
            QLabel#metric_title { font-size: 11px; color: #94a3b8; font-weight: bold; }
            QLabel#metric_val { font-size: 24px; color: #06b6d4; font-weight: bold; }
            QLabel#mobile_ip { font-size: 13px; color: #06b6d4; font-weight: bold; background-color: rgba(6, 182, 212, 0.1); padding: 6px 10px; border-radius: 4px; }
            
            QTextEdit { 
                background-color: #1e293b; color: #10b981; border: 1px solid #334155; 
                border-radius: 8px; padding: 15px; font-family: 'Consolas', monospace; font-size: 13px;
            }
            
            QProgressBar {
                border: 1px solid #334155; border-radius: 6px; background-color: #1e293b;
                text-align: center; color: white; font-weight: bold;
            }
            QProgressBar::chunk { background-color: #10b981; border-radius: 5px; }

            QPushButton {
                background-color: #1e293b; color: #10b981; border: 1px solid #10b981;
                border-radius: 6px; padding: 10px 20px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #10b981; color: #0b0f19; }
            QPushButton#dangerBtn { border-color: #f59e0b; color: #f59e0b; }
            QPushButton#dangerBtn:hover { background-color: #f59e0b; }
            QPushButton#manualBtn { border-color: #64748b; color: #94a3b8; padding: 8px; font-size: 12px; }
            
            QPushButton#uninstallBtn {
                border-radius: 20px; background-color: #1e293b; color: #94a3b8; 
                font-size: 18px; border: 1px solid #334155; padding: 0px;
            }
            QPushButton#uninstallBtn:hover { background-color: #ef4444; color: white; border: 1px solid #ef4444; }
        """)

    def _build_ui(self):
        central = QWidget()
        main_layout = QGridLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 3)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_png = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_png):
            logo_label.setPixmap(QPixmap(logo_png).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            
        title = QLabel("Khan TrapMind")
        title.setObjectName("title")
        
        self.mobile_ip = QLabel("📱 Loading IP...")
        self.mobile_ip.setObjectName("mobile_ip")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.mobile_ip)
        main_layout.addLayout(header_layout, 0, 0, 1, 2)

        # --- LEFT SIDEBAR ---
        sidebar_widget = QWidget()
        sidebar_widget.setMaximumWidth(300) 
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(0, 0, 0, 0)
        
        cpu_box = QFrame()
        cpu_box.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;")
        cpu_layout = QVBoxLayout(cpu_box)
        cpu_layout.setContentsMargins(15, 15, 15, 15)
        
        cpu_title = QLabel("SYSTEM LOAD (RL ENGINE)")
        cpu_title.setObjectName("metric_title")
        self.cpu_val = QLabel("0%")
        self.cpu_val.setObjectName("metric_val")
        self.cpu_proc = QLabel("Top: None")
        self.cpu_proc.setStyleSheet("color: #64748b; font-size: 12px;")
        
        cpu_layout.addWidget(cpu_title)
        cpu_layout.addWidget(self.cpu_val)
        cpu_layout.addWidget(self.cpu_proc)
        sidebar.addWidget(cpu_box)

        self.scan_btn = QPushButton("Run Full Scan")
        self.scan_btn.clicked.connect(self._start_full_scan)
        
        self.usb_btn = QPushButton("Scan USB Drive")
        self.usb_btn.setStyleSheet("border-color: #06b6d4; color: #06b6d4;")
        self.usb_btn.clicked.connect(self._scan_usb)
        
        self.quarantine_btn = QPushButton("Open Quarantine")
        self.quarantine_btn.setObjectName("dangerBtn")
        self.quarantine_btn.clicked.connect(self._open_quarantine)
        
        # Restored Manual Button
        self.manual_btn = QPushButton("📖 User Manual")
        self.manual_btn.setObjectName("manualBtn")
        self.manual_btn.clicked.connect(self._show_user_manual)
        
        sidebar.addWidget(self.scan_btn)
        sidebar.addWidget(self.usb_btn)
        sidebar.addWidget(self.quarantine_btn)
        sidebar.addWidget(self.manual_btn)
        sidebar.addStretch()

        bottom_layout = QHBoxLayout()
        self.uninstall_btn = QPushButton("🗑️")
        self.uninstall_btn.setObjectName("uninstallBtn")
        self.uninstall_btn.setFixedSize(40, 40)
        self.uninstall_btn.clicked.connect(self._uninstall)
        
        github_label = QLabel('<a href="https://github.com/iamthearafatkhan" style="color: #64748b; text-decoration: none; font-size: 12px;">Built by Arafat Khan</a>')
        github_label.setOpenExternalLinks(True)
        
        bottom_layout.addWidget(self.uninstall_btn)
        bottom_layout.addWidget(github_label)
        bottom_layout.addStretch()
        
        sidebar.addLayout(bottom_layout)
        main_layout.addWidget(sidebar_widget, 1, 0)

        # --- RIGHT SIDE ---
        right_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.append("[✔] Khan TrapMind UI Initialized instantly.")
        self.console.append("--------------------------------------------------")
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.setStyleSheet("padding: 5px 10px; font-size: 11px; color: #64748b; border-color: #334155;")
        clear_btn.clicked.connect(self._clear_logs)

        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.console)
        right_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(right_layout, 1, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # ... [Tray, Update, and Scan logic remains the same as previous version] ...
    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(self.icon_path): self.tray_icon.setIcon(QIcon(self.icon_path))
        tray_menu = QMenu()
        show_action = QAction("Open TrapMind", self); show_action.triggered.connect(self.showNormal)
        quit_action = QAction("Exit TrapMind", self); quit_action.triggered.connect(self._actually_quit)
        tray_menu.addAction(show_action); tray_menu.addSeparator(); tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu); self.tray_icon.show()
        self.tray_icon.activated.connect(lambda r: self.showNormal() if r == QSystemTrayIcon.ActivationReason.Trigger else None)

    def closeEvent(self, event):
        event.ignore(); self.hide()
        self.tray_icon.showMessage("Khan TrapMind", "Protection running in background.", QSystemTrayIcon.MessageIcon.Information, 3000)

    def _actually_quit(self):
        if self.monitor: self.monitor.stop()
        self.ml_thread.stop(); self.proc_thread.terminate(); QApplication.quit()

    def _clear_logs(self):
        self.console.clear(); GLOBAL_LOGS.clear(); self.console.append("[✔] Logs cleared.")

    def _update_log(self, message):
        GLOBAL_LOGS.append(message); self.console.append(message)
        scrollbar = self.console.verticalScrollBar(); scrollbar.setValue(scrollbar.maximum())
        if "CRITICAL" in message or "Malware detected" in message or "Anomaly" in message or "OS ALERT" in message:
            if not self.isVisible(): self.tray_icon.showMessage("THREAT DETECTED", message, QSystemTrayIcon.MessageIcon.Critical, 5000)
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Khan TrapMind - THREAT NEUTRALIZED")
                msg_box.setText("A threat was intercepted!"); msg_box.setInformativeText(message)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setStyleSheet("QMessageBox { background-color: #0b0f19; color: white; } QPushButton { background-color: #10b981; color: black; }")
                msg_box.exec()

    def _update_web_stats(self, stats): GLOBAL_STATS.update(stats)

    def _start_full_scan(self):
        self.scan_btn.setEnabled(False); self.scan_thread = FullScanThread()
        self.scan_thread.progress_update.connect(self.progress_bar.setValue)
        self.scan_thread.log_message.connect(self._update_log)
        self.scan_thread.scan_finished.connect(lambda: self.scan_btn.setEnabled(True))
        self.scan_thread.start()

    def _open_quarantine(self):
        dialog = QuarantineWindow(self); dialog.exec()

    def _scan_usb(self):
        self.usb_btn.setEnabled(False); self.usb_btn.setText("Scanning USB...")
        self.usb_thread = USBScanThread()
        self.usb_thread.log_message.connect(self._update_log)
        self.usb_thread.scan_finished.connect(lambda: (self.usb_btn.setEnabled(True), self.usb_btn.setText("Scan USB Drive")))
        self.usb_thread.start()

    def _show_user_manual(self):
        manual_window = QDialog(self)
        manual_window.setWindowTitle("Khan TrapMind - User Manual")
        manual_window.setGeometry(200, 200, 700, 500)
        manual_window.setStyleSheet("QDialog { background-color: #0b0f19; } QTextBrowser { background-color: #1e293b; color: #e2e8f0; border: none; padding: 20px; font-size: 14px; }")
        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        manual_path = os.path.join(os.path.dirname(__file__), "..", "..", "USER_MANUAL.md")
        if os.path.exists(manual_path):
            with open(manual_path, "r", encoding="utf-8") as f: text_browser.setMarkdown(f.read())
        else: text_browser.setPlainText("User manual not found.")
        layout.addWidget(text_browser); manual_window.setLayout(layout); manual_window.exec()

    def _uninstall(self):
        reply = QMessageBox.question(self, "Confirm Uninstall", "Are you sure you want to uninstall Khan TrapMind?\n\nThis will delete your quarantine vault, AI models, and stop all protection.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._update_log("[!] Uninstalling Khan TrapMind...")
            if self.monitor: self.monitor.stop()
            self.ml_thread.stop(); self.proc_thread.terminate()
            app_data_dir = os.path.expanduser("~/.khan_trapmind")
            if os.path.exists(app_data_dir):
                try: shutil.rmtree(app_data_dir); self._update_log("[✔] Deleted all app data and quarantine vaults.")
                except Exception as e: self._update_log(f"[!] Failed to delete app data: {e}")
            token_dir = os.path.expanduser("~/Downloads/Private_Backups")
            if os.path.exists(token_dir):
                try: shutil.rmtree(token_dir); self._update_log("[✔] Removed honeytokens.")
                except Exception: pass
            QMessageBox.information(self, "Uninstalled", "Khan TrapMind has been successfully uninstalled.")
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = KhanTrapMindWindow()
    window.show()
    sys.exit(app.exec())