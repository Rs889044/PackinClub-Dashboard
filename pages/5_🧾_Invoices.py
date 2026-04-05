"""
Page 5: Invoices — Create, edit, download PDF, delete
======================================================
- Default "Select" placeholder in dropdowns
- Clean, compact layout
- Auto-pushes to Orders table
"""

import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import (
    get_all_invoices, get_invoice_by_id, get_all_customers,
    get_all_products, get_line_items, create_invoice,
    update_invoice, delete_invoice, get_next_invoice_number, init_db
)
from pdf_generator import generate_invoice_pdf
from styles import inject_custom_css, page_header

st.set_page_config(page_title="Invoices", page_icon="🧾", layout="wide")
init_db()
inject_custom_css()

page_header("🧾", "Invoice Management", "Create, edit, and download PDF invoices.")

# Session state
if "inv_mode" not in st.session_state:
    st.session_state.inv_mode = "list"
    st.session_state.inv_edit_id = None
if "inv_items" not in st.session_state:
    st.session_state.inv_items = []


def add_blank_item():
    st.session_state.inv_items.append({"product_id": None, "product_name": "", "price": 0.0, "quantity": 1})


def remove_item(idx):
    st.session_state.inv_items.pop(idx)


def show_invoice_form(edit_data=None):
    is_edit = edit_data is not None
    st.markdown(f"#### {'✏️ Edit' if is_edit else '➕ New'} Invoice")

    if not is_edit:
        st.info(f"Next Invoice Number: **{get_next_invoice_number()}**")

    customers = get_all_customers()
    products = get_all_products()

    if not customers:
        st.warning("⚠️ No customers found. Please add customers first.")
        return
    if not products:
        st.warning("⚠️ No products found. Please add products first.")
        return

    # ── Customer selection with "Select" default ──
    cust_options = {f"{c['customer_id']} — {c['name']}": c for c in customers}
    cust_keys = list(cust_options.keys())

    if is_edit:
        # Find matching customer for edit mode
        default_idx = 0
        for ki, key in enumerate(cust_keys):
            if cust_options[key]["id"] == edit_data["customer_id"]:
                default_idx = ki
                break
        selected_cust_key = st.selectbox("Select Customer *", options=cust_keys, index=default_idx, key="inv_cust_select")
        customer_selected = True
    else:
        # Show "— Select Customer —" as default
        placeholder = "— Select Customer —"
        options_with_placeholder = [placeholder] + cust_keys
        selected_cust_key = st.selectbox("Select Customer *", options=options_with_placeholder, index=0, key="inv_cust_select")
        customer_selected = selected_cust_key != placeholder

    if customer_selected and selected_cust_key in cust_options:
        selected_cust = cust_options[selected_cust_key]

        # Auto-fill customer details (compact)
        with st.expander("📋 Customer Details", expanded=False):
            dc1, dc2, dc3 = st.columns(3)
            dc1.text_input("Address", value=selected_cust.get("address", ""), disabled=True, key="ica")
            dc2.text_input("Phone", value=selected_cust.get("phone", ""), disabled=True, key="icp")
            dc3.text_input("State", value=selected_cust.get("state", ""), disabled=True, key="ics")
    else:
        selected_cust = None

    # GST rate
    gst_rate = st.number_input("GST Rate (%)", min_value=0.0, max_value=100.0, value=18.0, step=0.5, key="inv_gst")

    # ── Line items ──
    st.markdown("#### 📦 Products")

    # Preload items if editing
    if is_edit and not st.session_state.inv_items:
        existing_items = get_line_items("invoice", edit_data["id"])
        st.session_state.inv_items = [
            {"product_id": item["product_id"], "product_name": item["product_name"],
             "price": item["price"], "quantity": item["quantity"]}
            for item in existing_items
        ]

    if not st.session_state.inv_items:
        add_blank_item()

    # Product dropdown with "Select" default
    prod_map = {f"{p['product_id']} — {p['name']}": p for p in products}
    prod_keys = list(prod_map.keys())
    prod_placeholder = "— Select Product —"
    prod_options_full = [prod_placeholder] + prod_keys

    # Column headers
    ph = st.columns([4, 2, 1.5, 2, 0.5])
    ph[0].markdown("**Product**")
    ph[1].markdown("**Price**")
    ph[2].markdown("**Qty**")
    ph[3].markdown("**Subtotal**")

    items_to_save = []
    for idx, item in enumerate(st.session_state.inv_items):
        cols = st.columns([4, 2, 1.5, 2, 0.5])

        # Determine default index
        if item.get("product_id"):
            default_prod_idx = 0  # fallback to placeholder
            for ki, k in enumerate(prod_keys):
                if prod_map[k]["id"] == item["product_id"]:
                    default_prod_idx = ki + 1  # +1 because of placeholder
                    break
        else:
            default_prod_idx = 0

        with cols[0]:
            sel = st.selectbox("Product", prod_options_full, index=default_prod_idx,
                               key=f"inv_prod_{idx}", label_visibility="collapsed")

        if sel != prod_placeholder and sel in prod_map:
            sel_prod = prod_map[sel]
            with cols[1]:
                st.text_input("Price", value=f"₹ {sel_prod['price']:,.2f}",
                              disabled=True, key=f"inv_price_{idx}", label_visibility="collapsed")
            with cols[2]:
                qty = st.number_input("Qty", min_value=1, value=item.get("quantity", 1),
                                      key=f"inv_qty_{idx}", label_visibility="collapsed")
            with cols[3]:
                subtotal = sel_prod["price"] * qty
                st.text_input("Subtotal", value=f"₹ {subtotal:,.2f}",
                              disabled=True, key=f"inv_sub_{idx}", label_visibility="collapsed")

            items_to_save.append({
                "product_id": sel_prod["id"],
                "product_name": sel_prod["name"],
                "price": sel_prod["price"],
                "quantity": qty,
            })
        else:
            with cols[1]:
                st.text_input("Price", value="—", disabled=True, key=f"inv_price_{idx}", label_visibility="collapsed")
            with cols[2]:
                st.number_input("Qty", min_value=1, value=1, key=f"inv_qty_{idx}", label_visibility="collapsed")
            with cols[3]:
                st.text_input("Subtotal", value="—", disabled=True, key=f"inv_sub_{idx}", label_visibility="collapsed")

        with cols[4]:
            if st.button("🗑️", key=f"inv_rm_{idx}"):
                remove_item(idx)
                st.rerun()

    if st.button("➕ Add Product Row", key="inv_add_row"):
        add_blank_item()
        st.rerun()

    # Totals preview
    total = sum(i["price"] * i["quantity"] for i in items_to_save)
    gst_amt = round(total * gst_rate / 100, 2)
    grand = round(total + gst_amt, 2)

    st.markdown("---")
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("Subtotal", f"₹ {total:,.2f}")
    tc2.metric(f"GST ({gst_rate}%)", f"₹ {gst_amt:,.2f}")
    tc3.metric("Grand Total", f"₹ {grand:,.2f}")

    # Action buttons
    st.markdown("---")
    bc1, bc2 = st.columns(2)
    with bc1:
        label = "💾 Update Invoice" if is_edit else "🧾 Generate Invoice"
        if st.button(label, use_container_width=True, type="primary"):
            if not customer_selected or selected_cust is None:
                st.error("Please select a customer.")
            elif not items_to_save:
                st.error("Add at least one product.")
            else:
                try:
                    if is_edit:
                        update_invoice(edit_data["id"], selected_cust["id"], items_to_save, gst_rate)
                        inv_data = get_invoice_by_id(edit_data["id"])
                        pdf_bytes, pdf_filename = generate_invoice_pdf(inv_data, "Invoice")
                        st.success("✅ Invoice updated!")
                    else:
                        inv_id, inv_num = create_invoice(selected_cust["id"], items_to_save, gst_rate)
                        inv_data = get_invoice_by_id(inv_id)
                        pdf_bytes, pdf_filename = generate_invoice_pdf(inv_data, "Invoice")
                        st.success(f"✅ Invoice {inv_num} created!")

                    st.download_button("📥 Download PDF", pdf_bytes,
                                       file_name=pdf_filename,
                                       mime="application/pdf")
                    st.session_state.inv_items = []
                    st.session_state.inv_mode = "list"
                except Exception as e:
                    st.error(f"Error: {e}")

    with bc2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.inv_items = []
            st.session_state.inv_mode = "list"
            st.rerun()


