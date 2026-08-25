# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import math
import jdatetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="داشبورد", layout="wide", initial_sidebar_state="expanded")
from utils.styles import apply_styles
apply_styles()

st.markdown("""
<style>
    .main .block-container { direction: rtl; padding-top: 1.2rem; max-width: 1200px; }
    div[data-testid="stMetric"] {
        direction: rtl; text-align: center; background: #f8f9fb;
        border: 1px solid #e8ecf1; border-radius: 10px; padding: 10px 8px; min-height: 78px;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.88rem !important; color: #475569 !important; font-weight: 600 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.05rem !important; font-weight: 600 !important; color: #0f172a !important;
    }
    .stTable, table { direction: rtl; text-align: center; font-size: 1.05rem; }
    .stExpander { direction: rtl; }
    h1 { font-size: 1.8rem !important; color: #0f172a !important; font-weight: 700 !important; }
    h2, h3 { color: #1e293b !important; font-size: 1.25rem !important; }
    .stCaption { color: #64748b !important; font-size: 0.82rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.6rem !important; margin-bottom: 0.35rem !important; }
    .status-ahead { color: #16a34a; font-weight: bold; }
    .status-behind { color: #dc2626; font-weight: bold; }
    .status-on-track { color: #ca8a04; font-weight: bold; }
    .progress-box {
        display: flex;
        gap: 4px;
        justify-content: center;
        align-items: center;
    }
    .progress-square {
        width: 18px;
        height: 18px;
        border-radius: 3px;
        border: 1px solid #cbd5e1;
        display: inline-block;
    }
    .progress-square.filled {
        background: #2563eb;
        border-color: #2563eb;
    }
    .progress-square.empty {
        background: #e8ecf1;
    }
    .progress-label {
        font-size: 11px;
        color: #64748b;
        margin-right: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("داشبورد تحلیل بنیادی سهام بورس ایران")
init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#ea580c", "#7c3aed", "#0891b2"]
MIN_YEAR, MAX_YEAR = 1390, 1410
AXIS_COLOR = "#0f172a"
GRID_COLOR = "#cbd5e1"


# ============================================================
# سال مالی
# ============================================================
def fiscal_period_end(fiscal_year, period_type, fiscal_end_month, fiscal_end_day=29):
    """
    پایان واقعی دوره نسبت به سال مالی.
    مثال ماه‌مالی=6 برای سال مالی 1405:
      3 → 09/1404 | 6 → 12/1404 | 9 → 03/1405 | 12 → 06/1405
    """
    months_back = {12: 0, 9: 3, 6: 6, 3: 9}
    back = months_back.get(int(period_type), 0)
    end_month = int(fiscal_end_month) - back
    cal_year = int(fiscal_year)
    if end_month <= 0:
        end_month += 12
        cal_year -= 1
    return cal_year, end_month, int(fiscal_end_day or 29)


def resolve_fiscal_year(row, fiscal_end_month, fiscal_end_day=29):
    """
    سال مالی واقعی رکورد را مشخص می‌کند.
    """
    y = int(row["year_solar"])
    pt = int(row["period_type"])
    F = int(fiscal_end_month)
    day = int(fiscal_end_day or 29)

    end_m = None
    try:
        if row["end_month"] is not None:
            end_m = int(row["end_month"])
    except Exception:
        end_m = None

    candidates = [y, y + 1, y - 1, y + 2, y - 2]

    if end_m:
        for cand in candidates:
            cy, em, _ = fiscal_period_end(cand, pt, F, day)
            if em == end_m and cy == y:
                return cand
        for cand in candidates:
            cy, em, _ = fiscal_period_end(cand, pt, F, day)
            if em == end_m and cand == y:
                return cand
        for cand in candidates:
            cy, em, _ = fiscal_period_end(cand, pt, F, day)
            if em == end_m:
                return cand
    return y


def period_axis_categories(fiscal_end_month, fiscal_end_day=29):
    """چهار برچسب ثابت محور X برای مقایسه سال‌ها."""
    names = {
        3: "۳ ماهه منتهی به",
        6: "۶ ماهه منتهی به",
        9: "۹ ماهه منتهی به",
        12: "۱۲ ماهه منتهی به",
    }
    order, cats = [], []
    for ptype in [3, 6, 9, 12]:
        _cy, end_m, _d = fiscal_period_end(1400, ptype, fiscal_end_month, fiscal_end_day)
        label = "{} {}".format(names[ptype], MONTH_NAMES.get(end_m, end_m))
        order.append(ptype)
        cats.append(label)
    return order, cats


def period_full_label(fiscal_year, period_type, fiscal_end_month, fiscal_end_day=29):
    names = {
        3: "۳ ماهه منتهی به",
        6: "۶ ماهه منتهی به",
        9: "۹ ماهه منتهی به",
        12: "۱۲ ماهه سالانه منتهی به",
    }
    cal_y, end_m, end_d = fiscal_period_end(fiscal_year, period_type, fiscal_end_month, fiscal_end_day)
    return "{} {} {} {}".format(
        names.get(int(period_type), period_type),
        end_d,
        MONTH_NAMES.get(end_m, end_m),
        cal_y,
    )


def get_first_quarter_months(fiscal_end_month):
    start = (int(fiscal_end_month) % 12) + 1
    return [((start - 1 + i) % 12) + 1 for i in range(3)]


def calendar_year_for_fiscal_month(fiscal_year, month, fiscal_end_month):
    if int(month) > int(fiscal_end_month):
        return int(fiscal_year) - 1
    return int(fiscal_year)


def get_q1_month_year_pairs(fiscal_year, fiscal_end_month):
    pairs = []
    for m in get_first_quarter_months(fiscal_end_month):
        cy = calendar_year_for_fiscal_month(fiscal_year, m, fiscal_end_month)
        pairs.append((cy, m))
    return pairs


def get_progress_based_on_reports(monthly_rows, target_year, fiscal_end_month):
    """
    محاسبه پیشرفت بر اساس تعداد ماه‌هایی که گزارش فروش برای آنها ثبت شده
    """
    try:
        start_month = (fiscal_end_month % 12) + 1
        reported_months = 0
        total_sales = 0
        
        for i in range(12):
            m = ((start_month - 1 + i) % 12) + 1
            cy = calendar_year_for_fiscal_month(target_year, m, fiscal_end_month)
            
            found = False
            for r in monthly_rows:
                if int(r["year_solar"]) == cy and int(r["month"]) == m:
                    tot = r["total_sales"]
                    if tot is None:
                        tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
                    if tot and float(tot) > 0:
                        found = True
                        total_sales += float(tot)
                    break
            
            if found:
                reported_months += 1
            else:
                break
        
        progress = (reported_months / 12) * 100
        return min(100, progress), reported_months, total_sales
    except Exception:
        return None, 0, 0


# ============================================================
# ✅ تابع اصلاح‌شده get_status_html (همانند dashboardtest.py)
# ============================================================
def get_status_html(coverage, progress):
    """بررسی وضعیت نسبت به برنامه - اصلاح‌شده نهایی"""
    if coverage is None or progress is None:
        return '<span style="color:#6b7280;">—</span>'
    
    try:
        coverage_val = float(coverage)
        progress_val = float(progress)
    except:
        return '<span style="color:#6b7280;">—</span>'
    
    # coverage به صورت اعشار هست (مثلاً 1.241)
    # progress به صورت درصد هست (مثلاً 58)
    progress_val = progress_val / 100
    
    # اگر coverage بیشتر از 10 باشه، یعنی به صورت درصد ذخیره شده (مثلاً 124)
    if coverage_val > 10:
        coverage_val = coverage_val / 100
    
    diff = coverage_val - progress_val
    diff_percent = diff * 100
    
    if diff > 0.05:
        return f'<span class="status-ahead">✅ جلوتر ({diff_percent:.1f}%)</span>'
    elif diff < -0.05:
        return f'<span class="status-behind">⚠️ عقب‌تر ({abs(diff_percent):.1f}%)</span>'
    else:
        return f'<span class="status-on-track">📊 طبق برنامه</span>'


def progress_html(progress, reported_months=None):
    """نمایش پیشرفت با ۴ مربع و تعداد ماه‌های گزارش‌شده"""
    if progress is None:
        return "—"
    
    try:
        progress_val = float(progress)
    except (TypeError, ValueError):
        return "—"
    
    if math.isnan(progress_val):
        return "—"
    
    if progress_val < 0 or progress_val > 100:
        return "—"
    
    filled = int(round(progress_val / 25))
    filled = min(4, max(0, filled))
    
    squares = []
    for i in range(4):
        if i < filled:
            squares.append('<span class="progress-square filled"></span>')
        else:
            squares.append('<span class="progress-square empty"></span>')
    
    month_text = ""
    if reported_months is not None and reported_months > 0:
        month_text = f'<span style="font-size:10px; color:#64748b; margin-right:4px;">({reported_months} ماه)</span>'
    
    return f'<div class="progress-box"><span class="progress-label">{int(progress_val)}%</span>{"".join(squares)}{month_text}</div>'


# ============================================================
# دیتابیس
# ============================================================
def get_companies():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, symbol, name_fa, industry, market_value, rank_in_industry,
               fiscal_end_month, fiscal_end_day
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
          AND p.year_solar BETWEEN ? AND ?
        ORDER BY p.year_solar DESC, p.period_type DESC
    """, (company_id, MIN_YEAR, MAX_YEAR)).fetchall()
    conn.close()
    return rows


