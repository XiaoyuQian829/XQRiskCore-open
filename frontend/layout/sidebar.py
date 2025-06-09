# frontend/layout/sidebar.py
"""
Sidebar Layout
- Display system nav, role-based panels
- Can include system-wide metrics or logout later
"""
import os
import streamlit as st
from core.request_context import RequestContext
from utils.avatar_loader import _load_base64_image

def render_sidebar(ctx: RequestContext):
    logo_path = os.path.join("frontend", "assets", "xqrisk_logo.png")
    
    if os.path.exists(logo_path):
        logo_base64 = _load_base64_image(logo_path)
        st.sidebar.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem; margin-top: 0.75rem; margin-bottom: 0.5rem;">
            <img src="data:image/png;base64,{logo_base64}" style="width: 140px;" />
            <div style="font-size: 0.85rem; font-weight: 600; color: #ccc;">XQRiskCore v1.0 (Beta)</div>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

