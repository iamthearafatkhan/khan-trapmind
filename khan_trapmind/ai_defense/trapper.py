# ai_defense/trapper.py
import json
import uuid

class LLMTrapper:
    """Plant CHeaT-style defenses into text assets."""

    TECHNIQUES = {
        "cloak": "S1",   # Obfuscate sensitive data
        "honey": "S2",   # Embed detectable tokens
        "trap": "S3",    # Loop/crash payload
    }

    def __init__(self, db_path="aegis_cheat_db.json"):
        self.db_path = db_path
        self._load_db()

    def _load_db(self):
        try:
            with open(self.db_path) as f:
                self.db = json.load(f)
        except FileNotFoundError:
            self.db = {"installed": []}

    def plant(self, file_path: str, technique: str = "random"):
        """Insert a defense payload into a text file."""
        with open(file_path, "r+") as f:
            content = f.read()
            payload = self._generate_payload(technique)
            f.seek(0)
            f.write(content + "\n" + payload)

        record = {
            "id": str(uuid.uuid4()),
            "file": file_path,
            "technique": technique,
        }
        self.db["installed"].append(record)
        self._save_db()
        return record

    def _generate_payload(self, technique):
        if technique == "honey":
            return "<!-- HONEY: " + str(uuid.uuid4()) + " -->"
        if technique == "trap":
            # A benign infinite loop for naive scrapers
            return "// TRAP: while(true){/*...*/}"
        # Cloak: misdirect with fake credentials
        return "/* CLOAK: admin_password=FAKE_REDACTED */"

    def _save_db(self):
        with open(self.db_path, "w") as f:
            json.dump(self.db, f)