def get_all_monthly_sales(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT year_solar, month, domestic_sales, export_sales, total_sales
        FROM monthly_sales
        WHERE company_id = ?
          AND year_solar BETWEEN ? AND ?
        ORDER BY year_solar, month
    """, (company_id, MIN_YEAR, MAX_YEAR)).fetchall()
    conn.close()
    return rows


def get_recurring_by_year(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT year_solar, SUM(amount) as total
        FROM non_operating_items
        WHERE company_id = ? AND is_recurring = 1
          AND year_solar BETWEEN ? AND ?
        GROUP BY year_solar ORDER BY year_solar
    """, (company_id, MIN_YEAR, MAX_YEAR)).fetchall()
    conn.close()
    return {r["year_solar"]: float(r["total"] or 0) for r in rows}


# ============================================================
# محاسبات
# ============================================================
def safe_div(a, b):
    try:
        if a is None or b is None or float(b) == 0:
            return None
        return float(a) / float(b)
    except Exception:
        return None


def positive_only(v):
    """سایر / غیرعملیاتی منفی در محاسبه لحاظ نشود."""
    try:
        if v is None:
            return 0.0
        x = float(v)
        return x if x > 0 else 0.0
    except Exception:
        return 0.0


def calc_metrics(row):
    revenue = row["operating_revenue"]
    other_inc = positive_only(row["other_income"])
    non_op = positive_only(row["non_operating_income"])
    net_profit = row["net_profit"]

    op_profit = None
    if net_profit is not None:
        op_profit = float(net_profit) - other_inc - non_op

    net_margin = safe_div(op_profit, revenue)
    recv_ratio = safe_div(row["trade_receivables"], row["current_assets"])
    div_ratio = safe_div(row["approved_dividend"], row["comprehensive_income"])
    return op_profit, net_margin, recv_ratio, div_ratio


