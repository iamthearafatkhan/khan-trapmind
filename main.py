# main.py
import sys
from PyQt6.QtWidgets import QApplication
from khan_trapmind.ui.main_window import KhanTrapMindWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = KhanTrapMindWindow()
    window.show()
    sys.exit(app.exec())