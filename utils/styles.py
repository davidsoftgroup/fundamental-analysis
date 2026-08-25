# -*- coding: utf-8 -*-
"""استایل سراسری سامانه تحلیل بنیادی"""

import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap');

    /* ==========================================
       پایه
       ========================================== */
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
    }

    /* ✅ اصلاح اصلی - پر کردن کامل صفحه */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    /* حذف حاشیه‌های اضافی */
    .main {
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
    }

    /* ستون‌ها را به‌خوبی پخش کن */
    .stColumn {
        padding: 0 0.5rem !important;
    }

    .stColumns {
        gap: 0.5rem !important;
    }

    /* ==========================================
       سایدبار - ساده و تمیز
       ========================================== */
    section[data-testid="stSidebar"] {
        background: #f1f5f9 !important;
        border-left: 1px solid #e2e8f0 !important;
        min-width: 280px !important;
        max-width: 320px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }

    /* ==========================================
       استایل المان‌ها (بقیه به‌قوت خود)
       ========================================== */
    /* عنوان منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"]::before {
        content: "📊 تحلیل بنیادی";
        display: block;
        color: #0f172a;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.8rem 1rem 1.2rem 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* آیتم‌های منو */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
        padding: 0.2rem 0.3rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li {
        margin-bottom: 0.3rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        color: #334155 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        background: transparent !important;
        border: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: #e2e8f0 !important;
        color: #0f172a !important;
    }

    /* آیتم فعال */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ==========================================
       جداول
       ========================================== */
    .stTable, table {
        border-radius: 12px !important;
        overflow: hidden !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 1rem !important;
        border-collapse: collapse !important;
        width: 100% !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stTable thead th, table thead th {
        background: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
        text-align: center !important;
        border: none !important;
    }

    .stTable tbody td, table tbody td {
        background: #ffffff !important;
        color: #1e293b !important;
        font-size: 0.95rem !important;
        padding: 11px 16px !important;
        text-align: center !important;
        border-bottom: 1px solid #f1f5f9 !important;
    }

    .stTable tbody tr:nth-child(even) td, table tbody tr:nth-child(even) td {
        background: #fafbfc !important;
    }

    .stTable tbody tr:hover td, table tbody tr:hover td {
        background: #f1f5f9 !important;
    }

    /* ==========================================
       متریک‌ها
       ========================================== */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem 1rem !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        min-height: 80px;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06) !important;
    }

    div[data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #0f172a !important;
        font-size: 1.3rem !important;
    }

    /* ==========================================
       اینپوت‌ها
       ========================================== */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox > div > div {
        color: #000000 !important;
        font-weight: 500 !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 1rem !important;
        background: #ffffff !important;
        border-radius: 10px !important;
        border: 1.5px solid #d1d5db !important;
        padding: 12px 16px !important;
        min-height: 48px !important;
        height: 48px !important;
        line-height: 1.5 !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }

    .stTextInput input::placeholder {
        color: #6b7280 !important;
        font-weight: 400 !important;
        opacity: 1 !important;
    }

    .stTextInput input:focus,
    .stNumberInput input:focus {
        border-color: #0f172a !important;
        box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.08) !important;
        color: #000000 !important;
        outline: none !important;
    }

    /* ==========================================
       سلکت‌باکس
       ========================================== */
    .stSelectbox > div > div {
        color: #000000 !important;
        font-weight: 500 !important;
        min-height: 48px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
    }

    .stSelectbox [data-baseweb="select"] div[role="button"] {
        color: #000000 !important;
        font-weight: 500 !important;
        background: #ffffff !important;
        min-height: 48px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 12px !important;
        font-size: 1rem !important;
    }

    /* ==========================================
       دکمه‌ها
       ========================================== */
    div.stButton > button {
        border-radius: 10px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 1.5rem !important;
        border: 1px solid #e2e8f0 !important;
        transition: all 0.2s ease !important;
        background: #ffffff !important;
        color: #0f172a !important;
    }

    div.stButton > button[kind="primary"] {
        background: #0f172a !important;
        color: #ffffff !important;
        border: none !important;
    }

    div.stButton > button:hover {
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.1) !important;
        transform: translateY(-1px);
    }

    /* ==========================================
       اکسپندر
       ========================================== */
    details {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        padding: 0.2rem !important;
    }

    details summary {
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.5rem 0.7rem !important;
        color: #0f172a !important;
    }

    /* ==========================================
       هشدارها
       ========================================== */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 0.95rem !important;
        padding: 0.8rem 1.2rem !important;
    }

    /* ==========================================
       تیترها
       ========================================== */
    h1 {
        font-size: 2rem !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 1.4rem !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #f1f5f9 !important;
    }

    h3 {
        font-size: 1.2rem !important;
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    /* ==========================================
       متن‌ها
       ========================================== */
    .main .stMarkdown p, .main .stMarkdown li {
        font-size: 0.95rem !important;
        line-height: 1.8 !important;
        color: #334155 !important;
    }

    .stCaption, caption {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
    }

    /* ==========================================
       خط جداکننده
       ========================================== */
    hr {
        border: none !important;
        border-top: 1px solid #e2e8f0 !important;
        margin: 2rem 0 !important;
    }

    /* ==========================================
       اسکرول‌بار
       ========================================== */
    ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }

    /* ==========================================
       ✅ صفحات - حذف فضای خالی اضافی
       ========================================== */
    .stApp {
        width: 100% !important;
        max-width: 100% !important;
    }

    .stAppViewContainer {
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
    }

    /* حذف padding اضافی از container اصلی */
    .st-emotion-cache-1y4p8pa {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* تنظیم grid برای استفاده کامل از فضا */
    .st-emotion-cache-1r6slb0 {
        gap: 0.5rem !important;
    }

    /* جدول را به‌خوبی پخش کن */
    .st-emotion-cache-16idsys {
        width: 100% !important;
        overflow-x: auto !important;
    }

    </style>
    """, unsafe_allow_html=True)