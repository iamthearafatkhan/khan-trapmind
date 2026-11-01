# main.py
import sys
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# --- WINDOWS TASKBAR ICON FIX ---
try:
    myappid = 'ArafatKhan.KhanTrapMind.App.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from khan_trapmind.ui.main_window import KhanTrapMindWindow

SERVER_NAME = "KhanTrapMind_Local_Instance"

def is_already_running():
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(500):
        socket.write(b"SHOW")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        return True
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    if is_already_running():
        sys.exit(0)

    server = QLocalServer()
    server.listen(SERVER_NAME)
    
    if pyi_splash:
        pyi_splash.update_text("Loading Khan TrapMind Engines...")
    
    window = KhanTrapMindWindow()
    
    if os.path.exists(window.icon_path):
        app.setWindowIcon(QIcon(window.icon_path))
        
    window.show()
    
    if pyi_splash:
        pyi_splash.close()
        
    def handle_connection():
        client = server.nextPendingConnection()
        if client:
            client.readyRead.connect(lambda: (
                client.readAll(),
                window.showNormal(),
                window.activateWindow(),
                client.disconnectFromServer()
            ))

    server.newConnection.connect(handle_connection)
    sys.exit(app.exec())