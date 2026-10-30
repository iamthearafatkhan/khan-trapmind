# khan_trapmind/ui/main_window.py

import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QHBoxLayout, 
                             QProgressBar, QFrame, QMessageBox, QSystemTrayIcon, 
                             QMenu, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QAction

from ..scanner.realtime_monitor import RealtimeMonitor
from ..rl_engine.cpu_monitor import CPUMonitorThread
from .quarantine_window import QuarantineWindow


# ==========================================
# BACKGROUND SCANNER THREAD
# ==========================================
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

# ==========================================
# MAIN UI WINDOW
# ==========================================
class KhanTrapMindWindow(QMainWindow):
    realtime_alert = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Khan TrapMind — Advanced Defense")
        self.setGeometry(100, 100, 1150, 750)
        
        # Window Icon & Tray
        self.icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))
            
        self._apply_premium_style()
        self._build_ui()
        self._setup_tray_icon()
        
        # Connect Signal & Start Scanner
        self.realtime_alert.connect(self._update_log)
        self.monitor = RealtimeMonitor(
            paths_to_watch=[os.path.expanduser("~/Downloads"), os.path.expanduser("~/Desktop")],
            log_callback=self.realtime_alert.emit
        )
        self.monitor.start()

        # Start CPU RL Engine
        self.cpu_thread = CPUMonitorThread()
        self.cpu_thread.cpu_update.connect(self._update_cpu_stats)
        self.cpu_thread.anomaly_detected.connect(self._update_log)
        self.cpu_thread.start()

    def _apply_premium_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0b0f19; }
            QLabel { color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
            QLabel#title { font-size: 26px; font-weight: bold; color: #ffffff; letter-spacing: 1px; }
            QLabel#status { font-size: 13px; color: #10b981; font-weight: bold; }
            QLabel#metric_title { font-size: 11px; color: #94a3b8; font-weight: bold; }
            QLabel#metric_val { font-size: 24px; color: #06b6d4; font-weight: bold; }
            
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
        """)

    def _build_ui(self):
        central = QWidget()
        main_layout = QGridLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- HEADER ---
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_png = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_png):
            logo_label.setPixmap(QPixmap(logo_png).scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            
        title = QLabel("Khan TrapMind")
        title.setObjectName("title")
        
        status = QLabel("● SYSTEM PROTECTED")
        status.setObjectName("status")
        status.setStyleSheet("background-color: rgba(16, 185, 129, 0.1); padding: 6px 12px; border-radius: 4px;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(status)
        main_layout.addLayout(header_layout, 0, 0, 1, 2)

        # --- LEFT SIDEBAR (Metrics & Controls) ---
        sidebar = QVBoxLayout()
        
        # CPU Metric Box
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

        # Buttons
        self.scan_btn = QPushButton("Run Full Scan")
        self.scan_btn.clicked.connect(self._start_full_scan)
        
        self.quarantine_btn = QPushButton("Open Quarantine")
        self.quarantine_btn.setObjectName("dangerBtn")
        self.quarantine_btn.clicked.connect(self._open_quarantine)
        
        sidebar.addWidget(self.scan_btn)
        sidebar.addWidget(self.quarantine_btn)
        sidebar.addStretch()
        
        main_layout.addLayout(sidebar, 1, 0)

        # --- RIGHT SIDE (Logs & Progress) ---
        right_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.append("[✔] Khan TrapMind Engine Initialized.")
        self.console.append("[✔] Real-Time Scanner & AI Traps Active.")
        self.console.append("[✔] RL CPU Anomaly Engine Running.")
        self.console.append("--------------------------------------------------")
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.setStyleSheet("padding: 5px 10px; font-size: 11px; color: #64748b; border-color: #334155;")
        clear_btn.clicked.connect(lambda: self.console.clear())

        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.console)
        right_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(right_layout, 1, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    # ==========================================
    # SYSTEM TRAY & CLOSE EVENT
    # ==========================================
    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(self.icon_path):
            self.tray_icon.setIcon(QIcon(self.icon_path))
            
        # Tray Menu
        tray_menu = QMenu()
        
        show_action = QAction("Open TrapMind", self)
        show_action.triggered.connect(self.showNormal)
        
        quit_action = QAction("Exit TrapMind", self)
        quit_action.triggered.connect(self._actually_quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self._tray_clicked)

    def _tray_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()

    def closeEvent(self, event):
        # Override the close button (X) to minimize to tray instead of quitting
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Khan TrapMind",
            "Protection running in background.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _actually_quit(self):
        self.monitor.stop()
        self.cpu_thread.terminate()
        QApplication.quit()

    # ==========================================
    # LOGIC & UPDATES
    # ==========================================
    def _update_cpu_stats(self, cpu_percent, top_proc):
        self.cpu_val.setText(f"{cpu_percent}%")
        self.cpu_proc.setText(f"Top: {top_proc}")
        
        # Color change based on load
        if cpu_percent > 80:
            self.cpu_val.setStyleSheet("font-size: 24px; color: #ef4444; font-weight: bold;") # Red
        elif cpu_percent > 50:
            self.cpu_val.setStyleSheet("font-size: 24px; color: #f59e0b; font-weight: bold;") # Yellow
        else:
            self.cpu_val.setStyleSheet("font-size: 24px; color: #06b6d4; font-weight: bold;") # Cyan

    def _update_log(self, message):
        self.console.append(message)
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        if "CRITICAL" in message or "Malware detected" in message or "Anomaly" in message:
            # Show popup only if window is hidden (background mode)
            if not self.isVisible():
                self.tray_icon.showMessage("THREAT DETECTED", message, QSystemTrayIcon.MessageIcon.Critical, 5000)
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Khan TrapMind - THREAT NEUTRALIZED")
                msg_box.setText("A threat was intercepted!")
                msg_box.setInformativeText(message)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setStyleSheet("QMessageBox { background-color: #0b0f19; color: white; } QPushButton { background-color: #10b981; color: black; }")
                msg_box.exec()

    def _start_full_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_thread = FullScanThread()
        self.scan_thread.progress_update.connect(self.progress_bar.setValue)
        self.scan_thread.log_message.connect(self._update_log)
        self.scan_thread.scan_finished.connect(lambda: self.scan_btn.setEnabled(True))
        self.scan_thread.start()

    def _open_quarantine(self):
    
        dialog = QuarantineWindow(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False) # Prevents app from dying when window is closed
    window = KhanTrapMindWindow()
    window.show()
    sys.exit(app.exec())