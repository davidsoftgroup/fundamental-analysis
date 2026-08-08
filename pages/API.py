# pages/99_تحلیل_بنیادی_مثل_فایل6.py
# -*- coding: utf-8 -*-

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import json
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.styles import apply_styles
apply_styles()

# =====================================================
# =============== استایل‌های جدول (مثل فایل 6) ========
# =====================================================

st.markdown("""
<style>
    .main .block-container { direction: rtl; padding-top: 1.2rem; }
    .stTable, table { direction: rtl; text-align: center; }
    h1 { font-size: 1.6rem !important; }
    h2, h3 { font-size: 1.2rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 تحلیل بنیادی از API")
st.markdown("---")

# =====================================================
# =============== توابع کمکی ==========================
# =====================================================

PERSIAN_DIGITS = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', 
                  '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}

def to_persian_number(num):
    """تبدیل عدد به فارسی"""
    if num is None or num == "" or (isinstance(num, float) and num != num):
        return "—"
    try:
        if isinstance(num, float):
            if num == int(num):
                num_str = f"{int(num):,}"
            else:
                num_str = f"{num:,.2f}"
        else:
            num_str = f"{int(num):,}"
        
        for en, fa in PERSIAN_DIGITS.items():
            num_str = num_str.replace(en, fa)
        return num_str
    except:
        return str(num)

def fmt(v):
    """فرمت اعداد"""
    if v is None:
        return "—"
    try:
        return f"{float(v):,.0f}"
    except Exception:
        return "—"

def fmt_market_value(v):
    """
    تبدیل ارزش بازار به میلیارد تومان
    مقدار ورودی از API به ریال است
    هر میلیارد تومان = 10,000,000,000 ریال
    """
    if v is None:
        return "—"
    try:
        # تبدیل ریال به میلیارد تومان
        value_billion = float(v) / 10_000_000_000
        # فرمت با یک رقم اعشار
        return f"{value_billion:,.1f}"
    except Exception:
        return "—"

def fmt_market_value_persian(v):
    """ارزش بازار به میلیارد تومان با اعداد فارسی"""
    if v is None:
        return "—"
    try:
        value_billion = float(v) / 10_000_000_000
        # تبدیل به فارسی
        num_str = f"{value_billion:,.1f}"
        for en, fa in PERSIAN_DIGITS.items():
            num_str = num_str.replace(en, fa)
        return num_str
    except Exception:
        return "—"

def fmt_pct(v):
    """فرمت درصد"""
    if v is None:
        return "—"
    try:
        return f"{float(v)*100:.1f}%"
    except Exception:
        return "—"

def fmt_ratio(v):
    """فرمت نسبت"""
    if v is None:
        return "—"
    try:
        return f"{float(v):.2f}"
    except Exception:
        return "—"

def pe_color(pe):
    """رنگ شرطی P/E"""
    if pe is None:
        return "#6b7280"
    if pe < 5:
        return "#16a34a"   # سبز
    if pe <= 7:
        return "#ca8a04"   # زرد
    return "#dc2626"       # قرمز

def pe_label(pe):
    """برچسب P/E"""
    if pe is None:
        return "—"
    if pe < 5:
        return f"{pe:.2f} (مناسب)"
    if pe <= 7:
        return f"{pe:.2f} (متوسط)"
    return f"{pe:.2f} (بالا)"

def pe_html(pe):
    """نمایش رنگی P/E در HTML"""
    if pe is None:
        return "—"
    color = pe_color(pe)
    label = pe_label(pe)
    return f'<span style="color:{color}; font-weight:bold;">{label}</span>'

def fetch_data_from_api():
    """دریافت داده از API"""
    url = "https://api.brsapi.ir/Tsetmc/AllSymbols.php?key=B9a9DpJKnmEAbgXDVkzh3kL3f7EzVSsd&type=1"
    
    try:
        session = requests.Session()
        session.trust_env = False
        session.verify = False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
        }
        
        response = session.get(url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"خطا در دریافت داده: {e}")
        return None

# =====================================================
# =============== دکمه دریافت داده ====================
# =====================================================

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 دریافت داده از API"):
        with st.spinner("در حال دریافت داده..."):
            data = fetch_data_from_api()
            if data:
                st.session_state['analysis_data'] = data
                with open('analysis_cache.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                st.success(f"✅ {len(data)} نماد دریافت شد!")
                st.experimental_rerun()
            else:
                st.error("❌ دریافت داده ناموفق")

with col2:
    if st.button("📂 بارگذاری از کش"):
        try:
            with open('analysis_cache.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state['analysis_data'] = data
                st.success(f"✅ {len(data)} نماد از کش بارگذاری شد!")
                st.experimental_rerun()
        except FileNotFoundError:
            st.error("❌ فایل کش پیدا نشد")

st.markdown("---")

# =====================================================
# =============== نمایش جدول ==========================
# =====================================================

if 'analysis_data' in st.session_state:
    data = st.session_state['analysis_data']
    df = pd.DataFrame(data)
    
    # ===== آماده‌سازی داده برای جدول =====
    # گرفتن ۲۰ شرکت برتر بر اساس ارزش بازار
    if 'mv' in df.columns:
        top_companies = df.nlargest(100, 'mv')
    else:
        top_companies = df.head(100)
    
    rows_data = []
    for _, row in top_companies.iterrows():
        rows_data.append({
            "نماد": row.get('l18', '—'),
            "نام": row.get('l30', '—'),
            "ارزش بازار (میلیارد تومان)": row.get('mv'),
            "قیمت": row.get('pc'),
            "تغییر": row.get('plp'),
            "P/E": row.get('pe'),
            "EPS": row.get('eps'),
            "حجم": row.get('tvol'),
        })
    
    df_table = pd.DataFrame(rows_data)
    
    # ===== ساخت HTML جدول =====
    st.subheader("📋 جدول تحلیل بنیادی")
    st.caption("💰 ارزش بازار بر اساس **میلیارد تومان** محاسبه شده است.")
    
    html = """
    <table style="width:100%; border-collapse:collapse; direction:rtl; text-align:center; font-size:13px;">
    <thead>
    <tr style="background:#1e3a5f; color:white;">
        <th style="padding:8px; border:1px solid #ccc;">ردیف</th>
        <th style="padding:8px; border:1px solid #ccc;">نماد</th>
        <th style="padding:8px; border:1px solid #ccc;">نام شرکت</th>
        <th style="padding:8px; border:1px solid #ccc;">ارزش بازار<br>(میلیارد تومان)</th>
        <th style="padding:8px; border:1px solid #ccc;">قیمت</th>
        <th style="padding:8px; border:1px solid #ccc;">تغییر %</th>
        <th style="padding:8px; border:1px solid #ccc;">P/E</th>
        <th style="padding:8px; border:1px solid #ccc;">EPS</th>
        <th style="padding:8px; border:1px solid #ccc;">حجم معاملات</th>
    </tr>
    </thead>
    <tbody>
    """
    
    for i, (_, row) in enumerate(df_table.iterrows(), 1):
        bg = "#f8fafc" if i % 2 == 0 else "#ffffff"
        
        # تغییرات با رنگ
        change = row["تغییر"]
        if change is not None and change > 0:
            change_display = f'<span style="color:#16a34a; font-weight:bold;">+{fmt(change)}%</span>'
        elif change is not None and change < 0:
            change_display = f'<span style="color:#dc2626; font-weight:bold;">{fmt(change)}%</span>'
        else:
            change_display = fmt(change)
        
        # P/E با رنگ
        pe_cell = pe_html(row["P/E"])
        
        # ارزش بازار به میلیارد تومان با اعداد فارسی
        market_value_display = fmt_market_value_persian(row["ارزش بازار (میلیارد تومان)"])
        
        html += f"""
    <tr style="background:{bg};">
        <td style="padding:7px; border:1px solid #ddd; font-weight:bold; color:#1e3a5f;">{to_persian_number(i)}</td>
        <td style="padding:7px; border:1px solid #ddd; font-weight:bold;">{row['نماد']}</td>
        <td style="padding:7px; border:1px solid #ddd; text-align:right; padding-right:14px;">{row['نام']}</td>
        <td style="padding:7px; border:1px solid #ddd; font-weight:bold; color:#1e3a5f;">{market_value_display}</td>
        <td style="padding:7px; border:1px solid #ddd;">{fmt(row['قیمت'])}</td>
        <td style="padding:7px; border:1px solid #ddd;">{change_display}</td>
        <td style="padding:7px; border:1px solid #ddd;">{pe_cell}</td>
        <td style="padding:7px; border:1px solid #ddd;">{fmt(row['EPS'])}</td>
        <td style="padding:7px; border:1px solid #ddd;">{fmt(row['حجم'])}</td>
    </tr>
    """
    
    html += """
    </tbody>
    </table>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    st.caption("P/E: 🟢 مناسب < ۵  |  🟡 متوسط ۵ تا ۷  |  🔴 بالا > ۷")
    
    # ===== دانلود =====
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود CSV",
        data=csv,
        file_name="fundamental_analysis.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # ===== نمودارها =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 توزیع P/E")
        if 'pe' in df.columns and not df.empty:
            pe_clean = df[(df['pe'] > 0) & (df['pe'] < 50)]['pe'].dropna()
            if not pe_clean.empty:
                fig = px.histogram(
                    pe_clean, 
                    nbins=30,
                    title='توزیع نسبت P/E (مقادیر مثبت)',
                    labels={'pe': 'نسبت P/E', 'count': 'تعداد نمادها'},
                    color_discrete_sequence=['#667eea']
                )
                fig.add_vline(x=5, line_dash="dash", line_color="#16a34a", annotation_text="مناسب")
                fig.add_vline(x=7, line_dash="dash", line_color="#ca8a04", annotation_text="متوسط")
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig)
    
    with col2:
        st.subheader("📊 ۱۰ شرکت برتر ارزش بازار")
        if 'mv' in df.columns and not df.empty:
            # تبدیل به میلیارد تومان برای نمودار
            df_chart = df.copy()
            df_chart['mv_billion'] = df_chart['mv'] / 10_000_000_000
            
            top_mv = df_chart.nlargest(10, 'mv_billion')
            fig = px.bar(
                top_mv,
                x='l18' if 'l18' in top_mv.columns else top_mv.index,
                y='mv_billion',
                title='۱۰ شرکت برتر از نظر ارزش بازار (میلیارد تومان)',
                labels={'x': 'نماد', 'y': 'ارزش بازار (میلیارد تومان)'},
                color='mv_billion',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig)

else:
    st.info("👈 برای شروع، روی دکمه 'دریافت داده از API' کلیک کنید.")

st.markdown("---")
st.caption("© ۱۴۰۴ - تحلیل بنیادی | توسعه‌یافته با Streamlit")