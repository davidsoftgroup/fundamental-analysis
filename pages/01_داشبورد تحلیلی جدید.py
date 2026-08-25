# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import math
import jdatetime

# ============================================================
# import نسبی
# ============================================================
from ..utils.database import get_connection, init_db
from ..utils.styles import apply_styles

st.set_page_config(page_title="داشبورد", layout="wide", initial_sidebar_state="expanded")
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
    
    /* ==========================================
       استایل تب‌ها
       ========================================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f1f5f9;
        border-radius: 12px;
        padding: 6px;
        direction: rtl;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        font-size: 15px;
        color: #475569;
        background-color: transparent;
        transition: all 0.2s ease;
        font-family: 'Vazirmatn', Tahoma, 'Segoe UI', sans-serif !important;
        white-space: nowrap;
        min-height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.15);
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }
    .stTabs [data-baseweb="tab"] p {
        font-family: 'Vazirmatn', Tahoma, 'Segoe UI', sans-serif !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) p {
        color: #475569 !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
    }
    
    /* ==========================================
       استایل چاپ
       ========================================== */
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; }
        .stTabs { display: none !important; }
        .st-emotion-cache-1y4p8pa { padding: 0 !important; }
        .report-container { 
            background: white !important;
            padding: 20px !important;
            font-size: 12px !important;
        }
        .season-card {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
            border: 1px solid #ddd !important;
        }
        .metric-card-print {
            border: 1px solid #ddd !important;
            padding: 8px !important;
            margin: 4px !important;
            border-radius: 4px !important;
        }
        table {
            font-size: 11px !important;
        }
        .heatmap-container {
            page-break-inside: avoid !important;
        }
        .conclusion-box {
            border: 2px solid #2563eb !important;
            padding: 15px !important;
            border-radius: 8px !important;
            background: #f8fafc !important;
        }
        .best-season { color: #16a34a !important; font-weight: bold !important; }
        .worst-season { color: #dc2626 !important; font-weight: bold !important; }
    }
    
    .print-button {
        background: #0f172a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 25px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        margin-bottom: 20px;
    }
    .print-button:hover {
        background: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    .report-container {
        background: white;
        padding: 20px;
        border-radius: 12px;
    }
    .season-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .season-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .best-season { color: #16a34a !important; font-weight: 700 !important; }
    .worst-season { color: #dc2626 !important; font-weight: 700 !important; }
    
    * {
        font-family: 'Vazirmatn', Tahoma, 'Segoe UI', sans-serif !important;
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
    months_back = {12: 0, 9: 3, 6: 6, 3: 9}
    back = months_back.get(int(period_type), 0)
    end_month = int(fiscal_end_month) - back
    cal_year = int(fiscal_year)
    if end_month <= 0:
        end_month += 12
        cal_year -= 1
    return cal_year, end_month, int(fiscal_end_day or 29)


def resolve_fiscal_year(row, fiscal_end_month, fiscal_end_day=29):
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
# توابع کمکی
# ============================================================
def get_status_html(coverage, progress):
    if coverage is None or progress is None:
        return '<span style="color:#6b7280;">—</span>'
    
    try:
        coverage_val = float(coverage)
        progress_val = float(progress)
    except:
        return '<span style="color:#6b7280;">—</span>'
    
    progress_val = progress_val / 100
    
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
        "payout_from_meeting": False, "payout_source": "financial"
    }

    if not periods and not monthly_rows:
        result["message"] = "داده کافی برای برآورد وجود ندارد."
        return result

    fiscal_end_month = int(company["fiscal_end_month"] or 12)
    fiscal_end_day = int(company["fiscal_end_day"] or 29)
    market_value = company["market_value"]

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

    progress, reported_months, actual_sales = get_progress_based_on_reports(
        monthly_rows, target_year, fiscal_end_month
    )
    result["progress"] = progress
    result["reported_months"] = reported_months
    result["actual_sales_current_year"] = actual_sales if actual_sales > 0 else None

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

    # ============================================================
    # محاسبه میانگین درصد سود تقسیمی - اولویت با جدول تصمیمات مجمع
    # ============================================================
    payouts = []
    payout_source = "financial"  # پیش‌فرض: از صورت‌های مالی
    payout_from_meeting = False
    
    # 1. ابتدا از جدول تصمیمات مجمع (meeting_decisions) امتحان کن
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # دریافت تصمیمات مجمع برای این شرکت
        cursor.execute("""
            SELECT dividend_percent, year_solar, approved_dividend, net_profit
            FROM meeting_decisions 
            WHERE symbol = ?
            ORDER BY year_solar DESC
            LIMIT 3
        """, (company["symbol"],))
        
        meeting_rows = cursor.fetchall()
        conn.close()
        
        if meeting_rows:
            # اگر اطلاعات در جدول تصمیمات مجمع وجود دارد
            for row in meeting_rows:
                dividend_percent = row[0]
                if dividend_percent is not None and dividend_percent > 0:
                    # تبدیل درصد به نسبت (مثلاً 57.3% → 0.573)
                    payouts.append(dividend_percent / 100)
            
            if payouts:
                payout_source = "meeting"
                payout_from_meeting = True
                
    except Exception as e:
        # در صورت خطا، ادامه با روش قبلی
        pass
    
    # 2. اگر اطلاعاتی از جدول تصمیمات مجمع پیدا نشد، از صورت‌های مالی استفاده کن
    if not payouts:
        for y in [target_year - 1, target_year - 2]:
            for r in periods:
                if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == y and int(r["period_type"]) == 12:
                    div, comp = r["approved_dividend"], r["comprehensive_income"]
                    if div is not None and comp is not None and float(comp) != 0:
                        payouts.append(float(div) / float(comp))
                    break
    
    # 3. اگر هیچ اطلاعاتی از هیچکدام نبود، از میانگین ۵۰% استفاده کن
    if not payouts:
        payouts = [0.5]  # مقدار پیش‌فرض ۵۰%
        payout_source = "default"
    
    # محاسبه میانگین
    payout_avg = sum(payouts) / len(payouts) if payouts else None
    result["payout_avg"] = payout_avg
    result["payout_source"] = payout_source
    result["payout_from_meeting"] = payout_from_meeting
    
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


def get_season_label(season):
    labels = {
        "Q1": "فصل ۱",
        "Q2": "فصل ۲",
        "Q3": "فصل ۳",
        "Q4": "فصل ۴"
    }
    return labels.get(season, season)


def get_season_color(season):
    colors = {
        "Q1": "#2563eb",
        "Q2": "#16a34a",
        "Q3": "#ea580c",
        "Q4": "#dc2626"
    }
    return colors.get(season, "#6b7280")


# ============================================================
# توابع بخش‌های مختلف
# ============================================================
def show_main_dashboard(company, periods, monthly_rows, df_sales, years_available, 
                         fiscal_end_month, fiscal_end_day, color_map):
    """تب اصلی - اطلاعات شرکت، برآوردها، پیشرفت فروش، گردش کالا"""
    
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
    
    st.markdown("---")
    
    # ============================================================
    # Forward
    # ============================================================
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
            # ============================================================
            # میانگین درصد سود تقسیمی - با نمایش منبع
            # ============================================================
            payout_display = fmt_pct(fwd["payout_avg"])
            payout_source = fwd.get("payout_source", "financial")
            
            if payout_source == "meeting":
                payout_display += " 📋"
                tooltip = "بر اساس تصمیمات مجمع"
            elif payout_source == "default":
                payout_display += " ⚠️"
                tooltip = "مقدار پیش‌فرض ۵۰%"
            else:
                tooltip = "بر اساس صورت‌های مالی"
            
            metric_card("میانگین درصد سود تقسیمی", payout_display, "#f8fafc", "#e2e8f0", "#0f172a")
            st.caption(tooltip)
    
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
            # ============================================================
            # سود تقسیمی برآوردی - با نمایش منبع
            # ============================================================
            est_dividend = fwd.get("est_dividend")
            if est_dividend is not None:
                if fwd.get("payout_source") == "meeting":
                    dividend_display = fmt(est_dividend) + " 📋"
                elif fwd.get("payout_source") == "default":
                    dividend_display = fmt(est_dividend) + " ⚠️"
                else:
                    dividend_display = fmt(est_dividend)
            else:
                dividend_display = "—"
            
            metric_card("سود تقسیمی برآوردی", dividend_display, "#f8fafc", "#e2e8f0", "#0f172a")
            if fwd.get("payout_source") == "meeting":
                st.caption("📋 بر اساس تصمیمات مجمع")
            elif fwd.get("payout_source") == "default":
                st.caption("⚠️ بر اساس پیش‌فرض ۵۰%")
            else:
                st.caption("بر اساس صورت‌های مالی")
        with col4:
            metric_card("P/S Forward", fmt_ratio(fwd.get("ps_forward")))
    
        # ============================================================
        # تحلیل ارزش بازار بر اساس P/E=5
        # ============================================================
        st.markdown("---")
        st.subheader("🎯 تحلیل ارزش بازار هدف (بر اساس P/E=5)")
    
        est_profit = fwd.get("est_profit")
        current_market_value = company["market_value"]
        
        if est_profit is not None and est_profit > 0 and current_market_value is not None and current_market_value > 0:
            target_pe = 5
            target_market_value = est_profit * target_pe
            current_pe = current_market_value / est_profit
            diff_percent = ((target_market_value - current_market_value) / current_market_value) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if current_pe <= 5:
                    metric_card("وضعیت P/E فعلی", "✅ عالی (زیر ۵)", "#dcfce7", "#16a34a", "#166534")
                elif current_pe <= 7:
                    metric_card("وضعیت P/E فعلی", "🟡 مناسب (۵ تا ۷)", "#fef9c3", "#ca8a04", "#854d0e")
                else:
                    metric_card("وضعیت P/E فعلی", "🔴 گران (بالای ۷)", "#fee2e2", "#dc2626", "#991b1b")
            
            with col2:
                metric_card("P/E فعلی شرکت", f"{current_pe:.2f}", "#f8fafc", "#e2e8f0", "#0f172a")
            
            with col3:
                metric_card("ارزش بازار فعلی", fmt(current_market_value), "#f8fafc", "#e2e8f0", "#0f172a")
            
            with col4:
                metric_card("ارزش بازار هدف (P/E=5)", fmt(target_market_value), "#eff6ff", "#bfdbfe", "#1e40af")
            
            st.markdown("---")
            st.markdown("#### 📊 تحلیل اصلاح قیمت برای رسیدن به P/E=5")
            
            if current_market_value > target_market_value:
                correction_needed = ((current_market_value - target_market_value) / current_market_value) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric_card("🔻 درصد اصلاح مورد نیاز", f"{correction_needed:.1f}%", "#fee2e2", "#dc2626", "#991b1b")
                    st.caption("برای رسیدن به P/E=5")
                
                with col2:
                    metric_card("💰 ارزش بازار هدف", fmt(target_market_value), "#eff6ff", "#bfdbfe", "#1e40af")
                
                with col3:
                    if current_pe > 5:
                        buy_percent = (target_market_value / current_market_value) * 100
                        metric_card("📊 نسبت قیمت هدف به فعلی", f"{buy_percent:.1f}%", "#fef3c7", "#fcd34d", "#92400e")
                        st.caption(f"ارزش بازار هدف {buy_percent:.1f}% ارزش فعلی")
                
                st.markdown(f"""
                <div style="background: #f1f5f9; border-radius: 12px; padding: 20px; border-right: 4px solid #dc2626; margin-top: 10px;">
                    <div style="font-size: 15px; line-height: 2; color: #0f172a;">
                        <strong>📈 تحلیل قیمت:</strong>
                        <ul style="list-style: none; padding-right: 20px; margin: 10px 0;">
                            <li>💰 <strong>ارزش بازار فعلی</strong>: {fmt(current_market_value)} میلیارد ریال</li>
                            <li>🎯 <strong>ارزش بازار هدف (P/E=5)</strong>: {fmt(target_market_value)} میلیارد ریال</li>
                            <li>📉 <strong>درصد اصلاح مورد نیاز</strong>: <span style="color: #dc2626; font-weight: bold;">{correction_needed:.1f}%</span></li>
                        </ul>
                        <div style="margin-top: 8px; padding: 10px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                            <strong>💡 توصیه:</strong>
                            {'با توجه به P/E بالای ۵، قیمت فعلی نسبت به ارزش منصفانه (P/E=5) گران است. ' +
                            f'برای خرید با P/E=5، قیمت باید حدود {correction_needed:.1f}% کاهش یابد.' if current_pe > 5 else
                            'قیمت فعلی بسیار مناسب است و از P/E=5 پایین‌تر است.'}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            elif current_market_value < target_market_value:
                upside_percent = ((target_market_value - current_market_value) / current_market_value) * 100
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric_card("📈 پتانسیل رشد", f"{upside_percent:.1f}%", "#dcfce7", "#16a34a", "#166534")
                    st.caption("تا رسیدن به P/E=5")
                
                with col2:
                    metric_card("💰 ارزش بازار هدف", fmt(target_market_value), "#eff6ff", "#bfdbfe", "#1e40af")
                
                with col3:
                    metric_card("✅ وضعیت", "ارزان", "#dcfce7", "#16a34a", "#166534")
                    st.caption("P/E کمتر از ۵")
                
                st.markdown(f"""
                <div style="background: #f1f5f9; border-radius: 12px; padding: 20px; border-right: 4px solid #16a34a; margin-top: 10px;">
                    <div style="font-size: 15px; line-height: 2; color: #0f172a;">
                        <strong>📈 تحلیل قیمت:</strong>
                        <ul style="list-style: none; padding-right: 20px; margin: 10px 0;">
                            <li>💰 <strong>ارزش بازار فعلی</strong>: {fmt(current_market_value)} میلیارد ریال</li>
                            <li>🎯 <strong>ارزش بازار هدف (P/E=5)</strong>: {fmt(target_market_value)} میلیارد ریال</li>
                            <li>📈 <strong>پتانسیل رشد</strong>: <span style="color: #16a34a; font-weight: bold;">{upside_percent:.1f}%</span></li>
                        </ul>
                        <div style="margin-top: 8px; padding: 10px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                            <strong>💡 توصیه:</strong>
                            قیمت فعلی بسیار مناسب است و از P/E=5 پایین‌تر است. پتانسیل رشد {upside_percent:.1f}% تا رسیدن به ارزش منصفانه وجود دارد.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.success("✅ ارزش بازار فعلی دقیقاً برابر با ارزش بازار هدف (P/E=5) است.")
            
            with st.expander("📖 توضیحات", expanded=False):
                st.markdown("""
                **P/E (Price to Earnings)**:
                - نسبت قیمت به سود هر سهم است.
                - P/E = قیمت هر سهم / سود هر سهم
                
                **چرا P/E=5 معیار خوبی برای خرید است؟**
                - در بورس ایران، معمولاً P/E زیر ۵ برای خرید مناسب در نظر گرفته می‌شود.
                - این نشان‌دهنده این است که شرکت با قیمت مناسبی معامله می‌شود.
                
                **ارزش بازار هدف**:
                - ارزش بازار = سود خالص × P/E
                - در این تحلیل، P/E=5 به عنوان معیار خرید در نظر گرفته شده است.
                """)
        else:
            st.info("برای محاسبه ارزش بازار هدف، به سود برآوردی معتبر نیاز است.")
    
    # ============================================================
    # پیشرفت فروش
    # ============================================================
    st.markdown("---")
    st.subheader("📊 پیشرفت فروش")
    
    if fwd.get("has_data") and fwd.get("sales_final") is not None:
        progress_val = fwd.get("progress")
        reported_months = fwd.get("reported_months", 0)
        actual_sales = fwd.get("actual_sales_current_year")
        estimated_sales = fwd.get("sales_final")
        
        coverage_ratio = None
        if actual_sales is not None and estimated_sales and estimated_sales > 0:
            try:
                coverage_ratio = float(actual_sales) / float(estimated_sales)
            except (TypeError, ValueError):
                coverage_ratio = None
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            progress_display = progress_html(progress_val, reported_months)
            metric_card("پیشرفت زمانی", progress_display, "#eff6ff", "#bfdbfe", "#1e40af")
        
        with col2:
            metric_card("فروش محقق‌شده", fmt(actual_sales), "#f0fdf4", "#bbf7d0", "#166534")
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
            
            metric_card("نسبت پوشش برآورد", coverage_display, bg, border, text)
        
        with col4:
            status_display = get_status_html(coverage_ratio, progress_val)
            metric_card("وضعیت", status_display, "#f8fafc", "#e2e8f0", "#0f172a")
        
        if coverage_ratio is not None and progress_val is not None:
            progress_decimal = progress_val / 100
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
        rows_sorted = sorted(
            periods,
            key=lambda r: (
                resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day),
                int(r["period_type"]),
            )
        )
        
        annual_periods = [r for r in rows_sorted if int(r["period_type"]) == 12]
        
        if annual_periods:
            latest_annual = annual_periods[-1]
            
            cogs = latest_annual["cogs"]
            inventory = latest_annual["inventory"]
            
            prev_inventory = None
            if len(annual_periods) >= 2:
                prev_annual = annual_periods[-2]
                prev_inventory = prev_annual["inventory"]
            
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
            
            receivables = latest_annual["trade_receivables"]
            revenue = latest_annual["operating_revenue"]
            dso = None
            if receivables is not None and revenue is not None and float(revenue) > 0:
                dso = (float(receivables) / float(revenue)) * 365
            
            operating_cycle = None
            if days_inventory is not None and dso is not None:
                operating_cycle = days_inventory + dso
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card("گردش موجودی کالا", f"{inventory_turnover:.2f}" if inventory_turnover else "—", 
                           "#f0f9ff", "#bae6fd", "#0369a1")
                st.caption(f"میانگین موجودی: {fmt(avg_inventory)}")
            
            with col2:
                metric_card("دوره گردش موجودی (روز)", f"{days_inventory:.1f}" if days_inventory else "—",
                           "#f0fdf4", "#bbf7d0", "#166534")
            
            with col3:
                metric_card("دوره وصول مطالبات (DSO)", f"{dso:.1f}" if dso else "—",
                           "#fef3c7", "#fcd34d", "#92400e")
            
            with col4:
                metric_card("🔄 چرخه عملیات (روز)", f"{operating_cycle:.1f}" if operating_cycle else "—",
                           "#eff6ff", "#bfdbfe", "#1e40af")
                st.caption("دوره گردش موجودی + دوره وصول مطالبات")
        else:
            st.info("برای محاسبه گردش کالا و چرخه عملیات به دوره‌های سالانه نیاز است.")
    else:
        st.info("دوره مالی ثبت نشده است.")


# ============================================================
# تب تحلیل فصلی
# ============================================================
def show_seasonal_analysis(periods, monthly_rows, fiscal_end_month, fiscal_end_day):
    """تب تحلیل فصلی با رنگ‌بندی و نمودارهای پیشرفته"""
    
    st.subheader("📊 تحلیل فصلی درآمد عملیاتی")
    
    def calculate_seasonal_revenue_advanced(periods, monthly_rows, fiscal_end_month, fiscal_end_day):
        fiscal_years = {}
        
        for r in periods:
            fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
            pt = int(r["period_type"])
            
            if pt in [3, 6, 9, 12]:
                if fy not in fiscal_years:
                    fiscal_years[fy] = {}
                fiscal_years[fy][pt] = r
        
        seasonal_data = {}
        
        for fy, periods_dict in fiscal_years.items():
            data = {
                "Q1": None, "Q2": None, "Q3": None, "Q4": None,
                "total": None, "available_seasons": [], "periods_available": []
            }
            
            if 3 in periods_dict:
                q1 = periods_dict[3]["operating_revenue"] or 0
                data["Q1"] = q1
                data["available_seasons"].append("Q1")
                data["periods_available"].append(3)
                
                if 6 in periods_dict:
                    q2 = (periods_dict[6]["operating_revenue"] or 0) - q1
                    data["Q2"] = q2
                    data["available_seasons"].append("Q2")
                    data["periods_available"].append(6)
                    
                    if 9 in periods_dict:
                        q3 = (periods_dict[9]["operating_revenue"] or 0) - (periods_dict[6]["operating_revenue"] or 0)
                        data["Q3"] = q3
                        data["available_seasons"].append("Q3")
                        data["periods_available"].append(9)
                        
                        if 12 in periods_dict:
                            q4 = (periods_dict[12]["operating_revenue"] or 0) - (periods_dict[9]["operating_revenue"] or 0)
                            data["Q4"] = q4
                            data["total"] = periods_dict[12]["operating_revenue"] or 0
                            data["available_seasons"].append("Q4")
                            data["periods_available"].append(12)
                        else:
                            data["total"] = periods_dict[9]["operating_revenue"] or 0
                    else:
                        data["total"] = periods_dict[6]["operating_revenue"] or 0
                else:
                    data["total"] = q1
            
            if data["available_seasons"]:
                seasonal_data[fy] = data
        
        return seasonal_data
    
    if periods:
        seasonal_data = calculate_seasonal_revenue_advanced(periods, monthly_rows, fiscal_end_month, fiscal_end_day)
        
        valid_years = []
        for fy, data in seasonal_data.items():
            has_valid_season = False
            for season in ["Q1", "Q2", "Q3", "Q4"]:
                if data[season] is not None and data[season] > 0:
                    has_valid_season = True
                    break
            
            if has_valid_season or (data["total"] is not None and data["total"] > 0):
                valid_years.append(fy)
        
        seasonal_data = {fy: seasonal_data[fy] for fy in valid_years}
        
        if seasonal_data:
            years_sorted = sorted(seasonal_data.keys())
            
            # ============================================================
            # وضعیت دوره‌ها
            # ============================================================
            st.info("📌 وضعیت دوره‌های موجود برای هر سال مالی:")
            
            status_data = []
            for fy in sorted(seasonal_data.keys()):
                data = seasonal_data[fy]
                status_row = {"سال مالی": fy}
                
                period_status = {
                    "۳ ماهه": "✅" if 3 in data["periods_available"] else "❌",
                    "۶ ماهه": "✅" if 6 in data["periods_available"] else "❌",
                    "۹ ماهه": "✅" if 9 in data["periods_available"] else "❌",
                    "۱۲ ماهه": "✅" if 12 in data["periods_available"] else "❌"
                }
                status_row.update(period_status)
                
                actual_seasons = 0
                for season in ["Q1", "Q2", "Q3", "Q4"]:
                    if data[season] is not None and data[season] > 0:
                        actual_seasons += 1
                
                status_row["فصل‌های قابل محاسبه"] = f"{actual_seasons} فصل"
                status_row["توضیح"] = f"{actual_seasons} از ۴ فصل"
                status_data.append(status_row)
            
            st.table(pd.DataFrame(status_data))
            
            # ============================================================
            # جدول فصلی
            # ============================================================
            st.markdown("#### 📋 جدول درآمد فصلی")
            
            df_seasonal_rows = []
            for fy in sorted(seasonal_data.keys()):
                data = seasonal_data[fy]
                
                actual_seasons = 0
                season_values = {}
                for season in ["Q1", "Q2", "Q3", "Q4"]:
                    val = data[season]
                    if val is not None and val > 0:
                        actual_seasons += 1
                        season_values[season] = val
                    else:
                        season_values[season] = None
                
                row = {
                    "سال مالی": fy,
                    "فصل ۱ (۳ ماهه)": fmt(season_values["Q1"]) if season_values["Q1"] is not None else "—",
                    "فصل ۲ (۳-۶ ماهه)": fmt(season_values["Q2"]) if season_values["Q2"] is not None else "—",
                    "فصل ۳ (۶-۹ ماهه)": fmt(season_values["Q3"]) if season_values["Q3"] is not None else "—",
                    "فصل ۴ (۹-۱۲ ماهه)": fmt(season_values["Q4"]) if season_values["Q4"] is not None else "—",
                    "کل (تا آخرین دوره)": fmt(data["total"]) if data["total"] is not None else "—",
                    "تعداد فصل": f"{actual_seasons}/۴"
                }
                df_seasonal_rows.append(row)
            
            st.table(pd.DataFrame(df_seasonal_rows))
            
            # ============================================================
            # 📊 نمودار مقایسه فصلی
            # ============================================================
            st.markdown("#### 📊 نمودار مقایسه درآمد فصلی")
            
            fig_seasons = go.Figure()
            
            season_order = ["Q1", "Q2", "Q3", "Q4"]
            season_labels = {
                "Q1": "فصل ۱",
                "Q2": "فصل ۲",
                "Q3": "فصل ۳",
                "Q4": "فصل ۴"
            }
            season_colors = {
                "Q1": "#2563eb",
                "Q2": "#16a34a",
                "Q3": "#ea580c",
                "Q4": "#dc2626"
            }
            
            for season in season_order:
                values = []
                for y in years_sorted:
                    data = seasonal_data[y]
                    val = data[season]
                    if val is not None and val > 0:
                        values.append(val)
                    else:
                        values.append(None)
                
                fig_seasons.add_trace(go.Bar(
                    x=[str(y) for y in years_sorted],
                    y=values,
                    name=season_labels[season],
                    marker_color=season_colors[season],
                    text=[fmt(v) if v is not None else "—" for v in values],
                    textposition="outside",
                    textfont=dict(size=11, color="#0f172a", family="Tahoma"),
                    hovertemplate="%{x}<br>%{fullData.name}: %{text}<extra></extra>"
                ))
            
            apply_chart_style(
                fig_seasons,
                "مقایسه درآمد فصلی در سال‌های مختلف",
                "سال مالی",
                "میلیارد ریال",
                cat_labels=[str(y) for y in years_sorted],
                y_suffix=""
            )
            fig_seasons.update_layout(
                barmode="group",
                height=450,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12, color="#0f172a", family="Tahoma")
                )
            )
            st.plotly_chart(fig_seasons, use_container_width=True)
            
            # ============================================================
            # 📈 نمودار روند هر فصل
            # ============================================================
            st.markdown("#### 📈 روند درآمد هر فصل در طول سال‌ها")
            
            fig_trend = go.Figure()
            
            for season in season_order:
                values = []
                years_show = []
                
                for y in years_sorted:
                    data = seasonal_data[y]
                    if data[season] is not None and data[season] > 0:
                        values.append(data[season])
                        years_show.append(y)
                
                if len(values) >= 2:
                    fig_trend.add_trace(go.Scatter(
                        x=[str(y) for y in years_show],
                        y=values,
                        mode="lines+markers+text",
                        name=season_labels[season],
                        line=dict(width=3, color=season_colors[season]),
                        marker=dict(size=10),
                        text=[fmt(v) for v in values],
                        textposition="top center",
                        textfont=dict(size=11, color="#0f172a", family="Tahoma"),
                        hovertemplate="%{x}<br>%{fullData.name}: %{text}<extra></extra>"
                    ))
            
            if len(fig_trend.data) > 0:
                apply_chart_style(
                    fig_trend,
                    "روند درآمد فصلی در سال‌های مختلف",
                    "سال مالی",
                    "میلیارد ریال",
                    cat_labels=[str(y) for y in years_sorted],
                    y_suffix=""
                )
                fig_trend.update_layout(
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12, color="#0f172a", family="Tahoma")
                    )
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("برای نمایش روند هر فصل به حداقل ۲ سال داده نیاز است.")
            
            # ============================================================
            # بهترین و بدترین عملکرد در هر سال با رنگ‌بندی
            # ============================================================
            st.markdown("#### 🏆 بهترین و بدترین عملکرد فصلی در هر سال")
            
            yearly_season_performance = {}
            for y in years_sorted:
                data = seasonal_data[y]
                season_values = {}
                for season in ["Q1", "Q2", "Q3", "Q4"]:
                    if data[season] is not None and data[season] > 0:
                        season_values[season] = data[season]
                
                if len(season_values) >= 2:
                    sorted_seasons = sorted(season_values.items(), key=lambda x: x[1], reverse=True)
                    yearly_season_performance[y] = {
                        "best": sorted_seasons[0],
                        "worst": sorted_seasons[-1],
                        "all": season_values,
                        "total": sum(season_values.values())
                    }
            
            if yearly_season_performance:
                st.markdown("##### عملکرد فصلی هر سال")
                
                num_years = len(yearly_season_performance)
                cols_per_row = 2
                year_items = sorted(yearly_season_performance.items(), reverse=True)
                
                for i in range(0, num_years, cols_per_row):
                    row_cols = st.columns(min(cols_per_row, num_years - i))
                    for j, (y, perf) in enumerate(year_items[i:i+cols_per_row]):
                        with row_cols[j]:
                            total = perf['total']
                            best_pct = (perf['best'][1] / total * 100) if total > 0 else 0
                            worst_pct = (perf['worst'][1] / total * 100) if total > 0 else 0
                            
                            st.markdown(f"""
                            <div class="season-card">
                                <div style="font-weight: 700; font-size: 18px; color: #0f172a; text-align: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 10px;">
                                    سال {y}
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; background: #f0fdf4; border-radius: 6px; padding: 6px 10px; margin-bottom: 4px;">
                                    <span style="color: #16a34a; font-weight: 600;">🏆 بهترین</span>
                                    <span style="color: #16a34a; font-weight: 700; font-size: 15px;">
                                        {get_season_label(perf['best'][0])}: {fmt(perf['best'][1])} 
                                        <span style="font-size: 12px; color: #64748b;">({best_pct:.1f}%)</span>
                                    </span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0; background: #fef2f2; border-radius: 6px; padding: 6px 10px;">
                                    <span style="color: #dc2626; font-weight: 600;">⚠️ بدترین</span>
                                    <span style="color: #dc2626; font-weight: 700; font-size: 15px;">
                                        {get_season_label(perf['worst'][0])}: {fmt(perf['worst'][1])}
                                        <span style="font-size: 12px; color: #64748b;">({worst_pct:.1f}%)</span>
                                    </span>
                                </div>
                                <div style="display: flex; justify-content: space-between; font-size: 12px; color: #64748b; border-top: 1px dashed #e2e8f0; padding-top: 6px; margin-top: 6px;">
                                    <span>مجموع فصل‌ها</span>
                                    <span style="font-weight: 600; color: #0f172a;">{fmt(total)}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # ============================================================
                # تحلیل الگوی فصلی شرکت با رنگ‌بندی
                # ============================================================
                st.markdown("---")
                st.markdown("#### 📊 تحلیل الگوی فصلی شرکت")
                
                season_stats = {}
                for season in ["Q1", "Q2", "Q3", "Q4"]:
                    season_values = []
                    for y in years_sorted:
                        data = seasonal_data[y]
                        if data[season] is not None and data[season] > 0:
                            season_values.append(data[season])
                    
                    if season_values:
                        season_stats[season] = {
                            "values": season_values, "count": len(season_values),
                            "avg": sum(season_values) / len(season_values),
                            "max": max(season_values), "min": min(season_values),
                            "total": sum(season_values)
                        }
                
                if season_stats:
                    best_season_overall = None
                    worst_season_overall = None
                    best_avg = -1
                    worst_avg = float('inf')
                    
                    for season, stats in season_stats.items():
                        if stats["avg"] > best_avg:
                            best_avg = stats["avg"]
                            best_season_overall = season
                        if stats["avg"] < worst_avg:
                            worst_avg = stats["avg"]
                            worst_season_overall = season
                    
                    # ============================================================
                    # 📊 نمودار مقایسه میانگین فصل‌ها
                    # ============================================================
                    st.markdown("#### 📊 مقایسه میانگین عملکرد فصل‌ها")
                    
                    fig_avg = go.Figure()
                    
                    avg_seasons = ["Q1", "Q2", "Q3", "Q4"]
                    avg_values = []
                    avg_stds = []
                    
                    for season in avg_seasons:
                        if season in season_stats:
                            avg_values.append(season_stats[season]["avg"])
                            values = season_stats[season]["values"]
                            if len(values) > 1:
                                mean = sum(values) / len(values)
                                variance = sum((x - mean) ** 2 for x in values) / len(values)
                                avg_stds.append(variance ** 0.5)
                            else:
                                avg_stds.append(0)
                        else:
                            avg_values.append(0)
                            avg_stds.append(0)
                    
                    fig_avg.add_trace(go.Bar(
                        x=[get_season_label(s) for s in avg_seasons],
                        y=avg_values,
                        marker_color=[get_season_color(s) for s in avg_seasons],
                        text=[fmt(v) for v in avg_values],
                        textposition="outside",
                        textfont=dict(size=11, color="#0f172a", family="Tahoma"),
                        error_y=dict(
                            type="data",
                            array=avg_stds,
                            visible=True,
                            color="#64748b"
                        ),
                        hovertemplate="%{x}<br>میانگین: %{text}<extra></extra>"
                    ))
                    
                    apply_chart_style(
                        fig_avg,
                        "میانگین درآمد هر فصل (با انحراف معیار)",
                        "فصل",
                        "میلیارد ریال",
                        cat_labels=[get_season_label(s) for s in avg_seasons],
                        y_suffix=""
                    )
                    fig_avg.update_layout(
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_avg, use_container_width=True)
                    
                    # ============================================================
                    # کارت‌های بهترین و بدترین فصل کلی
                    # ============================================================
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        season_labels = {"Q1": "فصل ۱", "Q2": "فصل ۲", 
                                        "Q3": "فصل ۳", "Q4": "فصل ۴"}
                        if best_season_overall:
                            metric_card("🏆 بهترین فصل کلی", f"{season_labels[best_season_overall]}",
                                       "#dcfce7", "#16a34a", "#166534")
                            st.caption(f"میانگین: {fmt(season_stats[best_season_overall]['avg'])}")
                    
                    with col2:
                        if worst_season_overall:
                            metric_card("⚠️ بدترین فصل کلی", f"{season_labels[worst_season_overall]}",
                                       "#fee2e2", "#dc2626", "#991b1b")
                            st.caption(f"میانگین: {fmt(season_stats[worst_season_overall]['avg'])}")
                    
                    with col3:
                        metric_card("📊 سال‌های تحلیل", f"{len(years_sorted)} سال",
                                   "#eff6ff", "#bfdbfe", "#1e40af")
                    
                    with col4:
                        all_avg = sum(stats["avg"] for stats in season_stats.values()) / len(season_stats)
                        if all_avg > 0:
                            variance = sum((stats["avg"] - all_avg) ** 2 for stats in season_stats.values()) / len(season_stats)
                            std_dev = variance ** 0.5
                            cv = (std_dev / all_avg) * 100 if all_avg > 0 else 0
                            if cv < 20:
                                status, color = "🟢 بالا", "#16a34a"
                            elif cv < 40:
                                status, color = "🟡 متوسط", "#ca8a04"
                            else:
                                status, color = "🔴 پایین", "#dc2626"
                            metric_card("ثبات عملکرد فصلی", status, "#f8fafc", "#e2e8f0", color)
                            st.caption(f"ضریب تغییرات: {cv:.1f}%")
                    
                    # ============================================================
                    # رتبه‌بندی فصل‌ها
                    # ============================================================
                    st.markdown("#### 📋 رتبه‌بندی فصل‌ها بر اساس میانگین عملکرد")
                    
                    rank_season_data = []
                    for season, stats in sorted(season_stats.items(), key=lambda x: x[1]["avg"], reverse=True):
                        if len(rank_season_data) == 0:
                            color = "🟢"
                        elif len(rank_season_data) == 1:
                            color = "🟡"
                        else:
                            color = "🔴"
                        
                        rank_season_data.append({
                            "رتبه": len(rank_season_data) + 1,
                            "فصل": f"{color} {get_season_label(season)}",
                            "میانگین": fmt(stats["avg"]),
                            "حداکثر": fmt(stats["max"]),
                            "حداقل": fmt(stats["min"]),
                            "تعداد سال": stats["count"],
                            "نشان": "🥇" if len(rank_season_data) == 0 else "🥈" if len(rank_season_data) == 1 else "🥉" if len(rank_season_data) == 2 else "—"
                        })
                    
                    st.table(pd.DataFrame(rank_season_data))
                    
                    # ============================================================
                    # نتیجه‌گیری نهایی
                    # ============================================================
                    st.markdown("---")
                    st.markdown("#### 💡 نتیجه‌گیری")
                    
                    if best_season_overall and worst_season_overall:
                        best_label = get_season_label(best_season_overall)
                        worst_label = get_season_label(worst_season_overall)
                        best_avg = season_stats[best_season_overall]["avg"]
                        worst_avg = season_stats[worst_season_overall]["avg"]
                        diff_pct = ((best_avg - worst_avg) / worst_avg * 100) if worst_avg > 0 else 0
                        
                        if best_season_overall in ['Q1', 'Q2'] and worst_season_overall in ['Q3', 'Q4']:
                            pattern = "فروش شرکت در فصل‌های ابتدایی سال (Q1, Q2) قوی‌تر است و در فصل‌های پایانی (Q3, Q4) ضعیف‌تر."
                            pattern_type = "early"
                        elif best_season_overall in ['Q3', 'Q4'] and worst_season_overall in ['Q1', 'Q2']:
                            pattern = "فروش شرکت در فصل‌های پایانی سال (Q3, Q4) قوی‌تر است و در فصل‌های ابتدایی (Q1, Q2) ضعیف‌تر."
                            pattern_type = "late"
                        elif abs(diff_pct) < 30:
                            pattern = "الگوی فصلی شرکت نسبتاً متعادل است و تفاوت معناداری بین فصل‌ها وجود ندارد."
                            pattern_type = "balanced"
                        else:
                            pattern = "الگوی فصلی شرکت نامنظم است و نیاز به بررسی دقیق‌تری دارد."
                            pattern_type = "irregular"
                        
                        if pattern_type == "early":
                            border_color = "#2563eb"
                            bg_color = "#eff6ff"
                        elif pattern_type == "late":
                            border_color = "#ea580c"
                            bg_color = "#fff7ed"
                        elif pattern_type == "balanced":
                            border_color = "#16a34a"
                            bg_color = "#f0fdf4"
                        else:
                            border_color = "#dc2626"
                            bg_color = "#fef2f2"
                        
                        st.markdown(f"""
                        <div style="background: {bg_color}; border-radius: 12px; padding: 20px; border-right: 4px solid {border_color}; margin-top: 10px;">
                            <div style="font-size: 15px; line-height: 2; color: #0f172a;">
                                <strong>📊 تحلیل الگوی فصلی شرکت:</strong>
                                <ul style="list-style: none; padding-right: 20px; margin: 10px 0;">
                                    <li>✅ <strong>بهترین فصل</strong>: <span class="best-season">{best_label}</span> با میانگین {fmt(best_avg)} میلیارد ریال</li>
                                    <li>❌ <strong>بدترین فصل</strong>: <span class="worst-season">{worst_label}</span> با میانگین {fmt(worst_avg)} میلیارد ریال</li>
                                    <li>📈 <strong>اختلاف</strong>: درآمد در بهترین فصل <span style="color: #16a34a; font-weight: bold;">{diff_pct:.1f}%</span> بیشتر از بدترین فصل است</li>
                                    <li>📊 <strong>تعداد سال‌های تحلیل</strong>: {len(years_sorted)} سال</li>
                                </ul>
                                <div style="margin-top: 8px; padding: 12px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                                    <strong>🎯 الگوی فصلی شرکت:</strong> {pattern}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # ============================================================
                    # نقشه حرارتی
                    # ============================================================
                    st.markdown("---")
                    st.markdown("#### 🌡️ نقشه حرارتی عملکرد فصلی")
                    st.caption("💡 **راهنما**: رنگ‌های تیره‌تر = عملکرد بهتر، رنگ‌های روشن‌تر = عملکرد ضعیف‌تر")
                    
                    heatmap_data = []
                    heatmap_years = []
                    heatmap_seasons = ["Q1", "Q2", "Q3", "Q4"]
                    
                    for y in years_sorted:
                        row = []
                        data = seasonal_data[y]
                        for season in heatmap_seasons:
                            if data[season] is not None and data[season] > 0:
                                row.append(data[season])
                            else:
                                row.append(None)
                        heatmap_data.append(row)
                        heatmap_years.append(str(y))
                    
                    all_values = [v for row in heatmap_data for v in row if v is not None]
                    if all_values:
                        min_val = min(all_values)
                        max_val = max(all_values)
                        range_val = max_val - min_val if max_val > min_val else 1
                        
                        normalized_data = []
                        for row in heatmap_data:
                            norm_row = []
                            for val in row:
                                if val is not None:
                                    norm_row.append((val - min_val) / range_val)
                                else:
                                    norm_row.append(None)
                            normalized_data.append(norm_row)
                        
                        fig_heatmap = go.Figure(data=go.Heatmap(
                            z=normalized_data,
                            x=[get_season_label(s) for s in heatmap_seasons],
                            y=heatmap_years,
                            colorscale=[
                                [0, "#fee2e2"],
                                [0.33, "#fef3c7"],
                                [0.66, "#dcfce7"],
                                [1, "#16a34a"]
                            ],
                            text=[[fmt(v) if v is not None else "—" for v in row] for row in heatmap_data],
                            texttemplate="%{text}",
                            textfont={"size": 12, "color": "#0f172a", "family": "Tahoma"},
                            hoverongaps=False,
                            hovertemplate="سال: %{y}<br>فصل: %{x}<br>درآمد: %{text}<extra></extra>",
                            zmid=0.5,
                            showscale=True,
                            colorbar=dict(
                                title="نسبت",
                                titleside="right",
                                tickvals=[0, 0.5, 1],
                                ticktext=["ضعیف", "متوسط", "قوی"],
                                thickness=20,
                                len=0.8
                            )
                        ))
                        
                        fig_heatmap.update_layout(
                            title=dict(
                                text="نقشه حرارتی عملکرد فصلی",
                                font=dict(size=16, color="#0f172a", family="Tahoma")
                            ),
                            xaxis=dict(
                                title=dict(text="فصل", font=dict(size=13, color="#0f172a", family="Tahoma")),
                                tickfont=dict(size=12, color="#0f172a", family="Tahoma"),
                                linecolor="#334155", linewidth=1.5, gridcolor="#cbd5e1"
                            ),
                            yaxis=dict(
                                title=dict(text="سال مالی", font=dict(size=13, color="#0f172a", family="Tahoma")),
                                tickfont=dict(size=12, color="#0f172a", family="Tahoma"),
                                linecolor="#334155", linewidth=1.5, gridcolor="#cbd5e1"
                            ),
                            height=400,
                            plot_bgcolor="white",
                            paper_bgcolor="white",
                            margin=dict(l=60, r=80, t=70, b=90),
                            font=dict(color="#0f172a", size=12, family="Tahoma")
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("برای نمایش بهترین/بدترین عملکرد در هر سال، نیاز به حداقل ۲ فصل معتبر در هر سال دارید.")
        else:
            st.info("داده‌های کافی برای محاسبه درآمد فصلی وجود ندارد. حداقل به دوره ۳ ماهه نیاز است.")
    else:
        st.info("دوره مالی ثبت نشده است.")


# ============================================================
# تب دوره‌های مالی
# ============================================================
def show_financial_periods(periods, fiscal_end_month, fiscal_end_day):
    """تب دوره‌های مالی"""
    
    st.subheader("📋 دوره‌های مالی")
    
    if not periods:
        st.info("دوره مالی ثبت نشده است.")
        return
    
    # آخرین دوره مالی
    st.markdown("#### آخرین دوره مالی")
    
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
    
    st.markdown("---")
    
    # روند درآمد و سود سالانه
    with st.expander("روند درآمد و سود سالانه", expanded=True):
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
    
    # جدول کامل دوره‌ها
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
    
    # جزئیات یک دوره
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
# تب نمودارها
# ============================================================
def show_charts(periods, monthly_rows, df_sales, years_available, fiscal_end_month, 
                fiscal_end_day, color_map):
    """تب نمودارها"""
    
    st.subheader("📊 نمودارها")
    
    # انتخاب سال‌ها - فقط یک بار
    if years_available:
        selected_years_chart = st.multiselect(
            "سال‌های فروش ماهانه", 
            options=years_available, 
            default=list(years_available),
            key="chart_year_select_unique"
        )
    else:
        selected_years_chart = []
        st.info("فروش ماهانه‌ای ثبت نشده است.")
    
    df_chart = (
        df_sales[df_sales["سال"].isin(selected_years_chart)].copy()
        if selected_years_chart and len(df_sales) else pd.DataFrame()
    )
    
    # ============================================================
    # توابع کمکی برای نمودارها
    # ============================================================
    def build_period_chart(title, y_title, value_fn):
        """ساخت نمودار دوره‌های مالی با فیلتر سال‌های انتخاب‌شده"""
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
            
            # فقط سال‌های انتخاب‌شده را نمایش بده
            if fy not in selected_years_chart:
                continue
                
            records.append({
                "سال_مالی": fy,
                "دوره": pt,
                "برچسب": ptype_to_label[pt],
                "مقدار": val,
            })
        
        if not records:
            st.info(f"داده‌ای برای سال‌های انتخاب‌شده در این نمودار موجود نیست.")
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
    
    # ============================================================
    # نمودار حاشیه سود
    # ============================================================
    with st.expander("نمودار حاشیه سود بر اساس دوره", expanded=True):
        def margin_pct(r):
            _, m, _, _ = calc_metrics(r)
            if m is None or not r["operating_revenue"]:
                return None
            return m * 100
        build_period_chart("حاشیه سود خالص عملیاتی", "حاشیه سود (%)", margin_pct)
    
    # ============================================================
    # نمودار نسبت مطالبات
    # ============================================================
    with st.expander("نمودار نسبت مطالبات به دارایی جاری", expanded=True):
        def recv_pct(r):
            _, _, rr, _ = calc_metrics(r)
            return None if rr is None else rr * 100
        build_period_chart("نسبت مطالبات به دارایی جاری", "نسبت مطالبات (%)", recv_pct)
    
    # ============================================================
    # نمودار فروش کل ماهانه
    # ============================================================
    with st.expander("نمودار فروش کل ماهانه", expanded=True):
        if selected_years_chart and len(df_chart) > 0:
            fig = go.Figure()
            for y in selected_years_chart:
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
    
    # ============================================================
    # نمودار فروش داخلی و صادراتی
    # ============================================================
    with st.expander("نمودار فروش داخلی و صادراتی", expanded=False):
        if selected_years_chart and len(df_chart) > 0:
            year_bar = st.selectbox(
                "سال", 
                options=selected_years_chart, 
                index=len(selected_years_chart) - 1, 
                key="bar_year_chart_unique"
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
                fig, "فروش داخلی و صادراتی — {}".format(year_bar),
                "ماه", "میلیارد ریال",
            )
            fig.update_layout(barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داده موجود نیست.")
    
    # ============================================================
    # جدول رشد فروش ماهانه
    # ============================================================
    with st.expander("جدول رشد فروش ماهانه", expanded=False):
        if len(selected_years_chart) >= 2 and len(df_chart) > 0:
            y_sorted = sorted(selected_years_chart)
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
# برنامه اصلی
# ============================================================
companies = get_companies()
if not companies:
    st.warning("هنوز هیچ شرکتی ثبت نشده است.")
    st.stop()

filtered = companies

if not filtered:
    st.warning("شرکتی پیدا نشد.")
    st.stop()

company_options = {"{} — {}".format(c["symbol"], c["name_fa"] or ""): c for c in filtered}
selected_label = st.selectbox("انتخاب شرکت", options=list(company_options.keys()))
company = company_options[selected_label]
company_id = company["id"]
fiscal_end_month = int(company["fiscal_end_month"] or 12)
fiscal_end_day = int(company["fiscal_end_day"] or 29)

# دریافت داده‌ها
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
# تب‌بندی اصلی
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 داشبورد اصلی", 
    "📈 تحلیل فصلی", 
    "📋 دوره‌های مالی", 
    "📉 نمودارها"
])

with tab1:
    show_main_dashboard(company, periods, monthly_rows, df_sales, years_available, 
                        fiscal_end_month, fiscal_end_day, color_map)

with tab2:
    show_seasonal_analysis(periods, monthly_rows, fiscal_end_month, fiscal_end_day)

with tab3:
    show_financial_periods(periods, fiscal_end_month, fiscal_end_day)

with tab4:
    show_charts(periods, monthly_rows, df_sales, years_available, fiscal_end_month, 
                fiscal_end_day, color_map)

# ============================================================
# امضای نویسنده
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px 0; font-size: 16px; color: #475569; border-top: 2px solid #e8ecf1;">
    📈 تحلیل از <strong style="color: #2563eb;">داود شورگشتی</strong>
</div>
""", unsafe_allow_html=True)