# === users/user_registry.py ===
import yaml
import os

USER_REGISTRY_FILE = "users/user_registry.yaml"

def load_user_registry():
    if not os.path.exists(USER_REGISTRY_FILE):
        return {}
    with open(USER_REGISTRY_FILE, "r") as f:
        return yaml.safe_load(f) or {}

def get_user(username: str):
    registry = load_user_registry()
    return registry.get(username, None)

def save_user_registry(registry: dict):
    with open(USER_REGISTRY_FILE, "w") as f:
        yaml.dump(registry, f)

def add_user(username: str, role: str, client_id: str = None):
    registry = load_user_registry()
    registry[username] = {"role": role, "client_id": client_id}
    save_user_registry(registry)
    return True