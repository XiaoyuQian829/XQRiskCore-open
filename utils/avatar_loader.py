# utils/avatar_loader.py

import os
import base64
import streamlit as st

def get_user_avatar_base64(username: str, avatar_dir: str = "frontend/assets/avatars", fallback: str = "default.png") -> str:
    avatar_path = os.path.join(avatar_dir, f"{username}.png")
    default_path = os.path.join(avatar_dir, fallback)

    if os.path.exists(avatar_path):
        return _load_base64_image(avatar_path)
    elif os.path.exists(default_path):
        return _load_base64_image(default_path)
    else:
        raise FileNotFoundError("No avatar or fallback image found.")

@st.cache_data(show_spinner=False)
def _load_base64_image(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()