def calc_forward_estimates(company, periods, monthly_rows):
    result = {
        "has_data": False, "target_year": None, "q1_revenue": None,
        "months_used": [], "sales_method1": None, "sales_method2": None,
        "sales_final": None, "margin_annual": None, "margin_last": None,
        "margin_avg": None, "est_profit": None, "est_recurring_non_op": None,
        "recurring_growth": None, "payout_avg": None, "est_dividend": None,
        "pe_forward": None, "pd_forward": None, "ps_forward": None, "message": "",
        "progress": None, "reported_months": 0, "actual_sales_current_year": None,
    }

    if not periods and not monthly_rows:
        result["message"] = "داده کافی برای برآورد وجود ندارد."
        return result

    fiscal_end_month = int(company["fiscal_end_month"] or 12)
    fiscal_end_day = int(company["fiscal_end_day"] or 29)
    market_value = company["market_value"]

    # سال‌های مالی واقعی از روی رکوردها
    fiscal_years = set()
    for r in periods:
        fiscal_years.add(resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day))
    for r in monthly_rows:
        fiscal_years.add(int(r["year_solar"]))

    all_years = sorted(y for y in fiscal_years if MIN_YEAR <= y <= MAX_YEAR)
    if not all_years:
        result["message"] = "هیچ داده‌ای ثبت نشده است."
        return result

    last_year = max(all_years)

    def has_annual_for(fy):
        for r in periods:
            if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == fy and int(r["period_type"]) == 12:
                return True
        return False

    has_annual_last = has_annual_for(last_year)
    target_year = last_year + 1 if has_annual_last else last_year
    result["target_year"] = target_year

    # ============================================================
    # پیشرفت بر اساس گزارش‌های موجود
    # ============================================================
    progress, reported_months, actual_sales = get_progress_based_on_reports(
        monthly_rows, target_year, fiscal_end_month
    )
    result["progress"] = progress
    result["reported_months"] = reported_months
    result["actual_sales_current_year"] = actual_sales if actual_sales > 0 else None

    # گزارش ۳ ماهه سال مالی هدف
    q1 = None
    for r in periods:
        if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == target_year and int(r["period_type"]) == 3:
            q1 = r
            break

    monthly_index = {}
    for r in monthly_rows:
        tot = r["total_sales"]
        if tot is None:
            tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
        if tot and float(tot) > 0:
            monthly_index[(int(r["year_solar"]), int(r["month"]))] = float(tot)

    q1_pairs = get_q1_month_year_pairs(target_year, fiscal_end_month)

    def collect_q1_sales():
        month_sales, used = {}, []
        for cy, m in q1_pairs:
            val = monthly_index.get((cy, m))
            if val is not None and val > 0:
                month_sales[m] = val
                used.append("{} {}".format(MONTH_NAMES.get(m, m), cy))
        return month_sales, used

    sales_m1 = sales_m2 = None
    months_used = []

    if q1 and q1["operating_revenue"] and float(q1["operating_revenue"]) > 0:
        rev = float(q1["operating_revenue"])
        result["q1_revenue"] = rev
        sales_m1 = (rev / 3.0) * 12.0
        month_sales, months_used = collect_q1_sales()
        if month_sales:
            ordered = [m for m in get_first_quarter_months(fiscal_end_month) if m in month_sales]
            last_val = month_sales[ordered[-1]]
            sum_existing = sum(month_sales.values())
            sales_m2 = last_val * (12 - len(month_sales)) + sum_existing
        else:
            sales_m2 = sales_m1
    else:
        month_sales, months_used = collect_q1_sales()
        if not month_sales:
            result["message"] = (
                "برای سال مالی {} نه گزارش سه‌ماهه و نه فروش ماهانه سه ماه اول وجود ندارد."
            ).format(target_year)
            return result
        n = len(month_sales)
        avg_month = sum(month_sales.values()) / float(n)
        sales_m1 = avg_month * 12.0
        ordered = [m for m in get_first_quarter_months(fiscal_end_month) if m in month_sales]
        last_val = month_sales[ordered[-1]]
        sum_existing = sum(month_sales.values())
        sales_m2 = last_val * (12 - n) + sum_existing
        result["q1_revenue"] = sum_existing

    result["months_used"] = months_used
    result["sales_method1"] = sales_m1
    result["sales_method2"] = sales_m2
    sales_final = min(sales_m1, sales_m2) if sales_m1 and sales_m2 else (sales_m1 or sales_m2)
    result["sales_final"] = sales_final

    # حاشیه سالانه = ۱۲ ماهه سال مالی قبل
    margin_annual = None
    for r in periods:
        if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == target_year - 1 and int(r["period_type"]) == 12:
            _, margin, _, _ = calc_metrics(r)
            if margin is not None:
                margin_annual = margin
            break

    margin_last = None
    candidates = []
    for r in periods:
        fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
        if fy <= target_year:
            candidates.append((fy, int(r["period_type"]), r))
    if candidates:
        non_annual = [c for c in candidates if c[1] != 12]
        pool = non_annual if non_annual else candidates
        last = max(pool, key=lambda x: (x[0], x[1]))
        _, margin, _, _ = calc_metrics(last[2])
        if margin is not None:
            margin_last = margin

    result["margin_annual"] = margin_annual
    result["margin_last"] = margin_last

    if margin_annual is not None and margin_last is not None:
        margin_avg = (margin_annual + margin_last) / 2.0
    elif margin_annual is not None:
        margin_avg = margin_annual
    elif margin_last is not None:
        margin_avg = margin_last
    else:
        result["message"] = "حاشیه سود سال قبل یا فصل آخر موجود نیست."
        return result

    result["margin_avg"] = margin_avg
    est_profit = sales_final * margin_avg

    recurring_map = get_recurring_by_year(company["id"])
    relevant = [y for y in sorted(recurring_map.keys()) if y < target_year]
    est_recurring = recurring_growth = None
    if len(relevant) >= 2:
        v1, v2 = recurring_map[relevant[-2]], recurring_map[relevant[-1]]
        recurring_growth = (v2 - v1) / v1 if v1 != 0 else 0
        est_recurring = v2 * (1 + recurring_growth)
    elif len(relevant) == 1:
        est_recurring = recurring_map[relevant[-1]]
        recurring_growth = 0

    result["est_recurring_non_op"] = est_recurring
    result["recurring_growth"] = recurring_growth
    if est_recurring is not None:
        est_profit = est_profit + est_recurring
    result["est_profit"] = est_profit

    payouts = []
    for y in [target_year - 1, target_year - 2]:
        for r in periods:
            if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == y and int(r["period_type"]) == 12:
                div, comp = r["approved_dividend"], r["comprehensive_income"]
                if div is not None and comp is not None and float(comp) != 0:
                    payouts.append(float(div) / float(comp))
                break
    payout_avg = sum(payouts) / len(payouts) if payouts else None
    result["payout_avg"] = payout_avg
    if payout_avg is not None and est_profit is not None:
        result["est_dividend"] = est_profit * payout_avg

    if market_value and est_profit and est_profit > 0:
        result["pe_forward"] = float(market_value) / est_profit
    if market_value and result.get("est_dividend") and result["est_dividend"] > 0:
        result["pd_forward"] = float(market_value) / result["est_dividend"]
    if market_value and sales_final and sales_final > 0:
        result["ps_forward"] = float(market_value) / sales_final

    result["has_data"] = True
    return result


