# khan_trapmind/ai_defense/honeytokens.py
import os
import json

class HoneytokenDeployer:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.token_names = [
            "admin_passwords.txt",
            "aws_secret_keys.json",
            "database_backup.env"
        ]

    def deploy_traps(self):
        """Creates fake, highly attractive files for hackers/AI to steal."""
        deployed = []
        os.makedirs(self.target_dir, exist_ok=True)
        
        # 1. Fake Password File
        pass_path = os.path.join(self.target_dir, self.token_names[0])
        with open(pass_path, "w") as f:
            f.write("SYSTEM_ADMIN_USER=admin\nSYSTEM_ADMIN_PASS=SuperSecretPassword123!\n# TRAPMIND HONEYTOKEN - DO NOT TOUCH")
        deployed.append(self.token_names[0])

        # 2. Fake AWS Keys File
        aws_path = os.path.join(self.target_dir, self.token_names[1])
        with open(aws_path, "w") as f:
            json.dump({"aws_access_key_id": "AKIA_FAKE_KEY_TRAPMIND", "aws_secret_access_key": "FAKE_SECRET_TRAPMIND"}, f, indent=4)
        deployed.append(self.token_names[1])

        return deployed