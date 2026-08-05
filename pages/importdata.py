# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
import re
from io import BytesIO

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="ورود از اکسل", layout="wide")

try:
    from utils.styles import apply_styles
    apply_styles()
except Exception:
    pass

st.markdown("""
<style>
    .main .block-container { direction: rtl; }
</style>
""", unsafe_allow_html=True)

st.title("ورود اطلاعات از اکسل")
st.caption("فایل اکسل با ساختار استاندارد (فروش ماهانه + صورت‌های مالی + غیرعملیاتی) را آپلود کنید.")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}


def get_companies():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, symbol, name_fa FROM companies ORDER BY symbol"
    ).fetchall()
    conn.close()
    return rows


def to_float(v):
    if v is None:
        return None
    try:
        if isinstance(v, float) and pd.isna(v):
            return None
        s = str(v).strip().replace(",", "")
        if s in ("", "-", "—", "#N/A", "#DIV/0!", "None", "nan"):
            return None
        return float(s)
    except Exception:
        return None


def to_int(v):
    f = to_float(v)
    if f is None:
        return None
    return int(round(f))


def cell(df, r, c):
    try:
        if r < 0 or c < 0:
            return None
        if r >= len(df) or c >= len(df.columns):
            return None
        return df.iat[r, c]
    except Exception:
        return None


def find_year_blocks(df):
    """
    در ردیف سال‌ها (معمولاً ردیف index=1) سال‌های شمسی را پیدا می‌کند.
    خروجی: [(year, start_col), ...]
    """
    blocks = []
    # چند ردیف اول را برای پیدا کردن سال جستجو کن
    for r in range(min(5, len(df))):
        for c in range(len(df.columns)):
            v = cell(df, r, c)
            try:
                y = int(float(v))
                if 1390 <= y <= 1420:
                    blocks.append((y, c, r))
            except Exception:
                pass
    # یکتا بر اساس سال + ستون
    seen = set()
    out = []
    for y, c, r in blocks:
        key = (y, c)
        if key in seen:
            continue
        seen.add(key)
        out.append((y, c))
    out.sort(key=lambda x: x[1])
    return out


def parse_monthly(df, year_blocks):
    """
    فروش داخلی / صادراتی را از ردیف‌هایی که برچسب فارسی دارند می‌خواند.
    """
    result = {}  # year -> {month: {domestic, export, total}}

    # پیدا کردن ردیف‌های فروش
    row_domestic = row_export = None
    for r in range(min(15, len(df))):
        label = str(cell(df, r, 0) or "").strip()
        if "فروش داخلی" in label and row_domestic is None:
            row_domestic = r
        if "فروش صادراتی" in label and row_export is None:
            row_export = r

    if row_domestic is None and row_export is None:
        return result

    for year, start_col in year_blocks:
        # ستون ماه‌ها معمولاً start_col+1 تا start_col+12
        # در فایل نمونه: سال در ستون start، بعد ماه 1 در start+1 ... یا ماه‌ها از start شروع می‌شوند
        # ساختار نمونه: col0=label, col1..12=months for first year
        months = {}
        for m in range(1, 13):
            # دو الگوی رایج:
            # A) سال در ستون c، ماه‌ها c+1 .. c+12
            # B) سال بالای ماه 1، ماه‌ها از همان ستون سال
            c1 = start_col + m          # الگوی A
            c2 = start_col + (m - 1)    # الگوی B

            dom = exp = None
            for c in (c1, c2):
                if row_domestic is not None:
                    d = to_float(cell(df, row_domestic, c))
                    if d is not None:
                        dom = d
                if row_export is not None:
                    e = to_float(cell(df, row_export, c))
                    if e is not None:
                        exp = e
                if dom is not None or exp is not None:
                    break

            if dom is None and exp is None:
                continue
            dom = dom or 0.0
            exp = exp or 0.0
            months[m] = {
                "domestic": dom,
                "export": exp,
                "total": dom + exp,
            }
        if months:
            result[year] = months
    return result


