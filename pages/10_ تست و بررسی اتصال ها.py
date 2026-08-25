# -*- coding: utf-8 -*-
"""
نسخه ساده شده برای دیباگ - با استایل یکپارچه
"""

import streamlit as st
import sys
import os

# ============================================================
# تنظیمات صفحه
# ============================================================
st.set_page_config(
    page_title="پایش کدال - ساده",
    layout="wide"
)

# اضافه کردن مسیر اصلی
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# اعمال استایل سراسری
from utils.styles import apply_styles
apply_styles()

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
    
    .step-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .step-box h2 {
        color: #0f172a;
        font-size: 1.3rem;
        margin-top: 0;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border-right: 4px solid #22c55e;
        margin: 0.3rem 0;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border-right: 4px solid #ef4444;
        margin: 0.3rem 0;
    }
    
    .status-info {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border-right: 4px solid #3b82f6;
        margin: 0.3rem 0;
    }
    
    .path-item {
        font-family: 'Courier New', monospace;
        background: #f1f5f9;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin: 0.2rem 0;
    }
    
    .folder-exists {
        color: #16a34a;
        font-weight: bold;
    }
    
    .folder-missing {
        color: #dc2626;
        font-weight: bold;
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
    
    .final-result {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1.5rem;
    }
    
    .final-result h3 {
        color: #166534;
        margin: 0;
    }
    
    .final-result p {
        color: #14532d;
        margin: 0.5rem 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# هدر صفحه
# ============================================================
st.markdown("""
<div class="header-box">
    <h1>🔍 پایش کدال - نسخه ساده</h1>
    <p>بررسی مسیرها، ایمپورت‌ها و اتصال به دیتابیس</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# مرحله ۱: بررسی مسیرها
# ============================================================
st.markdown("""
<div class="step-box">
    <h2>📁 مرحله ۱: بررسی مسیرها</h2>
""", unsafe_allow_html=True)

st.write(f"**ریشه پروژه:** `{project_root}`")

# بررسی وجود پوشه‌ها
folders = ["services", "utils", "data"]
for folder in folders:
    path = os.path.join(project_root, folder)
    exists = os.path.exists(path)
    status = "✅ موجود" if exists else "❌ وجود ندارد"
    color = "folder-exists" if exists else "folder-missing"
    st.markdown(f"""
    <div class="path-item">
        📂 <strong>{folder}</strong>: <span class="{color}">{status}</span>
        <span style="color: #94a3b8; font-size: 0.8rem;"> - {path}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# مرحله ۲: بررسی ایمپورت‌ها
# ============================================================
st.markdown("""
<div class="step-box">
    <h2>📦 مرحله ۲: بررسی ایمپورت‌ها</h2>
""", unsafe_allow_html=True)

# تست database
try:
    from utils.database import get_connection, get_all_symbols_from_db
    st.markdown('<div class="status-success">✅ utils.database import successful</div>', unsafe_allow_html=True)
except Exception as e:
    st.markdown(f'<div class="status-error">❌ Error importing database: {e}</div>', unsafe_allow_html=True)
    st.code(str(e))

# تست styles
try:
    from utils.styles import apply_styles
    st.markdown('<div class="status-success">✅ utils.styles import successful</div>', unsafe_allow_html=True)
except Exception as e:
    st.markdown(f'<div class="status-error">❌ Error importing styles: {e}</div>', unsafe_allow_html=True)
    st.code(str(e))

# تست سرویس
try:
    from services.codal_monitor_service import CodalMonitorService
    st.markdown('<div class="status-success">✅ services.codal_monitor_service import successful</div>', unsafe_allow_html=True)
except Exception as e:
    st.markdown(f'<div class="status-error">❌ Error importing CodalMonitorService: {e}</div>', unsafe_allow_html=True)
    st.code(str(e))

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# مرحله ۳: تست دیتابیس
# ============================================================
st.markdown("""
<div class="step-box">
    <h2>🗄️ مرحله ۳: تست دیتابیس</h2>
""", unsafe_allow_html=True)

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # لیست جدول‌ها
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if tables:
        st.markdown('<div class="status-info">📋 جدول‌های موجود:</div>', unsafe_allow_html=True)
        
        # ساخت داده برای جدول
        table_data = []
        for t in tables:
            table_name = t[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
            except:
                count = 0
            table_data.append({"نام جدول": table_name, "تعداد رکورد": count})
        
        # نمایش جدول با استایل
        import pandas as pd
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
    else:
        st.markdown('<div class="status-info">⚠️ هیچ جدولی در دیتابیس یافت نشد</div>', unsafe_allow_html=True)
    
    # تعداد نمادها
    try:
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        st.markdown(f'<div class="status-success">📊 تعداد نمادها در companies: <strong>{count}</strong></div>', unsafe_allow_html=True)
        
        if count > 0:
            cursor.execute("SELECT symbol, name_fa FROM companies LIMIT 5")
            samples = cursor.fetchall()
            symbols_list = []
            for s in samples:
                name = s[1] if s[1] else "—"
                symbols_list.append(f"{s[0]} ({name})")
            st.markdown(f'<div class="status-info">📌 نمونه نمادها: {", ".join(symbols_list)}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<div class="status-error">⚠️ خطا در خواندن companies: {e}</div>', unsafe_allow_html=True)
    
    conn.close()
    st.markdown('<div class="status-success">✅ دیتابیس متصل است</div>', unsafe_allow_html=True)
    
except Exception as e:
    st.markdown(f'<div class="status-error">❌ خطا در اتصال به دیتابیس: {e}</div>', unsafe_allow_html=True)
    st.code(str(e))

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# مرحله ۴: تست ایجاد سرویس
# ============================================================
st.markdown("""
<div class="step-box">
    <h2>⚙️ مرحله ۴: تست ایجاد سرویس</h2>
""", unsafe_allow_html=True)

try:
    service = CodalMonitorService()
    st.markdown('<div class="status-success">✅ سرویس ایجاد شد</div>', unsafe_allow_html=True)
    
    # تست دریافت آمار
    stats = service.get_statistics()
    st.markdown(f"""
    <div class="status-info">
        📊 آمار:<br>
        • تعداد نمادها: <strong>{stats.get('total_symbols', 0)}</strong><br>
        • کل گزارشات: <strong>{stats.get('total_reports', 0)}</strong><br>
        • گزارش‌های جدید: <strong>{stats.get('new_reports', 0)}</strong>
    </div>
    """, unsafe_allow_html=True)
    
except Exception as e:
    st.markdown(f'<div class="status-error">❌ خطا در ایجاد سرویس: {e}</div>', unsafe_allow_html=True)
    st.code(str(e))

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# نتیجه نهایی
# ============================================================
st.markdown("""
<div class="final-result">
    <h3>✅ بررسی کامل شد!</h3>
    <p>اگر همه مراحل سبز هستند، سیستم به درستی کار می‌کند.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# فوتر
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px 0; font-size: 14px; color: #94a3b8;">
    🔍 پایش کدال - نسخه ساده • {__import__('datetime').datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)