# khan_trapmind/web/dashboard.py
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()
GLOBAL_STATS = {"cpu": 0, "ram": 0, "net": 0}
GLOBAL_LOGS = []

def get_base_path():
    """Get the correct path for assets in both source and PyInstaller EXE."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(__file__))

@app.get("/api/stats")
def get_stats():
    return {"stats": GLOBAL_STATS, "logs": GLOBAL_LOGS[-10:]}

@app.get("/logo.png")
def get_logo():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(__file__))
        
    paths = [
        os.path.join(base, "khan_trapmind", "ui", "logo.png"),
        os.path.join(base, "ui", "logo.png"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui", "logo.png"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "khan_trapmind", "ui", "logo.png")
    ]
    
    for p in paths:
        if os.path.exists(p):
            return FileResponse(p)
            
    return {"error": "Logo not found"}

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Khan TrapMind</title>
        <link rel="icon" type="image/png" href="/logo.png">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { background-color: #0b0f19; color: #10b981; font-family: 'Segoe UI', sans-serif; padding: 20px; margin: 0; display: flex; flex-direction: column; min-height: 100vh; }
            .container { flex: 1; }
            .header { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; }
            .logo { width: 50px; height: 50px; }
            .card { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #334155; }
            h1 { color: white; margin: 0; font-size: 28px; }
            .metric { font-size: 24px; font-weight: bold; color: #06b6d4; }
            .log { font-family: monospace; font-size: 12px; color: #94a3b8; border-bottom: 1px solid #334155; padding: 5px 0; }
            .footer { text-align: center; padding: 20px; font-size: 14px; color: #64748b; }
            .footer a { color: #10b981; text-decoration: none; font-weight: bold; }
            .footer a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="/logo.png" class="logo" alt="Logo">
                <h1>Khan TrapMind</h1>
            </div>
            
            <div class="card">
                <h3>System Load</h3>
                <p>CPU: <span class="metric" id="cpu">0</span>%</p>
                <p>RAM: <span class="metric" id="ram">0</span>%</p>
                <p>Network: <span class="metric" id="net">0</span> MB</p>
            </div>
            <div class="card">
                <h3>Live Threats & Logs</h3>
                <div id="logs">Waiting for data...</div>
            </div>
        </div>
        
        <div class="footer">
            Built by <a href="https://github.com/iamthearafatkhan" target="_blank">Arafat Khan</a>
        </div>

        <script>
            setInterval(async () => {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('cpu').innerText = data.stats.cpu;
                document.getElementById('ram').innerText = data.stats.ram;
                document.getElementById('net').innerText = data.stats.net.toFixed(2);
                
                let logHtml = "";
                data.logs.forEach(log => { logHtml += `<div class="log">${log}</div>`; });
                document.getElementById('logs').innerHTML = logHtml;
            }, 2000);
        </script>
    </body>
    </html>
    """

def run_server(log_callback=None):
    try:
        if log_callback:
            log_callback("[🌐] Starting Web Dashboard server...")
        
        # CRITICAL FIX: Pass log_config=None to bypass Uvicorn's broken formatter
        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="critical", 
            log_config=None  
        )
        server = uvicorn.Server(config)
        
        # Prevent signal crash in threads
        server.install_signal_handlers = lambda: None 
        server.run()
        
    except Exception as e:
        if log_callback:
            log_callback(f"[!] Web Dashboard Failed: {e}")