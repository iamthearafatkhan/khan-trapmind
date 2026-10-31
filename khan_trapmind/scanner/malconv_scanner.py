# khan_trapmind/scanner/malconv_scanner.py

import os
import numpy as np

from huggingface_hub import hf_hub_download

class MalConvScanner:
    def __init__(self):
        self.model = None
        self.max_len = 1024 * 1024
        self._load_model()

    def _load_model(self):
        # IMPORT IT HERE (Lazy Loading)
        import tensorflow as tf

        try:
            print("[ML Engine] Downloading/Loading MalConv model...")
            model_path = hf_hub_download(
                repo_id="cycloevan/malconv",
                filename="models/malconv_model.h5"
            )
            self.model = tf.keras.models.load_model(model_path)
            print("[ML Engine] MalConv model loaded successfully.")
        except Exception as e:
            print(f"[!] Failed to load MalConv model: {e}")

    def _read_raw_bytes(self, file_path):
        """Reads the raw bytes of a file, up to max_len."""
        with open(file_path, "rb") as f:
            byte_data = f.read(self.max_len)
        
        # Convert bytes to integers (0-255) for the model
        byte_array = np.frombuffer(byte_data, dtype=np.uint8).astype(np.int32)
        return byte_array

    def scan_file(self, file_path):
        """Returns (is_threat, threat_name) using raw byte analysis."""
        if not self.model:
            return False, "Model_Not_Loaded"

        try:
            # 1. Read raw bytes
            byte_array = self._read_raw_bytes(file_path)
            
            # 2. Pad or truncate to the expected input size (max_len)
            if len(byte_array) < self.max_len:
                padded = np.zeros(self.max_len, dtype=np.int32)
                padded[:len(byte_array)] = byte_array
                byte_array = padded
            else:
                byte_array = byte_array[:self.max_len]
            
            # 3. Add batch dimension
            input_data = np.expand_dims(byte_array, axis=0)
            
            # 4. Predict (returns a single probability score)
            prediction = self.model.predict(input_data, verbose=0)
            score = prediction[0][0]  # Probability of being malicious
            
            # 5. Classify (threshold at 0.5)
            if score > 0.5:
                return True, f"MalConv_Malware (Confidence: {score:.2f})"
            else:
                return False, f"MalConv_Clean (Confidence: {score:.2f})"

        except Exception as e:
            # If the file is empty or unreadable, let YARA handle it
            return False, f"Error: {e}"