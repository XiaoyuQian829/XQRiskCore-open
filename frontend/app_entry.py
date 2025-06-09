# frontend/app_entry.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from frontend.login import login_page
from frontend.app import main_dashboard

st.set_page_config(page_title="XQRiskCore Console", layout="wide")

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_page()
else:
    ctx = st.session_state.get("request_ctx")
    if ctx:
        main_dashboard(ctx)
    else:
        st.session_state.clear()
        st.rerun()
