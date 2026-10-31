# 🛡️ Khan TrapMind - User Manual

Welcome to Khan TrapMind, an AI-Powered Next-Gen Endpoint Defense.

## 🌟 What TrapMind Does
1. **Real-Time Protection:** Watches your entire User profile (Documents, Downloads, Desktop) for malicious files.
2. **AI Malware Detection:** Uses TabNet (structure analysis) and MalConv (raw byte analysis) to catch zero-day malware.
3. **Quarantine:** Instantly locks suspicious files in a secure vault.
4. **AI Honeytokens:** Drops fake passwords in your `Downloads\Private_Backups` folder. If malware or an AI agent touches them, we alert you immediately.
5. **OS Security Monitor:** Detects Windows brute-force logins (Event ID 4625).
6. **Web Dashboard:** Open `http://localhost:8000` on your phone to monitor your PC in real-time.

## 🚫 What TrapMind Cannot Do
- It cannot prevent 100% of attacks if an attacker has full Administrator/Kernel access to your PC.
- It cannot block memory-only drive-by downloads (though it will kill the spawned process).
- It is not a VPN or a firewall.

## 🛠️ How to Use
- The app runs in your system tray (bottom right corner).
- Click "Run Full Scan" to scan your system.
- Click "Scan USB Drive" to scan removable media.
- Click "Open Quarantine" to see blocked threats. You can permanently delete them here.

## 🗑️ How to Uninstall
Use the "Uninstall" button in the app, or manually delete the `C:\Users\YourName\.khan_trapmind` folder and the TrapMind `.exe`.