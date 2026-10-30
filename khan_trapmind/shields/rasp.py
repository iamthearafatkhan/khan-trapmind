# shields/rasp.py
from cynapse import Monitor, TamperResponse, ProtectionLevel

class RASPShield:
    def __init__(self, config):
        self.monitor = (
            Monitor.builder()
            .interval(config.RASP_INTERVAL)
            .protection_level(ProtectionLevel.HIGH)
            .enable_bytecode_verification(True)
            .enable_module_tracking(True)
            .enable_import_hooks(True)
            .enable_auto_healing(True)
            .on_tamper(self._on_tamper)
            .build()
        )

    def _on_tamper(self, event):
        # Log, alert, and optionally terminate
        print(f"[RASP] Tampering detected: {event.type}")
        if event.can_restore:
            return TamperResponse.RESTORE
        return TamperResponse.TERMINATE

    def start(self):
        self.monitor.start()

    def stop(self):
        self.monitor.stop()