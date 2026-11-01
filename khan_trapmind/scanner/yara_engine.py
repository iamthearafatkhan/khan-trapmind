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
        self.rule_files = {}
        
        # 1. Add bundled rules
        self._add_rules_from_dir(rules_dir)
        
        # 2. Add downloaded cloud rules
        cloud_dir = os.path.expanduser("~/.khan_trapmind/cloud_rules")
        self._add_rules_from_dir(cloud_dir)
        
        self._compile_all()
        
        self.ml_scanner = TabNetScanner()
        self.malconv_scanner = MalConvScanner()

    def _add_rules_from_dir(self, directory):
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.endswith((".yar", ".yara")):
                    self.rule_files[file] = os.path.join(directory, file)

    def _compile_all(self):
        if self.rule_files:
            try:
                self.rules = yara.compile(filepaths=self.rule_files)
            except Exception as e:
                print(f"[!] YARA Compile Error: {e}")

    def scan_file(self, file_path):
        lower_path = file_path.lower()
        
        if self.rules:
            try:
                matches = self.rules.match(file_path, timeout=10)
                if matches:
                    return True, matches[0].rule
            except Exception:
                pass 
                
        dangerous_exts = (
            '.pdf.exe', '.jpg.exe', '.png.exe', '.txt.exe', 
            '.doc.exe', '.docx.exe', '.xls.exe', '.zip.exe',
            '.txt.bat', '.jpg.bat', '.pdf.bat', '.pdf.vbs'
        )
        if lower_path.endswith(dangerous_exts):
            return True, "Heuristic.DoubleExtension"
            
        if lower_path.endswith(('.exe', '.dll')):
            is_ml_threat, ml_reason = self.ml_scanner.scan_pe_file(file_path)
            if is_ml_threat:
                return True, ml_reason

        if lower_path.endswith(('.exe', '.dll', '.bin', '.dat')):
            is_malconv_threat, malconv_reason = self.malconv_scanner.scan_file(file_path)
            if is_malconv_threat:
                return True, malconv_reason

        if lower_path.endswith(('.h5', '.pkl', '.pt', '.pth')):
            if self.rules:
                try:
                    matches = self.rules.match(file_path, timeout=10)
                    if matches:
                        return True, f"ML_Model_Exploit:{matches[0].rule}"
                except Exception:
                    pass

        return False, None