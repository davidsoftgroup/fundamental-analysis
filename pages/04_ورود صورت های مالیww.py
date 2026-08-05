import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="ورود صورت‌های مالی", layout="wide")
from utils.styles import apply_styles
apply_styles()


st.markdown("""
<style>
    div[data-testid="stForm"] { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("ورود صورت‌های مالی")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

def get_companies():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, symbol, name_fa, fiscal_end_month, fiscal_end_day
        FROM companies ORDER BY symbol
    """).fetchall()
    conn.close()
    return rows

def get_periods(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.year_solar, p.period_type, p.end_month, p.end_day,
               f.operating_revenue, f.cogs, f.other_income, f.non_operating_income,
               f.net_profit, f.comprehensive_income, f.inventory,
               f.trade_receivables, f.equity, f.current_assets,
               f.total_assets, f.approved_dividend
        FROM periods p
        LEFT JOIN financials f ON f.period_id = p.id
        WHERE p.company_id = ?
        ORDER BY p.year_solar DESC, p.period_type DESC
    """, (company_id,)).fetchall()
    conn.close()
    return rows

def calc_end_date(fiscal_month, fiscal_day, period_type):
    months_back = {12: 0, 9: 3, 6: 6, 3: 9}
    back = months_back.get(period_type, 0)
    end_month = fiscal_month - back
    if end_month <= 0:
        end_month += 12
    return end_month, fiscal_day

def make_period_options(fiscal_month, fiscal_day):
    options = {}
    names = {
        3: "۳ ماهه منتهی به",
        6: "۶ ماهه منتهی به",
        9: "۹ ماهه منتهی به",
        12: "۱۲ ماهه سالانه منتهی به"
    }
    for ptype in [3, 6, 9, 12]:
        end_m, end_d = calc_end_date(fiscal_month, fiscal_day, ptype)
        month_name = MONTH_NAMES.get(end_m, str(end_m))
        label = f"{names[ptype]} {end_d} {month_name}"
        options[label] = ptype
    return options

def period_label(period_type, end_day=None, end_month=None):
    names = {
        3: "۳ ماهه منتهی به",
        6: "۶ ماهه منتهی به",
        9: "۹ ماهه منتهی به",
        12: "۱۲ ماهه سالانه منتهی به"
    }
    base = names.get(period_type, str(period_type))
    if end_day and end_month:
        month_name = MONTH_NAMES.get(end_month, str(end_month))
        return f"{base} {end_day} {month_name}"
    return base

def safe_div(a, b):
    try:
        if b is None or b == 0:
            return None
        return a / b
    except:
        return None

def calc_metrics(revenue, other_inc, non_op, net_profit, receivables, current_assets, comprehensive, dividend):
    op_profit = None
    if net_profit is not None:
        op_profit = net_profit - (other_inc or 0) - (non_op or 0)
    net_margin = safe_div(op_profit, revenue)
    recv_ratio = safe_div(receivables, current_assets)
    div_ratio = safe_div(dividend, comprehensive)
    return op_profit, net_margin, recv_ratio, div_ratio

def reset_form():
    """پاک کردن تمام فیلدهای فرم"""
    st.session_state.fin_year = 1404
    st.session_state.fin_period_type = 12
    st.session_state.operating_revenue = 0.0
    st.session_state.cogs = 0.0
    st.session_state.other_income = 0.0
    st.session_state.non_operating_income = 0.0
    st.session_state.net_profit = 0.0
    st.session_state.comprehensive_income = 0.0
    st.session_state.inventory = 0.0
    st.session_state.trade_receivables = 0.0
    st.session_state.equity = 0.0
    st.session_state.current_assets = 0.0
    st.session_state.total_assets = 0.0
    st.session_state.approved_dividend = 0.0

# ---------------- انتخاب شرکت ----------------
companies = get_companies()

if not companies:
    st.warning("هنوز هیچ شرکتی ثبت نشده است. ابتدا از صفحه ورود اطلاعات یک شرکت ثبت کنید.")
    st.stop()

company_options = {
    f"{c['symbol']} - {c['name_fa'] or ''} (پایان سال مالی: {c['fiscal_end_day']} {MONTH_NAMES.get(c['fiscal_end_month'], '')})": c
    for c in companies
}
selected_label = st.selectbox("انتخاب شرکت:", options=list(company_options.keys()))
selected_company = company_options[selected_label]
company_id = selected_company["id"]
fiscal_month = int(selected_company["fiscal_end_month"] or 12)
fiscal_day = int(selected_company["fiscal_end_day"] or 29)

st.markdown("---")

# ---------------- مقادیر پیش‌فرض ----------------
defaults = {
    "fin_year": 1404,
    "fin_period_type": 12,
    "operating_revenue": 0.0,
    "cogs": 0.0,
    "other_income": 0.0,
    "non_operating_income": 0.0,
    "net_profit": 0.0,
    "comprehensive_income": 0.0,
    "inventory": 0.0,
    "trade_receivables": 0.0,
    "equity": 0.0,
    "current_assets": 0.0,
    "total_assets": 0.0,
    "approved_dividend": 0.0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

period_options = make_period_options(fiscal_month, fiscal_day)
period_labels_list = list(period_options.keys())
period_values_list = list(period_options.values())

try:
    default_index = period_values_list.index(int(st.session_state.fin_period_type))
except ValueError:
    default_index = 3

# ---------------- فرم ----------------
st.subheader("ثبت / ویرایش صورت مالی")

with st.form("financial_form"):

    col_y, col_p = st.columns(2)
    with col_y:
        year = st.number_input("سال شمسی *", min_value=1390, max_value=1410, value=int(st.session_state.fin_year), step=1)
    with col_p:
        selected_period_label = st.selectbox("نوع دوره *", options=period_labels_list, index=default_index)
        period_type = period_options[selected_period_label]

    st.markdown("---")
    st.markdown("**صورت سود و زیان**")

    col1, col2, col3 = st.columns(3)
    with col1:
        operating_revenue = st.number_input("درآمد عملیاتی", min_value=0.0, value=float(st.session_state.operating_revenue), step=100.0)
        cogs = st.number_input("بهای تمام‌شده", min_value=0.0, value=float(st.session_state.cogs), step=100.0)
    with col2:
        other_income = st.number_input("سایر درآمدها", value=float(st.session_state.other_income), step=100.0)
        non_operating_income = st.number_input("سایر غیرعملیاتی", value=float(st.session_state.non_operating_income), step=100.0)
    with col3:
        net_profit = st.number_input("سود خالص", value=float(st.session_state.net_profit), step=100.0)

    st.markdown("---")
    st.markdown("**ترازنامه**")

    col4, col5, col6 = st.columns(3)
    with col4:
        inventory = st.number_input("موجودی کالا", min_value=0.0, value=float(st.session_state.inventory), step=100.0)
        trade_receivables = st.number_input("دریافتنی‌های تجاری", min_value=0.0, value=float(st.session_state.trade_receivables), step=100.0)
    with col5:
        equity = st.number_input("حقوق مالکانه", value=float(st.session_state.equity), step=100.0)
        current_assets = st.number_input("جمع دارایی‌های جاری", min_value=0.0, value=float(st.session_state.current_assets), step=100.0)
    with col6:
        total_assets = st.number_input("جمع کل دارایی‌ها", min_value=0.0, value=float(st.session_state.total_assets), step=100.0)

    st.markdown("---")
    st.markdown("**سایر**")

    col7, col8 = st.columns(2)
    with col7:
        comprehensive_income = st.number_input("سود (زیان) جامع سال", value=float(st.session_state.comprehensive_income), step=100.0)
    with col8:
        approved_dividend = st.number_input("سود سهام مصوب", min_value=0.0, value=float(st.session_state.approved_dividend), step=10.0)

    # شاخص‌های محاسباتی
    op_profit, net_margin, recv_ratio, div_ratio = calc_metrics(
        operating_revenue, other_income, non_operating_income, net_profit,
        trade_receivables, current_assets, comprehensive_income, approved_dividend
    )

    st.markdown("---")
    st.markdown("**شاخص‌های محاسباتی (خودکار)**")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("سود خالص عملیاتی", f"{op_profit:,.0f}" if op_profit is not None else "—")
    with m2:
        st.metric("حاشیه سود خالص", f"{net_margin*100:.1f}%" if net_margin is not None else "—")
    with m3:
        st.metric("نسبت مطالبات به دارایی جاری", f"{recv_ratio*100:.1f}%" if recv_ratio is not None else "—")
    with m4:
        st.metric("نسبت سود مصوب به جامع", f"{div_ratio*100:.1f}%" if div_ratio is not None else "—")

    st.markdown("---")

    # تأیید حذف
    confirm_delete = st.checkbox("برای حذف این دوره، این گزینه را فعال کنید")

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        submitted = st.form_submit_button("ثبت / به‌روزرسانی")
    with col_btn2:
        delete_btn = st.form_submit_button("حذف این دوره")
    with col_btn3:
        clear_btn = st.form_submit_button("پاک کردن فرم")

    if submitted:
        try:
            end_m, end_d = calc_end_date(fiscal_month, fiscal_day, period_type)
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id FROM periods
                WHERE company_id=? AND year_solar=? AND period_type=?
            """, (company_id, year, period_type))
            existing = cursor.fetchone()

            if existing:
                period_id = existing["id"]
                cursor.execute("UPDATE periods SET end_month=?, end_day=? WHERE id=?", (end_m, end_d, period_id))

                cursor.execute("SELECT id FROM financials WHERE period_id=?", (period_id,))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE financials SET
                            operating_revenue=?, cogs=?, other_income=?, non_operating_income=?,
                            net_profit=?, comprehensive_income=?,
                            inventory=?, trade_receivables=?, equity=?,
                            current_assets=?, total_assets=?, approved_dividend=?
                        WHERE period_id=?
                    """, (
                        operating_revenue, cogs, other_income, non_operating_income,
                        net_profit, comprehensive_income,
                        inventory, trade_receivables, equity,
                        current_assets, total_assets, approved_dividend, period_id
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO financials (
                            period_id, operating_revenue, cogs, other_income, non_operating_income,
                            net_profit, comprehensive_income,
                            inventory, trade_receivables, equity,
                            current_assets, total_assets, approved_dividend
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        period_id, operating_revenue, cogs, other_income, non_operating_income,
                        net_profit, comprehensive_income,
                        inventory, trade_receivables, equity,
                        current_assets, total_assets, approved_dividend
                    ))
                st.success(f"صورت مالی {period_label(period_type, end_d, end_m)} سال {year} به‌روزرسانی شد.")
            else:
                cursor.execute("""
                    INSERT INTO periods (company_id, year_solar, period_type, end_month, end_day)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, year, period_type, end_m, end_d))
                period_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO financials (
                        period_id, operating_revenue, cogs, other_income, non_operating_income,
                        net_profit, comprehensive_income,
                        inventory, trade_receivables, equity,
                        current_assets, total_assets, approved_dividend
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    period_id, operating_revenue, cogs, other_income, non_operating_income,
                    net_profit, comprehensive_income,
                    inventory, trade_receivables, equity,
                    current_assets, total_assets, approved_dividend
                ))
                st.success(f"صورت مالی {period_label(period_type, end_d, end_m)} سال {year} ثبت شد.")

            conn.commit()
            conn.close()

            # پاک کردن فرم بعد از ثبت موفق
            reset_form()
            st.experimental_rerun()

        except Exception as e:
            st.error(f"خطا در ثبت: {e}")

    if delete_btn:
        if not confirm_delete:
            st.warning("برای حذف، ابتدا گزینه «برای حذف این دوره، این گزینه را فعال کنید» را تیک بزنید.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM periods
                    WHERE company_id=? AND year_solar=? AND period_type=?
                """, (company_id, year, period_type))
                existing = cursor.fetchone()
                if existing:
                    period_id = existing["id"]
                    cursor.execute("DELETE FROM financials WHERE period_id=?", (period_id,))
                    cursor.execute("DELETE FROM periods WHERE id=?", (period_id,))
                    conn.commit()
                    st.success("دوره و صورت مالی با موفقیت حذف شد.")
                    reset_form()
                else:
                    st.warning("این دوره وجود ندارد.")
                conn.close()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"خطا در حذف: {e}")

    if clear_btn:
        reset_form()
        st.experimental_rerun()

st.markdown("---")

# ---------------- لیست دوره‌ها ----------------
st.subheader("دوره‌های ثبت‌شده این شرکت")

periods = get_periods(company_id)

if periods:
    data = []
    for row in periods:
        op_p, margin, recv_r, div_r = calc_metrics(
            row["operating_revenue"], row["other_income"], row["non_operating_income"],
            row["net_profit"], row["trade_receivables"], row["current_assets"],
            row["comprehensive_income"], row["approved_dividend"]
        )
        data.append({
            "سال": row["year_solar"],
            "دوره": period_label(row["period_type"], row["end_day"], row["end_month"]),
            "درآمد عملیاتی": f"{row['operating_revenue']:,.0f}" if row["operating_revenue"] is not None else "—",
            "سود خالص عملیاتی": f"{op_p:,.0f}" if op_p is not None else "—",
            "حاشیه سود": f"{margin*100:.1f}%" if margin is not None else "—",
            "نسبت مطالبات": f"{recv_r*100:.1f}%" if recv_r is not None else "—",
        })
    st.table(pd.DataFrame(data))

    st.markdown("**بارگذاری یک دوره برای ویرایش:**")
    load_col1, load_col2 = st.columns([3, 1])
    with load_col1:
        period_labels = [
            f"{r['year_solar']} - {period_label(r['period_type'], r['end_day'], r['end_month'])}"
            for r in periods
        ]
        selected_period_label = st.selectbox("انتخاب دوره:", options=period_labels, key="load_period")
    with load_col2:
        st.write("")
        st.write("")
        if st.button("بارگذاری"):
            idx = period_labels.index(selected_period_label)
            row = periods[idx]
            conn = get_connection()
            full = conn.execute("""
                SELECT p.year_solar, p.period_type, f.*
                FROM periods p
                LEFT JOIN financials f ON f.period_id = p.id
                WHERE p.id = ?
            """, (row["id"],)).fetchone()
            conn.close()

            if full:
                st.session_state.fin_year = full["year_solar"]
                st.session_state.fin_period_type = full["period_type"]
                st.session_state.operating_revenue = float(full["operating_revenue"] or 0)
                st.session_state.cogs = float(full["cogs"] or 0)
                st.session_state.other_income = float(full["other_income"] or 0)
                st.session_state.non_operating_income = float(full["non_operating_income"] or 0)
                st.session_state.net_profit = float(full["net_profit"] or 0)
                st.session_state.comprehensive_income = float(full["comprehensive_income"] or 0)
                st.session_state.inventory = float(full["inventory"] or 0)
                st.session_state.trade_receivables = float(full["trade_receivables"] or 0)
                st.session_state.equity = float(full["equity"] or 0)
                st.session_state.current_assets = float(full["current_assets"] or 0)
                st.session_state.total_assets = float(full["total_assets"] or 0)
                st.session_state.approved_dividend = float(full["approved_dividend"] or 0)
                st.success("اطلاعات در فرم بالا بارگذاری شد.")
                st.experimental_rerun()
else:
    st.info("هنوز هیچ دوره‌ای برای این شرکت ثبت نشده است.")