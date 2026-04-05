"""
Page 3: Customers — Full CRUD management
"""

import streamlit as st
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import (
    get_all_customers, get_customer_by_id,
    add_customer, update_customer, delete_customer, init_db
)
from styles import inject_custom_css, page_header

st.set_page_config(page_title="Customers", page_icon="👥", layout="wide")
init_db()
inject_custom_css()

page_header("👥", "Customer Management", "Add, edit, and manage your customer database.")

if "cust_mode" not in st.session_state:
    st.session_state.cust_mode = "list"
    st.session_state.cust_edit_id = None


def show_form(edit_data=None):
    is_edit = edit_data is not None
    st.markdown(f"#### {'✏️ Edit' if is_edit else '➕ Add'} Customer")

    with st.form("customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cust_id = st.text_input("Customer ID *", value=edit_data.get("customer_id", "") if is_edit else "")
            name = st.text_input("Name *", value=edit_data.get("name", "") if is_edit else "")
            phone = st.text_input("Phone", value=edit_data.get("phone", "") if is_edit else "")
        with col2:
            state = st.text_input("State", value=edit_data.get("state", "") if is_edit else "")
            onboarding = st.date_input(
                "Onboarding Date",
                value=date.fromisoformat(edit_data["onboarding_date"]) if is_edit and edit_data.get("onboarding_date") else date.today()
            )
        address = st.text_area("Address", value=edit_data.get("address", "") if is_edit else "", height=68)

        col_s, col_c = st.columns(2)
        save = col_s.form_submit_button("💾 Update" if is_edit else "💾 Save", use_container_width=True)
        cancel = col_c.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            st.session_state.cust_mode = "list"
            st.rerun()

        if save:
            if not cust_id.strip() or not name.strip():
                st.error("Customer ID and Name are required.")
            else:
                data = {
                    "customer_id": cust_id.strip(),
                    "name": name.strip(),
                    "address": address.strip(),
                    "phone": phone.strip(),
                    "state": state.strip(),
                    "onboarding_date": onboarding.isoformat(),
                }
                try:
                    if is_edit:
                        update_customer(st.session_state.cust_edit_id, data)
                        st.success("✅ Customer updated!")
                    else:
                        add_customer(data)
                        st.success("✅ Customer added!")
                    st.session_state.cust_mode = "list"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


# ── Main logic ──
if st.session_state.cust_mode in ("add", "edit"):
    edit_data = None
    if st.session_state.cust_mode == "edit" and st.session_state.cust_edit_id:
        edit_data = get_customer_by_id(st.session_state.cust_edit_id)
    show_form(edit_data)
else:
    top1, top2 = st.columns([5, 1])
    with top2:
        if st.button("➕ Add Customer", use_container_width=True):
            st.session_state.cust_mode = "add"
            st.rerun()

    customers = get_all_customers()
    if not customers:
        st.info("No customers yet. Click **Add Customer** to get started.")
    else:
        # Table header
        hdr = st.columns([1, 2, 3, 1.5, 1.2, 0.5, 0.5])
        hdr[0].markdown("**ID**")
        hdr[1].markdown("**Name**")
        hdr[2].markdown("**Address**")
        hdr[3].markdown("**Phone**")
        hdr[4].markdown("**State**")
        st.markdown("<hr style='margin:2px 0;border-color:#2D4A3E;'>", unsafe_allow_html=True)

        for cust in customers:
            cols = st.columns([1, 2, 3, 1.5, 1.2, 0.5, 0.5])
            cols[0].caption(cust["customer_id"])
            cols[1].write(cust["name"])
            cols[2].caption(cust.get("address", "—") or "—")
            cols[3].caption(cust.get("phone", "—") or "—")
            cols[4].caption(cust.get("state", "—") or "—")

            if cols[5].button("✏️", key=f"edit_c_{cust['id']}", help="Edit"):
                st.session_state.cust_mode = "edit"
                st.session_state.cust_edit_id = cust["id"]
                st.rerun()
            if cols[6].button("🗑️", key=f"del_c_{cust['id']}", help="Delete"):
                delete_customer(cust["id"])
                st.rerun()
