"""
Page 6: Quotations — Estimates with Confirm-to-Order
"""

import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import (
    get_all_quotations, get_quotation_by_id, get_all_customers,
    get_all_products, get_line_items, create_quotation,
    update_quotation, delete_quotation, confirm_quotation,
    get_next_quotation_number, get_invoice_by_id, init_db
)
from pdf_generator import generate_invoice_pdf
from styles import inject_custom_css, page_header

st.set_page_config(page_title="Quotations", page_icon="📋", layout="wide")
init_db()
inject_custom_css()

page_header("📋", "Quotation Management", "Create estimates and convert them to confirmed orders.")

if "quo_mode" not in st.session_state:
    st.session_state.quo_mode = "list"
    st.session_state.quo_edit_id = None
if "quo_items" not in st.session_state:
    st.session_state.quo_items = []


def add_blank_item():
    st.session_state.quo_items.append({"product_id": None, "product_name": "", "price": 0.0, "quantity": 1})


def remove_item(idx):
    st.session_state.quo_items.pop(idx)


def show_quotation_form(edit_data=None):
    is_edit = edit_data is not None
    st.markdown(f"#### {'✏️ Edit' if is_edit else '➕ New'} Quotation")

    if not is_edit:
        st.info(f"Next Quotation Number: **{get_next_quotation_number()}**")

    customers = get_all_customers()
    products = get_all_products()

    if not customers:
        st.warning("⚠️ No customers found. Please add customers first.")
        return
    if not products:
        st.warning("⚠️ No products found. Please add products first.")
        return

    # ── Customer selection ──
    cust_options = {f"{c['customer_id']} — {c['name']}": c for c in customers}
    cust_keys = list(cust_options.keys())

    if is_edit:
        default_idx = 0
        for ki, key in enumerate(cust_keys):
            if cust_options[key]["id"] == edit_data["customer_id"]:
                default_idx = ki
                break
        selected_cust_key = st.selectbox("Select Customer *", options=cust_keys, index=default_idx, key="quo_cust_select")
        customer_selected = True
    else:
        placeholder = "— Select Customer —"
        options_with_placeholder = [placeholder] + cust_keys
        selected_cust_key = st.selectbox("Select Customer *", options=options_with_placeholder, index=0, key="quo_cust_select")
        customer_selected = selected_cust_key != placeholder

    if customer_selected and selected_cust_key in cust_options:
        selected_cust = cust_options[selected_cust_key]
        with st.expander("📋 Customer Details", expanded=False):
            dc1, dc2, dc3 = st.columns(3)
            dc1.text_input("Address", value=selected_cust.get("address", ""), disabled=True, key="qca")
            dc2.text_input("Phone", value=selected_cust.get("phone", ""), disabled=True, key="qcp")
            dc3.text_input("State", value=selected_cust.get("state", ""), disabled=True, key="qcs")
    else:
        selected_cust = None

    gst_rate = st.number_input("GST Rate (%)", min_value=0.0, max_value=100.0, value=18.0, step=0.5, key="quo_gst")

    # ── Line items ──
    st.markdown("#### 📦 Products")

    if is_edit and not st.session_state.quo_items:
        existing = get_line_items("quotation", edit_data["id"])
        st.session_state.quo_items = [
            {"product_id": i["product_id"], "product_name": i["product_name"],
             "price": i["price"], "quantity": i["quantity"]}
            for i in existing
        ]

    if not st.session_state.quo_items:
        add_blank_item()

    prod_map = {f"{p['product_id']} — {p['name']}": p for p in products}
    prod_keys = list(prod_map.keys())
    prod_placeholder = "— Select Product —"
    prod_options_full = [prod_placeholder] + prod_keys

    ph = st.columns([4, 2, 1.5, 2, 0.5])
    ph[0].markdown("**Product**")
    ph[1].markdown("**Price**")
    ph[2].markdown("**Qty**")
    ph[3].markdown("**Subtotal**")

    items_to_save = []
    for idx, item in enumerate(st.session_state.quo_items):
        cols = st.columns([4, 2, 1.5, 2, 0.5])

        if item.get("product_id"):
            default_prod_idx = 0
            for ki, k in enumerate(prod_keys):
                if prod_map[k]["id"] == item["product_id"]:
                    default_prod_idx = ki + 1
                    break
        else:
            default_prod_idx = 0

        with cols[0]:
            sel = st.selectbox("Product", prod_options_full, index=default_prod_idx,
                               key=f"quo_prod_{idx}", label_visibility="collapsed")

        if sel != prod_placeholder and sel in prod_map:
            sel_prod = prod_map[sel]
            with cols[1]:
                st.text_input("Price", value=f"₹ {sel_prod['price']:,.2f}",
                              disabled=True, key=f"quo_price_{idx}", label_visibility="collapsed")
            with cols[2]:
                qty = st.number_input("Qty", min_value=1, value=item.get("quantity", 1),
                                      key=f"quo_qty_{idx}", label_visibility="collapsed")
            with cols[3]:
                subtotal = sel_prod["price"] * qty
                st.text_input("Subtotal", value=f"₹ {subtotal:,.2f}",
                              disabled=True, key=f"quo_sub_{idx}", label_visibility="collapsed")
            items_to_save.append({
                "product_id": sel_prod["id"],
                "product_name": sel_prod["name"],
                "price": sel_prod["price"],
                "quantity": qty,
            })
        else:
            with cols[1]:
                st.text_input("Price", value="—", disabled=True, key=f"quo_price_{idx}", label_visibility="collapsed")
            with cols[2]:
                st.number_input("Qty", min_value=1, value=1, key=f"quo_qty_{idx}", label_visibility="collapsed")
            with cols[3]:
                st.text_input("Subtotal", value="—", disabled=True, key=f"quo_sub_{idx}", label_visibility="collapsed")

        with cols[4]:
            if st.button("🗑️", key=f"quo_rm_{idx}"):
                remove_item(idx)
                st.rerun()

    if st.button("➕ Add Product Row", key="quo_add_row"):
        add_blank_item()
        st.rerun()

    total = sum(i["price"] * i["quantity"] for i in items_to_save)
    gst_amt = round(total * gst_rate / 100, 2)
    grand = round(total + gst_amt, 2)

    st.markdown("---")
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("Subtotal", f"₹ {total:,.2f}")
    tc2.metric(f"GST ({gst_rate}%)", f"₹ {gst_amt:,.2f}")
    tc3.metric("Grand Total", f"₹ {grand:,.2f}")

    st.markdown("---")
    bc1, bc2 = st.columns(2)
    with bc1:
        label = "💾 Update Quotation" if is_edit else "📋 Generate Quotation"
        if st.button(label, use_container_width=True, type="primary"):
            if not customer_selected or selected_cust is None:
                st.error("Please select a customer.")
            elif not items_to_save:
                st.error("Add at least one product.")
            else:
                try:
                    if is_edit:
                        update_quotation(edit_data["id"], selected_cust["id"], items_to_save, gst_rate)
                        quo_full = get_quotation_by_id(edit_data["id"])
                        pdf_bytes, pdf_filename = generate_invoice_pdf(quo_full, "Quotation")
                        st.success("✅ Quotation updated!")
                    else:
                        quo_id, quo_num = create_quotation(selected_cust["id"], items_to_save, gst_rate)
                        quo_full = get_quotation_by_id(quo_id)
                        pdf_bytes, pdf_filename = generate_invoice_pdf(quo_full, "Quotation")
                        st.success(f"✅ Quotation {quo_num} created!")

                    st.download_button("📥 Download PDF", pdf_bytes,
                                       file_name=pdf_filename,
                                       mime="application/pdf")
                    st.session_state.quo_items = []
                    st.session_state.quo_mode = "list"
                except Exception as e:
                    st.error(f"Error: {e}")

    with bc2:
        if st.button("Cancel", use_container_width=True, key="quo_cancel"):
            st.session_state.quo_items = []
            st.session_state.quo_mode = "list"
            st.rerun()


