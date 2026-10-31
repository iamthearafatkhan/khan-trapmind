# khan_trapmind/scanner/yara_engine.py

import os
import yara
from .ml_scanner import TabNetScanner
from .malconv_scanner import MalConvScanner

class YaraScanner:
    def __init__(self, rules_dir=None):
        if rules_dir is None:
            rules_dir = os.path.join(os.path.dirname(__file__), "rules")
            
        self.rules = None
        self._compile_rules(rules_dir)
        
        # Initialize the AI Scanners
        self.ml_scanner = TabNetScanner()
        self.malconv_scanner = MalConvScanner()

    def _compile_rules(self, rules_dir):
        rule_files = {}
        if os.path.exists(rules_dir):
            for file in os.listdir(rules_dir):
                if file.endswith(".yar") or file.endswith(".yara"):
                    rule_files[file] = os.path.join(rules_dir, file)
        
        if rule_files:
            try:
                self.rules = yara.compile(filepaths=rule_files)
            except Exception as e:
                print(f"[!] YARA Compile Error: {e}")

    def scan_file(self, file_path):
        """Returns (is_threat, threat_name)"""
        
        lower_path = file_path.lower()

        # 1. YARA Rule Check (Fastest)
        if self.rules:
            try:
                matches = self.rules.match(file_path, timeout=10)
                if matches:
                    return True, matches[0].rule
            except Exception:
                pass 
                
        # 2. Heuristic: Flag dangerous double extensions (Fast)
        dangerous_exts = (
            '.pdf.exe', '.jpg.exe', '.png.exe', '.txt.exe', 
            '.doc.exe', '.docx.exe', '.xls.exe', '.zip.exe',
            '.txt.bat', '.jpg.bat', '.pdf.bat', '.pdf.vbs'
        )
        if lower_path.endswith(dangerous_exts):
            return True, "Heuristic.DoubleExtension"
            
        # 3. AI TabNet Check (Structural PE Analysis)
        if lower_path.endswith(('.exe', '.dll')):
            is_ml_threat, ml_reason = self.ml_scanner.scan_pe_file(file_path)
            if is_ml_threat:
                return True, ml_reason

        # 4. AI MalConv Check (Raw Byte Analysis)
        if lower_path.endswith(('.exe', '.dll', '.bin', '.dat')):
            is_malconv_threat, malconv_reason = self.malconv_scanner.scan_file(file_path)
            if is_malconv_threat:
                return True, malconv_reason

        # 5. NEW: Deep Scan for ML Model Files (.h5, .pkl, .pt, .pth)
        # Prevents malicious deserialization payloads from executing
        if lower_path.endswith(('.h5', '.pkl', '.pt', '.pth')):
            if self.rules:
                try:
                    matches = self.rules.match(file_path, timeout=10)
                    if matches:
                        return True, f"ML_Model_Exploit:{matches[0].rule}"
                except Exception:
                    pass

        return False, None