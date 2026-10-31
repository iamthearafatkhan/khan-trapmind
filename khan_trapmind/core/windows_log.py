# khan_trapmind/core/windows_log.py

import time
import sys
from PyQt6.QtCore import QThread, pyqtSignal

# Only import win32 if we are on Windows
if sys.platform == "win32":
    import win32evtlog
else:
    win32evtlog = None

class WindowsEventMonitorThread(QThread):
    # Signal to send alerts to the UI
    security_alert = pyqtSignal(str)

    def run(self):
        if sys.platform != "win32" or win32evtlog is None:
            self.security_alert.emit("[!] Windows Event Log monitoring is only available on Windows.")
            return

        server = 'localhost'
        logtype = 'Security'
        
        # Critical Event IDs to watch
        # 4625: Failed Logon, 4720: Account Created, 4732: Added to Admin Group
        CRITICAL_EVENTS = {
            4625: "Failed Login Attempt (Potential Brute Force)",
            4720: "New User Account Created",
            4732: "User Added to Privileged Group (Admin)"
        }

        last_record_id = 0

        # Get the current latest record ID so we only look at NEW events
        try:
            hand = win32evtlog.OpenEventLog(server, logtype)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if events:
                last_record_id = events[0].RecordNumber
            win32evtlog.CloseEventLog(hand)
        except Exception as e:
            self.security_alert.emit(f"[!] Could not access Windows Event Log. Run as Administrator. ({e})")
            return

        self.security_alert.emit("[✔] Windows Security Log Monitor Active.")

        while True:
            time.sleep(3) # Check every 3 seconds
            try:
                hand = win32evtlog.OpenEventLog(server, logtype)
                flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                
                while True:
                    events = win32evtlog.ReadEventLog(hand, flags, 0)
                    if not events:
                        break
                        
                    for event in events:
                        if event.RecordNumber > last_record_id:
                            last_record_id = event.RecordNumber
                            
                            if event.EventID in CRITICAL_EVENTS:
                                # Extract the time and threat name
                                threat_name = CRITICAL_EVENTS[event.EventID]
                                time_generated = event.TimeGenerated.Format()
                                
                                # Send the alert to the UI
                                self.security_alert.emit(
                                    f"[🚨 OS ALERT] {threat_name} detected at {time_generated} (Event ID: {event.EventID})"
                                )
                                
                win32evtlog.CloseEventLog(hand)
            except Exception:
                # Silently fail if log is locked (Windows often locks it briefly)
                pass