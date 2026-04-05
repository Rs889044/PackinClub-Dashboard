"""
app.py — Main entry point for the Invoice Dashboard
=====================================================
Run with: streamlit run app.py
"""

import streamlit as st
from database import init_db

# ── Page config (must be first Streamlit call) ──
st.set_page_config(
    page_title="PackinClub — Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize database on first run ──
init_db()

# ── Custom CSS ──
st.markdown("""
<style>
    /* ── Global spacing reduction ── */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.35rem; }
    div[data-testid="stHorizontalBlock"] > div { gap: 0.5rem; }
    .element-container { margin-bottom: 0.15rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B3A2D 0%, #2D4A3E 100%);
    }
    [data-testid="stSidebar"] * { color: #d4e4d4 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label { font-weight: 600; }

    /* ── Header banner ── */
    .main-header {
        background: linear-gradient(135deg, #1B3A2D 0%, #2D4A3E 60%, #3E6B52 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 4px solid #C5A55A;
    }
    .main-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
    .main-header p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.88rem; }

    /* ── Navigation cards ── */
    .nav-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 18px 16px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        border: 1px solid #e8efe8;
        margin-bottom: 8px;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(27,58,45,0.12);
        border-color: #C5A55A;
    }
    .nav-card .card-icon { font-size: 2rem; margin-bottom: 4px; }
    .nav-card .card-title { font-size: 0.95rem; font-weight: 700; color: #1B3A2D; }
    .nav-card .card-desc  { font-size: 0.75rem; color: #6B8C7A; margin-top: 2px; }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: #f7faf7;
        border-radius: 8px;
        padding: 12px 14px;
        border: 1px solid #e0ece0;
    }
    [data-testid="stMetric"] label { color: #2D4A3E !important; font-size: 0.8rem; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1B3A2D !important; font-size: 1.5rem; font-weight: 700;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 4px 12px;
        transition: all 0.2s;
    }

    /* ── Tables ── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ── Divider ── */
    hr { margin: 8px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── HOME PAGE ──
st.markdown("""
<div class="main-header">
    <h1>🌿 PackinClub - Dashboard</h1>
    <p>Manage customers, products, invoices, quotations, and orders in one place.</p>
</div>
""", unsafe_allow_html=True)

# ── Quick stats ──
from database import get_all_customers, get_all_products, get_all_invoices, get_all_orders

customers = get_all_customers()
products = get_all_products()
invoices = get_all_invoices()
orders = get_all_orders()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", len(customers))
col2.metric("Products", len(products))
col3.metric("Invoices", len(invoices))
col4.metric("Orders", len(orders))

# Revenue stats
if orders:
    total_revenue = sum(o["grand_total"] for o in orders)
    avg_order = total_revenue / len(orders) if orders else 0
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    col6.metric("Avg. Order Value", f"₹ {avg_order:,.0f}")
    col7.metric("From Invoices", len([o for o in orders if o.get("source_type") == "invoice"]))
    col8.metric("From Quotations", len([o for o in orders if o.get("source_type") == "quotation"]))

st.markdown("")

# Navigation cards
cards = [
    ("👥", "Customers",    "Manage customer database",         "3_👥_Customers"),
    ("📦", "Products",     "Product catalogue & pricing",       "4_📦_Products"),
    ("👤", "User Profile", "Company details & branding",        "2_👤_User_Profile"),
    ("🧾", "Invoices",     "Create & download PDF invoices",    "5_🧾_Invoices"),
    ("📋", "Quotations",   "Estimates & convert to orders",     "6_📋_Quotations"),
    ("📊", "Orders",       "Confirmed orders & export",         "7_📊_Orders"),
]

cols = st.columns(3)
for i, (icon, title, desc, page) in enumerate(cards):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="nav-card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Open {title}", key=f"nav_{page}", use_container_width=True):
            st.switch_page(f"pages/{page}.py")

# ── Recent Orders Table ──
if orders:
    st.markdown("---")
    st.markdown("#### Recent Orders")
    import pandas as pd
    recent = orders[:5]
    df = pd.DataFrame(recent)
    display_cols = {
        "order_number": "Order #",
        "source_type": "Source",
        "customer_name": "Customer",
        "grand_total": "Total (₹)",
        "created_at": "Date",
    }
    df_disp = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)
    if "Total (₹)" in df_disp.columns:
        df_disp["Total (₹)"] = df_disp["Total (₹)"].apply(lambda x: f"₹ {x:,.2f}")
    if "Date" in df_disp.columns:
        df_disp["Date"] = df_disp["Date"].apply(lambda x: x[:10] if x else "—")
    if "Source" in df_disp.columns:
        df_disp["Source"] = df_disp["Source"].str.capitalize()
    st.dataframe(df_disp, use_container_width=True, hide_index=True)
