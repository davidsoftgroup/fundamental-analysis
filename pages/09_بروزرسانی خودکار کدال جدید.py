# -*- coding: utf-8 -*-
"""
بررسی خودکار گزارش‌های جدید کدال برای همه نمادها
نسخه جمع‌وجور با نمایش خلاصه وضعیت
"""

import streamlit as st
import sys
import os
import pandas as pd
import requests
import time
import re
import random
from datetime import datetime, timedelta
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
# تنظیمات مدیریت درخواست
# ============================================================
REQUEST_CONFIG = {
    "min_delay": 1.5,          
    "max_delay": 3.0,          
    "max_workers": 2,          
    "max_retries": 3,          
    "timeout": 20,             
    "batch_size": 10,          
    "batch_delay": 5.0,        
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

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
    .stat-card .number.green { color: #22c55e; }
    .stat-card .number.red { color: #ef4444; }
    .stat-card .number.orange { color: #f59e0b; }
    .stat-card .number.blue { color: #3b82f6; }
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
    .download-link-pdf { background: #dc2626; }
    .download-link-pdf:hover { background: #b91c1c; }
    .download-link-attach { background: #2563eb; }
    .download-link-attach:hover { background: #1d4ed8; }
    
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
    
    .info-box {
        background: #dbeafe;
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .warning-box {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .status-container {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        direction: rtl;
    }
    
    .status-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.5rem;
        text-align: center;
    }
    .status-item {
        padding: 0.3rem;
        border-radius: 6px;
        background: white;
    }
    .status-item .num {
        font-size: 1.5rem;
        font-weight: 700;
    }
    .status-item .lbl {
        font-size: 0.7rem;
        color: #64748b;
    }
    .status-item .num.green { color: #22c55e; }
    .status-item .num.red { color: #ef4444; }
    .status-item .num.blue { color: #3b82f6; }
    .status-item .num.orange { color: #f59e0b; }
    .status-item .num.purple { color: #8b5cf6; }
    
    .progress-container {
        margin: 0.5rem 0;
    }
    
    .live-status {
        font-size: 0.9rem;
        color: #64748b;
        text-align: center;
        padding: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# کلاس مدیریت درخواست
# ============================================================
class RequestManager:
    def __init__(self):
        self.last_request_time = 0
        self.request_count = 0
        self.user_agents = USER_AGENTS.copy()
        self.failed_requests = 0
        self.max_failures = 5
    
    def get_user_agent(self):
        return random.choice(self.user_agents)
    
    def wait_if_needed(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        delay = random.uniform(REQUEST_CONFIG["min_delay"], REQUEST_CONFIG["max_delay"])
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def is_blocked(self):
        return self.failed_requests >= self.max_failures
    
    def reset_failures(self):
        self.failed_requests = 0

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

def fetch_codal_data(symbol, request_manager, max_retries=None):
    if max_retries is None:
        max_retries = REQUEST_CONFIG["max_retries"]
    
    if request_manager.is_blocked():
        return None
    
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
        'User-Agent': request_manager.get_user_agent(),
        'Accept': 'application/json',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'
    }
    
    for attempt in range(max_retries):
        try:
            request_manager.wait_if_needed()
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_CONFIG["timeout"])
            
            if response.status_code == 429 or response.status_code == 403:
                request_manager.failed_requests += 1
                wait_time = 10 + (attempt * 5)
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            request_manager.reset_failures()
            return response.json()
            
        except requests.exceptions.Timeout:
            time.sleep(2)
            continue
        except requests.exceptions.RequestException:
            request_manager.failed_requests += 1
            time.sleep(3)
            continue
    
    return None

def get_latest_report_from_db(symbol):
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
    except Exception:
        return None

def parse_letter(symbol, letter):
    letter_code = letter.get("LetterCode", "")
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
            1,
            0
        ))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def check_symbol(symbol, request_manager):
    result = {
        "symbol": symbol,
        "status": "no_change",
        "message": "",
        "report": None
    }
    
    try:
        data = fetch_codal_data(symbol, request_manager)
        
        if request_manager.is_blocked():
            result["status"] = "error"
            result["message"] = "IP مسدود شده"
            return result
        
        if not data:
            result["status"] = "error"
            result["message"] = "خطا در دریافت"
            return result
        
        letters = data.get("Letters", [])
        if not letters:
            result["status"] = "no_report"
            result["message"] = "بدون گزارش"
            return result
        
        latest_letter = letters[0]
        latest_report = parse_letter(symbol, latest_letter)
        last_db = get_latest_report_from_db(symbol)
        
        if not last_db:
            result["status"] = "new_report"
            result["message"] = "اولین گزارش"
            result["report"] = latest_report
            return result
        
        if str(last_db["tracing_no"]) == str(latest_report["tracing_no"]):
            result["status"] = "no_change"
            result["message"] = "بدون تغییر"
            return result
        
        if last_db["sent_date"] and latest_report["sent_date"]:
            try:
                last_num = int(last_db["sent_date"].replace('/', '').replace(' ', '')[:8])
                new_num = int(latest_report["sent_date"].replace('/', '').replace(' ', '')[:8])
                if new_num <= last_num:
                    result["status"] = "no_change"
                    result["message"] = "گزارش قدیمی‌تر"
                    return result
            except:
                pass
        
        result["status"] = "new_report"
        result["message"] = "گزارش جدید"
        result["report"] = latest_report
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)[:30]
    
    return result

def check_all_symbols(symbols, max_workers=2):
    """بررسی همه نمادها با نمایش خلاصه"""
    
    # placeholderها برای نمایش وضعیت
    status_placeholder = st.empty()
    progress_placeholder = st.empty()
    result_placeholder = st.empty()
    
    results = {
        "new_reports": [],
        "errors": [],
        "no_change": [],
        "no_report": [],
        "total": len(symbols),
        "blocked": False,
        "current_symbol": "",
        "completed": 0
    }
    
    request_manager = RequestManager()
    
    # نمایش وضعیت اولیه
    status_placeholder.markdown("""
    <div class="status-container">
        <div class="status-grid">
            <div class="status-item"><div class="num blue">0</div><div class="lbl">📊 کل</div></div>
            <div class="status-item"><div class="num">0</div><div class="lbl">✅ بررسی</div></div>
            <div class="status-item"><div class="num green">0</div><div class="lbl">🆕 جدید</div></div>
            <div class="status-item"><div class="num">0</div><div class="lbl">📄 بدون تغییر</div></div>
            <div class="status-item"><div class="num orange">0</div><div class="lbl">📭 بدون گزارش</div></div>
            <div class="status-item"><div class="num red">0</div><div class="lbl">⚠️ خطا</div></div>
        </div>
        <div class="live-status">⏳ آماده شروع...</div>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = progress_placeholder.progress(0)
    
    # تقسیم به دسته‌ها
    batch_size = REQUEST_CONFIG["batch_size"]
    symbol_batches = [symbols[i:i+batch_size] for i in range(0, len(symbols), batch_size)]
    
    completed = 0
    total_symbols = len(symbols)
    
    for batch_idx, batch in enumerate(symbol_batches):
        if request_manager.is_blocked():
            results["blocked"] = True
            break
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(check_symbol, symbol, request_manager): symbol 
                for symbol in batch
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                results["completed"] = completed
                
                try:
                    result = future.result()
                    
                    progress = completed / total_symbols
                    progress_bar.progress(progress)
                    
                    if result["status"] == "new_report":
                        if result["report"] and save_report_to_db(result["report"]):
                            results["new_reports"].append(result)
                    elif result["status"] == "error":
                        results["errors"].append(result)
                    elif result["status"] == "no_change":
                        results["no_change"].append(result)
                    else:
                        results["no_report"].append(result)
                    
                    # به‌روزرسانی وضعیت
                    status_placeholder.markdown(f"""
                    <div class="status-container">
                        <div class="status-grid">
                            <div class="status-item"><div class="num blue">{total_symbols}</div><div class="lbl">📊 کل</div></div>
                            <div class="status-item"><div class="num">{completed}</div><div class="lbl">✅ بررسی</div></div>
                            <div class="status-item"><div class="num green">{len(results['new_reports'])}</div><div class="lbl">🆕 جدید</div></div>
                            <div class="status-item"><div class="num">{len(results['no_change'])}</div><div class="lbl">📄 بدون تغییر</div></div>
                            <div class="status-item"><div class="num orange">{len(results['no_report'])}</div><div class="lbl">📭 بدون گزارش</div></div>
                            <div class="status-item"><div class="num red">{len(results['errors'])}</div><div class="lbl">⚠️ خطا</div></div>
                        </div>
                        <div class="live-status">🔄 در حال بررسی: <strong>{symbol}</strong> ({int(progress*100)}%)</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    results["errors"].append({
                        "symbol": symbol,
                        "status": "error",
                        "message": str(e)[:30]
                    })
        
        if results.get("blocked", False):
            break
        
        if batch_idx < len(symbol_batches) - 1:
            time.sleep(REQUEST_CONFIG["batch_delay"])
    
    progress_bar.empty()
    
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
# دریافت نمادها
# ============================================================
try:
    symbols_data = get_all_symbols_from_db()
    symbols = [s['symbol'] for s in symbols_data] if symbols_data else []
    
    if not symbols:
        st.warning("⚠️ هیچ نمادی در دیتابیس یافت نشد!")
        st.info("💡 لطفاً ابتدا نمادها را به دیتابیس اضافه کنید.")
        st.stop()
    
    # ============================================================
    # تنظیمات
    # ============================================================
    st.markdown("""
    <div class="info-box">
        🛡️ <strong>حفاظت از IP:</strong> تاخیر {}-{} ثانیه بین درخواست‌ها برای جلوگیری از مسدود شدن
    </div>
    """.format(REQUEST_CONFIG["min_delay"], REQUEST_CONFIG["max_delay"]), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        max_workers = st.number_input(
            "تعداد بررسی همزمان",
            min_value=1,
            max_value=5,
            value=2
        )
    
    with col2:
        min_delay = st.number_input(
            "تاخیر (ثانیه)",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.5
        )
        REQUEST_CONFIG["min_delay"] = min_delay
        REQUEST_CONFIG["max_delay"] = min_delay + 1.0
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 شروع بررسی"):
            st.session_state['run_check'] = True
    
    st.info(f"📊 {len(symbols)} نماد در دیتابیس موجود است")
    st.caption(f"⏱️ زمان تقریبی: حدود {len(symbols) * REQUEST_CONFIG['min_delay'] / 60:.1f} دقیقه")
    
    # ============================================================
    # اجرای بررسی
    # ============================================================
    if st.session_state.get('run_check', False):
        results = check_all_symbols(symbols, max_workers=max_workers)
        
        # نمایش خلاصه نهایی
        st.markdown("---")
        st.subheader("📊 خلاصه نهایی")
        
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
            st.subheader(f"🎉 گزارش‌های جدید ({len(results['new_reports'])})")
            
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
                            <div style="margin-top: 0.3rem; font-size: 0.9rem;">{report.get('title', '')}</div>
                            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.2rem;">
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
            with st.expander(f"⚠️ {len(results['errors'])} خطا", expanded=False):
                for error in results['errors'][:10]:
                    st.warning(f"**{error.get('symbol', '')}**: {error.get('message', '')}")
                if len(results['errors']) > 10:
                    st.info(f"... و {len(results['errors']) - 10} خطای دیگر")
        
        # دکمه پاک کردن
        if st.button("🗑️ پاک کردن نتایج"):
            st.session_state['run_check'] = False
            st.experimental_rerun()
    
    else:
        st.info("👈 برای شروع، روی دکمه 'شروع بررسی' کلیک کنید.")
        
        # نمایش وضعیت فعلی
        st.markdown("---")
        st.subheader("📊 وضعیت فعلی دیتابیس")
        
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
    🤖 بررسی خودکار کدال • {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
</div>
""", unsafe_allow_html=True)