def fmt(val):
    if val is None:
        return "—"
    try:
        return "{:,.0f}".format(float(val))
    except Exception:
        return "—"


def fmt_pct(val):
    if val is None:
        return "—"
    try:
        return "{:.1f}%".format(float(val) * 100)
    except Exception:
        return "—"


def fmt_ratio(val):
    if val is None:
        return "—"
    try:
        return "{:.2f}".format(float(val))
    except Exception:
        return "—"


def metric_card(title, value, bg="#f1f5f9", border="#cbd5e1", text="#0f172a"):
    st.markdown(
        '<div style="background:{bg};border:1.5px solid {border};border-radius:10px;'
        'padding:10px 8px;text-align:center;min-height:78px;">'
        '<div style="font-size:0.88rem;font-weight:600;color:#64748b;margin-bottom:4px;">{title}</div>'
        '<div style="font-size:1.15rem;font-weight:700;color:{text};">{value}</div></div>'.format(
            bg=bg, border=border, text=text, title=title, value=value
        ),
        unsafe_allow_html=True,
    )


def apply_chart_style(fig, title, x_title, y_title, cat_labels=None, y_suffix=""):
    xaxis = dict(
        title=dict(text=x_title, font=dict(size=13, color=AXIS_COLOR, family="Tahoma")),
        tickfont=dict(size=12, color=AXIS_COLOR, family="Tahoma"),
        linecolor="#334155",
        linewidth=1.5,
        gridcolor=GRID_COLOR,
        tickangle=-15,
    )
    if cat_labels is not None:
        xaxis["categoryorder"] = "array"
        xaxis["categoryarray"] = cat_labels

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=AXIS_COLOR, family="Tahoma")),
        xaxis=xaxis,
        yaxis=dict(
            title=dict(text=y_title, font=dict(size=13, color=AXIS_COLOR, family="Tahoma")),
            ticksuffix=y_suffix,
            tickfont=dict(size=12, color=AXIS_COLOR, family="Tahoma"),
            linecolor="#334155",
            linewidth=1.5,
            gridcolor=GRID_COLOR,
            zeroline=True,
            zerolinecolor="#94a3b8",
        ),
        legend=dict(orientation="h", y=1.12, font=dict(size=12, color=AXIS_COLOR)),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=30, t=70, b=90),
        hovermode="x unified",
        font=dict(color=AXIS_COLOR, size=12, family="Tahoma"),
    )
    return fig


# ============================================================
# UI
# ============================================================
companies = get_companies()
if not companies:
    st.warning("هنوز هیچ شرکتی ثبت نشده است.")
    st.stop()

search = st.text_input("جستجوی نماد یا نام شرکت", placeholder="مثال: شپنا").strip()
filtered = companies
if search:
    su = search.upper()
    filtered = [c for c in companies if su in (c["symbol"] or "").upper() or search in (c["name_fa"] or "")]
if not filtered:
    st.warning("شرکتی پیدا نشد.")
    st.stop()

company_options = {"{} — {}".format(c["symbol"], c["name_fa"] or ""): c for c in filtered}
selected_label = st.selectbox("انتخاب شرکت", options=list(company_options.keys()))
company = company_options[selected_label]
company_id = company["id"]
fiscal_end_month = int(company["fiscal_end_month"] or 12)
fiscal_end_day = int(company["fiscal_end_day"] or 29)

st.markdown("---")
st.subheader("{}  ·  {}".format(company["symbol"], company["name_fa"] or ""))

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("ارزش بازار", fmt(company["market_value"]))
with c2:
    metric_card("رتبه در صنعت", str(company["rank_in_industry"] or "—"))
with c3:
    metric_card("پایان سال مالی", "{} {}".format(fiscal_end_day, MONTH_NAMES.get(fiscal_end_month, "")))
with c4:
    metric_card("صنعت", company["industry"] or "—")

monthly_rows = get_all_monthly_sales(company_id)
periods = get_periods(company_id)

if monthly_rows:
    records = []
    for r in monthly_rows:
        tot = r["total_sales"]
        if tot is None:
            tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
        records.append({
            "سال": int(r["year_solar"]), "ماه": int(r["month"]),
            "داخلی": float(r["domestic_sales"] or 0),
            "صادراتی": float(r["export_sales"] or 0),
            "کل": float(tot or 0),
        })
    df_sales = pd.DataFrame(records)
    years_available = sorted(df_sales["سال"].unique().tolist())
