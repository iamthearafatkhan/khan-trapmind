<div align="center">
  <img src="https://raw.githubusercontent.com/iamthearafatkhan/khan-trapmind/main/khan_trapmind/ui/logo.png" alt="Khan TrapMind Logo" width="150" height="150">
  
  # 🛡️ Khan TrapMind
  **Next-Gen AI-Powered Endpoint Defense & Threat Interceptor**

  [![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](https://github.com/iamthearafatkhan/khan-trapmind/releases)
  [![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
  
  <br>
  
  [![Download Khan TrapMind](https://img.shields.io/badge/⬇_Download_v1.0.0_Executable-10b981?style=for-the-badge&logo=windows)](https://github.com/iamthearafatkhan/khan-trapmind/releases/latest)
</div>

---

## 📖 Introduction

**Khan TrapMind** is a free, lightweight, and powerful Endpoint Detection and Response (EDR) tool designed for modern threats. Unlike traditional antivirus software that relies solely on old signatures, TrapMind uses a multi-layered approach combining **Machine Learning (AI), Behavioral Analysis, and Deception Technology (Honeytokens)** to protect your Windows PC.

Built with Python and PyQt6, it provides a premium, dark-themed dashboard that rivals paid enterprise security solutions—completely free of charge.

## ✨ Key Features

*   🧠 **Dual AI Malware Detection:** Uses **TabNet** (PE structural analysis) and **MalConv** (raw byte analysis) to catch zero-day malware before it runs.
*   ⚡ **Real-Time Protection:** Monitors your entire user profile instantly. Suspicious files are instantly quarantined.
*   🍯 **AI Honeytokens (Deception Tech):** Drops fake, highly attractive files (like `admin_passwords.txt`) in your system. If malware or an AI Agent tries to read them, TrapMind catches them in the act.
*   🕵️ **Behavioral Process Monitor:** Instantly kills malicious scripts (like drive-by downloads spawning a hidden PowerShell) and blocks cookie theft attempts.
*   🔒 **Windows Event Log Monitor:** Detects brute-force login attempts and unauthorized admin account creation in real-time.
*   📱 **Mobile Web Dashboard:** Monitor your PC's security status and live threats from your phone via `http://YOUR_IP:8000`.
*   🔄 **Cloud Threat Intelligence:** Automatically fetches the latest YARA rules from the cloud to stay updated against new threats.

---

## 🚨 IMPORTANT: Before You Run (First Time Users)

1.  **Administrator Privileges:** When you double-click the `.exe`, Windows will show a UAC prompt. You **MUST** click **"Yes"**. This is required so TrapMind can read the Windows Security Event Logs (to catch brute-force attacks).
2.  **Windows SmartScreen:** Because this is a free, open-source tool without a $300/year digital signature, Windows Defender might show a blue popup saying *"Windows protected your PC"*. Click **"More info"** and then **"Run anyway"**.
3.  **First Run Takes Time:** The first time you open TrapMind, it will take a few seconds to load the AI models. The logo splash screen will appear. Please wait a moment. (You need an internet connection on the first run to download the 15MB AI models from Hugging Face).
4.  **Antivirus False Positives:** Because TrapMind monitors system processes and is built with Python (PyInstaller), some antivirus software might falsely flag it. This is a known industry issue. You may need to add an exclusion in Windows Defender.

---

## 🚀 Installation & Usage

### Option 1: Standalone Executable (Recommended for Users)
1. Go to the [**Releases Page**](https://github.com/iamthearafatkhan/khan-trapmind/releases).
2. Download the latest `Khan_TrapMind.exe`.
3. Double-click to run. (See the warnings above).

### Option 2: Run from Source (For Developers)
```bash
# 1. Clone the repository
git clone https://github.com/iamthearafatkhan/khan-trapmind.git
cd khan-trapmind

# 2. Create a virtual environment
python -m venv trap_venv
source trap_venv/Scripts/activate  # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application (as Administrator)
python main.py
```


## 🛡️ How to Use Khan TrapMind
*   **System Tray:** Closing the window (X) hides the app in your system tray (bottom right). Right-click the tray icon to exit.

*   **Mobile Dashboard:** Ensure your phone is on the same Wi-Fi. Open the URL shown in the top-right corner of the app (e.g., http://192.168.1.5:8000) to monitor your PC remotely.

*   **Honeytokens:** TrapMind automatically creates a folder at Downloads\Private_Backups. If you ever see malware touching this folder, the UI will scream at you!

*   **Quarantine:** If a threat is found, it is moved to a secure vault. You can view and permanently delete it via the "Open Quarantine" button.

*   **Scanning:** Use "Run Full Scan" or "Scan USB Drive" to proactively check your files.


## 🗑️ How to Uninstall

1. Open Khan TrapMind.

2. Click the 🗑️ (Trash Can) icon at the bottom left of the sidebar.

3. Confirm the uninstall. The app will clean up its hidden folders, delete the fake honeytokens, and close itself.

4. You can now safely delete the Khan_TrapMind.exe file.


## 🚫 Limitations (The Honest Truth)
No software is 100% invincible. TrapMind is highly effective, but you should know its limits:

1. **Kernel-Level Attacks:** TrapMind runs in User-Mode (Ring 3). It cannot stop an attacker who already has full Administrator/Kernel access (Ring 0).

2. **Memory-Only Threats:** Advanced fileless malware that runs purely in RAM without touching the disk (though TrapMind will kill the spawned processes and flag CPU anomalies).

3. **Phishing:** TrapMind does not scan your emails or browser text; it protects the endpoint (the device).

## 📊 Outcome
With Khan TrapMind running, you have an enterprise-grade, multi-layered shield that actively detects, quarantines, and analyzes threats. It turns any standard Windows PC into a proactive security environment.

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Credits
---
<div align="center"> <i>Built with ❤️ by <a href="https://github.com/iamthearafatkhan">Arafat Khan</a></i> </div>

---
<div align="center">
**If you find this project helpful, please consider giving it a ⭐ on GitHub!** 

</div>