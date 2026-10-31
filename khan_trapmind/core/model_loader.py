import os
from huggingface_hub import hf_hub_download

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def download_models(log_callback=print):
    """Downloads all required AI models if they don't already exist."""
    
    # 1. TabNet Model (PE File Analysis)
    tabnet_path = os.path.join(MODELS_DIR, "tabnet_PE.zip")
    if not os.path.exists(tabnet_path):
        log_callback("[☁️ Cloud] Downloading TabNet AI Model (7.4 MB)...")
        try:
            hf_hub_download(
                repo_id="cycloevan/ember-model",
                filename="tabnet/tabnet_PE.zip",
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False
            )
            # Move it to the correct directory for our scanner
            downloaded_path = os.path.join(MODELS_DIR, "tabnet", "tabnet_PE.zip")
            if os.path.exists(downloaded_path):
                os.rename(downloaded_path, tabnet_path)
            log_callback("[✔] TabNet Model downloaded.")
        except Exception as e:
            log_callback(f"[!] Failed to download TabNet: {e}")

    # 2. MalConv Model (Raw Byte Analysis)
    malconv_path = os.path.join(MODELS_DIR, "malconv_model.h5")
    if not os.path.exists(malconv_path):
        log_callback("[☁️ Cloud] Downloading MalConv AI Model (8.3 MB)...")
        try:
            hf_hub_download(
                repo_id="cycloevan/malconv",
                filename="models/malconv_model.h5",
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False
            )
            downloaded_path = os.path.join(MODELS_DIR, "models", "malconv_model.h5")
            if os.path.exists(downloaded_path):
                os.rename(downloaded_path, malconv_path)
            log_callback("[✔] MalConv Model downloaded.")
        except Exception as e:
            log_callback(f"[!] Failed to download MalConv: {e}")

    log_callback("[✔] All AI Models are ready.")