else:
    df_sales = pd.DataFrame()
    years_available = []

color_map = {y: COLORS[i % len(COLORS)] for i, y in enumerate(years_available)}

# ============================================================
# Forward
# ============================================================
st.markdown("---")
st.subheader("برآورد و نسبت‌های Forward")

fwd = calc_forward_estimates(company, periods, monthly_rows)

if not fwd["has_data"]:
    st.info(fwd["message"] or "داده کافی برای محاسبه برآورد وجود ندارد.")
else:
    months_str = "، ".join(fwd["months_used"]) if fwd["months_used"] else "گزارش سه‌ماهه"
    st.caption("سال مالی هدف: {}  |  مبنا: {}".format(fwd["target_year"], months_str))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("برآورد فروش نرمال", fmt(fwd["sales_method1"]))
    with col2:
        metric_card("برآورد فروش بر اساس ماه آخر", fmt(fwd["sales_method2"]))
    with col3:
        metric_card("برآورد غیرعملیاتی تکرارپذیر", fmt(fwd.get("est_recurring_non_op")))
    with col4:
        metric_card("برآورد سود نهایی", fmt(fwd["est_profit"]))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("حاشیه سود سال قبل", fmt_pct(fwd["margin_annual"]))
    with col2:
        metric_card("حاشیه سود فصل آخر", fmt_pct(fwd["margin_last"]))
    with col3:
        metric_card("میانگین حاشیه سود", fmt_pct(fwd["margin_avg"]))
    with col4:
        metric_card("میانگین درصد تقسیم سود", fmt_pct(fwd["payout_avg"]))

    col1, col2, col3, col4 = st.columns(4)
    pe = fwd.get("pe_forward")
    with col1:
        if pe is None:
            metric_card("P/E Forward", "—")
        elif pe < 5:
            metric_card("P/E Forward", "{:.2f}".format(pe), "#dcfce7", "#16a34a", "#166534")
        elif pe <= 7:
            metric_card("P/E Forward", "{:.2f}".format(pe), "#fef9c3", "#ca8a04", "#854d0e")
        else:
            metric_card("P/E Forward", "{:.2f}".format(pe), "#fee2e2", "#dc2626", "#991b1b")
    with col2:
        metric_card("P/D Forward", fmt_ratio(fwd.get("pd_forward")))
    with col3:
        metric_card("سود تقسیمی برآوردی", fmt(fwd.get("est_dividend")))
    with col4:
        metric_card("P/S Forward", fmt_ratio(fwd.get("ps_forward")))
# ============================================================
# پیشرفت فروش (اصلاح‌شده نهایی)
# ============================================================
st.markdown("---")
st.subheader("📊 پیشرفت فروش")

if fwd.get("has_data") and fwd.get("sales_final") is not None:
    progress_val = fwd.get("progress")
    reported_months = fwd.get("reported_months", 0)
    actual_sales = fwd.get("actual_sales_current_year")
    estimated_sales = fwd.get("sales_final")
    
    # محاسبه نسبت پوشش
    coverage_ratio = None
    if actual_sales is not None and estimated_sales and estimated_sales > 0:
        try:
            coverage_ratio = float(actual_sales) / float(estimated_sales)
        except (TypeError, ValueError):
            coverage_ratio = None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # نمایش پیشرفت با مربع‌ها
        progress_display = progress_html(progress_val, reported_months)
        metric_card(
            "پیشرفت زمانی",
            progress_display,
            "#eff6ff", "#bfdbfe", "#1e40af"
        )
    
    with col2:
        metric_card(
            "فروش محقق‌شده",
            fmt(actual_sales),
            "#f0fdf4", "#bbf7d0", "#166534"
        )
        st.caption(f"تعداد ماه‌های گزارش: {reported_months}")
    
    with col3:
        coverage_display = fmt_pct(coverage_ratio) if coverage_ratio is not None else "—"
        if coverage_ratio is not None:
            if coverage_ratio >= 0.9:
                bg, border, text = "#dcfce7", "#16a34a", "#166534"
            elif coverage_ratio >= 0.6:
                bg, border, text = "#fef9c3", "#ca8a04", "#854d0e"
            else:
                bg, border, text = "#fee2e2", "#dc2626", "#991b1b"
        else:
            bg, border, text = "#f1f5f9", "#cbd5e1", "#0f172a"
        
        metric_card(
            "نسبت پوشش برآورد",
            coverage_display,
            bg, border, text
        )
    
    with col4:
        status_display = get_status_html(coverage_ratio, progress_val)
        metric_card(
            "وضعیت",
            status_display,
            "#f8fafc", "#e2e8f0", "#0f172a"
        )
    
    # ============================================================
    # ✅ توضیح مختصر - اصلاح‌شده نهایی
    # ============================================================
    if coverage_ratio is not None and progress_val is not None:
        # coverage_ratio به صورت اعشار هست (مثلاً 1.241 = 124.1%)
        # progress_val به صورت درصد هست (مثلاً 58 = 58%)
        
        # تبدیل progress_val به اعشار
        progress_decimal = progress_val / 100
        
        # محاسبه اختلاف به درصد
        diff_percent = (coverage_ratio - progress_decimal) * 100
        
        if diff_percent > 5:
            st.success(f"✅ شرکت {diff_percent:.1f}% از برنامه فروش جلوتر است.")
        elif diff_percent < -5:
            st.warning(f"⚠️ شرکت {abs(diff_percent):.1f}% از برنامه فروش عقب‌تر است.")
        else:
            st.info(f"📊 شرکت دقیقاً طبق برنامه فروش پیش می‌رود.")
