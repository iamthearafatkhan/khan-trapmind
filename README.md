# 🛡️ Khan TrapMind
**Next-Gen AI-Powered Endpoint Defense & Threat Interceptor**

Khan TrapMind is a lightweight, Python-based security tool designed to defend against traditional malware and advanced LLM/AI-driven attacks. 

## 🚀 Features
- **Real-Time File Interception:** Uses `watchdog` and YARA rules to instantly detect and quarantine malware (like double-extension attacks).
- **AI Honeytokens:** Deploys deceptive traps to detect if an AI agent or hacker is snooping through your files.
- **RL CPU Monitor:** A heuristic anomaly engine that detects unauthorized CPU spikes (e.g., crypto-miners).
- **Premium UI:** A sleek, dark-themed PyQt6 dashboard.
- **System Tray Integration:** Runs silently in the background.

## 🛠️ Installation
1. Clone the repo: `git clone https://github.com/iamthearafatkhan/khan-trapmind.git`
2. Install requirements: `pip install -r requirements.txt`
3. Run the app: `python main.py`

## ⚠️ Disclaimer
Khan TrapMind is an educational and defensive tool. No software can guarantee 100% protection against an attacker with full root/administrator access. Use responsibly.