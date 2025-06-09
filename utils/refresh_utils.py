# utils/refresh_utils.py
import time
import streamlit as st

def auto_refresh(interval_sec=10):
    if "last_refresh" not in st.session_state:
        st.session_state["last_refresh"] = time.time()
    if time.time() - st.session_state["last_refresh"] > interval_sec:
        st.session_state["last_refresh"] = time.time()
        st.rerun()
