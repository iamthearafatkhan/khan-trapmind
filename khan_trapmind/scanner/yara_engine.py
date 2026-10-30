# khan_trapmind/scanner/yara_engine.py

import os
import yara

class YaraScanner:
    def __init__(self, rules_dir=None):
        if rules_dir is None:
            rules_dir = os.path.join(os.path.dirname(__file__), "rules")
            
        self.rules = None
        self._compile_rules(rules_dir)

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
        
        # 1. YARA Rule Check
        if self.rules:
            try:
                matches = self.rules.match(file_path, timeout=10)
                if matches:
                    return True, matches[0].rule
            except Exception:
                pass 
                
        # 2. Heuristic: Flag dangerous double extensions
        lower_path = file_path.lower()
        dangerous_exts = (
            '.pdf.exe', '.jpg.exe', '.png.exe', '.txt.exe', 
            '.doc.exe', '.docx.exe', '.xls.exe', '.zip.exe',
            '.txt.bat', '.jpg.bat', '.pdf.bat', '.pdf.vbs'
        )
        if lower_path.endswith(dangerous_exts):
            return True, "Heuristic.DoubleExtension"
            
        return False, None