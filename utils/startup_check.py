# utils/startup_check.py

import os, shutil
from pathlib import Path

def ensure_runtime_files_exist():
    required_files = {
        "users/user_registry.yaml": "defaults/user_registry_template.yaml",
        "config/client_registry.yaml": "defaults/client_registry_template.yaml",
    }

    for target, fallback in required_files.items():
        target_path = Path(target)
        fallback_path = Path(fallback)

        if not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if fallback_path.exists():
                shutil.copy(fallback_path, target_path)
            else:
                print(f"[WARN] Missing fallback: {fallback}")
