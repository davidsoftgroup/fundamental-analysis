# -*- coding: utf-8 -*-
"""
صفحه ورود اطلاعات تصمیمات مجمع سالیانه
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
import jdatetime
import traceback
import sqlite3

# تنظیمات صفحه
st.set_page_config(
    page_title="تصمیمات مجمع سالیانه",
    layout="wide",
    initial_sidebar_state="expanded"
)

# اضافه کردن مسیر اصلی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.styles import apply_styles
apply_styles()

from utils.database import (
    get_connection, 
    get_all_symbols_from_db,
    save_meeting_decision,
    get_meeting_decisions,
    get_meeting_decisions_stats,
    delete_meeting_decision
)

# ============================================================
# استایل اختصاصی صفحه
# ============================================================
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-box h1 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem;
    }
    
    .header-box p {
        color: #94a3b8 !important;
        font-size: 1rem;
    }
    
    .form-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .form-box h3 {
        color: #0f172a;
        margin-top: 0;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        height: 100%;
        transition: all 0.2s ease;
    }
    
    .stat-card:hover {
        border-color: #0f172a;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    
    .stat-card .number {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }
    
    .stat-card .number.green {
        color: #22c55e;
    }
    
    .stat-card .number.blue {
        color: #3b82f6;
    }
    
    .stat-card .number.purple {
        color: #8b5cf6;
    }
    
    .stat-card .number.orange {
        color: #f59e0b;
    }
    
    .stat-card .number.red {
        color: #ef4444;
    }
    
    .stat-card .label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .dataframe-container {
        overflow-x: auto;
        margin: 1rem 0;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    .dataframe-container table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 0.9rem;
        direction: rtl;
    }
    
    .dataframe-container th {
        background-color: #0f172a !important;
        color: white !important;
        font-weight: 600;
        padding: 12px 16px !important;
        text-align: center !important;
        border: none !important;
        white-space: nowrap;
    }
    
    .dataframe-container td {
        background: #ffffff !important;
        color: #1e293b !important;
        padding: 10px 14px !important;
        text-align: center !important;
        border-bottom: 1px solid #f1f5f9 !important;
    }
    
    .dataframe-container tr:nth-child(even) td {
        background: #fafbfc !important;
    }
    
    .dataframe-container tr:hover td {
        background: #f1f5f9 !important;
    }
    
    .stButton button {
        background-color: #0f172a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    
    .success-box {
        background: #dcfce7;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        animation: fadeIn 0.5s ease;
    }
    
    .success-box .icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .success-box .title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #166534;
    }
    
    .success-box .subtitle {
        font-size: 0.9rem;
        color: #14532d;
        margin-top: 0.3rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .error-box {
        background: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        border-radius: 12px;
        padding: 6px;
        direction: rtl;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease;
        background: transparent !important;
        height: auto !important;
        white-space: nowrap;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background-color: #1e293b !important;
        color: white !important;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox > div > div {
        background-color: white !important;
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        font-family: 'Vazirmatn', Tahoma, sans-serif !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #0f172a !important;
        box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.1) !important;
    }
    
    /* کوچک کردن اینپوت‌های تاریخ */
    .date-input-small .stNumberInput input {
        font-size: 0.85rem !important;
        padding: 0.25rem 0.4rem !important;
        min-height: 32px !important;
        height: 32px !important;
    }
    
    .date-input-small .stSelectbox > div > div {
        font-size: 0.85rem !important;
        min-height: 32px !important;
        height: 32px !important;
        padding: 0 0.4rem !important;
    }
    
    .date-input-small label {
        font-size: 0.75rem !important;
        color: #64748b !important;
        margin-bottom: 0.1rem !important;
    }
    
    .calculated-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.3rem 0;
    }
    
    .calculated-box .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #166534;
    }
    
    .calculated-box .label {
        font-size: 0.8rem;
        color: #14532d;
        margin-top: 0.2rem;
    }
    
    .ratio-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.3rem 0;
    }
    
    .ratio-box .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #92400e;
    }
    
    .ratio-box .label {
        font-size: 0.8rem;
        color: #78350f;
        margin-top: 0.2rem;
    }
    
    .form-reset {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    .system-error {
        background: #1e293b;
        color: #f1f5f9;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #ef4444;
        direction: ltr;
        text-align: left;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .system-error .error-title {
        color: #ef4444;
        font-weight: bold;
        font-size: 1rem;
        margin-bottom: 0.5rem;
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# توابع تبدیل تاریخ
# ============================================================
def get_current_jalali_date():
    """دریافت تاریخ شمسی فعلی"""
    return jdatetime.datetime.now()

# ============================================================
# مقداردهی اولیه session_state
# ============================================================
if 'form_reset' not in st.session_state:
    st.session_state.form_reset = False

if 'show_success' not in st.session_state:
    st.session_state.show_success = False

if 'saved_symbol' not in st.session_state:
    st.session_state.saved_symbol = ""

if 'saved_year' not in st.session_state:
    st.session_state.saved_year = 1403

if 'show_error_details' not in st.session_state:
    st.session_state.show_error_details = False

# ============================================================
# هدر صفحه
# ============================================================
st.markdown("""
<div class="header-box">
    <h1>📋 تصمیمات مجمع سالیانه</h1>
    <p>ثبت و مدیریت اطلاعات تصمیمات مجمع شرکت‌ها</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# دریافت لیست نمادها
