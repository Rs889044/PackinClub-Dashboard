"""
Page 7: Orders — Read-only view with Excel/CSV export
"""

import streamlit as st
import pandas as pd
import os, sys
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database import get_all_orders, EXPORT_DIR, init_db
from styles import inject_custom_css, page_header

st.set_page_config(page_title="Orders", page_icon="📊", layout="wide")
init_db()
inject_custom_css()

page_header("📊", "Confirmed Orders", "Orders are auto-created from invoices or confirmed quotations.")

orders = get_all_orders()

if not orders:
    st.info("No orders yet. Generate an invoice or confirm a quotation to see orders here.")
else:
    # Summary metrics at top
    m1, m2, m3 = st.columns(3)
    total_orders = len(orders)
    total_revenue = sum(o["grand_total"] for o in orders)
    avg_order = total_revenue / total_orders if total_orders else 0

    m1.metric("Total Orders", total_orders)
    m2.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
    m3.metric("Avg. Order Value", f"₹ {avg_order:,.2f}")

    st.markdown("---")

    # Build dataframe
    df = pd.DataFrame(orders)
    display_cols = {
        "order_number": "Order #",
        "source_type": "Source",
        "customer_name": "Customer",
        "cust_code": "Customer ID",
        "total_amount": "Subtotal (₹)",
        "gst_amount": "GST (₹)",
        "grand_total": "Grand Total (₹)",
        "created_at": "Date",
    }

    df_display = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)

    for col in ["Subtotal (₹)", "GST (₹)", "Grand Total (₹)"]:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f"₹ {x:,.2f}")

    if "Date" in df_display.columns:
        df_display["Date"] = df_display["Date"].apply(lambda x: x[:10] if x else "—")
    if "Source" in df_display.columns:
        df_display["Source"] = df_display["Source"].str.capitalize()

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Export buttons
    st.markdown("---")
    exp1, exp2, _ = st.columns([1, 1, 4])

    with exp1:
        buffer = BytesIO()
        export_df = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, sheet_name="Orders", index=False)
        st.download_button("📥 Export Excel", data=buffer.getvalue(),
                           file_name="orders_export.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

    with exp2:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", data=csv_data,
                           file_name="orders_export.csv", mime="text/csv",
                           use_container_width=True)
