# -*- coding: utf-8 -*-
"""
صفحه نمایش اطلاعات کدال و ذخیره در دیتابیس
نام فایل: pages/05_codal.py
"""

import streamlit as st
import sys
import os
import json
import requests
import pandas as pd
import re
import time
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(
    page_title="اطلاعات کدال", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# اضافه کردن مسیر اصلی برای دسترسی به ماژول‌ها
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.styles import apply_styles
apply_styles()

# اضافه کردن برای دسترسی به دیتابیس
from utils.database import get_connection, get_all_symbols_from_db

# ============================================================
# دیکشنری کدهای گزارش
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

# ============================================================
# استایل اختصاصی صفحه کدال
# ============================================================
st.markdown("""
<style>
    .main .block-container { 
        direction: rtl; 
        padding-top: 1.2rem; 
        max-width: 1200px; 
    }
    
    .codal-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .codal-header h1 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem;
    }
    
    .codal-header p {
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
    }
    
    .stat-card .number {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
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
    
    .stButton button {
        width: 100%;
        background-color: #0f172a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .stButton button:hover {
        background-color: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    
    .retry-container {
        background: #fef3c7;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
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
    
    .stSelectbox > div > div {
        background-color: white !important;
    }
    
    .stSelectbox label {
        font-weight: 600 !important;
        color: #0f172a !important;
    }
    
    .stSelectbox {
        margin-bottom: 0.5rem;
    }
    
    .stNumberInput input {
        text-align: center !important;
    }
    
    .save-success {
        background: #dcfce7;
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .status-saved {
        color: #16a34a;
        font-weight: bold;
    }
    
    .status-not-saved {
        color: #dc2626;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# توابع اصلی
# ============================================================

def get_report_type_description(letter_code):
    """دریافت توضیحات نوع گزارش بر اساس کد"""
    return REPORT_TYPES.get(letter_code, letter_code)

def get_report_types_for_select():
    """ایجاد لیست گزینه‌های کمبوباکس با فرمت "کد - توضیحات" """
    options = ["همه"]
    for code, desc in REPORT_TYPES.items():
        options.append(f"{code} - {desc}")
    return options

def get_code_from_display(display_text):
    """استخراج کد از متن نمایشی کمبوباکس"""
    if display_text == "همه":
        return None
    if " - " in display_text:
        return display_text.split(" - ")[0]
    return display_text

def fetch_codal_data(symbol, page_number=1, letter_code=None, letter_type=None, max_retries=3):
    """دریافت داده‌های کدال برای یک نماد خاص با قابلیت تکرار مجدد"""
    base_url = "https://search.codal.ir/api/search/v2/q"
    
    params = {
        "Symbol": symbol,
        "PageNumber": page_number,
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
    
    if letter_code:
        params["LetterCode"] = letter_code
    
    if letter_type:
        params["LetterType"] = letter_type
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                base_url, 
                params=params, 
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏳ زمان پاسخ‌دهی طولانی شد. تلاش مجدد {attempt + 2} از {max_retries}...")
                time.sleep(2)
                continue
            else:
                st.error("❌ زمان پاسخ‌دهی سرور کدال بیش از حد طول کشید. لطفاً بعداً تلاش کنید.")
                return None
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                st.warning(f"🔄 مشکل در اتصال به سرور. تلاش مجدد {attempt + 2} از {max_retries}...")
                time.sleep(3)
                continue
            else:
                st.error("❌ مشکل در اتصال به سرور کدال. لطفاً اتصال اینترنت خود را بررسی کنید.")
                return None
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                st.warning(f"⚠️ خطا: {str(e)}. تلاش مجدد...")
                time.sleep(2)
                continue
            else:
                st.error(f"❌ خطا در دریافت داده: {e}")
                return None
    
    return None

def parse_codal_response(json_data):
    """پردازش پاسخ JSON از API کدال با مرتب‌سازی بر اساس تاریخ"""
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    result = {
        "total_count": data.get("Total", 0),
        "page": data.get("Page", 1),
        "letters": [],
        "company_name": "",
        "symbol": "",
        "summary": {}
    }
    
    letters = data.get("Letters", [])
    
    if not letters:
        return result
    
    first_letter = letters[0]
    result["company_name"] = first_letter.get("CompanyName", "")
    result["symbol"] = first_letter.get("Symbol", "")
    
    for letter in letters:
        letter_code = letter.get("LetterCode", "")
        letter_info = {
            "tracing_no": letter.get("TracingNo"),
            "symbol": letter.get("Symbol"),
            "company_name": letter.get("CompanyName"),
            "title": letter.get("Title"),
            "letter_code": letter_code,
            "report_type": get_report_type_description(letter_code),
            "sent_date": letter.get("SentDateTime"),
            "publish_date": letter.get("PublishDateTime"),
            "has_html": letter.get("HasHtml", False),
            "has_pdf": letter.get("HasPdf", False),
            "has_excel": letter.get("HasExcel", False),
            "has_attachment": letter.get("HasAttachment", False),
            "is_estimate": letter.get("IsEstimate", False),
            "url": letter.get("Url"),
            "pdf_url": letter.get("PdfUrl"),
            "attachment_url": letter.get("AttachmentUrl"),
            "tedan_url": letter.get("TedanUrl", ""),
            "under_supervision": letter.get("UnderSupervision", 0)
        }
        
        year_match = re.search(r'منتهی به\s+(\d{4})', letter_info["title"])
        if year_match:
            letter_info["financial_year"] = year_match.group(1)
        else:
            letter_info["financial_year"] = None
        
        period_match = re.search(r'دوره\s+(\d+)\s+ماهه', letter_info["title"])
        if period_match:
            letter_info["period_months"] = int(period_match.group(1))
        else:
            letter_info["period_months"] = None
        
        try:
            date_str = letter_info["sent_date"]
            if date_str and len(date_str) >= 10:
                if ' ' in date_str:
                    date_part = date_str.split()[0]
                else:
                    date_part = date_str
                
                parts = date_part.split('/')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    letter_info["sort_date"] = (year * 10000) + (month * 100) + day
                else:
                    letter_info["sort_date"] = 0
            else:
                letter_info["sort_date"] = 0
        except Exception as e:
            letter_info["sort_date"] = 0
        
        result["letters"].append(letter_info)
    
    result["letters"] = sorted(result["letters"], key=lambda x: x.get("sort_date", 0), reverse=True)
    
    result["summary"] = {
        "total_letters": len(letters),
        "company": result["company_name"],
        "symbol": result["symbol"],
        "years": sorted(set([l.get("financial_year") for l in result["letters"] if l.get("financial_year")])),
        "report_types": list(set([l.get("report_type") for l in result["letters"]])),
        "has_pdf": any([l.get("has_pdf") for l in result["letters"]]),
        "has_attachment": any([l.get("has_attachment") for l in result["letters"]]),
        "has_excel": any([l.get("has_excel") for l in result["letters"]]),
    }
    
    return result

def build_full_url(url):
    """ساخت لینک کامل برای دانلود فایل‌های کدال"""
    if not url:
        return None
    if url.startswith('http'):
        return url
    if url.startswith('/'):
        return f"https://www.codal.ir{url}"
    return f"https://www.codal.ir/{url}"

# ============================================================
# توابع مربوط به دیتابیس
# ============================================================

def get_symbols_from_db():
    """دریافت لیست نمادها از دیتابیس"""
    try:
        symbols = get_all_symbols_from_db()
        if symbols:
            return [s['symbol'] for s in symbols]
        return []
    except Exception as e:
        print(f"خطا در دریافت نمادها: {e}")
        return []

def check_report_saved(tracing_no):
    """بررسی اینکه آیا یک گزارش قبلاً ذخیره شده است یا خیر"""
    if not tracing_no:
        return False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tracing_str = str(tracing_no).strip()
        
        # روش‌های مختلف برای تطابق
        cursor.execute("SELECT id FROM codal_reports WHERE tracing_no = ?", (tracing_str,))
        if cursor.fetchone():
            conn.close()
            return True
        
        cursor.execute("SELECT id FROM codal_reports WHERE tracing_no LIKE ?", (f"%{tracing_str}%",))
        if cursor.fetchone():
            conn.close()
            return True
        
        if tracing_str.isdigit():
            cursor.execute("SELECT id FROM codal_reports WHERE CAST(tracing_no AS INTEGER) = ?", (int(tracing_str),))
            if cursor.fetchone():
                conn.close()
                return True
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"Error in check_report_saved: {e}")
        return False

def save_report_to_db(letter_info):
    """ذخیره یک گزارش در دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tracing_no = str(letter_info.get("tracing_no", "")).strip()
        
        # بررسی تکراری نبودن
        cursor.execute("SELECT id FROM codal_reports WHERE tracing_no = ?", (tracing_no,))
        if cursor.fetchone():
            conn.close()
            return False, "گزارش قبلاً ذخیره شده است"
        
        # ذخیره گزارش
        cursor.execute("""
            INSERT INTO codal_reports (
                symbol, tracing_no, title, letter_code, report_type,
                sent_date, publish_date, has_pdf, has_attachment,
                pdf_url, attachment_url, financial_year, period_months,
                is_new, seen
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            letter_info.get("symbol"),
            tracing_no,
            letter_info.get("title"),
            letter_info.get("letter_code"),
            letter_info.get("report_type"),
            letter_info.get("sent_date"),
            letter_info.get("publish_date"),
            1 if letter_info.get("has_pdf") else 0,
            1 if letter_info.get("has_attachment") else 0,
            letter_info.get("pdf_url"),
            letter_info.get("attachment_url"),
            letter_info.get("financial_year"),
            letter_info.get("period_months"),
            1,  # is_new
            0   # seen
        ))
        
        conn.commit()
        conn.close()
        return True, "گزارش با موفقیت ذخیره شد"
        
    except Exception as e:
        return False, f"خطا در ذخیره: {str(e)}"

def save_all_reports(letters, symbol):
    """ذخیره همه گزارش‌های یک نماد"""
    saved_count = 0
    skipped_count = 0
    errors = []
    
    for letter in letters:
        success, message = save_report_to_db(letter)
        if success:
            saved_count += 1
        elif "قبلاً ذخیره شده" in message:
            skipped_count += 1
        else:
            errors.append(message)
    
    return {
        "saved": saved_count,
        "skipped": skipped_count,
        "errors": errors
    }

def display_reports_table(letters):
    """نمایش جدول کامل گزارش‌ها با لینک‌های دانلود و وضعیت ذخیره"""
    if not letters:
        st.info("هیچ گزارشی برای نمایش وجود ندارد.")
        return
    
    table_data = []
    for letter in letters:
        pdf_link = build_full_url(letter.get("pdf_url"))
        attach_link = build_full_url(letter.get("attachment_url"))
        
        pdf_btn = f'<a href="{pdf_link}" target="_blank" class="download-link download-link-pdf">📄 PDF</a>' if pdf_link and letter.get("has_pdf") else '—'
        attach_btn = f'<a href="{attach_link}" target="_blank" class="download-link download-link-attach">📎 پیوست</a>' if attach_link and letter.get("has_attachment") else '—'
        
        sent_date = letter.get("sent_date", "—")
        if sent_date != "—" and len(sent_date) > 16:
            sent_date = sent_date[:16]
        
        title = letter.get("title", "—")
        if len(title) > 80:
            title = title[:80] + "..."
        
        report_type_display = letter.get("report_type", letter.get("letter_code", "—"))
        
        tracing_no = letter.get("tracing_no")
        if tracing_no:
            saved = check_report_saved(tracing_no)
            saved_status = "✅" if saved else "❌"
        else:
            saved_status = "—"
        
        download_links = f"{pdf_btn} {attach_btn}".strip()
        if download_links == "" or download_links == "— —":
            download_links = "—"
        
        table_data.append({
            "نوع گزارش": report_type_display,
            "عنوان": title,
            "تاریخ ارسال": sent_date,
            "ذخیره": saved_status,
            "دانلود": download_links
        })
    
    df_table = pd.DataFrame(table_data)
    
    html_table = df_table.to_html(
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

# ============================================================
# نمایش صفحه
# ============================================================

# هدر صفحه
st.markdown("""
<div class="codal-header">
    <h1>📊 سامانه اطلاع‌رسانی کدال</h1>
    <p>دریافت و نمایش گزارش‌های مالی شرکت‌های بورس ایران</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# بخش جستجو
# ============================================================
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.subheader("🔍 جستجوی اطلاعات")

# دریافت لیست نمادها از دیتابیس
symbols_list = get_symbols_from_db()

col1, col2, col3, col4 = st.columns([1.2, 1.8, 1.5, 0.8])

with col1:
    if symbols_list:
        selected_symbol = st.selectbox(
            "انتخاب نماد از دیتابیس",
            options=[""] + symbols_list,
            index=0,
            help="نمادهای موجود در دیتابیس"
        )
        
        if selected_symbol:
            symbol_value = selected_symbol
        else:
            symbol_value = "شسپا"
    else:
        symbol_value = "شسپا"
        st.info("ℹ️ هیچ نمادی در دیتابیس یافت نشد. می‌توانید دستی وارد کنید.")

with col2:
    symbol = st.text_input(
        "نماد (دستی)", 
        value=symbol_value, 
        placeholder="مثال: شسپا",
        help="می‌توانید دستی وارد کنید یا از لیست انتخاب کنید"
    )

with col3:
    report_options = get_report_types_for_select()
    selected_report_display = st.selectbox(
        "نوع گزارش",
        options=report_options,
        index=0,
        help="نوع گزارش مورد نظر را انتخاب کنید"
    )
    selected_letter_code = get_code_from_display(selected_report_display)

with col4:
    page_number = st.number_input(
        "صفحه", 
        min_value=1, 
        value=1, 
        step=1,
        help="شماره صفحه نتایج"
    )

search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
with search_col2:
    search_button = st.button("🔍 دریافت اطلاعات")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# نمایش نتایج
# ============================================================

if search_button:
    if not symbol:
        st.warning("⚠️ لطفاً نماد شرکت را وارد کنید.")
    else:
        status_placeholder = st.empty()
        status_placeholder.info(f"🔄 در حال دریافت اطلاعات از کدال برای نماد {symbol}...")
        
        data = fetch_codal_data(symbol, page_number, selected_letter_code)
        
        if data:
            result = parse_codal_response(data)
            
            if result["letters"]:
                status_placeholder.empty()
                
                st.success(f"✅ اطلاعات با موفقیت دریافت شد. تعداد گزارش‌ها: {result['total_count']}")
                
                # کارت‌های آمار
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="number">{result['total_count']}</div>
                        <div class="label">📄 تعداد کل</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="number">{len(result['summary']['years'])}</div>
                        <div class="label">📅 سال مالی</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="number">{len(result['summary']['report_types'])}</div>
                        <div class="label">📋 نوع گزارش</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    pdf_count = sum(1 for l in result["letters"] if l.get("has_pdf"))
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="number">{pdf_count}</div>
                        <div class="label">📄 PDF</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    attach_count = sum(1 for l in result["letters"] if l.get("has_attachment"))
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="number">{attach_count}</div>
                        <div class="label">📎 پیوست</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # اطلاعات شرکت
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🏢 شرکت:** {result['company_name']}")
                with col2:
                    st.markdown(f"**📌 نماد:** {result['symbol']}")
                
                if result["summary"]["years"]:
                    st.markdown(f"**📅 سال‌های موجود:** {', '.join(result['summary']['years'])}")
                
                # ============================================================
                # دکمه ذخیره همه گزارش‌ها
                # ============================================================
                st.markdown("---")
                
                save_col1, save_col2, save_col3 = st.columns([1, 2, 1])
                with save_col2:
                    if st.button("💾 ذخیره همه گزارش‌ها در دیتابیس"):
                        with st.spinner(f"در حال ذخیره {len(result['letters'])} گزارش..."):
                            save_result = save_all_reports(result["letters"], symbol)
                            
                            if save_result["saved"] > 0:
                                st.markdown(f"""
                                <div class="save-success">
                                    ✅ {save_result['saved']} گزارش با موفقیت ذخیره شد
                                    {f'<br>⏭️ {save_result["skipped"]} گزارش قبلاً ذخیره شده بودند' if save_result["skipped"] > 0 else ''}
                                    {f'<br>⚠️ {len(save_result["errors"])} خطا' if save_result["errors"] else ''}
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                st.experimental_rerun()
                            else:
                                st.warning("هیچ گزارش جدیدی برای ذخیره وجود نداشت")
                
                # ============================================================
                # جدول کامل گزارش‌ها
                # ============================================================
                st.markdown("---")
                st.subheader("📋 لیست گزارش‌ها (جدیدترین اول)")
                
                years = result["summary"]["years"]
                if years:
                    selected_year = st.selectbox(
                        "فیلتر بر اساس سال",
                        options=["همه"] + years,
                        index=0,
                        key="year_filter"
                    )
                else:
                    selected_year = "همه"
                
                filtered_letters = result["letters"]
                if selected_year != "همه":
                    filtered_letters = [l for l in filtered_letters if l.get("financial_year") == selected_year]
                
                display_reports_table(filtered_letters)
                
            else:
                status_placeholder.empty()
                st.warning(f"⚠️ هیچ داده‌ای برای نماد '{symbol}' یافت نشد.")
        else:
            status_placeholder.empty()
            st.markdown("""
            <div class="retry-container">
                <strong>💡 نکات برای رفع خطا:</strong>
                <ul>
                    <li>⏳ ممکن است سرور کدال شلوغ باشد. چند لحظه بعد دوباره تلاش کنید.</li>
                    <li>🔍 مطمئن شوید که نماد شرکت را درست وارد کرده‌اید (مثال: شسپا، فولاد، وغدیر).</li>
                    <li>🌐 اتصال اینترنت خود را بررسی کنید.</li>
                    <li>📱 اگر از VPN استفاده می‌کنید، ممکن است لازم باشد آن را غیرفعال کنید.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            retry_col1, retry_col2, retry_col3 = st.columns([1, 2, 1])
            with retry_col2:
                if st.button("🔄 تلاش مجدد"):
                    st.experimental_rerun()

else:
    st.info("👈 لطفاً نماد شرکت مورد نظر را وارد کرده و دکمه 'دریافت اطلاعات' را کلیک کنید.")
    
    if symbols_list:
        st.info(f"📊 {len(symbols_list)} نماد در دیتابیس موجود است. از لیست کشویی انتخاب کنید.")

# ============================================================
# فوتر صفحه
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; font-size: 14px; color: #94a3b8;">
    📊 داده‌ها از <strong>سامانه اطلاع‌رسانی کدال</strong> دریافت می‌شوند
</div>
""", unsafe_allow_html=True)