else:
    st.info("داده کافی برای نمایش پیشرفت فروش وجود ندارد.")
# ============================================================
# گردش کالا و چرخه عملیات
# ============================================================
st.markdown("---")
st.subheader("🔄 گردش کالا و چرخه عملیات")

if periods:
    # دریافت داده‌های مورد نیاز
    rows_sorted = sorted(
        periods,
        key=lambda r: (
            resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day),
            int(r["period_type"]),
        )
    )
    
    # پیدا کردن آخرین دوره سالانه
    annual_periods = [r for r in rows_sorted if int(r["period_type"]) == 12]
    
    if annual_periods:
        latest_annual = annual_periods[-1]
        fy = resolve_fiscal_year(latest_annual, fiscal_end_month, fiscal_end_day)
        
        # محاسبه گردش موجودی کالا
        cogs = latest_annual["cogs"]
        inventory = latest_annual["inventory"]
        
        # برای میانگین موجودی، نیاز به موجودی دوره قبل داریم
        prev_inventory = None
        if len(annual_periods) >= 2:
            prev_annual = annual_periods[-2]
            prev_inventory = prev_annual["inventory"]
        
        # محاسبه گردش موجودی
        avg_inventory = None
        inventory_turnover = None
        days_inventory = None
        
        if inventory is not None and cogs is not None and float(cogs) > 0:
            if prev_inventory is not None:
                avg_inventory = (float(inventory) + float(prev_inventory)) / 2
            else:
                avg_inventory = float(inventory)
            
            if avg_inventory > 0:
                inventory_turnover = float(cogs) / avg_inventory
                days_inventory = 365 / inventory_turnover if inventory_turnover > 0 else None
        
        # محاسبه دوره وصول مطالبات (DSO)
        receivables = latest_annual["trade_receivables"]
        revenue = latest_annual["operating_revenue"]
        dso = None
        if receivables is not None and revenue is not None and float(revenue) > 0:
            dso = (float(receivables) / float(revenue)) * 365
        
        # محاسبه چرخه عملیات (بدون DPO)
        operating_cycle = None
        
        if days_inventory is not None and dso is not None:
            operating_cycle = days_inventory + dso
        
        # نمایش کارت‌های اطلاعاتی
        col1, col2, col3 ,col4= st.columns(4)
        with col1:
            metric_card(
                "گردش موجودی کالا",
                f"{inventory_turnover:.2f}" if inventory_turnover else "—",
                "#f0f9ff", "#bae6fd", "#0369a1"
            )
            st.caption(f"میانگین موجودی: {fmt(avg_inventory)}")
        
        with col2:
            metric_card(
                "دوره گردش موجودی (روز)",
                f"{days_inventory:.1f}" if days_inventory else "—",
                "#f0fdf4", "#bbf7d0", "#166534"
            )
        
        with col3:
            metric_card(
                "دوره وصول مطالبات (DSO)",
                f"{dso:.1f}" if dso else "—",
                "#fef3c7", "#fcd34d", "#92400e"
            )
     
        with col4:
            metric_card(
                "🔄 چرخه عملیات (روز)",
                f"{operating_cycle:.1f}" if operating_cycle else "—",
                "#eff6ff", "#bfdbfe", "#1e40af"
            )
            st.caption("دوره گردش موجودی + دوره وصول مطالبات")

        
        # توضیحات
        with st.expander("📖 توضیحات فرمول‌ها", expanded=False):
            st.markdown("""
            **گردش موجودی کالا** = بهای تمام‌شده / میانگین موجودی کالا
            - نشان‌دهنده تعداد دفعاتی است که موجودی کالا در طول سال به فروش می‌رسد.
            - هرچه بالاتر باشد، کارایی بیشتری در مدیریت موجودی دارد.
            
            **دوره گردش موجودی (روز)** = 365 / گردش موجودی کالا
            - میانگین تعداد روزهایی که کالا در انبار می‌ماند.
            
            **دوره وصول مطالبات (DSO)** = (مطالبات تجاری / درآمد عملیاتی) × 365
            - میانگین تعداد روزهایی که از مشتریان طلب داریم.
            
            **چرخه عملیات** = دوره گردش موجودی + دوره وصول مطالبات
            - مدت زمانی که از خرید مواد اولیه تا وصول وجه از مشتری طول می‌کشد.
            """)
        
    else:
        st.info("برای محاسبه گردش کالا و چرخه عملیات به دوره‌های سالانه نیاز است.")
else:
    st.info("دوره مالی ثبت نشده است.")

# ============================================================
# نمودارها
# ============================================================
st.markdown("---")
st.subheader("نمودارها")

if years_available:
    selected_years = st.multiselect(
        "سال‌های فروش ماهانه", options=years_available, default=list(years_available)
    )
else:
    selected_years = []
    st.info("فروش ماهانه‌ای ثبت نشده است.")

df_chart = (
    df_sales[df_sales["سال"].isin(selected_years)].copy()
    if selected_years and len(df_sales) else pd.DataFrame()
)