def parse_financials(df, year_blocks):
    """
    صورت‌های مالی تجمعی ۳/۶/۹/۱۲ ماهه
    """
    # نقشه برچسب‌ها به فیلد
    label_map = {
        "درآمدهای عملیاتی": "operating_revenue",
        "درآمد عملیاتی": "operating_revenue",
        "سایر درآمدها": "other_income",
        "درآمدها  و هزینه های غیر عملیاتی": "non_operating_income",
        "درآمدها و هزینه های غیر عملیاتی": "non_operating_income",
        "غیر عملیاتی": "non_operating_income",
        "سود خالص": "net_profit",
        "بهای تمام شده": "cogs",
        "بهای تمام‌شده": "cogs",
        "موجودی کالا": "inventory",
        "دزیافتنی های تجاری": "trade_receivables",
        "دریافتنی های تجاری": "trade_receivables",
        "دریافتنی‌های تجاری": "trade_receivables",
        "حقوق مالکانه": "equity",
        "جمع درایی های جاری": "current_assets",
        "جمع دارایی های جاری": "current_assets",
        "جمع دارایی‌های جاری": "current_assets",
        "جمع کل درایی ها": "total_assets",
        "جمع کل دارایی ها": "total_assets",
        "جمع کل دارایی‌ها": "total_assets",
        "سود(زیان ) جامع سال": "comprehensive_income",
        "سود(زیان) جامع سال": "comprehensive_income",
        "سود جامع": "comprehensive_income",
        "سود سهام مصوب": "approved_dividend",
    }

    # پیدا کردن ردیف هر فیلد
    field_rows = {}
    for r in range(len(df)):
        for c in range(min(5, len(df.columns))):
            label = str(cell(df, r, c) or "").strip()
            if not label:
                continue
            for key, field in label_map.items():
                if key in label and field not in field_rows:
                    field_rows[field] = (r, c)
                    break

    # پیدا کردن ردیف دوره‌ها و ستون هر دوره
    # period_type از متن «منتهی به تاریخ 03/31» و مشابه
    period_cols = []  # (year, period_type, col, end_month, end_day)

    for r in range(len(df)):
        for c in range(len(df.columns)):
            v = str(cell(df, r, c) or "")
            if "منتهی" in v or "دوره" in v:
                # تاریخ مثل 03/31 یا 3/31 یا 09/30
                m = re.search(r"(\d{1,2})\s*/\s*(\d{1,2})", v)
                if not m:
                    continue
                end_month = int(m.group(1))
                end_day = int(m.group(2))
                # تشخیص period_type از ماه پایان (نسبت به سال مالی اسفند)
                # در فایل نمونه: 03→3ماهه، 06→6، 09→9، 12→12
                if end_month in (3,):
                    ptype = 3
                elif end_month in (6,):
                    ptype = 6
                elif end_month in (9,):
                    ptype = 9
                elif end_month in (12,):
                    ptype = 12
                else:
                    # نزدیک‌ترین
                    ptype = min([3, 6, 9, 12], key=lambda x: abs(x - end_month))

                # سال مربوط به نزدیک‌ترین year_block سمت چپ
                year = None
                for y, yc in year_blocks:
                    if yc <= c:
                        year = y
                if year is None and year_blocks:
                    year = year_blocks[0][0]
                if year is None:
                    continue
                period_cols.append((year, ptype, c, end_month, end_day))

    # یکتا کردن
    uniq = {}
    for item in period_cols:
        key = (item[0], item[1])
        uniq[key] = item
    period_cols = list(uniq.values())

    financials = []
    for year, ptype, col, end_m, end_d in period_cols:
        rec = {
            "year": year,
            "period_type": ptype,
            "end_month": end_m,
            "end_day": end_d,
            "operating_revenue": None,
            "cogs": None,
            "other_income": None,
            "non_operating_income": None,
            "net_profit": None,
            "comprehensive_income": None,
            "inventory": None,
            "trade_receivables": None,
            "equity": None,
            "current_assets": None,
            "total_assets": None,
            "approved_dividend": None,
        }
        for field, (fr, fc) in field_rows.items():
            # مقدار معمولاً در همان ستون دوره است؛ گاهی چند ستون بعد از برچسب
            val = to_float(cell(df, fr, col))
            if val is None:
                # گاهی مقدار ۱ یا ۲ ستون بعد از label است اگر col روی label افتاده
                for dc in range(0, 4):
                    val = to_float(cell(df, fr, col + dc))
                    if val is not None:
                        break
            rec[field] = val

        # فقط اگر حداقل درآمد یا سود داشته باشد
        if rec["operating_revenue"] is not None or rec["net_profit"] is not None:
            financials.append(rec)

    return financials