# ══════════════════════════════════════
# MAIN VIEW LOGIC
# ══════════════════════════════════════
if st.session_state.inv_mode in ("add", "edit"):
    edit_data = None
    if st.session_state.inv_mode == "edit" and st.session_state.inv_edit_id:
        edit_data = get_invoice_by_id(st.session_state.inv_edit_id)
    show_invoice_form(edit_data)
else:
    top1, top2 = st.columns([5, 1])
    with top2:
        if st.button("➕ Create Invoice", use_container_width=True):
            st.session_state.inv_items = []
            st.session_state.inv_mode = "add"
            st.rerun()

    invoices = get_all_invoices()
    if not invoices:
        st.info("No invoices yet. Click **Create Invoice** to generate your first one.")
    else:
        hdr = st.columns([2, 2, 2, 2, 0.6, 0.6, 0.6])
        hdr[0].markdown("**Invoice #**")
        hdr[1].markdown("**Customer**")
        hdr[2].markdown("**Date**")
        hdr[3].markdown("**Grand Total**")
        st.markdown("<hr style='margin:2px 0;border-color:#2D4A3E;'>", unsafe_allow_html=True)

        for inv in invoices:
            cols = st.columns([2, 2, 2, 2, 0.6, 0.6, 0.6])
            cols[0].caption(inv["invoice_number"])
            cols[1].write(inv.get("customer_name", "—"))
            cols[2].caption(inv["created_at"][:10] if inv["created_at"] else "—")
            cols[3].write(f"₹ {inv['grand_total']:,.2f}")

            if cols[4].button("✏️", key=f"edit_i_{inv['id']}", help="Edit"):
                st.session_state.inv_items = []
                st.session_state.inv_mode = "edit"
                st.session_state.inv_edit_id = inv["id"]
                st.rerun()

            if cols[5].button("📥", key=f"pdf_i_{inv['id']}", help="Download PDF"):
                inv_full = get_invoice_by_id(inv["id"])
                pdf_bytes, pdf_filename = generate_invoice_pdf(inv_full, "Invoice")
                st.download_button("⬇️ PDF", pdf_bytes,
                                   file_name=pdf_filename,
                                   mime="application/pdf",
                                   key=f"dl_i_{inv['id']}")

            if cols[6].button("🗑️", key=f"del_i_{inv['id']}", help="Delete"):
                delete_invoice(inv["id"])
                st.rerun()