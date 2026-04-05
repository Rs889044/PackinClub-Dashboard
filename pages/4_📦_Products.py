"""
Page 4: Products — Catalogue management
"""

import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import (
    get_all_products, get_product_by_id,
    add_product, update_product, delete_product, init_db
)
from styles import inject_custom_css, page_header

st.set_page_config(page_title="Products", page_icon="📦", layout="wide")
init_db()
inject_custom_css()

page_header("📦", "Product Catalogue", "Manage your product inventory and pricing.")

if "prod_mode" not in st.session_state:
    st.session_state.prod_mode = "list"
    st.session_state.prod_edit_id = None


def show_product_form(edit_data=None):
    is_edit = edit_data is not None
    st.markdown(f"#### {'✏️ Edit' if is_edit else '➕ Add'} Product")

    with st.form("product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            prod_id = st.text_input("Product ID *", value=edit_data.get("product_id", "") if is_edit else "")
            name = st.text_input("Product Name *", value=edit_data.get("name", "") if is_edit else "")
        with col2:
            price = st.number_input(
                "Price (₹) *", min_value=0.0, step=0.01, format="%.2f",
                value=float(edit_data.get("price", 0)) if is_edit else 0.0
            )

        col_s, col_c = st.columns(2)
        save = col_s.form_submit_button("💾 Update" if is_edit else "💾 Save", use_container_width=True)
        cancel = col_c.form_submit_button("Cancel", use_container_width=True)

        if cancel:
            st.session_state.prod_mode = "list"
            st.rerun()

        if save:
            if not prod_id.strip() or not name.strip():
                st.error("Product ID and Name are required.")
            elif price <= 0:
                st.error("Price must be greater than zero.")
            else:
                data = {"product_id": prod_id.strip(), "name": name.strip(), "price": price}
                try:
                    if is_edit:
                        update_product(st.session_state.prod_edit_id, data)
                        st.success("✅ Product updated!")
                    else:
                        add_product(data)
                        st.success("✅ Product added!")
                    st.session_state.prod_mode = "list"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


if st.session_state.prod_mode in ("add", "edit"):
    edit_data = None
    if st.session_state.prod_mode == "edit" and st.session_state.prod_edit_id:
        edit_data = get_product_by_id(st.session_state.prod_edit_id)
    show_product_form(edit_data)
else:
    top1, top2 = st.columns([5, 1])
    with top2:
        if st.button("➕ Add Product", use_container_width=True):
            st.session_state.prod_mode = "add"
            st.rerun()

    products = get_all_products()
    if not products:
        st.info("No products yet. Click **Add Product** to create your catalogue.")
    else:
        hdr = st.columns([1.5, 4, 2, 0.5, 0.5])
        hdr[0].markdown("**Product ID**")
        hdr[1].markdown("**Name**")
        hdr[2].markdown("**Price (₹)**")
        st.markdown("<hr style='margin:2px 0;border-color:#2D4A3E;'>", unsafe_allow_html=True)

        for prod in products:
            cols = st.columns([1.5, 4, 2, 0.5, 0.5])
            cols[0].caption(prod["product_id"])
            cols[1].write(prod["name"])
            cols[2].write(f"₹ {prod['price']:,.2f}")

            if cols[3].button("✏️", key=f"edit_p_{prod['id']}", help="Edit"):
                st.session_state.prod_mode = "edit"
                st.session_state.prod_edit_id = prod["id"]
                st.rerun()
            if cols[4].button("🗑️", key=f"del_p_{prod['id']}", help="Delete"):
                delete_product(prod["id"])
                st.rerun()