def build_period_chart(title, y_title, value_fn):
    if not periods:
        st.info("دوره مالی ثبت نشده است.")
        return

    ptypes, cat_labels = period_axis_categories(fiscal_end_month, fiscal_end_day)
    ptype_to_label = dict(zip(ptypes, cat_labels))

    records = []
    for r in periods:
        val = value_fn(r)
        if val is None:
            continue
        pt = int(r["period_type"])
        if pt not in ptype_to_label:
            continue
        fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
        records.append({
            "سال_مالی": fy,
            "دوره": pt,
            "برچسب": ptype_to_label[pt],
            "مقدار": val,
        })

    if not records:
        st.info("داده برای این نمودار موجود نیست.")
        return

    df_p = pd.DataFrame(records)
    fig = go.Figure()
    years_p = sorted(df_p["سال_مالی"].unique())

    for i, y in enumerate(years_p):
        d = df_p[df_p["سال_مالی"] == y].copy()
        d = d.sort_values("دوره").drop_duplicates(subset=["دوره"], keep="last")
        fig.add_trace(go.Scatter(
            x=d["برچسب"].tolist(),
            y=d["مقدار"].tolist(),
            mode="lines+markers+text",
            name=str(y),
            line=dict(width=2.8, color=COLORS[i % len(COLORS)]),
            marker=dict(size=9),
            text=["{:.1f}%".format(v) for v in d["مقدار"]],
            textposition="top center",
            textfont=dict(size=12, color=AXIS_COLOR, family="Tahoma"),
        ))

    apply_chart_style(fig, title, "دوره نسبت به سال مالی", y_title, cat_labels, y_suffix="%")
    st.plotly_chart(fig, use_container_width=True)


with st.expander("نمودار حاشیه سود بر اساس دوره", expanded=True):
    def margin_pct(r):
        _, m, _, _ = calc_metrics(r)
        if m is None or not r["operating_revenue"]:
            return None
        return m * 100
    build_period_chart("حاشیه سود خالص عملیاتی", "حاشیه سود (%)", margin_pct)

with st.expander("نمودار نسبت مطالبات به دارایی جاری", expanded=True):
    def recv_pct(r):
        _, _, rr, _ = calc_metrics(r)
        return None if rr is None else rr * 100
    build_period_chart("نسبت مطالبات به دارایی جاری", "نسبت مطالبات (%)", recv_pct)

with st.expander("نمودار فروش کل ماهانه", expanded=True):
    if selected_years and len(df_chart) > 0:
        fig = go.Figure()
        for y in selected_years:
            df_y = df_chart[df_chart["سال"] == y].sort_values("ماه")
            nonzero = df_y[df_y["کل"] > 0]
            if len(nonzero) == 0:
                continue
            last_m = int(nonzero["ماه"].max())
            df_y = df_y[df_y["ماه"] <= last_m]
            fig.add_trace(go.Scatter(
                x=df_y["ماه"].tolist(),
                y=df_y["کل"].tolist(),
                mode="lines+markers+text",
                name=str(y),
                line=dict(width=2.8, color=color_map.get(y, "#333")),
                marker=dict(size=8),
                text=["{:,.0f}".format(v) for v in df_y["کل"]],
                textposition="top center",
                textfont=dict(size=11, color=AXIS_COLOR, family="Tahoma"),
            ))
        fig.update_layout(
            xaxis=dict(
                title=dict(text="ماه", font=dict(size=13, color=AXIS_COLOR)),
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=[MONTH_NAMES[i] for i in range(1, 13)],
                tickfont=dict(size=12, color=AXIS_COLOR),
                linecolor="#334155", linewidth=1.5, gridcolor=GRID_COLOR,
            )
        )
        apply_chart_style(fig, "فروش کل ماهانه", "ماه", "میلیارد ریال")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("فروش ماهانه ثبت نشده است.")

with st.expander("نمودار فروش داخلی و صادراتی", expanded=False):
    if selected_years and len(df_chart) > 0:
        year_bar = st.selectbox(
            "سال", options=selected_years, index=len(selected_years) - 1, key="bar_year"
        )
        df_bar = df_chart[df_chart["سال"] == year_bar].sort_values("ماه")
        nonzero = df_bar[df_bar["کل"] > 0]
        if len(nonzero) > 0:
            last_m = int(nonzero["ماه"].max())
            df_bar = df_bar[df_bar["ماه"] <= last_m]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in df_bar["ماه"]],
            y=df_bar["داخلی"].tolist(),
            name="داخلی", marker_color="#2563eb",
            text=["{:,.0f}".format(v) for v in df_bar["داخلی"]],
            textposition="outside",
            textfont=dict(size=11, color=AXIS_COLOR),
        ))
        fig.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in df_bar["ماه"]],
            y=df_bar["صادراتی"].tolist(),
            name="صادراتی", marker_color="#ea580c",
            text=["{:,.0f}".format(v) for v in df_bar["صادراتی"]],
            textposition="outside",
            textfont=dict(size=11, color=AXIS_COLOR),
        ))
        apply_chart_style(
            fig,
            "فروش داخلی و صادراتی — {}".format(year_bar),
            "ماه",
            "میلیارد ریال",
        )
        fig.update_layout(barmode="group")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("داده موجود نیست.")

with st.expander("جدول رشد فروش ماهانه", expanded=False):
    if len(selected_years) >= 2 and len(df_chart) > 0:
        y_sorted = sorted(selected_years)
        growth_data = []
        for m in range(1, 13):
            row_g = {"ماه": MONTH_NAMES[m]}
            has_any = False
            for i, y in enumerate(y_sorted):
                val_s = df_chart[(df_chart["سال"] == y) & (df_chart["ماه"] == m)]["کل"]
                val = float(val_s.iloc[0]) if len(val_s) > 0 else None
                if val is not None and val > 0:
                    row_g[str(y)] = "{:,.0f}".format(val)
                    has_any = True
                else:
                    row_g[str(y)] = "—"
                if i > 0:
                    prev_y = y_sorted[i - 1]
                    prev_s = df_chart[(df_chart["سال"] == prev_y) & (df_chart["ماه"] == m)]["کل"]
                    prev_val = float(prev_s.iloc[0]) if len(prev_s) > 0 else None
                    if val and prev_val and prev_val > 0:
                        row_g["رشد {}".format(y)] = "{:+.1f}%".format((val - prev_val) / prev_val * 100)
                    else:
                        row_g["رشد {}".format(y)] = "—"
            if has_any:
                growth_data.append(row_g)
        if growth_data:
            st.table(pd.DataFrame(growth_data))
        else:
            st.info("داده‌ای برای مقایسه رشد نیست.")
    else:
        st.info("حداقل دو سال انتخاب کنید.")

