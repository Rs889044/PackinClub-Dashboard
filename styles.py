"""
styles.py — Shared CSS for all pages
======================================
Inject via: inject_custom_css()
"""

import streamlit as st


def inject_custom_css():
    """Inject the shared PackinClub-themed CSS into any page."""
    st.markdown("""
<style>
    /* ── Global spacing ── */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    div[data-testid="stVerticalBlock"] > div { gap: 0.35rem; }
    div[data-testid="stHorizontalBlock"] > div { gap: 0.5rem; }
    .element-container { margin-bottom: 0.15rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B3A2D 0%, #2D4A3E 100%);
    }
    [data-testid="stSidebar"] * { color: #d4e4d4 !important; }

    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #1B3A2D 0%, #2D4A3E 60%, #3E6B52 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 10px;
        margin-bottom: 16px;
        border-left: 4px solid #C5A55A;
    }
    .page-header h2 { margin: 0; font-size: 1.35rem; font-weight: 700; color: white !important; }
    .page-header p  { margin: 3px 0 0; opacity: 0.8; font-size: 0.82rem; color: #d4e4d4 !important; }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #f7faf7;
        border-radius: 8px;
        padding: 10px 12px;
        border: 1px solid #e0ece0;
    }
    [data-testid="stMetric"] label { color: #2D4A3E !important; font-size: 0.78rem; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1B3A2D !important; font-size: 1.4rem; font-weight: 700;
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        padding: 4px 10px;
    }

    /* ── Tables / Data rows ── */
    .data-row {
        display: flex;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #eef3ee;
        font-size: 0.88rem;
    }
    .data-header {
        font-weight: 700;
        color: #1B3A2D;
        font-size: 0.82rem;
        padding-bottom: 6px;
        border-bottom: 2px solid #2D4A3E;
        margin-bottom: 2px;
    }

    /* ── Form styling ── */
    .stForm { border: 1px solid #e0ece0 !important; border-radius: 10px !important; padding: 16px !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader { font-size: 0.88rem !important; font-weight: 600 !important; }

    /* ── Divider ── */
    hr { margin: 6px 0 !important; border-color: #e8efe8 !important; }

    /* ── Status badges ── */
    .badge-confirmed {
        background: #d4edda; color: #155724;
        padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: 600;
    }
    .badge-draft {
        background: #fff3cd; color: #856404;
        padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: 600;
    }

    /* ── DataFrames ── */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ── Remove extra padding in columns ── */
    div[data-testid="column"] { padding: 0 4px; }
</style>
""", unsafe_allow_html=True)


def page_header(icon, title, subtitle=""):
    """Render a consistent page header."""
    sub_html = f'<p>{subtitle}</p>' if subtitle else ''
    st.markdown(f"""
    <div class="page-header">
        <h2>{icon} {title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
