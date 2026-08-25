# -*- coding: utf-8 -*-
"""
نمایش گزارش‌های ذخیره شده در دیتابیس
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(
    page_title="گزارش‌های ذخیره شده",
    layout="wide",
    initial_sidebar_state="expanded"
)

# اضافه کردن مسیر اصلی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.styles import apply_styles
apply_styles()

from utils.database import get_connection

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
    
    .stat-card .label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .filter-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
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
        table-layout: fixed; /* برای کنترل عرض ستون‌ها */
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
        vertical-align: middle;
        word-wrap: break-word; /* شکستن کلمات طولانی */
        white-space: normal; /* اجازه دادن به چند خطی شدن */
    }
    
    /* عرض ستون‌ها */
    .dataframe-container td:nth-child(1) { width: 8%; }  /* نماد */
    .dataframe-container td:nth-child(2) { width: 12%; } /* نوع گزارش */
    .dataframe-container td:nth-child(3) { width: 40%; } /* عنوان - بزرگترین */
    .dataframe-container td:nth-child(4) { width: 15%; } /* تاریخ ارسال */
    .dataframe-container td:nth-child(5) { width: 10%; } /* وضعیت */
    .dataframe-container td:nth-child(6) { width: 15%; } /* دانلود */
    
    /* همینطور برای هدرها */
    .dataframe-container th:nth-child(1) { width: 8%; }
    .dataframe-container th:nth-child(2) { width: 12%; }
    .dataframe-container th:nth-child(3) { width: 40%; }
    .dataframe-container th:nth-child(4) { width: 15%; }
    .dataframe-container th:nth-child(5) { width: 10%; }
    .dataframe-container th:nth-child(6) { width: 15%; }
    
    .dataframe-container tr:nth-child(even) td {
        background: #fafbfc !important;
    }
    
    .dataframe-container tr:hover td {
        background: #f1f5f9 !important;
    }
    
    /* استایل برای متن عنوان */
    .report-title {
        text-align: right !important;
        line-height: 1.6;
        font-size: 0.85rem;
    }
    
    .badge-new {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-seen {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-old {
        display: inline-block;
        background: #f1f5f9;
        color: #64748b;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .download-link {
        display: inline-block;
        color: white !important;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        text-decoration: none;
        font-size: 0.7rem;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .download-link:hover {
        transform: translateY(-1px);
        opacity: 0.9;
    }
    
    .download-link-pdf {
        background: #dc2626;
    }
    
    .download-link-pdf:hover {
        background: #b91c1c;
    }
    
    .download-link-attach {
        background: #2563eb;
    }
    
    .download-link-attach:hover {
        background: #1d4ed8;
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
    }
    
    .stButton button:hover {
        background-color: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# هدر صفحه
# ============================================================
st.markdown("""
<div class="header-box">
    <h1>📊 گزارش‌های ذخیره شده</h1>
    <p>نمایش تمام گزارش‌های ذخیره شده در دیتابیس</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# اتصال به دیتابیس و دریافت داده