# ============================================================
# آخرین دوره مالی
# ============================================================
st.markdown("---")
st.subheader("آخرین دوره مالی")

if not periods:
    st.info("دوره مالی ثبت نشده است.")
else:
    # مرتب‌سازی بر اساس سال مالی واقعی
    enriched = []
    for r in periods:
        fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
        enriched.append((fy, int(r["period_type"]), r))
    enriched.sort(key=lambda x: (x[0], x[1]), reverse=True)
    latest = enriched[0][2]
    latest_fy = enriched[0][0]

    op_p, margin, recv_r, div_r = calc_metrics(latest)
    st.caption(period_full_label(latest_fy, latest["period_type"], fiscal_end_month, fiscal_end_day))

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("درآمد عملیاتی", fmt(latest["operating_revenue"]))
    with k2:
        st.metric("سود خالص عملیاتی", fmt(op_p))
    with k3:
        st.metric("حاشیه سود", fmt_pct(margin))
    with k4:
        st.metric("نسبت مطالبات", fmt_pct(recv_r))
    with k5:
        st.metric("نسبت سود مصوب", fmt_pct(div_r))

    with st.expander("روند درآمد و سود سالانه", expanded=False):
        annual = []
        for r in periods:
            if int(r["period_type"]) == 12:
                fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
                annual.append((fy, r))
        if annual:
            annual = sorted(annual, key=lambda x: x[0])
            years_a = [a[0] for a in annual]
            revenues = [a[1]["operating_revenue"] or 0 for a in annual]
            op_profits = []
            for a in annual:
                op, _, _, _ = calc_metrics(a[1])
                op_profits.append(op if op is not None else 0)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=years_a, y=revenues, name="درآمد عملیاتی", marker_color="#2563eb"))
            fig.add_trace(go.Bar(x=years_a, y=op_profits, name="سود خالص عملیاتی", marker_color="#dc2626"))
            apply_chart_style(fig, "روند سالانه", "سال مالی", "میلیارد ریال")
            fig.update_layout(barmode="group", height=360)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("دوره سالانه ثبت نشده است.")

    with st.expander("جدول کامل دوره‌های مالی", expanded=True):
        data = []
        rows_sorted = sorted(
            periods,
            key=lambda r: (
                resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day),
                int(r["period_type"]),
            )
        )
        for row in rows_sorted:
            fy = resolve_fiscal_year(row, fiscal_end_month, fiscal_end_day)
            op_p, margin, recv_r, div_r = calc_metrics(row)
            data.append({
                "سال مالی": fy,
                "دوره": period_full_label(fy, row["period_type"], fiscal_end_month, fiscal_end_day),
                "درآمد عملیاتی": fmt(row["operating_revenue"]),
                "سود خالص": fmt(row["net_profit"]),
                "سود خالص عملیاتی": fmt(op_p),
                "حاشیه سود": fmt_pct(margin),
                "نسبت مطالبات": fmt_pct(recv_r),
                "حقوق مالکانه": fmt(row["equity"]),
            })
        st.table(pd.DataFrame(data))

    with st.expander("جزئیات یک دوره", expanded=False):
        period_labels = []
        period_rows = []
        for r in sorted(
            periods,
            key=lambda x: (
                resolve_fiscal_year(x, fiscal_end_month, fiscal_end_day),
                int(x["period_type"]),
            )
        ):
            fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
            period_labels.append(period_full_label(fy, r["period_type"], fiscal_end_month, fiscal_end_day))
            period_rows.append(r)

        chosen = st.selectbox("انتخاب دوره", options=period_labels)
        if chosen:
            idx = period_labels.index(chosen)
            row = period_rows[idx]
            op_p, margin, recv_r, div_r = calc_metrics(row)
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**سود و زیان**")
                st.write("درآمد عملیاتی: {}".format(fmt(row["operating_revenue"])))
                st.write("بهای تمام‌شده: {}".format(fmt(row["cogs"])))
                st.write("سایر درآمدها: {}".format(fmt(row["other_income"])))
                st.write("سایر غیرعملیاتی: {}".format(fmt(row["non_operating_income"])))
                st.write("سود خالص: {}".format(fmt(row["net_profit"])))
                st.write("**سود عملیاتی: {}**".format(fmt(op_p)))
                st.write("**حاشیه سود: {}**".format(fmt_pct(margin)))
            with d2:
                st.markdown("**ترازنامه**")
                st.write("موجودی کالا: {}".format(fmt(row["inventory"])))
                st.write("دریافتنی تجاری: {}".format(fmt(row["trade_receivables"])))
                st.write("حقوق مالکانه: {}".format(fmt(row["equity"])))
                st.write("دارایی جاری: {}".format(fmt(row["current_assets"])))
                st.write("جمع دارایی‌ها: {}".format(fmt(row["total_assets"])))
                st.write("**نسبت مطالبات: {}**".format(fmt_pct(recv_r)))
            with d3:
                st.markdown("**سایر**")
                st.write("سود جامع: {}".format(fmt(row["comprehensive_income"])))
                st.write("سود مصوب: {}".format(fmt(row["approved_dividend"])))
                st.write("**نسبت سود مصوب: {}**".format(fmt_pct(div_r)))

# ============================================================
# امضای نویسنده
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; font-size: 16px; color: #475569; border-top: 2px solid #e8ecf1;">
    📈 تحلیل از <strong style="color: #2563eb;">داود شورگشتی</strong>
</div>
""", unsafe_allow_html=True)