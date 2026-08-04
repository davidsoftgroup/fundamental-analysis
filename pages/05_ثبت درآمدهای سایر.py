import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="درآمد غیرعملیاتی", layout="wide")
from utils.styles import apply_styles
apply_styles()


st.markdown("""
<style>
    div[data-testid="stForm"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("ثبت اقلام درآمد غیرعملیاتی و سایر")

init_db()

def get_companies():
    conn = get_connection()
    rows = conn.execute("SELECT id, symbol, name_fa FROM companies ORDER BY symbol").fetchall()
    conn.close()
    return rows

def get_items(company_id, year=None):
    conn = get_connection()
    if year:
        rows = conn.execute("""
            SELECT id, year_solar, title, amount, is_recurring, notes
            FROM non_operating_items
            WHERE company_id = ? AND year_solar = ?
            ORDER BY year_solar DESC, id
        """, (company_id, year)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, year_solar, title, amount, is_recurring, notes
            FROM non_operating_items
            WHERE company_id = ?
            ORDER BY year_solar DESC, id
        """, (company_id,)).fetchall()
    conn.close()
    return rows

def get_recurring_sum_by_year(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT year_solar, SUM(amount) as total
        FROM non_operating_items
        WHERE company_id = ? AND is_recurring = 1
        GROUP BY year_solar
        ORDER BY year_solar
    """, (company_id,)).fetchall()
    conn.close()
    return rows

# ---------------- انتخاب شرکت ----------------
companies = get_companies()
if not companies:
    st.warning("هنوز شرکتی ثبت نشده است.")
    st.stop()

company_options = {f"{c['symbol']} - {c['name_fa'] or ''}": c["id"] for c in companies}
selected_label = st.selectbox("انتخاب شرکت:", options=list(company_options.keys()))
company_id = company_options[selected_label]

st.markdown("---")

# ---------------- فرم ثبت ----------------
st.subheader("ثبت قلم جدید")

with st.form("item_form"):
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("سال شمسی *", min_value=1390, max_value=1410, value=1403, step=1)
        title = st.text_input("عنوان *", placeholder="مثال: سود سهام زیرمجموعه")
    with col2:
        amount = st.number_input("مبلغ (میلیارد ریال) *", value=0.0, step=10.0)
        is_recurring = st.checkbox("تکرارپذیر است (احتمالاً سال بعد هم وجود دارد)", value=True)
    notes = st.text_input("توضیحات (اختیاری)", placeholder="")

    submitted = st.form_submit_button("ثبت قلم")

    if submitted:
        if not title or amount == 0:
            st.error("عنوان و مبلغ الزامی است.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO non_operating_items
                    (company_id, year_solar, title, amount, is_recurring, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (company_id, year, title.strip(), amount, 1 if is_recurring else 0, notes.strip() or None))
                conn.commit()
                conn.close()
                st.success("قلم با موفقیت ثبت شد.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"خطا: {e}")

st.markdown("---")

# ---------------- لیست اقلام ----------------
st.subheader("لیست اقلام ثبت‌شده")

filter_year = st.number_input("فیلتر سال (۰ = همه):", min_value=0, max_value=1410, value=0, step=1)
items = get_items(company_id, year=filter_year if filter_year > 0 else None)

if items:
    data = []
    for r in items:
        data.append({
            "شناسه": r["id"],
            "سال": r["year_solar"],
            "عنوان": r["title"],
            "مبلغ": f"{r['amount']:,.0f}",
            "تکرارپذیر": "بله" if r["is_recurring"] else "خیر",
            "توضیحات": r["notes"] or "—",
        })
    st.table(pd.DataFrame(data))

    # حذف
    st.markdown("**حذف یک قلم**")
    del_id = st.number_input("شناسه قلم برای حذف:", min_value=0, step=1, value=0)
    confirm = st.checkbox("تأیید حذف")
    if st.button("حذف"):
        if not confirm:
            st.warning("تأیید را تیک بزنید.")
        elif del_id <= 0:
            st.warning("شناسه معتبر وارد کنید.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM non_operating_items WHERE id=? AND company_id=?", (del_id, company_id))
            conn.commit()
            conn.close()
            st.success("حذف شد.")
            st.experimental_rerun()
else:
    st.info("هنوز قلمی ثبت نشده است.")

st.markdown("---")

# ---------------- خلاصه تکرارپذیرها ----------------
st.subheader("جمع اقلام تکرارپذیر به تفکیک سال")

recurring = get_recurring_sum_by_year(company_id)
if recurring:
    data = []
    prev = None
    for r in recurring:
        total = r["total"] or 0
        growth = "—"
        if prev is not None and prev != 0:
            g = (total - prev) / prev * 100
            growth = f"{g:+.1f}%"
        data.append({
            "سال": r["year_solar"],
            "جمع تکرارپذیر": f"{total:,.0f}",
            "رشد نسبت به سال قبل": growth,
        })
        prev = total
    st.table(pd.DataFrame(data))

    # برآورد سال بعد
    if len(recurring) >= 1:
        last = recurring[-1]
        last_total = last["total"] or 0
        if len(recurring) >= 2:
            prev_total = recurring[-2]["total"] or 0
            if prev_total != 0:
                growth_rate = (last_total - prev_total) / prev_total
            else:
                growth_rate = 0
            est = last_total * (1 + growth_rate)
            st.success(f"برآورد غیرعملیاتی تکرارپذیر سال {last['year_solar'] + 1}: **{est:,.0f}** میلیارد ریال (رشد {growth_rate*100:+.1f}٪)")
        else:
            st.info(f"فقط یک سال داده وجود دارد. برآورد سال بعد ≈ **{last_total:,.0f}** (بدون رشد)")
else:
    st.info("هنوز قلم تکرارپذیری ثبت نشده است.")