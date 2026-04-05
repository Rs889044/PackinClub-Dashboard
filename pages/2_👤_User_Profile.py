"""
Page 2: User Profile — Company branding & details
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_user_profile, save_user_profile, UPLOAD_DIR, init_db
from styles import inject_custom_css, page_header

st.set_page_config(page_title="User Profile", page_icon="👤", layout="wide")
init_db()
inject_custom_css()

page_header("👤", "Company Profile", "This information appears on all your invoices and quotations.")

profile = get_user_profile() or {}

with st.form("profile_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input("Company Name *", value=profile.get("company_name", ""))
        phone = st.text_input("Phone Number", value=profile.get("phone", ""))
        email = st.text_input("Email Address", value=profile.get("email", ""))

    with col2:
        website = st.text_input("Website", value=profile.get("website", ""))
        gst_number = st.text_input("GST Number", value=profile.get("gst_number", ""))

    address = st.text_area("Company Address", value=profile.get("address", ""), height=68)

    st.markdown("**Company Logo**")
    logo_file = st.file_uploader(
        "Upload logo (PNG, JPG)", type=["png", "jpg", "jpeg"], key="logo_upload"
    )

    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if submitted:
        if not company_name.strip():
            st.error("Company Name is required.")
        else:
            logo_path = profile.get("logo_path", "")
            if logo_file is not None:
                # Delete old logo if it exists
                if logo_path and os.path.isfile(logo_path):
                    os.remove(logo_path)
                logo_path = os.path.join(UPLOAD_DIR, f"logo_{logo_file.name}")
                with open(logo_path, "wb") as f:
                    f.write(logo_file.getbuffer())

            save_user_profile({
                "company_name": company_name.strip(),
                "address": address.strip(),
                "phone": phone.strip(),
                "website": website.strip(),
                "email": email.strip(),
                "gst_number": gst_number.strip(),
                "logo_path": logo_path,
            })
            st.success("✅ Profile saved successfully!")
            st.rerun()

if profile.get("logo_path") and os.path.isfile(profile["logo_path"]):
    st.markdown("**Current Logo:**")
    st.image(profile["logo_path"], width=140)
