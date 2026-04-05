"""
Page 1: Home — Redirect to main dashboard
"""

import streamlit as st

st.switch_page("app.py")

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.markdown("### 🏠 Home")
st.info("Use the sidebar to navigate, or go to the main dashboard.")

if st.button("← Back to Dashboard"):
    st.switch_page("app.py")
