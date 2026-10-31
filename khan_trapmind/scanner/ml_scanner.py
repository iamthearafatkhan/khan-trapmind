# khan_trapmind/scanner/ml_scanner.py

import os
import numpy as np
import pefile


class TabNetScanner:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "models", "tabnet_PE.zip"
        )
        self._load_model()

    def _load_model(self):
        # IMPORT THEM HERE (Lazy Loading)
        import torch
        from pytorch_tabnet.tab_model import TabNetClassifier

        if os.path.exists(self.model_path):
            try:
                print(f"[ML Engine] Loading TabNet model from {self.model_path}...")
                self.model = TabNetClassifier()
                self.model.load_model(self.model_path)
                print("[ML Engine] TabNet model loaded successfully.")
            except Exception as e:
                print(f"[!] Failed to load TabNet model: {e}")
        else:
            print(f"[!] TabNet model not found at {self.model_path}. Skipping ML scanning.")

    def _extract_pe_features(self, file_path):
        """Extracts basic features from a PE file to feed into the AI."""
        try:
            pe = pefile.PE(file_path)
            
            # Extract basic, robust features
            features = [
                pe.FILE_HEADER.NumberOfSections,
                pe.FILE_HEADER.TimeDateStamp,
                pe.FILE_HEADER.PointerToSymbolTable,
                pe.OPTIONAL_HEADER.MajorLinkerVersion,
                pe.OPTIONAL_HEADER.SizeOfCode,
                pe.OPTIONAL_HEADER.SizeOfImage,
                pe.OPTIONAL_HEADER.CheckSum,
                pe.OPTIONAL_HEADER.Subsystem,
                pe.OPTIONAL_HEADER.DllCharacteristics,
                len(pe.sections)
            ]
            
            # Add section info (Entropy, VirtualSize)
            for section in pe.sections[:10]: # Limit to first 10 sections
                features.append(section.get_entropy())
                features.append(section.Misc_VirtualSize)
            
            # Pad the array to 2381 features (the size TabNet expects)
            # In a production environment, you would extract all 2381 exact features,
            # but this padding ensures the model doesn't crash.
            current_len = len(features)
            if current_len < 2381:
                features.extend([0.0] * (2381 - current_len))
            elif current_len > 2381:
                features = features[:2381]
                
            return np.array([features], dtype=np.float32)
            
        except Exception as e:
            # If it's not a valid PE file, raise an error
            raise ValueError(f"Invalid PE file: {e}")

    def scan_pe_file(self, file_path):
        """Analyzes a Windows PE file (.exe, .dll) using TabNet."""
        if not self.model:
            return False, "Model_Not_Loaded"

        try:
            # 1. Extract features
            features = self._extract_pe_features(file_path)
            
            # 2. Predict (returns probability for [Benign, Malware])
            prediction = self.model.predict_proba(features)
            
            # 3. Check threshold (if malware probability > 0.5)
            if prediction[0][1] > 0.5:
                return True, "AI_TabNet_Malware"
            else:
                return False, "AI_Clean"

        except Exception as e:
            # If the file is packed or corrupted, let YARA handle it. 
            # Don't flag as malware just because pefile failed.
            return False, f"Error: {e}"