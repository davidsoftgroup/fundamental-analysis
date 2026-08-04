import streamlit as st
import sys
import os
import pandas as pd
import time
from utils.tsetmc import update_company_market_value
from utils.database import get_connection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="ورود اطلاعات شرکت", layout="wide")
from utils.styles import apply_styles
apply_styles()


st.markdown("""
<style>
    div[data-testid="stForm"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("ورود و مدیریت اطلاعات شرکت")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

def get_companies():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, symbol, name_fa, industry, market_value, rank_in_industry,
               fiscal_end_month, fiscal_end_day
        FROM companies
        ORDER BY symbol
    """).fetchall()
    conn.close()
    return rows

for key, val in {
    "edit_symbol": "",
    "edit_name": "",
    "edit_industry": "",
    "edit_market": 0.0,
    "edit_rank": 0,
    "edit_fiscal_month": 12,
    "edit_fiscal_day": 29,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.subheader("فرم ثبت و ویرایش شرکت")



with st.form("company_form"):
    col1, col2 = st.columns(2)

    with col1:
        symbol = st.text_input("نماد شرکت *", value=st.session_state.edit_symbol, placeholder="مثال: شپنا").strip().upper()
        name_fa = st.text_input("نام شرکت", value=st.session_state.edit_name, placeholder="پالایش نفت اصفهان")
        industry = st.text_input("صنعت", value=st.session_state.edit_industry, placeholder="فرآورده‌های نفتی")

    with col2:
        market_value = st.number_input("ارزش بازار (میلیارد ریال)", min_value=0.0, step=100.0, value=float(st.session_state.edit_market))
        rank = st.number_input("رتبه در صنعت", min_value=0, step=1, value=int(st.session_state.edit_rank))
        fiscal_end_month = st.number_input("ماه پایان سال مالی (۱ تا ۱۲)", min_value=1, max_value=12, value=int(st.session_state.edit_fiscal_month), step=1)
        fiscal_end_day = st.number_input("روز پایان سال مالی", min_value=1, max_value=31, value=int(st.session_state.edit_fiscal_day), step=1)

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        submitted = st.form_submit_button("ثبت / به‌روزرسانی")
    with col_btn2:
        delete_btn = st.form_submit_button("حذف شرکت")
    with col_btn3:
        clear_btn = st.form_submit_button("پاک کردن فرم")

    if submitted:
        if not symbol:
            st.error("نماد شرکت الزامی است.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE companies
                        SET name_fa=?, industry=?, market_value=?, rank_in_industry=?,
                            fiscal_end_month=?, fiscal_end_day=?
                        WHERE symbol=?
                    """, (name_fa, industry, market_value, rank, fiscal_end_month, fiscal_end_day, symbol))
                    st.success(f"اطلاعات شرکت «{symbol}» به‌روزرسانی شد.")
                else:
                    cursor.execute("""
                        INSERT INTO companies
                        (symbol, name_fa, industry, market_value, rank_in_industry, fiscal_end_month, fiscal_end_day)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (symbol, name_fa, industry, market_value, rank, fiscal_end_month, fiscal_end_day))
                    st.success(f"شرکت «{symbol}» با موفقیت ثبت شد.")

                conn.commit()
                conn.close()

                st.session_state.edit_symbol = ""
                st.session_state.edit_name = ""
                st.session_state.edit_industry = ""
                st.session_state.edit_market = 0.0
                st.session_state.edit_rank = 0
                st.session_state.edit_fiscal_month = 12
                st.session_state.edit_fiscal_day = 29
                st.experimental_rerun()
            except Exception as e:
                st.error(f"خطا در ثبت: {e}")

    if delete_btn:
        if not symbol:
            st.error("برای حذف، ابتدا نماد را وارد یا بارگذاری کنید.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM companies WHERE symbol = ?", (symbol,))
                conn.commit()
                conn.close()
                st.success(f"شرکت «{symbol}» حذف شد.")
                st.session_state.edit_symbol = ""
                st.session_state.edit_name = ""
                st.session_state.edit_industry = ""
                st.session_state.edit_market = 0.0
                st.session_state.edit_rank = 0
                st.session_state.edit_fiscal_month = 12
                st.session_state.edit_fiscal_day = 29
                st.experimental_rerun()
            except Exception as e:
                st.error(f"خطا در حذف: {e}")

    if clear_btn:
        st.session_state.edit_symbol = ""
        st.session_state.edit_name = ""
        st.session_state.edit_industry = ""
        st.session_state.edit_market = 0.0
        st.session_state.edit_rank = 0
        st.session_state.edit_fiscal_month = 12
        st.session_state.edit_fiscal_day = 29
        st.experimental_rerun()

st.markdown("---")
st.subheader("جستجو و لیست شرکت‌ها")
from utils.tsetmc import update_company_market_value, update_all_companies_market_value
import time

# ---------- به‌روزرسانی ارزش بازار ----------
st.markdown("---")

col_u1, col_u2 = st.columns(2)


with col_u1:
    if st.button("به‌روزرسانی همه نمادها"):
        try:
            with st.spinner("دریافت همه نمادها از API..."):
                ok, fail, details = update_all_companies_market_value(
                    get_connection, get_companies
                )
            st.success("موفق: **{}** | ناموفق: **{}**".format(ok, fail))
            if details:
                st.dataframe(details)
            st.experimental_rerun()
        except Exception as e:
            st.error(str(e))   



search_col1, search_col2 = st.columns([3, 1])
with search_col1:
    search_symbol = st.text_input("جستجوی نماد برای ویرایش:", placeholder="نماد را بنویسید", key="search_box").strip().upper()
with search_col2:
    st.write("")
    st.write("")
    load_btn = st.button("بارگذاری برای ویرایش")

rows = get_companies()

if load_btn:
    if not search_symbol:
        st.warning("لطفاً یک نماد وارد کنید.")
    else:
        found = False
        for row in rows:
            if row["symbol"] == search_symbol:
                st.session_state.edit_symbol = row["symbol"] or ""
                st.session_state.edit_name = row["name_fa"] or ""
                st.session_state.edit_industry = row["industry"] or ""
                st.session_state.edit_market = float(row["market_value"] or 0)
                st.session_state.edit_rank = int(row["rank_in_industry"] or 0)
                st.session_state.edit_fiscal_month = int(row["fiscal_end_month"] or 12)
                st.session_state.edit_fiscal_day = int(row["fiscal_end_day"] or 29)
                found = True
                st.success(f"اطلاعات شرکت «{search_symbol}» بارگذاری شد.")
                st.experimental_rerun()
                break
        if not found:
            st.error(f"شرکت با نماد «{search_symbol}» پیدا نشد.")

st.write("")

if rows:
    data = []
    for row in rows:
        month_name = MONTH_NAMES.get(row["fiscal_end_month"], "")
        fiscal = f"{row['fiscal_end_day'] or '—'} {month_name}"
        data.append({
            "شناسه": row["id"],
            "نماد": row["symbol"],
            "نام شرکت": row["name_fa"] or "—",
            "صنعت": row["industry"] or "—",
            "ارزش بازار": f"{row['market_value']:,.0f}" if row["market_value"] is not None else "—",
            "رتبه": row["rank_in_industry"] if row["rank_in_industry"] is not None else "—",
            "پایان سال مالی": fiscal,
        })
    st.table(pd.DataFrame(data))
else:
    st.info("هنوز هیچ شرکتی ثبت نشده است.")
    
    
    