# ============================================================
symbols_data = get_all_symbols_from_db()
symbols_list = [s['symbol'] for s in symbols_data] if symbols_data else []

if not symbols_list:
    st.warning("⚠️ هیچ نمادی در دیتابیس یافت نشد!")
    st.info("💡 لطفاً ابتدا نمادها را به دیتابیس اضافه کنید.")
    st.stop()

# ============================================================
# تب‌ها
# ============================================================
tab1, tab2, tab3 = st.tabs(["📝 ورود اطلاعات", "📊 مشاهده و مدیریت", "📈 آمار"])

# ============================================================
# تب ۱: ورود اطلاعات
# ============================================================
with tab1:
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("➕ ثبت تصمیم مجمع جدید")
    
    # اطلاعات پایه - ستون اول (سمت راست)
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox(
            "📌 انتخاب نماد *",
            options=symbols_list,
            key="input_symbol"
        )
        
        year_solar = st.number_input(
            "📅 سال مالی *",
            min_value=1390,
            max_value=1410,
            value=st.session_state.saved_year if st.session_state.form_reset else 1403,
            step=1,
            key="input_year"
        )
        
        # ============================================================
        # سرمایه با پشتیبانی از اعشار
        # ============================================================
        capital = st.number_input(
            "💰 سرمایه (هزار میلیارد تومان) *",
            min_value=0.0,
            value=56000000.0,
            step=1000000.0,
            key="input_capital",
            help="مبلغ سرمایه شرکت به ریال (مثال: 56000000 یا 0.1)"
        )
    
    # اطلاعات پایه - ستون دوم (سمت چپ)
    with col2:
        net_profit = st.number_input(
            "💵 سود خالص (هزار میلیارد تومان) *",
            min_value=0.0,
            value=195495785.0,
            step=1000000.0,
            key="net_profit",
            help="سود خالص شرکت به هزار میلیارد تومان"
        )
        
        retained_earnings = st.number_input(
            "🏦 سود انباشته پایان دوره (هزار میلیارد تومان) *",
            min_value=0.0,
            value=195495785.0,
            step=1000000.0,
            key="retained_earnings",
            help="مبلغ سود انباشته پایان دوره به هزار میلیارد تومان"
        )
        
        approved_dividend = st.number_input(
            "📋 سود سهام مصوب (هزار میلیارد تومان) *",
            min_value=0.0,
            value=112000000.0,
            step=1000000.0,
            key="approved_dividend",
            help="مبلغ سود سهام مصوب در مجمع سال جاری به هزار میلیارد تومان"
        )
    
    # ============================================================
    # تاریخ مجمع (کوچک) - یک سلول واحد
    # ============================================================
    st.markdown("---")
    st.markdown('<div class="date-input-small">', unsafe_allow_html=True)
    
    st.markdown("📆 **تاریخ مجمع** *")
    
    current_jalali = get_current_jalali_date()
    
    # سه ستون برای سال، ماه، روز
    col_year, col_month, col_day = st.columns(3)
    
    with col_year:
        jalali_year = st.number_input(
            "سال",
            min_value=1390,
            max_value=1410,
            value=current_jalali.year,
            step=1,
            key="jalali_year"
        )
    
    with col_month:
        jalali_month = st.selectbox(
            "ماه",
            options=list(range(1, 13)),
            index=current_jalali.month - 1,
            key="jalali_month",
            format_func=lambda x: f"{x:02d}"
        )
    
    with col_day:
        if jalali_month in [1, 2, 3, 4, 5, 6]:
            max_day = 31
        elif jalali_month in [7, 8, 9, 10, 11]:
            max_day = 30
        else:
            if (jalali_year % 33 in [1, 5, 9, 13, 17, 22, 26, 30]):
                max_day = 30
            else:
                max_day = 29
        
        jalali_day = st.number_input(
            "روز",
            min_value=1,
            max_value=max_day,
            value=min(current_jalali.day, max_day),
            step=1,
            key="jalali_day"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ساخت تاریخ شمسی
    try:
        meeting_date = jdatetime.datetime(
            year=jalali_year,
            month=jalali_month,
            day=jalali_day
        )
        meeting_date_str = meeting_date.strftime('%Y/%m/%d')
        st.markdown(f"""
        <div style="background: #f1f5f9; padding: 0.3rem; border-radius: 6px; text-align: center; margin-top: 0.2rem; font-size: 0.85rem; border: 1px solid #e2e8f0;">
            📆 تاریخ انتخاب شده: <strong>{meeting_date_str}</strong>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error("❌ تاریخ وارد شده معتبر نیست")
        meeting_date = None
        meeting_date_str = ""
    
    # ============================================================
    # محاسبات خودکار
    # ============================================================
    st.markdown("---")
    st.subheader("📊 محاسبات خودکار")
    
    # محاسبه سود هر سهم
    eps = net_profit / capital if capital > 0 else 0
    
    # محاسبه سود نقدی هر سهم
    dps = approved_dividend / capital if capital > 0 else 0
    
    # محاسبه درصد تقسیم سود = (سود سهام مصوب ÷ سود انباشته پایان دوره) × ۱۰۰
    dividend_percent = (approved_dividend / retained_earnings * 100) if retained_earnings > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="calculated-box">
            <div class="value">{eps:,.2f}</div>
            <div class="label">💰 سود هر سهم (تومان)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="calculated-box">
            <div class="value">{dps:,.2f}</div>
            <div class="label">💵 سود نقدی هر سهم (تومان)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = "#166534" if dividend_percent <= 100 else "#dc2626"
        st.markdown(f"""
        <div class="calculated-box" style="border-color: {color};">
            <div class="value" style="color: {color};">{dividend_percent:.1f}%</div>
            <div class="label">📊 درصد تقسیم سود</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================================
    # دکمه ذخیره
    # ============================================================
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 ذخیره اطلاعات"):
            # اعتبارسنجی
            errors = []
            
            if not symbol:
                errors.append("لطفاً نماد را انتخاب کنید!")
            if year_solar < 1390:
                errors.append("سال مالی معتبر نیست!")
            if capital <= 0:
                errors.append("سرمایه باید بزرگتر از صفر باشد!")
            if net_profit <= 0:
                errors.append("سود خالص باید بزرگتر از صفر باشد!")
            if retained_earnings <= 0:
                errors.append("سود انباشته پایان دوره باید بزرگتر از صفر باشد!")
            if approved_dividend <= 0:
                errors.append("سود سهام مصوب باید بزرگتر از صفر باشد!")
            if not meeting_date:
                errors.append("تاریخ مجمع معتبر نیست!")
            
            if errors:
                error_text = "<br>".join([f"• {e}" for e in errors])
                st.markdown(f"""
                <div class="error-box">
                    ❌ لطفاً موارد زیر را اصلاح کنید:<br>
                    {error_text}
                </div>
                """, unsafe_allow_html=True)
            else:
                # ساخت دیکشنری داده
                data = {
                    'symbol': symbol,
                    'year_solar': year_solar,
                    'capital': capital,
                    'net_profit': net_profit,
                    'retained_earnings': retained_earnings,
                    'approved_dividend': approved_dividend,
                    'eps': eps,
                    'dps': dps,
                    'dividend_percent': dividend_percent,
                    'meeting_date': meeting_date_str,
                    'decision_date': get_current_jalali_date().strftime('%Y/%m/%d'),
                    'is_approved': 1,
                    'notes': f"سرمایه: {capital:,.2f} | سود خالص: {net_profit:,.2f} | سود انباشته: {retained_earnings:,.2f} | سود مصوب: {approved_dividend:,.2f}",
                    'source': "ورود دستی"
                }
                
                # ذخیره در دیتابیس
                try:
                    result = save_meeting_decision(data)
                    
                    if result:
                        st.session_state.show_success = True
                        st.session_state.saved_symbol = symbol
                        st.session_state.saved_year = year_solar
                        st.session_state.form_reset = True
                        st.experimental_rerun()
                    else:
                        st.markdown("""
                        <div class="error-box">
                            ❌ خطا در ذخیره اطلاعات. ممکن است این سال برای این نماد قبلاً ثبت شده باشد.
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    error_trace = traceback.format_exc()
                    st.markdown(f"""
                    <div class="system-error">
                        <div class="error-title">❌ خطای سیستمی:</div>
                        {error_trace}
                    </div>
                    """, unsafe_allow_html=True)
    
    # نمایش پیام موفقیت در پایین (زیر دکمه ذخیره)
    if st.session_state.show_success:
        st.markdown(f"""
        <div class="success-box" style="margin-top: 1rem;">
            <div class="icon">✅</div>
            <div class="title">اطلاعات با موفقیت ذخیره شد!</div>
            <div class="subtitle">
                نماد: <strong>{st.session_state.saved_symbol}</strong> | 
                سال: <strong>{st.session_state.saved_year}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # دکمه بستن پیام
        if st.button("✖️ بستن", key="close_success_bottom"):
            st.session_state.show_success = False
            st.experimental_rerun()
    
    # نمایش پیام ریست فرم
    if st.session_state.form_reset and not st.session_state.show_success:
        st.markdown("""
        <div class="form-reset">
            ✅ فرم برای ورود اطلاعات جدید آماده است.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# تب ۲: مشاهده و مدیریت
# ============================================================
with tab2:
    st.subheader("📋 لیست تصمیمات مجمع")
    
    # فیلترها - فقط فیلتر بر اساس نماد
    filter_symbol = st.selectbox(
        "🔍 انتخاب نماد",
        options=["همه"] + symbols_list,
        index=0,
        key="filter_symbol"
    )
    
    # دریافت داده بر اساس فیلتر
    try:
        if filter_symbol == "همه":
            decisions = get_meeting_decisions(limit=200)
        else:
            decisions = get_meeting_decisions(symbol=filter_symbol, limit=200)
        
        if decisions:
            # نمایش آمار
            col1, col2 = st.columns(2)
            
            total_records = len(decisions)
            avg_dividend_percent = sum([d.get('dividend_percent', 0) for d in decisions if d.get('dividend_percent')]) / total_records if total_records > 0 else 0
            
            with col1:
                st.metric("📄 تعداد رکوردها", total_records)
            with col2:
                st.metric("📊 میانگین درصد تقسیم", f"{avg_dividend_percent:.0f}%")
            
            st.markdown("---")
            
            # نمایش جدول (بدون اعشار)
            table_data = []
            for d in decisions:
                table_data.append({
                    "نماد": d.get('symbol', ''),
                    "سال": d.get('year_solar', ''),
                    "سرمایه": f"{d.get('capital', 0):,.2f}" if d.get('capital') else "—",
                    "سود خالص": f"{d.get('net_profit', 0):,.2f}" if d.get('net_profit') else "—",
                    "سود انباشته": f"{d.get('retained_earnings', 0):,.2f}" if d.get('retained_earnings') else "—",
                    "سود مصوب": f"{d.get('approved_dividend', 0):,.2f}" if d.get('approved_dividend') else "—",
                    "سود هر سهم": f"{d.get('eps', 0):,.2f}" if d.get('eps') else "—",
                    "سود نقدی هر سهم": f"{d.get('dps', 0):,.2f}" if d.get('dps') else "—",
                    "درصد تقسیم": f"{d.get('dividend_percent', 0):.0f}%" if d.get('dividend_percent') else "—",
                    "تاریخ مجمع": d.get('meeting_date', ''),
                    "id": d.get('id')
                })
            
            df = pd.DataFrame(table_data)
            
            html_table = df.drop(columns=['id']).to_html(
                index=False,
                classes="dataframe",
                border=0,
                escape=False
            )
            
            st.markdown(f"""
            <div class="dataframe-container">
                {html_table}
            </div>
            """, unsafe_allow_html=True)
            
            st.caption(f"نمایش {len(decisions)} رکورد")
            
            # عملیات حذف
            st.markdown("---")
            st.subheader("🗑️ حذف رکورد")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                delete_options = [f"{d.get('symbol')} - {d.get('year_solar')}" for d in decisions]
                if delete_options:
                    selected_delete = st.selectbox(
                        "انتخاب رکورد برای حذف",
                        options=delete_options,
                        key="delete_select"
                    )
                    
                    if st.button("🗑️ حذف"):
                        parts = selected_delete.split(" - ")
                        symbol_del = parts[0]
                        year_del = int(parts[1])
                        
                        if delete_meeting_decision(symbol_del, year_del):
                            st.success(f"✅ رکورد {selected_delete} با موفقیت حذف شد!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ خطا در حذف رکورد")
        else:
            st.info("📭 هیچ تصمیم مجمعی یافت نشد")
            
    except Exception as e:
        error_trace = traceback.format_exc()
        st.markdown(f"""
        <div class="system-error">
            <div class="error-title">❌ خطا در دریافت داده:</div>
            {error_trace}
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# تب ۳: آمار
# ============================================================
with tab3:
    st.subheader("📊 آمار تصمیمات مجمع")
    
    try:
        stats = get_meeting_decisions_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number">{stats.get('total', 0)}</div>
                <div class="label">📄 کل تصمیمات</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number purple">{stats.get('symbols', 0)}</div>
                <div class="label">📌 تعداد نمادها</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📊 آمار به تفکیک نماد")
        
        all_decisions = get_meeting_decisions(limit=500)
        
        if all_decisions:
            symbol_stats = {}
            for d in all_decisions:
                sym = d.get('symbol')
                if sym not in symbol_stats:
                    symbol_stats[sym] = {
                        'count': 0,
                        'years': [],
                        'total_eps': 0,
                        'total_dps': 0,
                        'total_percent': 0
                    }
                symbol_stats[sym]['count'] += 1
                if d.get('year_solar'):
                    symbol_stats[sym]['years'].append(d.get('year_solar'))
                if d.get('eps'):
                    symbol_stats[sym]['total_eps'] += d.get('eps', 0)
                if d.get('dps'):
                    symbol_stats[sym]['total_dps'] += d.get('dps', 0)
                if d.get('dividend_percent'):
                    symbol_stats[sym]['total_percent'] += d.get('dividend_percent', 0)
            
            stats_data = []
            for sym, data in symbol_stats.items():
                count = data['count']
                stats_data.append({
                    "نماد": sym,
                    "تعداد": count,
                    "سال‌ها": ", ".join([str(y) for y in sorted(data['years'])]),
                    "میانگین EPS": f"{data['total_eps']/count:,.2f}" if data['total_eps'] > 0 else "—",
                    "میانگین DPS": f"{data['total_dps']/count:,.2f}" if data['total_dps'] > 0 else "—",
                    "میانگین درصد تقسیم": f"{data['total_percent']/count:.0f}%" if data['total_percent'] > 0 else "—"
                })
            
            df_stats = pd.DataFrame(stats_data)
            
            html_table = df_stats.to_html(
                index=False,
                classes="dataframe",
                border=0,
                escape=False
            )
            
            st.markdown(f"""
            <div class="dataframe-container">
                {html_table}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📭 هنوز داده‌ای برای نمایش وجود ندارد")
            
    except Exception as e:
        error_trace = traceback.format_exc()
        st.markdown(f"""
        <div class="system-error">
            <div class="error-title">❌ خطا در دریافت آمار:</div>
            {error_trace}
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# فوتر
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px 0; font-size: 14px; color: #94a3b8;">
    📋 آخرین بروزرسانی: {get_current_jalali_date().strftime('%Y/%m/%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)