def parse_non_operating(df):
    """
    بخش پایین اکسل: درآمد غیرعملیاتی با سال‌ها
    """
    items = []
    # پیدا کردن ردیف هدر که «درآمد غیر عملیاتی» دارد
    header_r = None
    year_cols = {}  # year -> col
    for r in range(len(df)):
        for c in range(len(df.columns)):
            v = str(cell(df, r, c) or "")
            if "غیر عملیاتی" in v or "غیرعملیاتی" in v:
                header_r = r
                break
        if header_r is not None:
            break

    if header_r is None:
        return items

    # سال‌ها روی همان ردیف یا ردیف بعدی
    for r in range(header_r, min(header_r + 3, len(df))):
        for c in range(len(df.columns)):
            v = cell(df, r, c)
            try:
                y = int(float(v))
                if 1390 <= y <= 1420:
                    year_cols[y] = c
            except Exception:
                pass

    if not year_cols:
        return items

    # ردیف‌های بعد از هدر تا چند خط
    for r in range(header_r + 1, min(header_r + 15, len(df))):
        title = None
        for c in range(min(8, len(df.columns))):
            t = str(cell(df, r, c) or "").strip()
            if t and not re.match(r"^[\d\.\-]+$", t) and "مجموع" not in t and "برآورد" not in t:
                # اگر شبیه عنوان است
                if any(k in t for k in ["سود", "اجاره", "سپرده", "سرمایه", "درآمد", "سایر"]):
                    title = t
                    break
        if not title:
            continue
        for y, c in year_cols.items():
            amt = to_float(cell(df, r, c))
            if amt is None or amt == 0:
                continue
            items.append({
                "year": y,
                "title": title,
                "amount": amt,
                "is_recurring": 1,
            })
    return items


def save_monthly(company_id, monthly):
    conn = get_connection()
    cur = conn.cursor()
    n = 0
    for year, months in monthly.items():
        for m, vals in months.items():
            cur.execute("""
                INSERT INTO monthly_sales
                    (company_id, year_solar, month, domestic_sales, export_sales, total_sales)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, year_solar, month)
                DO UPDATE SET
                    domestic_sales=excluded.domestic_sales,
                    export_sales=excluded.export_sales,
                    total_sales=excluded.total_sales
            """, (
                company_id, year, m,
                vals["domestic"], vals["export"], vals["total"]
            ))
            n += 1
    conn.commit()
    conn.close()
    return n


