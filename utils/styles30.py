# -*- coding: utf-8 -*-
"""استایل سراسری سامانه تحلیل بنیادی - طراحی مدرن، کاربرپسند با منوی چپ"""

import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    /* ============================================ */
    /* فونت وزیرمتن */
    /* ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');

    /* ============================================ */
    /* استایل پایه */
    /* ============================================ */
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', 'Tahoma', 'Segoe UI', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 15px !important;
        line-height: 1.8 !important;
        color: #1e293b !important;
        background: #f8fafc !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
        direction: rtl !important;
        background: #f8fafc;
    }

    /* ============================================ */
    /* سایدبار - چپ با گرادیانت ملایم */
    /* ============================================ */
    section[data-testid="stSidebar"] {
        position: fixed !important;
        left: 0 !important;
        right: auto !important;
        top: 0 !important;
        bottom: 0 !important;
        width: 260px !important;
        height: 100vh !important;
        background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 50%, #d1d9e6 100%) !important;
        border-left: none !important;
        border-right: 1px solid rgba(100, 116, 139, 0.15) !important;
        box-shadow: -4px 0 30px rgba(0, 0, 0, 0.04) !important;
        direction: ltr !important;
        border-radius: 0 16px 16px 0 !important;
        z-index: 999 !important;
    }

    section[data-testid="stSidebar"] > div {
        direction: rtl !important;
        padding-top: 1rem !important;
    }

    section[data-testid="stSidebar"] * {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption {
        color: #475569 !important;
        font-size: 14px !important;
    }

    /* ============================================ */
    /* محتوای اصلی - فاصله از منو */
    /* ============================================ */
    .main .block-container {
        padding-right: 2rem !important;
        padding-left: 2rem !important;
        margin-right: 260px !important;
    }

    /* ============================================ */
    /* لوگوی سایدبار */
    /* ============================================ */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
        content: "📊 تحلیل بنیادی";
        display: block;
        color: #0f172a;
        font-size: 1.2rem;
        font-weight: 800;
        padding: 0.8rem 1.2rem 1rem 1.2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(15, 23, 42, 0.08);
        background: rgba(255, 255, 255, 0.4);
        border-radius: 14px;
        margin-left: 0.5rem;
        margin-right: 0.5rem;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        text-align: center !important;
        letter-spacing: 0.5px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* ============================================ */
    /* آیتم‌های منو */
    /* ============================================ */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding: 0.3rem 0.6rem !important;
        margin: 0 !important;
        list-style: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin-bottom: 0.4rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        border-radius: 14px !important;
        padding: 0.7rem 1.1rem !important;
        color: #334155 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid transparent !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: right !important;
        direction: rtl !important;
        gap: 0.6rem !important;
        backdrop-filter: blur(4px);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 255, 255, 0.8) !important;
        color: #0f172a !important;
        border-color: rgba(148, 163, 184, 0.3) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #0f172a !important;
        border-color: rgba(37, 99, 235, 0.2) !important;
        font-weight: 700 !important;
        border-left: 4px solid #2563eb !important;
        border-right: none !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.08) !important;
    }

    /* ============================================ */
    /* عناوین */
    /* ============================================ */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
        color: #0f172a !important;
    }

    h1 {
        font-size: 2.4rem !important;
        margin-bottom: 0.8rem !important;
        background: linear-gradient(135deg, #0f172a, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        padding-left: 1rem;
        border-left: 4px solid #2563eb;
    }

    h2 {
        font-size: 1.7rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.7rem !important;
        padding-right: 0.8rem;
        border-right: 4px solid #2563eb;
    }

    h3 {
        font-size: 1.35rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        color: #1e293b !important;
    }

    /* ============================================ */
    /* لیبل‌ها */
    /* ============================================ */
    label {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        margin-bottom: 4px !important;
    }

    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }

    /* ============================================ */
    /* تکست باکس‌ها */
    /* ============================================ */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox > div > div,
    .stTextArea textarea {
        border-radius: 14px !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 15px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        padding: 0.7rem 1.2rem !important;
        direction: rtl !important;
        text-align: right !important;
        background: #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        color: #1e293b !important;
        min-height: 48px !important;
        height: auto !important;
        line-height: 1.6 !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.08) !important;
        outline: none !important;
    }

    .stSelectbox > div > div {
        padding: 0.5rem 1.2rem !important;
        background: #ffffff !important;
        min-height: 48px !important;
    }

    /* ============================================ */
    /* متریک‌ها */
    /* ============================================ */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 18px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-height: 90px;
        direction: rtl !important;
        text-align: center !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #2563eb, #7c3aed);
        border-radius: 0 4px 4px 0;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-4px) !important;
        border-color: #cbd5e1 !important;
    }

    div[data-testid="stMetric"] label {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 0.9rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
        letter-spacing: 0.3px;
        margin-bottom: 4px !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        font-size: 1.5rem !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
        background: linear-gradient(135deg, #0f172a, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ============================================ */
    /* کپشن‌ها */
    /* ============================================ */
    .stCaption {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        color: #64748b !important;
        font-size: 0.85rem !important;
        direction: rtl !important;
        text-align: right !important;
        margin-top: 0.3rem !important;
        font-weight: 500 !important;
    }

    /* ============================================ */
    /* جداول */
    /* ============================================ */
    .stTable, table {
        border-radius: 16px !important;
        overflow: hidden;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        font-size: 14px !important;
        width: 100% !important;
        direction: rtl !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
    }

    .stTable thead th,
    table thead th {
        background: linear-gradient(135deg, #1e293b, #0f172a) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 14px 18px !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        text-align: center !important;
        white-space: nowrap !important;
        border: none !important;
        border-bottom: 3px solid #2563eb !important;
    }

    .stTable tbody td,
    table tbody td {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        color: #1e293b !important;
        text-align: center !important;
        background: #ffffff !important;
        font-weight: 500 !important;
    }

    .stTable tbody tr:hover td,
    table tbody tr:hover td {
        background: #f8fafc !important;
    }

    .stTable tbody tr:nth-child(even) td,
    table tbody tr:nth-child(even) td {
        background: #fafbfc !important;
    }

    /* ============================================ */
    /* دکمه‌ها */
    /* ============================================ */
    div.stButton > button {
        border-radius: 14px !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.6rem !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        filter: brightness(1.05);
        box-shadow: 0 6px 30px rgba(37, 99, 235, 0.4) !important;
        transform: translateY(-3px) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06) !important;
    }

    /* ============================================ */
    /* Expander */
    /* ============================================ */
    details {
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 0.8rem !important;
        direction: rtl !important;
        overflow: hidden !important;
    }

    details summary {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 1rem !important;
        color: #0f172a !important;
        text-align: right !important;
        direction: rtl !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        background: #f8fafc !important;
    }

    details summary:hover {
        color: #2563eb !important;
        background: #f1f5f9 !important;
    }

    details[open] summary {
        border-bottom: 1px solid #e2e8f0 !important;
        color: #2563eb !important;
    }

    /* ============================================ */
    /* Tab ها */
    /* ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        direction: rtl !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px !important;
        padding: 10px 24px !important;
        background: #f1f5f9 !important;
        color: #334155 !important;
        transition: all 0.3s ease !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #e2e8f0 !important;
        color: #0f172a !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important;
    }

    /* ============================================ */
    /* Alert */
    /* ============================================ */
    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 14px !important;
        padding: 1rem 1.5rem !important;
        direction: rtl !important;
        text-align: right !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03) !important;
    }

    /* ============================================ */
    /* ستون‌ها */
    /* ============================================ */
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem !important;
        margin-bottom: 0.8rem !important;
        direction: rtl !important;
    }

    /* ============================================ */
    /* اسکرول‌بار */
    /* ============================================ */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #2563eb, #7c3aed);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #1d4ed8, #6d28d9);
    }

    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 5px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.3);
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.5);
    }

    /* ============================================ */
    /* Subheader */
    /* ============================================ */
    .stSubheader {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        font-size: 1.4rem !important;
        direction: rtl !important;
        text-align: right !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
    }

    /* ============================================ */
    /* Divider */
    /* ============================================ */
    hr {
        margin: 1.5rem 0 !important;
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #2563eb, transparent) !important;
        opacity: 0.15 !important;
    }

    /* ============================================ */
    /* Selectbox در سایدبار */
    /* ============================================ */
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 14px !important;
        color: #475569 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid rgba(100, 116, 139, 0.15) !important;
        border-radius: 12px !important;
        color: #1e293b !important;
    }
    </style>
    """, unsafe_allow_html=True)