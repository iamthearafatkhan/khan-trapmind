# main.py
import sys
from PyQt6.QtWidgets import QApplication

# Try to import the PyInstaller splash screen module
try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from khan_trapmind.ui.main_window import KhanTrapMindWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    if pyi_splash:
        pyi_splash.update_text("Loading Khan TrapMind Engines...")
    
    window = KhanTrapMindWindow()
    window.show()
    
    if pyi_splash:
        pyi_splash.close()
        
    sys.exit(app.exec())