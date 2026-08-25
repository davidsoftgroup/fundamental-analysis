# -*- coding: utf-8 -*-
"""
بررسی خودکار گزارش‌های جدید کدال برای همه نمادها
"""

import streamlit as st
import sys
import os
import pandas as pd
import requests
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# تنظیمات صفحه
st.set_page_config(
    page_title="بررسی خودکار کدال",
    layout="wide",
    initial_sidebar_state="expanded"
)

# اضافه کردن مسیر اصلی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.styles import apply_styles
apply_styles()

from utils.database import get_connection, get_all_symbols_from_db

# ============================================================
# استایل اختصاصی
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
    
    .stat-card .number.red {
        color: #ef4444;
    }
    
    .stat-card .number.orange {
        color: #f59e0b;
    }
    
    .stat-card .number.blue {
        color: #3b82f6;
    }
    
    .stat-card .label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .new-report-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
        animation: pulse-green 2s infinite;
        transition: all 0.3s ease;
    }
    
    .new-report-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(34, 197, 94, 0.2);
    }
    
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
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
    
    .badge-new {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
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
    
    .progress-container {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .no-change {
        color: #64748b;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# توابع اصلی
# ============================================================

REPORT_TYPES = {
    "ن-13": "زمانبندی پرداخت سود",
    "ن-10": "اطلاعات و صورت‌های مالی",
    "ن-11": "گزارش فعالیت هیئت مدیره",
    "ن-30": "گزارش فعالیت ماهانه",
    "ن-26": "توضیحات در خصوص صورت‌های مالی",
    "ن-20": "افشای اطلاعات با اهمیت",
    "ن-42": "آگهی ثبت تصمیمات مجمع عادی سالیانه",
    "ن-52": "تصمیمات مجمع عمومی عادی سالیانه",
    "ن-51": "خلاصه تصمیمات مجمع عمومی سالیانه",
    "ن-50": "آگهی دعوت به مجمع عمومی",
    "ن-57": "تصمیمات مجمع عمومی فوق‌العاده",
    "ن-67": "آگهی ثبت افزایش سرمایه",
    "ن-60": "پیشنهاد هیئت مدیره جهت افزایش سرمایه",
    "ن-62": "مدارک و مستندات درخواست افزایش سرمایه",
    "ن-61": "اظهارنظر حسابرس در مورد افزایش سرمایه"
}

def get_report_type(letter_code):
    return REPORT_TYPES.get(letter_code, letter_code)

def build_full_url(url):
    if not url:
        return None
    if url.startswith('http'):
        return url
    if url.startswith('/'):
        return f"https://www.codal.ir{url}"
    return f"https://www.codal.ir/{url}"

def fetch_codal_data(symbol, max_retries=2):
    """دریافت داده‌های کدال برای یک نماد"""
    url = "https://search.codal.ir/api/search/v2/q"
    
    params = {
        "Symbol": symbol,
        "PageNumber": 1,
        "Audited": "true",
        "Mains": "true",
        "NotAudited": "true",
        "Childs": "true",
        "Publisher": "false",
        "Length": "-1",
        "search": "true",
        "CompanyState": 0,
        "CompanyType": -1,
        "Consolidatable": True,
        "IsNotAudited": False,
        "NotConsolidatable": True,
        "Category": -1,
        "AuditorRef": -1,
        "IndustryGroup": -1,
        "ReportingType": 1000000,
        "TracingNo": -1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return None
    
    return None

def get_latest_report_from_db(symbol):
    """دریافت آخرین گزارش از دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tracing_no, sent_date, title, report_type, pdf_url, attachment_url
            FROM codal_reports 
            WHERE symbol = ? 
            ORDER BY sent_date DESC, created_at DESC 
            LIMIT 1
        """, (symbol,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "tracing_no": row[0],
                "sent_date": row[1],
                "title": row[2],
                "report_type": row[3],
                "pdf_url": row[4],
                "attachment_url": row[5]
            }
        return None
    except Exception as e:
        print(f"Error getting latest report for {symbol}: {e}")
        return None

def parse_letter(symbol, letter):
    """پردازش یک نامه از کدال"""
    letter_code = letter.get("LetterCode", "")
    
    # استخراج سال مالی
    title = letter.get("Title", "")
    year_match = re.search(r'منتهی به\s+(\d{4})', title)
    financial_year = year_match.group(1) if year_match else None
    
    return {
        "symbol": symbol,
        "tracing_no": letter.get("TracingNo"),
        "title": title,
        "letter_code": letter_code,
        "report_type": get_report_type(letter_code),
        "sent_date": letter.get("SentDateTime"),
        "publish_date": letter.get("PublishDateTime"),
        "has_pdf": 1 if letter.get("HasPdf") else 0,
        "has_attachment": 1 if letter.get("HasAttachment") else 0,
        "pdf_url": build_full_url(letter.get("PdfUrl")),
        "attachment_url": build_full_url(letter.get("AttachmentUrl")),
        "financial_year": financial_year,
        "is_new": 1,
        "seen": 0
    }

def save_report_to_db(report_data):
    """ذخیره گزارش در دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO codal_reports (
                symbol, tracing_no, title, letter_code, report_type,
                sent_date, publish_date, has_pdf, has_attachment,
                pdf_url, attachment_url, financial_year,
                is_new, seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_data["symbol"],
            report_data["tracing_no"],
            report_data["title"],
            report_data["letter_code"],
            report_data["report_type"],
            report_data["sent_date"],
            report_data["publish_date"],
            report_data["has_pdf"],
            report_data["has_attachment"],
            report_data["pdf_url"],
            report_data["attachment_url"],
            report_data["financial_year"],
            1,  # is_new
            0   # seen
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False

def check_symbol(symbol):
    """بررسی یک نماد برای گزارش جدید"""
    result = {
        "symbol": symbol,
        "status": "no_change",
        "message": "",
        "report": None
    }
    
    try:
        # دریافت داده از کدال
        data = fetch_codal_data(symbol)
        if not data:
            result["status"] = "error"
            result["message"] = "خطا در دریافت داده"
            return result
        
        letters = data.get("Letters", [])
        if not letters:
            result["status"] = "no_report"
            result["message"] = "هیچ گزارشی یافت نشد"
            return result
        
        # آخرین گزارش از کدال
        latest_letter = letters[0]
        latest_report = parse_letter(symbol, latest_letter)
        
        # دریافت آخرین گزارش از دیتابیس
        last_db = get_latest_report_from_db(symbol)
        
        # اگر گزارشی در دیتابیس نیست → گزارش جدید است
        if not last_db:
            result["status"] = "new_report"
            result["message"] = "اولین گزارش"
            result["report"] = latest_report
            return result
        
        # مقایسه tracing_no
        if str(last_db["tracing_no"]) == str(latest_report["tracing_no"]):
            result["status"] = "no_change"
            result["message"] = "بدون تغییر"
            return result
        
        # مقایسه تاریخ
        if last_db["sent_date"] and latest_report["sent_date"]:
            last_num = int(last_db["sent_date"].replace('/', '').replace(' ', '')[:8])
            new_num = int(latest_report["sent_date"].replace('/', '').replace(' ', '')[:8])
            
            if new_num <= last_num:
                result["status"] = "no_change"
                result["message"] = "گزارش قدیمی‌تر"
                return result
        
        # گزارش جدید است
        result["status"] = "new_report"
        result["message"] = "گزارش جدید"
        result["report"] = latest_report
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
    
    return result

def check_all_symbols(symbols, max_workers=3):
    """بررسی همه نمادها به صورت موازی"""
    results = {
        "new_reports": [],
        "errors": [],
        "no_change": [],
        "no_report": [],
        "total": len(symbols)
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(check_symbol, symbol): symbol 
            for symbol in symbols
        }
        
        completed = 0
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            completed += 1
            
            try:
                result = future.result()
                status_text.text(f"🔄 در حال بررسی: {symbol} ({completed}/{len(symbols)})")
                progress_bar.progress(completed / len(symbols))
                
                if result["status"] == "new_report":
                    # ذخیره در دیتابیس
                    if result["report"] and save_report_to_db(result["report"]):
                        results["new_reports"].append(result)
                    else:
                        results["errors"].append(result)
                elif result["status"] == "error":
                    results["errors"].append(result)
                elif result["status"] == "no_change":
                    results["no_change"].append(result)
                else:
                    results["no_report"].append(result)
                    
            except Exception as e:
                results["errors"].append({
                    "symbol": symbol,
                    "status": "error",
                    "message": str(e)
                })
    
    progress_bar.empty()
    status_text.empty()
    
    return results

# ============================================================
# نمایش صفحه
# ============================================================

# هدر
st.markdown("""
<div class="header-box">
    <h1>🤖 بررسی خودکار کدال</h1>
    <p>بررسی همه نمادهای موجود در دیتابیس برای یافتن گزارش‌های جدید</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# دریافت نمادها از دیتابیس
# ============================================================
try:
    symbols_data = get_all_symbols_from_db()
    symbols = [s['symbol'] for s in symbols_data] if symbols_data else []
    
    if not symbols:
        st.warning("⚠️ هیچ نمادی در دیتابیس یافت نشد!")
        st.info("💡 لطفاً ابتدا نمادها را به دیتابیس اضافه کنید.")
        st.stop()
    
    # نمایش آمار
    st.info(f"📊 {len(symbols)} نماد در دیتابیس موجود است")
    
    # ============================================================
    # تنظیمات
    # ============================================================
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        max_workers = st.number_input(
            "تعداد بررسی همزمان",
            min_value=1,
            max_value=10,
            value=3,
            help="تعداد بیشتر = سرعت بیشتر"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 شروع بررسی همه نمادها"):
            st.session_state['run_check'] = True
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 بروزرسانی"):
            st.experimental_rerun()
    
    # ============================================================
    # اجرای بررسی
    # ============================================================
    if st.session_state.get('run_check', False):
        with st.spinner("در حال بررسی نمادها..."):
            results = check_all_symbols(symbols, max_workers=max_workers)
        
        # نمایش نتایج
        st.markdown("---")
        
        # کارت‌های آمار
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number green">{len(results['new_reports'])}</div>
                <div class="label">🆕 گزارش جدید</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number blue">{len(results['no_change'])}</div>
                <div class="label">📄 بدون تغییر</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number orange">{len(results['no_report'])}</div>
                <div class="label">📭 بدون گزارش</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="number red">{len(results['errors'])}</div>
                <div class="label">❌ خطا</div>
            </div>
            """, unsafe_allow_html=True)
        
        # نمایش گزارش‌های جدید
        if results['new_reports']:
            st.markdown("---")
            st.subheader(f"🎉 گزارش‌های جدید یافت شده ({len(results['new_reports'])})")
            
            for result in results['new_reports']:
                report = result['report']
                pdf_link = build_full_url(report.get("pdf_url"))
                attach_link = build_full_url(report.get("attachment_url"))
                
                pdf_btn = f'<a href="{pdf_link}" target="_blank" class="download-link download-link-pdf">📄 PDF</a>' if pdf_link else '—'
                attach_btn = f'<a href="{attach_link}" target="_blank" class="download-link download-link-attach">📎 پیوست</a>' if attach_link else '—'
                
                st.markdown(f"""
                <div class="new-report-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                <strong style="font-size: 1.1rem;">📌 {report.get('symbol')}</strong>
                                <span class="badge-new">🆕 جدید</span>
                                <span style="color: #475569; font-size: 0.85rem;">{report.get('report_type', '')}</span>
                            </div>
                            <div style="margin-top: 0.3rem; font-size: 0.95rem;">{report.get('title', '')}</div>
                            <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.2rem;">
                                📅 {report.get('sent_date', '')}
                            </div>
                        </div>
                        <div style="display: flex; gap: 0.3rem; margin-top: 0.3rem;">
                            {pdf_btn} {attach_btn}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # نمایش خطاها
        if results['errors']:
            st.markdown("---")
            st.subheader(f"⚠️ خطاها ({len(results['errors'])})")
            for error in results['errors'][:10]:
                st.warning(f"**{error.get('symbol', '')}**: {error.get('message', '')}")
        
        # دکمه پاک کردن نتایج
        if st.button("🗑️ پاک کردن نتایج"):
            st.session_state['run_check'] = False
            st.experimental_rerun()
    
    else:
        st.info("👈 برای شروع بررسی، روی دکمه 'شروع بررسی همه نمادها' کلیک کنید.")
        
        # نمایش آخرین وضعیت
        st.markdown("---")
        st.subheader("📊 وضعیت فعلی")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM codal_reports")
        total_reports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM codal_reports WHERE is_new = 1")
        new_reports = cursor.fetchone()[0]
        
        conn.close()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 کل گزارشات ذخیره شده", total_reports)
        with col2:
            st.metric("🆕 گزارش‌های جدید", new_reports)

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
    🤖 بررسی خودکار کدال • آخرین بروزرسانی: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)