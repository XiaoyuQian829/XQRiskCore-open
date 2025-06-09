# admin/user_registry.py

import yaml
import os
from datetime import datetime

USER_FILE = "users/user_registry.yaml"

def _load_users():
    try:
        with open(USER_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def _save_users(users):
    with open(USER_FILE, "w") as f:
        yaml.safe_dump(users, f, sort_keys=False)

def list_users():
    return _load_users()

def add_user(username, password, role="trader", email="", phone="", client_id="__ALL__", preferred_language="en", timezone="UTC"):
    users = _load_users()
    if username in users:
        return False

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users[username] = {
        "password": password,
        "role": role,
        "email": email,
        "phone": phone,
        "client_id": client_id,
        "created_at": now_str,
        "last_login": "",
        "active": True,
        "preferred_language": preferred_language,
        "timezone": timezone,
        "access_scope": [],
        "notes": "",
        "2fa_enabled": False
    }
    _save_users(users)
    return True

def delete_user(username):
    users = _load_users()
    if username not in users:
        return False
    del users[username]
    _save_users(users)
    return True

def get_user_role(username):
    users = _load_users()
    return users.get(username, {}).get("role")

def get_user_scope(username):
    users = _load_users()
    return users.get(username, {}).get("access_scope", [])

def has_access(username, scope_name):
    scopes = get_user_scope(username)
    return scope_name in scopes or "__ALL__" in scopes

def authenticate(username, password):
    users = _load_users()
    user = users.get(username, {})
    if not user or not user.get("active", True):
        return False
    return user.get("password") == password