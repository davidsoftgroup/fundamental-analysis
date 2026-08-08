# -*- coding: utf-8 -*-
"""استایل سراسری سامانه تحلیل بنیادی - استخوانی با لبه‌های گرد"""

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
        background: #f8f5f0 !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
        direction: rtl !important;
        background: #f8f5f0;
    }

    /* ============================================ */
    /* سایدبار - استخوانی با لبه‌های گرد */
    /* ============================================ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5efe8 0%, #ede5db 30%, #e8ddd1 60%, #ddd0c2 100%) !important;
        border-left: none !important;
        border-right: 2px solid rgba(200, 180, 165, 0.3) !important;
        box-shadow: -4px 0 30px rgba(0, 0, 0, 0.05) !important;
        border-radius: 0 20px 20px 0 !important;
        direction: ltr !important;
        left: 0 !important;
        right: auto !important;
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
        color: #5a4e42 !important;
        font-size: 14px !important;
    }

    /* ============================================ */
    /* لوگوی سایدبار */
    /* ============================================ */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
        content: "📊 تحلیل بنیادی";
        display: block;
        color: #4a3f35;
        font-size: 1.2rem;
        font-weight: 800;
        padding: 0.8rem 1.2rem 1rem 1.2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(90, 78, 66, 0.12);
        background: rgba(255, 248, 240, 0.5);
        border-radius: 16px;
        margin-left: 0.5rem;
        margin-right: 0.5rem;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        text-align: center !important;
        letter-spacing: 0.5px;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 248, 240, 0.4);
    }

    /* ============================================ */
    /* آیتم‌های منو - استخوانی با لبه‌های گرد */
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
        border-radius: 16px !important;
        padding: 0.75rem 1.1rem !important;
        color: #5a4e42 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        background: rgba(255, 248, 240, 0.4) !important;
        border: 1px solid rgba(255, 248, 240, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-align: right !important;
        direction: rtl !important;
        gap: 0.6rem !important;
        backdrop-filter: blur(4px);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(255, 248, 240, 0.8) !important;
        color: #3a3028 !important;
        border-color: rgba(200, 180, 165, 0.5) !important;
        transform: translateX(4px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg, #ede5db, #e8ddd1) !important;
        color: #3a3028 !important;
        border-color: #c8b4a5 !important;
        font-weight: 700 !important;
        border-left: 4px solid #a8907a !important;
        border-right: none !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
    }

    /* ============================================ */
    /* عناوین - سرمه‌ای */
    /* ============================================ */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px !important;
        color: #2a221c !important;
    }

    h1 {
        font-size: 2.4rem !important;
        margin-bottom: 0.8rem !important;
        background: linear-gradient(135deg, #2a221c, #5a4e42);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        padding-left: 1rem;
        border-left: 4px solid #a8907a;
    }

    h2 {
        font-size: 1.7rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.7rem !important;
        padding-right: 0.8rem;
        border-right: 4px solid #a8907a;
        color: #2a221c !important;
    }

    h3 {
        font-size: 1.35rem !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        color: #3a3028 !important;
    }

    h4 {
        font-size: 1.1rem !important;
        color: #3a3028 !important;
        font-weight: 700 !important;
    }

    /* ============================================ */
    /* لیبل‌ها */
    /* ============================================ */
    label {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #3a3028 !important;
        margin-bottom: 4px !important;
    }

    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #3a3028 !important;
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
        border: 2px solid #e8ddd1 !important;
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
        border-color: #a8907a !important;
        box-shadow: 0 0 0 4px rgba(168, 144, 122, 0.15) !important;
        outline: none !important;
    }

    .stSelectbox > div > div {
        padding: 0.5rem 1.2rem !important;
        background: #ffffff !important;
        min-height: 48px !important;
    }

    /* ============================================ */
    /* متریک‌ها - با لبه‌های گرد */
    /* ============================================ */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e8ddd1 !important;
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
        background: linear-gradient(180deg, #a8907a, #c8b4a5);
        border-radius: 0 4px 4px 0;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 8px 35px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-4px) !important;
        border-color: #c8b4a5 !important;
    }

    div[data-testid="stMetric"] label {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 0.9rem !important;
        color: #5a4e42 !important;
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
        color: #2a221c !important;
        font-size: 1.5rem !important;
        text-align: center !important;
        display: block !important;
        width: 100% !important;
    }

    /* ============================================ */
    /* جداول - لبه‌های گرد و طیف سرمه‌ای */
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
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
    }

    .stTable thead th,
    table thead th {
        background: linear-gradient(135deg, #2a221c, #3a3028) !important;
        color: #f5efe8 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 14px 18px !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        text-align: center !important;
        white-space: nowrap !important;
        border: none !important;
        border-bottom: 3px solid #a8907a !important;
        border-radius: 0 !important;
    }

    .stTable thead th:first-child,
    table thead th:first-child {
        border-radius: 0 16px 0 0 !important;
    }

    .stTable thead th:last-child,
    table thead th:last-child {
        border-radius: 16px 0 0 0 !important;
    }

    .stTable tbody td,
    table tbody td {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
        border-bottom: 1px solid #ede5db !important;
        color: #1e293b !important;
        text-align: center !important;
        background: #ffffff !important;
        font-weight: 500 !important;
    }

    .stTable tbody tr:hover td,
    table tbody tr:hover td {
        background: #faf6f1 !important;
    }

    .stTable tbody tr:nth-child(even) td,
    table tbody tr:nth-child(even) td {
        background: #fcfaf7 !important;
    }

    .stTable tbody tr:nth-child(even):hover td,
    table tbody tr:nth-child(even):hover td {
        background: #faf6f1 !important;
    }

    .stTable tbody tr:last-child td:first-child,
    table tbody tr:last-child td:first-child {
        border-radius: 0 0 0 16px !important;
    }

    .stTable tbody tr:last-child td:last-child,
    table tbody tr:last-child td:last-child {
        border-radius: 0 0 16px 0 !important;
    }

    /* ============================================ */
    /* کپشن‌ها */
    /* ============================================ */
    .stCaption {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        color: #5a4e42 !important;
        font-size: 0.85rem !important;
        direction: rtl !important;
        text-align: right !important;
        margin-top: 0.3rem !important;
        font-weight: 500 !important;
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
        background: linear-gradient(135deg, #3a3028, #2a221c) !important;
        color: #f5efe8 !important;
        box-shadow: 0 4px 20px rgba(42, 34, 28, 0.2) !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #2a221c, #3a3028) !important;
        box-shadow: 0 6px 30px rgba(42, 34, 28, 0.3) !important;
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
        border: 1px solid #e8ddd1 !important;
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
        color: #2a221c !important;
        text-align: right !important;
        direction: rtl !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        background: #faf8f5 !important;
    }

    details summary:hover {
        color: #5a4e42 !important;
        background: #f5efe8 !important;
    }

    details[open] summary {
        border-bottom: 1px solid #e8ddd1 !important;
        color: #5a4e42 !important;
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
        background: #ede5db !important;
        color: #3a3028 !important;
        transition: all 0.3s ease !important;
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #e8ddd1 !important;
        color: #2a221c !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3a3028, #2a221c) !important;
        color: #f5efe8 !important;
        box-shadow: 0 4px 20px rgba(42, 34, 28, 0.2) !important;
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
        background: #ede5db;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #a8907a, #c8b4a5);
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #8a7a6a, #b8a490);
    }

    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 5px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(90, 78, 66, 0.25);
        border-radius: 10px;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
        background: rgba(90, 78, 66, 0.4);
    }

    /* ============================================ */
    /* Subheader */
    /* ============================================ */
    .stSubheader {
        font-family: 'Vazirmatn', 'Tahoma', sans-serif !important;
        font-weight: 700 !important;
        color: #2a221c !important;
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
        background: linear-gradient(90deg, transparent, #c8b4a5, transparent) !important;
        opacity: 0.3 !important;
    }

    /* ============================================ */
    /* Selectbox در سایدبار */
    /* ============================================ */
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 14px !important;
        color: #5a4e42 !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 248, 240, 0.5) !important;
        border: 1px solid rgba(200, 180, 165, 0.3) !important;
        border-radius: 12px !important;
        color: #3a3028 !important;
    }
    </style>
    """, unsafe_allow_html=True)