/*
    Khan TrapMind - Base YARA Rules
*/

rule EICAR_Test_String {
    meta:
        description = "Standard industry antivirus test file"
        author = "Khan TrapMind"
    strings:
        $eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $eicar
}

rule Malicious_Model_Payload {
    meta:
        description = "Detects suspicious execution payloads inside ML model files (H5, PKL, PT)"
        author = "Khan TrapMind"
    strings:
        // HDF5 magic bytes (\x89HDF\r\n\x1a\n) or Python Pickle magic bytes
        $h5_magic  = { 89 48 44 46 0D 0A 1A 0A }
        $pkl_magic = { 80 04 } 
        
        // Suspicious execution strings commonly used in malicious pickles
        $s1 = "os.system"
        $s2 = "subprocess.Popen"
        $s3 = "eval("
        $s4 = "exec("
        $s5 = "base64.b64decode"
        $s6 = "__reduce__"
    condition:
        ($h5_magic at 0 or $pkl_magic at 0) and any of ($s*)
}

rule Suspicious_Shell_Script {
    meta:
        description = "Flags basic PowerShell or Command Prompt download strings"
    strings:
        $ps1 = "Invoke-WebRequest"
        $ps2 = "DownloadString"
        $ps3 = "IEX("
        $cmd1 = "certutil -urlcache"
        $cmd2 = "bitsadmin /transfer"
    condition:
        any of them
}