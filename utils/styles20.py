# -*- coding: utf-8 -*-
"""استایل سراسری سامانه تحلیل بنیادی"""

import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap');

    /* ---- پایه ---- */
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    h1, h2, h3, h4 {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-weight: 600 !important;
    }

    /* ============================================================ */
    /* ★★★ سایدبار با طیف سرمه‌ای-خاکستری شیک ★★★ */
    /* ============================================================ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 40%, #0f172a 100%) !important;
        border-radius: 18px !important;
        margin: 10px 8px !important;
        border: 1px solid rgba(100, 116, 139, 0.2) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 0.5rem;
        padding-left: 6px !important;
        padding-right: 6px !important;
    }

    /* عنوان بالای منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
        content: "📊 تحلیل بنیادی";
        display: block;
        color: #f1f5f9;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 0.8rem 1rem 1.2rem 1rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid rgba(148, 163, 184, 0.15);
        letter-spacing: 0.5px;
        text-align: center;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* آیتم‌های منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding: 0.2rem 0.3rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin-bottom: 0.5rem !important;
        list-style: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 14px !important;
        padding: 0.75rem 1.1rem !important;
        color: #cbd5e1 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(148, 163, 184, 0.08) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        margin: 2px 0 !important;
        text-decoration: none !important;
        display: block !important;
        backdrop-filter: blur(4px) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(37, 99, 235, 0.15) !important;
        color: #ffffff !important;
        border-color: rgba(37, 99, 235, 0.3) !important;
        transform: translateX(-4px) scale(1.01) !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.15) !important;
    }

    /* آیتم فعال */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span[data-testid="stSidebarNavLink"][aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.35) !important;
        font-weight: 600 !important;
        border-right: 4px solid #60a5fa !important;
        transform: translateX(-2px) !important;
    }

    /* متن‌های سایدبار */
    section[data-testid="stSidebar"] * {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    /* اسکرول‌بار سایدبار */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 4px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(37, 99, 235, 0.4);
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
        background: transparent;
    }

    /* ============================================================ */
    /* ★★★ جداول با طراحی حرفه‌ای و طیف سرمه‌ای ★★★ */
    /* ============================================================ */
    .stTable, table {
        border-radius: 20px !important;
        overflow: hidden !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 1.05rem !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        width: 100% !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08) !important;
    }

    /* هدر جدول - طیف سرمه‌ای */
    .stTable thead tr, table thead tr {
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
    }

    .stTable thead th, table thead th {
        background: linear-gradient(135deg, #0f172a, #1e293b) !important;
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 14px 18px !important;
        text-align: center !important;
        border: none !important;
        letter-spacing: 0.3px !important;
        border-bottom: 3px solid #2563eb !important;
    }

    .stTable thead th:first-child, table thead th:first-child {
        border-radius: 20px 0 0 0 !important;
    }
    .stTable thead th:last-child, table thead th:last-child {
        border-radius: 0 20px 0 0 !important;
    }

    /* بدنه جدول */
    .stTable tbody td, table tbody td {
        background: #ffffff !important;
        color: #0f172a !important;
        font-size: 1.05rem !important;
        padding: 14px 18px !important;
        text-align: center !important;
        border-bottom: 1px solid #e8ecf1 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stTable tbody tr:nth-child(even) td, table tbody tr:nth-child(even) td {
        background: #f8fafc !important;
    }

    .stTable tbody tr:hover td, table tbody tr:hover td {
        background: #e2e8f0 !important;
        transform: scale(1.002);
    }

    /* گوشه‌های پایین جدول */
    .stTable tbody tr:last-child td:first-child, table tbody tr:last-child td:first-child {
        border-radius: 0 0 0 20px !important;
    }
    .stTable tbody tr:last-child td:last-child, table tbody tr:last-child td:last-child {
        border-radius: 0 0 20px 0 !important;
    }

    /* ستون اول با رنگ کمی متفاوت */
    .stTable tbody td:first-child, table tbody td:first-child {
        font-weight: 600 !important;
        color: #1e293b !important;
        background: #f1f5f9 !important;
        border-left: 3px solid #2563eb !important;
    }
    .stTable tbody tr:nth-child(even) td:first-child, table tbody tr:nth-child(even) td:first-child {
        background: #e8ecf1 !important;
    }

    /* ============================================================ */
    /* ★★★ سایر المان‌ها ★★★ */
    /* ============================================================ */

    /* دکمه‌ها */
    div.stButton > button {
        border-radius: 14px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.55rem 1.5rem !important;
        border: none !important;
        transition: all 0.25s ease !important;
        background: linear-gradient(135deg, #1e293b, #334155) !important;
        color: white !important;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
    }

    div.stButton > button:hover {
        filter: brightness(1.08);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
        transform: translateY(-2px) scale(1.02);
    }

    /* اینپوت‌ها */
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
        border-radius: 14px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 1.05rem !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.7rem 1.2rem !important;
        transition: all 0.2s ease !important;
        background: #ffffff !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox > div > div:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }

    /* متریک‌ها */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 18px !important;
        padding: 1.2rem 1rem !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.25s ease !important;
        min-height: 90px;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 6px 24px rgba(37, 99, 235, 0.1) !important;
        transform: translateY(-3px) !important;
        border-color: #2563eb !important;
    }

    div[data-testid="stMetric"] label {
        font-size: 0.95rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #0f172a !important;
        font-size: 1.4rem !important;
    }

    /* Expander */
    details {
        border-radius: 18px !important;
        border: 2px solid #e2e8f0 !important;
        background: #ffffff !important;
        padding: 0.3rem !important;
        transition: all 0.2s ease !important;
    }

    details:hover {
        border-color: #2563eb !important;
    }

    details summary {
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        padding: 0.7rem 0.8rem !important;
        color: #1e293b !important;
    }

    /* Alert */
    div[data-testid="stAlert"] {
        border-radius: 18px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 1.05rem !important;
        padding: 1rem 1.5rem !important;
        border: 2px solid transparent !important;
    }

    div[data-testid="stAlert"]:has(.stAlert-success) {
        border-color: #16a34a !important;
    }
    div[data-testid="stAlert"]:has(.stAlert-warning) {
        border-color: #ca8a04 !important;
    }
    div[data-testid="stAlert"]:has(.stAlert-info) {
        border-color: #2563eb !important;
    }

    /* تیترها */
    h1 {
        font-size: 2.2rem !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        margin-bottom: 1.2rem !important;
        background: linear-gradient(135deg, #0f172a, #1e293b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2, h3 {
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 0.8rem !important;
    }

    /* متن‌های عادی */
    .main .stMarkdown p, .main .stMarkdown li, .main .stMarkdown div {
        font-size: 1.05rem !important;
        line-height: 1.9 !important;
        color: #1e293b !important;
    }

    /* Caption */
    .stCaption, caption {
        font-size: 1rem !important;
        color: #64748b !important;
        font-weight: 400 !important;
    }

    /* Selectbox */
    .stSelectbox > div > div > div {
        font-size: 1.05rem !important;
    }

    /* Checkbox & Radio */
    .stCheckbox label, .stRadio label {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: #1e293b !important;
    }

    /* Subheader */
    .stSubheader {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }

    /* خط جداکننده */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #2563eb, transparent) !important;
        margin: 2rem 0 !important;
        opacity: 0.3 !important;
    }

    </style>
    """, unsafe_allow_html=True)