def save_financials(company_id, financials):
    conn = get_connection()
    cur = conn.cursor()
    n = 0
    for rec in financials:
        cur.execute("""
            SELECT id FROM periods
            WHERE company_id=? AND year_solar=? AND period_type=?
        """, (company_id, rec["year"], rec["period_type"]))
        existing = cur.fetchone()
        if existing:
            period_id = existing["id"]
            cur.execute(
                "UPDATE periods SET end_month=?, end_day=? WHERE id=?",
                (rec["end_month"], rec["end_day"], period_id)
            )
        else:
            cur.execute("""
                INSERT INTO periods (company_id, year_solar, period_type, end_month, end_day)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, rec["year"], rec["period_type"], rec["end_month"], rec["end_day"]))
            period_id = cur.lastrowid

        cur.execute("SELECT id FROM financials WHERE period_id=?", (period_id,))
        fin = cur.fetchone()
        vals = (
            rec.get("operating_revenue"),
            rec.get("cogs"),
            rec.get("other_income"),
            rec.get("non_operating_income"),
            rec.get("net_profit"),
            rec.get("comprehensive_income"),
            rec.get("inventory"),
            rec.get("trade_receivables"),
            rec.get("equity"),
            rec.get("current_assets"),
            rec.get("total_assets"),
            rec.get("approved_dividend"),
        )
        if fin:
            cur.execute("""
                UPDATE financials SET
                    operating_revenue=?, cogs=?, other_income=?, non_operating_income=?,
                    net_profit=?, comprehensive_income=?,
                    inventory=?, trade_receivables=?, equity=?,
                    current_assets=?, total_assets=?, approved_dividend=?
                WHERE period_id=?
            """, vals + (period_id,))
        else:
            cur.execute("""
                INSERT INTO financials (
                    period_id, operating_revenue, cogs, other_income, non_operating_income,
                    net_profit, comprehensive_income,
                    inventory, trade_receivables, equity,
                    current_assets, total_assets, approved_dividend
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (period_id,) + vals)
        n += 1
    conn.commit()
    conn.close()
    return n


def save_non_op(company_id, items):
    if not items:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    years = list(set(i["year"] for i in items))
    for y in years:
        cur.execute(
            "DELETE FROM non_operating_items WHERE company_id=? AND year_solar=?",
            (company_id, y)
        )
    n = 0
    for it in items:
        cur.execute("""
            INSERT INTO non_operating_items
                (company_id, year_solar, title, amount, is_recurring)
            VALUES (?, ?, ?, ?, ?)
        """, (company_id, it["year"], it["title"], it["amount"], it.get("is_recurring", 1)))
        n += 1
    conn.commit()
    conn.close()
    return n


# ============================================================
# UI
# ============================================================
companies = get_companies()
if not companies:
    st.warning("ابتدا حداقل یک شرکت ثبت کنید.")
    st.stop()

placeholder = "— یک شرکت انتخاب کنید —"
options = {placeholder: None}
for c in companies:
    options["{} — {}".format(c["symbol"], c["name_fa"] or "")] = c

selected = st.selectbox("انتخاب شرکت:", list(options.keys()))
if selected == placeholder or options[selected] is None:
    st.info("ابتدا شرکت را انتخاب کنید، سپس فایل اکسل را آپلود کنید.")
    st.stop()

company = options[selected]
company_id = company["id"]
st.success("شرکت انتخاب‌شده: **{}**".format(company["symbol"]))

uploaded = st.file_uploader(
    "فایل اکسل (.xlsx)",
    type=["xlsx", "xls"],
    help="ساختار فایل باید مشابه نمونه باشد: فروش ماهانه + صورت‌های مالی + غیرعملیاتی"
)

if not uploaded:
    st.stop()

# خواندن اکسل
try:
    df = pd.read_excel(BytesIO(uploaded.read()), header=None, engine="openpyxl")
except Exception as e:
    st.error("خطا در خواندن فایل: {}".format(e))
    st.stop()

st.write("ابعاد فایل:", df.shape[0], "ردیف ×", df.shape[1], "ستون")

year_blocks = find_year_blocks(df)
if not year_blocks:
    st.error("سال شمسی در فایل پیدا نشد. ردیف سال‌ها را بررسی کنید.")
    st.stop()

st.write("سال‌های شناسایی‌شده:", ", ".join(str(y) for y, _ in year_blocks))

monthly = parse_monthly(df, year_blocks)
financials = parse_financials(df, year_blocks)
non_op = parse_non_operating(df)

# پیش‌نمایش
st.subheader("پیش‌نمایش داده‌های استخراج‌شده")

tab1, tab2, tab3 = st.tabs(["فروش ماهانه", "صورت‌های مالی", "غیرعملیاتی"])

with tab1:
    if not monthly:
        st.warning("فروش ماهانه پیدا نشد.")
    else:
        for year, months in sorted(monthly.items()):
            st.markdown("**سال {}** — {} ماه".format(year, len(months)))
            rows = []
            for m in range(1, 13):
                if m not in months:
                    continue
                v = months[m]
                rows.append({
                    "ماه": MONTH_NAMES.get(m, m),
                    "داخلی": "{:,.0f}".format(v["domestic"]),
                    "صادراتی": "{:,.0f}".format(v["export"]),
                    "کل": "{:,.0f}".format(v["total"]),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

with tab2:
    if not financials:
        st.warning("صورت مالی پیدا نشد.")
    else:
        rows = []
        for r in financials:
            rows.append({
                "سال": r["year"],
                "دوره": "{} ماهه".format(r["period_type"]),
                "پایان": "{}/{}".format(r["end_month"], r["end_day"]),
                "درآمد": r.get("operating_revenue"),
                "بهای تمام‌شده": r.get("cogs"),
                "سود خالص": r.get("net_profit"),
                "سایر": r.get("other_income"),
                "غیرعملیاتی": r.get("non_operating_income"),
                "موجودی": r.get("inventory"),
                "مطالبات": r.get("trade_receivables"),
                "دارایی جاری": r.get("current_assets"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with tab3:
    if not non_op:
        st.info("قلم غیرعملیاتی پیدا نشد (اختیاری).")
    else:
        st.dataframe(pd.DataFrame(non_op), use_container_width=True)

st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    do_import = st.button("ثبت در دیتابیس", type="primary")
with col_b:
    st.caption("در صورت وجود داده قبلی برای همان سال/دوره، به‌روزرسانی می‌شود.")

if do_import:
    try:
        n1 = save_monthly(company_id, monthly) if monthly else 0
        n2 = save_financials(company_id, financials) if financials else 0
        n3 = save_non_op(company_id, non_op) if non_op else 0
        st.success(
            "ثبت شد — فروش ماهانه: {} | صورت مالی: {} | غیرعملیاتی: {}".format(n1, n2, n3)
        )
    except Exception as e:
        st.error("خطا در ذخیره‌سازی: {}".format(e))
        import traceback
        st.code(traceback.format_exc())