# ============================================================
try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # بررسی وجود جدول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='codal_reports'")
    if not cursor.fetchone():
        st.warning("⚠️ جدول codal_reports در دیتابیس وجود ندارد!")
        st.info("💡 لطفاً ابتدا گزارش‌ها را از صفحه کدال ذخیره کنید.")
        st.stop()
    
    # دریافت آمار
    cursor.execute("SELECT COUNT(*) FROM codal_reports")
    total_reports = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT symbol) FROM codal_reports")
    total_symbols = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM codal_reports WHERE is_new = 1")
    new_reports = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM codal_reports WHERE seen = 1")
    seen_reports = cursor.fetchone()[0]
    
    # نمایش کارت‌های آمار
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{total_reports}</div>
            <div class="label">📄 کل گزارش‌ها</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number purple">{total_symbols}</div>
            <div class="label">📌 تعداد نمادها</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number green">{new_reports}</div>
            <div class="label">🆕 گزارش‌های جدید</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="number blue">{seen_reports}</div>
            <div class="label">✅ دیده شده</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================================
    # فیلترها
    # ============================================================
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.subheader("🔍 فیلترها")
    
    # دریافت لیست نمادها
    cursor.execute("SELECT DISTINCT symbol FROM codal_reports ORDER BY symbol")
    symbols_list = [row[0] for row in cursor.fetchall()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_symbol = st.selectbox(
            "فیلتر بر اساس نماد",
            options=["همه"] + symbols_list,
            index=0
        )
    
    with col2:
        filter_status = st.selectbox(
            "وضعیت",
            options=["همه", "جدید", "دیده شده"],
            index=0
        )
    
    with col3:
        filter_limit = st.selectbox(
            "تعداد نمایش",
            options=[10, 20, 50, 100, "همه"],
            index=1
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # ساخت کوئری بر اساس فیلترها
    # ============================================================
    query = """
        SELECT symbol, title, report_type, sent_date, 
               is_new, seen, pdf_url, attachment_url, 
               financial_year, created_at
        FROM codal_reports 
        WHERE 1=1
    """
    params = []
    
    if filter_symbol != "همه":
        query += " AND symbol = ?"
        params.append(filter_symbol)
    
    if filter_status == "جدید":
        query += " AND is_new = 1"
    elif filter_status == "دیده شده":
        query += " AND seen = 1"
    
    query += " ORDER BY sent_date DESC, created_at DESC"
    
    if filter_limit != "همه":
        query += " LIMIT ?"
        params.append(int(filter_limit))
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # ============================================================
    # نمایش داده‌ها
    # ============================================================
    if rows:
        st.success(f"✅ {len(rows)} گزارش یافت شد")
        
        # ساخت دیتا برای جدول
        table_data = []
        for row in rows:
            # تعیین وضعیت
            if row[4] == 1:  # is_new
                status_badge = '<span class="badge-new">🆕 جدید</span>'
            elif row[5] == 1:  # seen
                status_badge = '<span class="badge-seen">✅ دیده شده</span>'
            else:
                status_badge = '<span class="badge-old">📄 قدیمی</span>'
            
            # ساخت لینک‌های دانلود
            pdf_link = row[6] if row[6] else None
            attach_link = row[7] if row[7] else None
            
            pdf_btn = f'<a href="{pdf_link}" target="_blank" class="download-link download-link-pdf">📄 PDF</a>' if pdf_link else '—'
            attach_btn = f'<a href="{attach_link}" target="_blank" class="download-link download-link-attach">📎 پیوست</a>' if attach_link else '—'
            
            # تاریخ
            sent_date = row[3] if row[3] else "—"
            if sent_date != "—" and len(sent_date) > 16:
                sent_date = sent_date[:16]
            
            # عنوان - نمایش کامل (بدون برش)
            title = row[1] if row[1] else "—"
            
            table_data.append({
                "نماد": row[0],
                "نوع گزارش": row[2] if row[2] else "—",
                "عنوان": title,  # نمایش کامل
                "تاریخ ارسال": sent_date,
                "وضعیت": status_badge,
                "دانلود": f"{pdf_btn} {attach_btn}".strip()
            })
        
        # نمایش جدول
        df = pd.DataFrame(table_data)
        
        html_table = df.to_html(
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
        
        # نمایش تعداد
        st.caption(f"نمایش {len(rows)} گزارش از کل {total_reports} گزارش")
        
        # ============================================================
        # دکمه‌های عملیاتی
        # ============================================================
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ علامت‌گذاری همه به عنوان دیده شده"):
                try:
                    cursor.execute("UPDATE codal_reports SET seen = 1, is_new = 0 WHERE is_new = 1")
                    conn.commit()
                    st.success("✅ همه گزارش‌ها به عنوان دیده شده علامت‌گذاری شدند")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ خطا: {e}")
        
        with col2:
            if st.button("🗑️ حذف همه گزارش‌ها"):
                confirm = st.checkbox("⚠️ تایید حذف همه گزارش‌ها")
                if confirm:
                    try:
                        cursor.execute("DELETE FROM codal_reports")
                        conn.commit()
                        st.success("✅ همه گزارش‌ها حذف شدند")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"❌ خطا: {e}")
        
        with col3:
            if st.button("🔄 بروزرسانی"):
                st.experimental_rerun()
    
    else:
        st.info("📭 هیچ گزارشی در دیتابیس یافت نشد")
        
        if total_reports == 0:
            st.markdown("""
            <div style="background: #f8fafc; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0; margin-top: 1rem;">
                <h4>💡 راهنمایی</h4>
                <ul>
                    <li>برای ذخیره گزارش‌ها، به صفحه <strong>اطلاعات کدال</strong> بروید</li>
                    <li>یک نماد را جستجو کنید</li>
                    <li>روی دکمه <strong>💾 ذخیره همه گزارش‌ها در دیتابیس</strong> کلیک کنید</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    conn.close()

except Exception as e:
    st.error(f"❌ خطا: {e}")
    import traceback
    st.code(traceback.format_exc())

# ============================================================
# فوتر
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px 0; font-size: 14px; color: #94a3b8;">
    📊 آخرین بروزرسانی: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)