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

    /* ---- سایدبار ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 55%, #0f172a 100%);
        border-left: 1px solid rgba(148, 163, 184, 0.15);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    /* عنوان / لوگو بالای منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
        content: "تحلیل بنیادی";
        display: block;
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 700;
        padding: 0.4rem 1rem 1rem 1rem;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        letter-spacing: 0.3px;
    }

    /* لینک‌های منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding: 0.5rem 0.75rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin-bottom: 0.35rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 12px !important;
        padding: 0.7rem 1rem !important;
        color: #e2e8f0 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(59, 130, 246, 0.18) !important;
        color: #ffffff !important;
        border-color: rgba(59, 130, 246, 0.35) !important;
        transform: translateX(-2px);
    }

    /* صفحه فعال */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span[data-testid="stSidebarNavLink"][aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
        border-color: transparent !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        font-weight: 600 !important;
    }

    /* متن‌های سایدبار */
    section[data-testid="stSidebar"] * {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }

    /* ---- دکمه‌ها ---- */
    div.stButton > button {
        border-radius: 10px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-weight: 500 !important;
        padding: 0.45rem 1.1rem !important;
        border: none !important;
        transition: all 0.15s ease !important;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
    }

    div.stButton > button:hover {
        filter: brightness(1.08);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    /* ---- اینپوت‌ها ---- */
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
        border-radius: 10px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    /* ---- متریک‌ها ---- */
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        color: #64748b !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* ---- جداول ---- */
    .stTable, table {
        border-radius: 12px !important;
        overflow: hidden;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    /* ---- Expander ---- */
    details {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
    }

    details summary {
        font-weight: 600 !important;
        padding: 0.4rem 0.2rem !important;
    }

    /* ---- Info / Success / Warning ---- */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    /* ---- اسکرول‌بار سایدبار ---- */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 6px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.4);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)