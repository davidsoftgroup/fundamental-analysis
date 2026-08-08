import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="فروش ماهانه", layout="wide")
from utils.styles import apply_styles
apply_styles()


st.markdown("""
<style>
    div[data-testid="stForm"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("ورود فروش ماهانه")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

def get_companies():
    conn = get_connection()
    rows = conn.execute("SELECT id, symbol, name_fa FROM companies ORDER BY symbol").fetchall()
    conn.close()
    return rows

def get_monthly_sales(company_id, year):
    conn = get_connection()
    rows = conn.execute("""
        SELECT month, domestic_sales, export_sales, total_sales
        FROM monthly_sales
        WHERE company_id = ? AND year_solar = ?
        ORDER BY month
    """, (company_id, year)).fetchall()
    conn.close()
    return {r["month"]: r for r in rows}

def save_month(company_id, year, month, domestic, export_sales):
    total = (domestic or 0) + (export_sales or 0)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM monthly_sales
        WHERE company_id=? AND year_solar=? AND month=?
    """, (company_id, year, month))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE monthly_sales
            SET domestic_sales=?, export_sales=?, total_sales=?
            WHERE company_id=? AND year_solar=? AND month=?
        """, (domestic, export_sales, total, company_id, year, month))
    else:
        cursor.execute("""
            INSERT INTO monthly_sales
            (company_id, year_solar, month, domestic_sales, export_sales, total_sales)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, year, month, domestic, export_sales, total))
    conn.commit()
    conn.close()

def delete_year(company_id, year):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monthly_sales WHERE company_id=? AND year_solar=?", (company_id, year))
    conn.commit()
    conn.close()

# ---------------- انتخاب شرکت و سال ----------------
companies = get_companies()

if not companies:
    st.warning("هنوز هیچ شرکتی ثبت نشده است.")
    st.stop()

company_options = {f"{c['symbol']} - {c['name_fa'] or ''}": c["id"] for c in companies}
selected_label = st.selectbox("انتخاب شرکت:", options=list(company_options.keys()))
company_id = company_options[selected_label]

year = st.number_input("سال شمسی:", min_value=1390, max_value=1410, value=1403, step=1)

st.markdown("---")

# ---------------- بارگذاری داده‌های موجود ----------------
existing = get_monthly_sales(company_id, year)

st.subheader(f"فروش ماهانه سال {year}")
st.caption("مقادیر را به میلیارد ریال وارد کنید. فروش کل = داخلی + صادراتی")

with st.form("monthly_form"):

    domestic_values = {}
    export_values = {}

    for m in range(1, 13):
        row_data = existing.get(m)
        def_dom = float(row_data["domestic_sales"] or 0) if row_data else 0.0
        def_exp = float(row_data["export_sales"] or 0) if row_data else 0.0

        st.markdown(f"**{MONTH_NAMES[m]}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            domestic_values[m] = st.number_input(
                f"فروش داخلی - {MONTH_NAMES[m]}",
                min_value=0.0, value=def_dom, step=10.0,
                key=f"dom_{m}"
            )
        with c2:
            export_values[m] = st.number_input(
                f"فروش صادراتی - {MONTH_NAMES[m]}",
                min_value=0.0, value=def_exp, step=10.0,
                key=f"exp_{m}"
            )
        with c3:
            total = domestic_values[m] + export_values[m]
            st.write(f"فروش کل: **{total:,.0f}**")

        st.markdown("---")

    confirm_del = st.checkbox("تأیید حذف تمام ماه‌های این سال")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submitted = st.form_submit_button("ثبت / به‌روزرسانی همه ماه‌ها")
    with col_btn2:
        delete_btn = st.form_submit_button("حذف تمام ماه‌های این سال")

    if submitted:
        try:
            for m in range(1, 13):
                save_month(company_id, year, m, domestic_values[m], export_values[m])
            st.success(f"فروش ماهانه سال {year} با موفقیت ذخیره شد.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"خطا در ذخیره: {e}")

    if delete_btn:
        if not confirm_del:
            st.warning("برای حذف، گزینه تأیید را تیک بزنید.")
        else:
            try:
                delete_year(company_id, year)
                st.success(f"تمام فروش‌های ماهانه سال {year} حذف شد.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"خطا در حذف: {e}")

st.markdown("---")

# ---------------- جدول خلاصه ----------------
st.subheader("خلاصه فروش ماهانه")

existing = get_monthly_sales(company_id, year)

if existing:
    data = []
    sum_dom = 0.0
    sum_exp = 0.0
    sum_total = 0.0
    for m in range(1, 13):
        row = existing.get(m)
        if row:
            dom = float(row["domestic_sales"] or 0)
            exp = float(row["export_sales"] or 0)
            tot = float(row["total_sales"] or (dom + exp))
            sum_dom += dom
            sum_exp += exp
            sum_total += tot
            data.append({
                "ماه": MONTH_NAMES[m],
                "فروش داخلی": f"{dom:,.0f}",
                "فروش صادراتی": f"{exp:,.0f}",
                "فروش کل": f"{tot:,.0f}",
            })
        else:
            data.append({
                "ماه": MONTH_NAMES[m],
                "فروش داخلی": "—",
                "فروش صادراتی": "—",
                "فروش کل": "—",
            })

    data.append({
        "ماه": "جمع کل سال",
        "فروش داخلی": f"{sum_dom:,.0f}",
        "فروش صادراتی": f"{sum_exp:,.0f}",
        "فروش کل": f"{sum_total:,.0f}",
    })

    st.table(pd.DataFrame(data))
else:
    st.info("هنوز فروشی برای این سال ثبت نشده است.")