# ══════════════════════════════════════
# MAIN VIEW
# ══════════════════════════════════════
if st.session_state.quo_mode in ("add", "edit"):
    edit_data = None
    if st.session_state.quo_mode == "edit" and st.session_state.quo_edit_id:
        edit_data = get_quotation_by_id(st.session_state.quo_edit_id)
    show_quotation_form(edit_data)
else:
    top1, top2 = st.columns([5, 1])
    with top2:
        if st.button("➕ Create Quotation", use_container_width=True):
            st.session_state.quo_items = []
            st.session_state.quo_mode = "add"
            st.rerun()

    quotations = get_all_quotations()
    if not quotations:
        st.info("No quotations yet. Click **Create Quotation** to start.")
    else:
        hdr = st.columns([2, 2, 1.5, 2, 1.2, 0.5, 0.5, 0.5, 1.2])
        hdr[0].markdown("**Quotation #**")
        hdr[1].markdown("**Customer**")
        hdr[2].markdown("**Date**")
        hdr[3].markdown("**Total**")
        hdr[4].markdown("**Status**")
        st.markdown("<hr style='margin:2px 0;border-color:#2D4A3E;'>", unsafe_allow_html=True)

        for quo in quotations:
            cols = st.columns([2, 2, 1.5, 2, 1.2, 0.5, 0.5, 0.5, 1.2])
            cols[0].caption(quo["quotation_number"])
            cols[1].write(quo.get("customer_name", "—"))
            cols[2].caption(quo["created_at"][:10] if quo["created_at"] else "—")
            cols[3].write(f"₹ {quo['grand_total']:,.2f}")

            status = quo.get("status", "draft")
            if status == "confirmed":
                cols[4].markdown('<span class="badge-confirmed">✅ Confirmed</span>', unsafe_allow_html=True)
            else:
                cols[4].markdown('<span class="badge-draft">📝 Draft</span>', unsafe_allow_html=True)

            # Edit (only drafts)
            if status == "draft":
                if cols[5].button("✏️", key=f"edit_q_{quo['id']}"):
                    st.session_state.quo_items = []
                    st.session_state.quo_mode = "edit"
                    st.session_state.quo_edit_id = quo["id"]
                    st.rerun()

            if cols[6].button("📥", key=f"pdf_q_{quo['id']}", help="PDF"):
                quo_full = get_quotation_by_id(quo["id"])
                pdf_bytes, pdf_filename = generate_invoice_pdf(quo_full, "Quotation")
                st.download_button("⬇️ PDF", pdf_bytes,
                                   file_name=pdf_filename,
                                   mime="application/pdf",
                                   key=f"dl_q_{quo['id']}")

            if cols[7].button("🗑️", key=f"del_q_{quo['id']}"):
                delete_quotation(quo["id"])
                st.rerun()

            if status == "draft":
                if cols[8].button("✅ Confirm", key=f"conf_q_{quo['id']}"):
                    inv_id, inv_num = confirm_quotation(quo["id"])
                    if inv_id:
                        st.success(f"✅ Order confirmed! Invoice {inv_num} created.")
                        st.rerun()
                    else:
                        st.error("Could not confirm quotation.")