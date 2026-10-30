# khan_trapmind/ui/quarantine_window.py
import os
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt

class QuarantineWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Khan TrapMind — Quarantine Vault")
        self.setGeometry(200, 200, 800, 500)
        self.quarantine_dir = os.path.expanduser("~/.khan_trapmind/quarantine")
        self.setStyleSheet("""
            QDialog { background-color: #0b0f19; }
            QTableWidget { background-color: #1e293b; color: white; border: none; gridline-color: #334155; }
            QHeaderView::section { background-color: #0f172a; color: #10b981; padding: 5px; border: 1px solid #1e293b; font-weight: bold; }
            QPushButton { background-color: #1e293b; color: #10b981; border: 1px solid #10b981; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton:hover { background-color: #10b981; color: #0b0f19; }
            QPushButton#deleteBtn { border-color: #ef4444; color: #ef4444; }
            QPushButton#deleteBtn:hover { background-color: #ef4444; color: white; }
        """)
        self._build_ui()
        self._load_files()

    def _build_ui(self):
        layout = QVBoxLayout()
        
        # Table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Quarantined File", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Permanently Delete")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self._delete_selected)
        
        close_btn = QPushButton("Close Vault")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_files(self):
        self.table.setRowCount(0)
        if not os.path.exists(self.quarantine_dir):
            return
            
        files = os.listdir(self.quarantine_dir)
        for row, file in enumerate(files):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(file))
            self.table.setItem(row, 1, QTableWidgetItem("🔒 Locked"))

    def _delete_selected(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a file to delete.")
            return

        file_name = self.table.item(selected_row, 0).text()
        file_path = os.path.join(self.quarantine_dir, file_name)

        try:
            os.remove(file_path) # Delete the file
            self.table.removeRow(selected_row)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete file: {e}")