# -*- coding: utf-8 -*-
"""
صفحه پرینت گزارش تحلیلی جامع
با استایل اختصاصی برای چاپ
"""

import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go
import math
import jdatetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(
    page_title="پرینت گزارش جامع", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

from utils.styles import apply_styles
apply_styles()

# ============================================================
# استایل اختصاصی چاپ
# ============================================================
st.markdown("""
<style>
    .main .block-container {
        direction: rtl;
        padding: 1rem 1.5rem;
        max-width: 1200px;
    }
    
    .report-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .report-header h1 {
        color: white !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem;
    }
    .report-header p {
        color: #94a3b8 !important;
        font-size: 1rem;
    }
    
    .section-title {
        background: #f8fafc;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        margin: 1.5rem 0 1rem 0;
        border-right: 4px solid #2563eb;
    }
    .section-title h2 {
        margin: 0;
        color: #0f172a;
        font-size: 1.3rem;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    .metric-grid-5 {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    .metric-grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: white;
        border: 1.5px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #0f172a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .metric-card .value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-card .value.green { color: #16a34a; }
    .metric-card .value.red { color: #dc2626; }
    .metric-card .value.blue { color: #2563eb; }
    .metric-card .value.orange { color: #ea580c; }
    .metric-card .value.purple { color: #7c3aed; }
    .metric-card .value.gold { color: #ca8a04; }
    
    .dataframe-container {
        overflow-x: auto;
        margin: 0.8rem 0;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    .dataframe-container table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        direction: rtl;
    }
    .dataframe-container th {
        background: #0f172a;
        color: white;
        padding: 0.6rem 0.8rem;
        text-align: center;
        font-weight: 600;
    }
    .dataframe-container td {
        padding: 0.5rem 0.8rem;
        border-bottom: 1px solid #f1f5f9;
        text-align: center;
    }
    .dataframe-container tr:nth-child(even) td {
        background: #fafbfc;
    }
    .dataframe-container tr:hover td {
        background: #f1f5f9;
    }
    
    .season-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .season-card .year-title {
        font-weight: 700;
        font-size: 1rem;
        color: #0f172a;
        text-align: center;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.3rem;
        margin-bottom: 0.5rem;
    }
    .season-item {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        margin-bottom: 0.2rem;
        font-size: 0.85rem;
    }
    .season-item.best { background: #dcfce7; }
    .season-item.worst { background: #fee2e2; }
    .season-item.neutral { background: #f1f5f9; }
    
    .conclusion-box {
        background: #eff6ff;
        border: 2px solid #2563eb;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 1rem 0;
    }
    .conclusion-box .title {
        font-weight: 700;
        font-size: 1rem;
        color: #1e40af;
        margin-bottom: 0.3rem;
    }
    .conclusion-box .text {
        font-size: 0.9rem;
        color: #1e293b;
        line-height: 1.8;
    }
    .conclusion-box .highlight-green { color: #16a34a; font-weight: 600; }
    .conclusion-box .highlight-red { color: #dc2626; font-weight: 600; }
    
    .print-button {
        background: #0f172a;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2.5rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        font-family: 'Vazirmatn', Tahoma, sans-serif;
        transition: all 0.2s ease;
        margin: 0.5rem 0;
    }
    .print-button:hover {
        background: #1e293b;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
    }
    
    .footer {
        text-align: center;
        border-top: 2px solid #e2e8f0;
        padding-top: 1rem;
        margin-top: 1.5rem;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    
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
        width: 16px;
        height: 16px;
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
        font-size: 10px;
        color: #64748b;
        margin-left: 4px;
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
            padding: 15px !important;
            font-size: 11px !important;
        }
        .season-card { break-inside: avoid !important; }
        .metric-grid { grid-template-columns: repeat(4, 1fr); }
        .metric-grid-5 { grid-template-columns: repeat(5, 1fr); }
        .metric-grid-3 { grid-template-columns: repeat(3, 1fr); }
        .metric-card { padding: 4px 6px; }
        .metric-card .value { font-size: 12px; }
        .dataframe-container table { font-size: 10px; }
        .conclusion-box { break-inside: avoid !important; }
        .chart-container { break-inside: avoid !important; }
        .section-break { page-break-before: always !important; }
        .report-header { background: #0f172a !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        .metric-card { background: white !important; }
        .season-card { background: #f8fafc !important; }
        .season-item.best { background: #dcfce7 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        .season-item.worst { background: #fee2e2 !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        .conclusion-box { background: #eff6ff !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        .dataframe-container th { background: #0f172a !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        .dataframe-container tr:nth-child(even) td { background: #fafbfc !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ثابت‌ها
# ============================================================
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
# توابع کمکی
# ============================================================
def fmt(val):
    if val is None:
        return "—"
    try:
        return "{:,.0f}".format(float(val))
    except:
        return "—"

def fmt_pct(val):
    if val is None:
        return "—"
    try:
        return "{:.1f}%".format(float(val) * 100)
    except:
        return "—"

def fmt_ratio(val):
    if val is None:
        return "—"
    try:
        return "{:.2f}".format(float(val))
    except:
        return "—"

def get_current_jalali_date():
    return jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')

def get_season_label(season):
    labels = {"Q1": "فصل ۱", "Q2": "فصل ۲", "Q3": "فصل ۳", "Q4": "فصل ۴"}
    return labels.get(season, season)

def get_season_color(season):
    colors = {"Q1": "#2563eb", "Q2": "#16a34a", "Q3": "#ea580c", "Q4": "#dc2626"}
    return colors.get(season, "#6b7280")

def metric_card(title, value, bg="#f8fafc", border="#e2e8f0", text="#0f172a"):
    st.markdown(
        '<div class="metric-card" style="background:{bg};border-color:{border};">'
        '<div class="label">{title}</div>'
        '<div class="value" style="color:{text};">{value}</div></div>'.format(
            bg=bg, border=border, text=text, title=title, value=value
        ),
        unsafe_allow_html=True,
    )

# ============================================================
# توابع محاسباتی (دقیقاً مشابه داشبورد)
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
    
    months_back = {12: 0, 9: 3, 6: 6, 3: 9}
    back = months_back.get(pt, 0)
    end_month = F - back
    cal_year = y
    if end_month <= 0:
        end_month += 12
        cal_year -= 1
    
    end_m = None
    try:
        if row["end_month"] is not None:
            end_m = int(row["end_month"])
    except:
        pass
    
    if end_m:
        candidates = [y, y+1, y-1]
        for cand in candidates:
            back2 = months_back.get(pt, 0)
            em = F - back2
            cy = cand
            if em <= 0:
                em += 12
                cy -= 1
            if em == end_m and cy == y:
                return cand
        return y
    return y

def period_full_label(fiscal_year, period_type, fiscal_end_month, fiscal_end_day=29):
    names = {
        3: "۳ ماهه منتهی به",
        6: "۶ ماهه منتهی به",
        9: "۹ ماهه منتهی به",
        12: "۱۲ ماهه سالانه منتهی به",
    }
    months_back = {12: 0, 9: 3, 6: 6, 3: 9}
    back = months_back.get(int(period_type), 0)
    end_month = int(fiscal_end_month) - back
    cal_year = int(fiscal_year)
    if end_month <= 0:
        end_month += 12
        cal_year -= 1
    return "{} {} {} {}".format(
        names.get(int(period_type), period_type),
        int(fiscal_end_day or 29),
        MONTH_NAMES.get(end_month, end_month),
        cal_year,
    )

def calc_metrics(row):
    revenue = row["operating_revenue"]
    other_inc = row["other_income"] or 0
    non_op = row["non_operating_income"] or 0
    net_profit = row["net_profit"]
    
    op_profit = None
    if net_profit is not None:
        op_profit = float(net_profit) - other_inc - non_op
    
    net_margin = None
    if op_profit is not None and revenue and float(revenue) > 0:
        net_margin = op_profit / float(revenue)
    
    recv_ratio = None
    if row["trade_receivables"] is not None and row["current_assets"] is not None and float(row["current_assets"]) > 0:
        recv_ratio = float(row["trade_receivables"]) / float(row["current_assets"])
    
    div_ratio = None
    if row["approved_dividend"] is not None and row["comprehensive_income"] is not None and float(row["comprehensive_income"]) > 0:
        div_ratio = float(row["approved_dividend"]) / float(row["comprehensive_income"])
    
    return op_profit, net_margin, recv_ratio, div_ratio

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

def calendar_year_for_fiscal_month(fiscal_year, month, fiscal_end_month):
    if int(month) > int(fiscal_end_month):
        return int(fiscal_year) - 1
    return int(fiscal_year)

def get_first_quarter_months(fiscal_end_month):
    start = (int(fiscal_end_month) % 12) + 1
    return [((start - 1 + i) % 12) + 1 for i in range(3)]

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

def calc_forward_estimates(company, periods, monthly_rows):
    """محاسبه برآوردها - دقیقاً مشابه داشبورد"""
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

    # ============================================================
    # غیرعملیاتی تکرارپذیر - دقیقاً مشابه داشبورد
    # ============================================================
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
    # میانگین درصد سود تقسیمی - دقیقاً مشابه داشبورد
    # ============================================================
    payouts = []
    payout_source = "financial"
    payout_from_meeting = False
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
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
            for row in meeting_rows:
                dividend_percent = row[0]
                if dividend_percent is not None and dividend_percent > 0:
                    payouts.append(dividend_percent / 100)
            
            if payouts:
                payout_source = "meeting"
                payout_from_meeting = True
    except Exception as e:
        pass
    
    if not payouts:
        for y in [target_year - 1, target_year - 2]:
            for r in periods:
                if resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day) == y and int(r["period_type"]) == 12:
                    div, comp = r["approved_dividend"], r["comprehensive_income"]
                    if div is not None and comp is not None and float(comp) != 0:
                        payouts.append(float(div) / float(comp))
                    break
    
    if not payouts:
        payouts = [0.5]
        payout_source = "default"
    
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

def get_seasonal_data(periods, fiscal_end_month, fiscal_end_day):
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
        data = {"Q1": None, "Q2": None, "Q3": None, "Q4": None, "total": None}
        
        if 3 in periods_dict:
            q1 = periods_dict[3]["operating_revenue"] or 0
            data["Q1"] = q1
            if 6 in periods_dict:
                q2 = (periods_dict[6]["operating_revenue"] or 0) - q1
                data["Q2"] = q2
                if 9 in periods_dict:
                    q3 = (periods_dict[9]["operating_revenue"] or 0) - (periods_dict[6]["operating_revenue"] or 0)
                    data["Q3"] = q3
                    if 12 in periods_dict:
                        q4 = (periods_dict[12]["operating_revenue"] or 0) - (periods_dict[9]["operating_revenue"] or 0)
                        data["Q4"] = q4
                        data["total"] = periods_dict[12]["operating_revenue"] or 0
                    else:
                        data["total"] = periods_dict[9]["operating_revenue"] or 0
                else:
                    data["total"] = periods_dict[6]["operating_revenue"] or 0
            else:
                data["total"] = q1
        
        has_data = any(v for v in [data["Q1"], data["Q2"], data["Q3"], data["Q4"]] if v and v > 0)
        if has_data:
            seasonal_data[fy] = data
    
    return seasonal_data

# ============================================================
# توابع تولید نمودارها
# ============================================================
def create_revenue_trend_chart(periods, fiscal_end_month, fiscal_end_day):
    annual = []
    for r in periods:
        if int(r["period_type"]) == 12:
            fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
            annual.append((fy, r))
    
    if not annual:
        return None
    
    annual = sorted(annual, key=lambda x: x[0])
    years = [a[0] for a in annual]
    revenues = [a[1]["operating_revenue"] or 0 for a in annual]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=revenues,
        name="درآمد عملیاتی",
        marker_color="#2563eb",
        text=[fmt(v) for v in revenues],
        textposition="outside",
        textfont=dict(size=10, color="#0f172a")
    ))
    
    fig.update_layout(
        title="روند درآمد سالانه",
        xaxis_title="سال مالی",
        yaxis_title="میلیارد ریال",
        height=300,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(family="Tahoma", size=11),
        xaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5),
        yaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5)
    )
    return fig

def create_seasonal_chart(seasonal_data):
    if not seasonal_data:
        return None
    
    years_sorted = sorted(seasonal_data.keys())
    season_labels = {"Q1": "فصل ۱", "Q2": "فصل ۲", "Q3": "فصل ۳", "Q4": "فصل ۴"}
    season_colors = {"Q1": "#2563eb", "Q2": "#16a34a", "Q3": "#ea580c", "Q4": "#dc2626"}
    
    fig = go.Figure()
    
    for season in ["Q1", "Q2", "Q3", "Q4"]:
        values = []
        for y in years_sorted:
            data = seasonal_data[y]
            val = data[season]
            if val is not None and val > 0:
                values.append(val)
            else:
                values.append(None)
        
        fig.add_trace(go.Bar(
            x=[str(y) for y in years_sorted],
            y=values,
            name=season_labels[season],
            marker_color=season_colors[season],
            text=[fmt(v) if v is not None else "—" for v in values],
            textposition="outside",
            textfont=dict(size=9, color="#0f172a")
        ))
    
    fig.update_layout(
        title="مقایسه درآمد فصلی",
        xaxis_title="سال مالی",
        yaxis_title="میلیارد ریال",
        barmode="group",
        height=280,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(family="Tahoma", size=11),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5),
        yaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5)
    )
    return fig

def create_margin_chart(periods, fiscal_end_month, fiscal_end_day):
    data_points = []
    for r in periods:
        fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
        _, margin, _, _ = calc_metrics(r)
        if margin is not None:
            data_points.append((fy, int(r["period_type"]), margin * 100))
    
    if not data_points:
        return None
    
    df = pd.DataFrame(data_points, columns=["سال", "دوره", "حاشیه"])
    
    fig = go.Figure()
    for year in sorted(df["سال"].unique()):
        d = df[df["سال"] == year].sort_values("دوره")
        if len(d) > 0:
            periods_label = []
            for pt in d["دوره"]:
                if pt == 3:
                    periods_label.append("۳ ماهه")
                elif pt == 6:
                    periods_label.append("۶ ماهه")
                elif pt == 9:
                    periods_label.append("۹ ماهه")
                else:
                    periods_label.append("۱۲ ماهه")
            
            fig.add_trace(go.Scatter(
                x=periods_label,
                y=d["حاشیه"],
                mode="lines+markers+text",
                name=str(year),
                line=dict(width=2.5),
                marker=dict(size=8),
                text=[f"{v:.1f}%" for v in d["حاشیه"]],
                textposition="top center",
                textfont=dict(size=9, color="#0f172a")
            ))
    
    fig.update_layout(
        title="روند حاشیه سود",
        xaxis_title="دوره",
        yaxis_title="درصد",
        height=280,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(family="Tahoma", size=11),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5),
        yaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5, ticksuffix="%")
    )
    return fig

def create_monthly_sales_chart(monthly_rows, years_selected=None):
    if not monthly_rows:
        return None
    
    data = []
    for r in monthly_rows:
        data.append({
            "year_solar": int(r["year_solar"]),
            "month": int(r["month"]),
            "total_sales": float(r["total_sales"] or 0)
        })
    
    df = pd.DataFrame(data)
    if df.empty:
        return None
    
    years = sorted(df["year_solar"].unique())
    if years_selected:
        years = [y for y in years if y in years_selected]
    if len(years) > 5:
        years = years[-5:]
    
    fig = go.Figure()
    for y in years:
        d = df[df["year_solar"] == y].sort_values("month")
        d = d[d["total_sales"] > 0]
        if len(d) == 0:
            continue
        
        month_labels = [MONTH_NAMES.get(m, str(m)) for m in d["month"]]
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=d["total_sales"],
            mode="lines+markers+text",
            name=str(y),
            line=dict(width=2.5),
            marker=dict(size=7),
            text=[fmt(v) for v in d["total_sales"]],
            textposition="top center",
            textfont=dict(size=8, color="#0f172a")
        ))
    
    if len(fig.data) == 0:
        return None
    
    fig.update_layout(
        title="روند فروش ماهانه",
        xaxis_title="ماه",
        yaxis_title="میلیارد ریال",
        height=300,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        font=dict(family="Tahoma", size=11),
        legend=dict(orientation="h", y=1.05, x=0.5, xanchor="center"),
        xaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5),
        yaxis=dict(gridcolor="#e2e8f0", linecolor="#334155", linewidth=1.5)
    )
    return fig

def create_heatmap(seasonal_data):
    if not seasonal_data:
        return None
    
    years_sorted = sorted(seasonal_data.keys())
    seasons = ["Q1", "Q2", "Q3", "Q4"]
    season_labels = {"Q1": "فصل ۱", "Q2": "فصل ۲", "Q3": "فصل ۳", "Q4": "فصل ۴"}
    
    heatmap_data = []
    for y in years_sorted:
        row = []
        data = seasonal_data[y]
        for season in seasons:
            if data[season] is not None and data[season] > 0:
                row.append(data[season])
            else:
                row.append(None)
        heatmap_data.append(row)
    
    all_values = [v for row in heatmap_data for v in row if v is not None]
    if not all_values:
        return None
    
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
    
    fig = go.Figure(data=go.Heatmap(
        z=normalized_data,
        x=[season_labels[s] for s in seasons],
        y=[str(y) for y in years_sorted],
        colorscale=[
            [0, "#fee2e2"],
            [0.33, "#fef3c7"],
            [0.66, "#dcfce7"],
            [1, "#16a34a"]
        ],
        text=[[fmt(v) if v is not None else "—" for v in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 10, "color": "#0f172a"},
        hoverongaps=False,
        showscale=True,
        colorbar=dict(
            title="عملکرد",
            titleside="right",
            tickvals=[0, 0.5, 1],
            ticktext=["ضعیف", "متوسط", "قوی"],
            thickness=15,
            len=0.7
        )
    ))
    
    fig.update_layout(
        title="نقشه حرارتی عملکرد فصلی",
        height=260,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=60, t=50, b=40),
        font=dict(family="Tahoma", size=11),
        xaxis=dict(linecolor="#334155", gridcolor="#e2e8f0", linewidth=1.5),
        yaxis=dict(linecolor="#334155", gridcolor="#e2e8f0", linewidth=1.5)
    )
    return fig

# ============================================================
# توابع کمکی نمایش
# ============================================================
def get_progress_html(progress, reported_months=None):
    if progress is None:
        return "—"
    
    try:
        progress_val = float(progress)
    except (TypeError, ValueError):
        return "—"
    
    if math.isnan(progress_val) or progress_val < 0 or progress_val > 100:
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
        month_text = f'<span style="font-size:9px; color:#64748b; margin-right:3px;">({reported_months} ماه)</span>'
    
    return f'<div class="progress-box"><span class="progress-label">{int(progress_val)}%</span>{"".join(squares)}{month_text}</div>'

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

def get_monthly_sales(company_id):
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

# ============================================================
# صفحه اصلی
# ============================================================
st.markdown("""
<div style="text-align: center; padding: 10px 0 15px 0;" class="no-print">
    <button onclick="window.print()" class="print-button">
        🖨️ پرینت گزارش جامع
    </button>
    <br>
    <span style="font-size: 12px; color: #94a3b8;">
        💡 برای بهترین نتیجه، در پنجره پرینت: 
        <strong>مقیاس ۷۵-۸۰%</strong> • 
        <strong>حاشیه کم</strong> • 
        <strong>رنگی</strong> را انتخاب کنید
    </span>
</div>
""", unsafe_allow_html=True)

# انتخاب شرکت
companies = get_companies()
if not companies:
    st.warning("هنوز هیچ شرکتی ثبت نشده است.")
    st.stop()

company_options = {"{} — {}".format(c["symbol"], c["name_fa"] or ""): c for c in companies}
selected_label = st.selectbox("انتخاب شرکت", options=list(company_options.keys()), key="print_company_select")
company = company_options[selected_label]
company_id = company["id"]
fiscal_end_month = int(company["fiscal_end_month"] or 12)
fiscal_end_day = int(company["fiscal_end_day"] or 29)

periods = get_periods(company_id)
monthly_rows = get_monthly_sales(company_id)

if not periods:
    st.warning("دوره مالی برای این شرکت ثبت نشده است.")
    st.stop()

# دریافت داده‌های فصلی
seasonal_data = get_seasonal_data(periods, fiscal_end_month, fiscal_end_day)

# ============================================================
# تولید گزارش
# ============================================================
st.markdown('<div class="report-container" id="printable-report">', unsafe_allow_html=True)

# ============================================================
# هدر گزارش
# ============================================================
st.markdown(f"""
<div class="report-header">
    <h1>📊 گزارش تحلیل بنیادی جامع</h1>
    <p>گزارش کامل مالی و عملیاتی شرکت</p>
    <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.1); padding: 4px 15px; border-radius: 20px; color: #cbd5e1;">📌 {company["symbol"]}</span>
        <span style="background: rgba(255,255,255,0.1); padding: 4px 15px; border-radius: 20px; color: #cbd5e1;">🏢 {company["name_fa"] or "—"}</span>
        <span style="background: rgba(255,255,255,0.1); padding: 4px 15px; border-radius: 20px; color: #cbd5e1;">🏭 {company["industry"] or "—"}</span>
        <span style="background: rgba(255,255,255,0.1); padding: 4px 15px; border-radius: 20px; color: #cbd5e1;">📅 {get_current_jalali_date()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# بخش ۱: اطلاعات کلی شرکت
# ============================================================
st.markdown('<div class="section-title"><h2>📌 اطلاعات کلی شرکت</h2></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("ارزش بازار", fmt(company["market_value"]))
with col2:
    metric_card("رتبه در صنعت", str(company["rank_in_industry"] or "—"))
with col3:
    metric_card("پایان سال مالی", "{} {}".format(fiscal_end_day, MONTH_NAMES.get(fiscal_end_month, "")))
with col4:
    metric_card("صنعت", company["industry"] or "—")

# ============================================================
# بخش ۲: آخرین دوره مالی
# ============================================================
st.markdown('<div class="section-title"><h2>📊 آخرین دوره مالی</h2></div>', unsafe_allow_html=True)

enriched = []
for r in periods:
    fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
    enriched.append((fy, int(r["period_type"]), r))
enriched.sort(key=lambda x: (x[0], x[1]), reverse=True)
latest = enriched[0][2]
latest_fy = enriched[0][0]

op_p, margin, recv_r, div_r = calc_metrics(latest)

st.markdown(f"""
<div style="text-align: center; margin-bottom: 8px; font-size: 13px; color: #64748b;">
    {period_full_label(latest_fy, latest["period_type"], fiscal_end_month, fiscal_end_day)}
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    metric_card("درآمد عملیاتی", fmt(latest["operating_revenue"]), "#eff6ff", "#bfdbfe", "#2563eb")
with col2:
    metric_card("سود خالص عملیاتی", fmt(op_p), "#f0fdf4", "#bbf7d0", "#16a34a")
with col3:
    metric_card("حاشیه سود", fmt_pct(margin), "#f3e8ff", "#d8b4fe", "#7c3aed")
with col4:
    metric_card("سود خالص", fmt(latest["net_profit"]))
with col5:
    metric_card("حقوق مالکانه", fmt(latest["equity"]), "#fef3c7", "#fcd34d", "#ca8a04")

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("نسبت مطالبات", fmt_pct(recv_r))
with col2:
    metric_card("نسبت سود مصوب", fmt_pct(div_r))
with col3:
    metric_card("دارایی جاری", fmt(latest["current_assets"]), "#eff6ff", "#bfdbfe", "#2563eb")
with col4:
    metric_card("جمع دارایی‌ها", fmt(latest["total_assets"]))

# ============================================================
# بخش ۳: برآورد Forward - با استفاده از تابع یکسان
# ============================================================
st.markdown('<div class="section-title"><h2>🔮 برآورد و نسبت‌های Forward</h2></div>', unsafe_allow_html=True)

fwd = calc_forward_estimates(company, periods, monthly_rows)

if fwd.get("has_data"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("سال مالی هدف", str(fwd.get("target_year", "—")), "#eff6ff", "#bfdbfe", "#2563eb")
    with col2:
        metric_card("برآورد فروش", fmt(fwd.get("sales_final")))
    with col3:
        metric_card("برآورد سود خالص", fmt(fwd.get("est_profit")), "#f0fdf4", "#bbf7d0", "#16a34a")
    with col4:
        pe_val = fwd.get("pe_forward")
        if pe_val is not None:
            if pe_val < 5:
                bg, border, text = "#dcfce7", "#16a34a", "#166534"
            elif pe_val <= 7:
                bg, border, text = "#fef9c3", "#ca8a04", "#854d0e"
            else:
                bg, border, text = "#fee2e2", "#dc2626", "#991b1b"
        else:
            bg, border, text = "#f8fafc", "#e2e8f0", "#0f172a"
        metric_card("P/E Forward", fmt_ratio(pe_val), bg, border, text)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("P/S Forward", fmt_ratio(fwd.get("ps_forward")), "#f3e8ff", "#d8b4fe", "#7c3aed")
    with col2:
        payout_source = fwd.get("payout_source", "financial")
        payout_display = fmt_pct(fwd.get("payout_avg"))
        if payout_source == "meeting":
            payout_display += " 📋"
        elif payout_source == "default":
            payout_display += " ⚠️"
        metric_card("درصد تقسیم سود", payout_display, "#fef3c7", "#fcd34d", "#ca8a04")
    with col3:
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
        metric_card("سود تقسیمی برآوردی", dividend_display)
    with col4:
        metric_card("P/D Forward", fmt_ratio(fwd.get("pd_forward")), "#fef3c7", "#fcd34d", "#ca8a04")
    
    # ============================================================
    # تحلیل ارزش بازار بر اساس P/E=5
    # ============================================================
    st.markdown("---")
    st.markdown("#### 🎯 تحلیل ارزش بازار هدف (بر اساس P/E=5)")
    
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
else:
    st.info(fwd.get("message", "داده کافی برای محاسبه برآورد وجود ندارد."))

# ============================================================
# بخش ۴: پیشرفت فروش
# ============================================================
st.markdown('<div class="section-title"><h2>📊 پیشرفت فروش</h2></div>', unsafe_allow_html=True)

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
        progress_display = get_progress_html(progress_val, reported_months)
        metric_card("پیشرفت زمانی", progress_display, "#eff6ff", "#bfdbfe", "#1e40af")
    
    with col2:
        metric_card("فروش محقق‌شده", fmt(actual_sales), "#f0fdf4", "#bbf7d0", "#166534")
    
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
# بخش ۵: گردش کالا
# ============================================================
st.markdown('<div class="section-title"><h2>🔄 گردش کالا و چرخه عملیات</h2></div>', unsafe_allow_html=True)

enriched_all = []
for r in periods:
    fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
    enriched_all.append((fy, int(r["period_type"]), r))
enriched_all.sort(key=lambda x: (x[0], x[1]))
annual_periods = [r for _, _, r in enriched_all if _ == 12]

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
    
    with col2:
        metric_card("دوره گردش موجودی (روز)", f"{days_inventory:.1f}" if days_inventory else "—",
                   "#f0fdf4", "#bbf7d0", "#166534")
    
    with col3:
        metric_card("دوره وصول مطالبات (DSO)", f"{dso:.1f}" if dso else "—",
                   "#fef3c7", "#fcd34d", "#92400e")
    
    with col4:
        metric_card("🔄 چرخه عملیات (روز)", f"{operating_cycle:.1f}" if operating_cycle else "—",
                   "#eff6ff", "#bfdbfe", "#1e40af")
else:
    st.info("برای محاسبه گردش کالا به دوره‌های سالانه نیاز است.")

# ============================================================
# بخش ۶: نمودارها
# ============================================================
st.markdown('<div class="section-title"><h2>📈 نمودارهای تحلیلی</h2></div>', unsafe_allow_html=True)

# نمودار ۱: روند درآمد سالانه
st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">📊 روند درآمد سالانه</h3>', unsafe_allow_html=True)
fig1 = create_revenue_trend_chart(periods, fiscal_end_month, fiscal_end_day)
if fig1:
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.markdown('<div style="color: #64748b;">داده کافی برای نمایش وجود ندارد.</div>', unsafe_allow_html=True)

# نمودار ۲: تحلیل فصلی
if seasonal_data:
    st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">📊 تحلیل فصلی</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig2 = create_seasonal_chart(seasonal_data)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig4 = create_heatmap(seasonal_data)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)

# نمودار ۳: فروش ماهانه
if monthly_rows:
    st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">📊 روند فروش ماهانه</h3>', unsafe_allow_html=True)
    fig3 = create_monthly_sales_chart(monthly_rows)
    if fig3:
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.markdown('<div style="color: #64748b;">داده کافی برای نمایش وجود ندارد.</div>', unsafe_allow_html=True)

# نمودار ۴: حاشیه سود
st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">📊 روند حاشیه سود</h3>', unsafe_allow_html=True)
fig5 = create_margin_chart(periods, fiscal_end_month, fiscal_end_day)
if fig5:
    st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# بخش ۷: تحلیل فصلی کامل
# ============================================================
if seasonal_data:
    st.markdown('<div class="section-title"><h2>📈 تحلیل فصلی کامل</h2></div>', unsafe_allow_html=True)
    
    years_sorted = sorted(seasonal_data.keys())
    
    # جدول فصلی
    st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">📋 جدول درآمد فصلی</h3>', unsafe_allow_html=True)
    df_rows = []
    for fy in sorted(seasonal_data.keys()):
        data = seasonal_data[fy]
        row = {
            "سال مالی": fy,
            "فصل ۱": fmt(data["Q1"]) if data["Q1"] else "—",
            "فصل ۲": fmt(data["Q2"]) if data["Q2"] else "—",
            "فصل ۳": fmt(data["Q3"]) if data["Q3"] else "—",
            "فصل ۴": fmt(data["Q4"]) if data["Q4"] else "—",
            "کل": fmt(data["total"]) if data["total"] else "—"
        }
        df_rows.append(row)
    
    st.markdown("""
    <div class="dataframe-container">
    """, unsafe_allow_html=True)
    st.table(pd.DataFrame(df_rows))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # بهترین و بدترین عملکرد
    st.markdown('<h3 style="font-size: 1rem; margin: 0.5rem 0;">🏆 بهترین و بدترین عملکرد فصلی</h3>', unsafe_allow_html=True)
    
    yearly_perf = {}
    for fy in years_sorted:
        data = seasonal_data[fy]
        season_vals = {}
        for season in ["Q1", "Q2", "Q3", "Q4"]:
            if data[season] and data[season] > 0:
                season_vals[season] = data[season]
        if len(season_vals) >= 2:
            sorted_seasons = sorted(season_vals.items(), key=lambda x: x[1], reverse=True)
            yearly_perf[fy] = {
                "best": sorted_seasons[0], 
                "worst": sorted_seasons[-1], 
                "total": sum(season_vals.values())
            }
    
    if yearly_perf:
        cols_per_row = 3
        year_items = sorted(yearly_perf.items(), reverse=True)
        
        for i in range(0, len(year_items), cols_per_row):
            row_cols = st.columns(min(cols_per_row, len(year_items) - i))
            for j, (fy, perf) in enumerate(year_items[i:i+cols_per_row]):
                with row_cols[j]:
                    total = perf["total"]
                    best_pct = (perf["best"][1] / total * 100) if total > 0 else 0
                    worst_pct = (perf["worst"][1] / total * 100) if total > 0 else 0
                    
                    st.markdown(f"""
                    <div class="season-card">
                        <div class="year-title">سال {fy}</div>
                        <div class="season-item best">
                            <span>🏆 {get_season_label(perf['best'][0])}</span>
                            <span>{fmt(perf['best'][1])} ({best_pct:.1f}%)</span>
                        </div>
                        <div class="season-item worst">
                            <span>⚠️ {get_season_label(perf['worst'][0])}</span>
                            <span>{fmt(perf['worst'][1])} ({worst_pct:.1f}%)</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================
# بخش ۸: لیست کامل دوره‌های مالی
# ============================================================
st.markdown('<div class="section-title"><h2>📋 لیست کامل دوره‌های مالی</h2></div>', unsafe_allow_html=True)

rows_sorted = sorted(
    periods,
    key=lambda r: (
        resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day),
        int(r["period_type"]),
    ),
    reverse=True
)

table_data = []
for row in rows_sorted[:15]:
    fy = resolve_fiscal_year(row, fiscal_end_month, fiscal_end_day)
    op_p, margin, recv_r, div_r = calc_metrics(row)
    table_data.append({
        "سال": fy,
        "دوره": period_full_label(fy, row["period_type"], fiscal_end_month, fiscal_end_day),
        "درآمد": fmt(row["operating_revenue"]),
        "سود خالص": fmt(row["net_profit"]),
        "حاشیه سود": fmt_pct(margin),
        "نسبت مطالبات": fmt_pct(recv_r)
    })

if table_data:
    st.markdown("""
    <div class="dataframe-container">
    """, unsafe_allow_html=True)
    st.table(pd.DataFrame(table_data))
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"نمایش {len(table_data)} دوره از کل {len(periods)} دوره")

# ============================================================
# بخش ۹: جمع‌بندی نهایی
# ============================================================
st.markdown('<div class="section-title"><h2>📋 جمع‌بندی و تحلیل کلی</h2></div>', unsafe_allow_html=True)

annual_data = []
for r in periods:
    if int(r["period_type"]) == 12:
        fy = resolve_fiscal_year(r, fiscal_end_month, fiscal_end_day)
        annual_data.append((fy, r))

if len(annual_data) >= 2:
    annual_data = sorted(annual_data, key=lambda x: x[0])
    latest_ann = annual_data[-1][1]
    prev_ann = annual_data[-2][1] if len(annual_data) >= 2 else None
    
    latest_rev = latest_ann["operating_revenue"] or 0
    prev_rev = prev_ann["operating_revenue"] or 0 if prev_ann else 0
    rev_growth = ((latest_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0
    
    latest_profit = latest_ann["net_profit"] or 0
    prev_profit = prev_ann["net_profit"] or 0 if prev_ann else 0
    profit_growth = ((latest_profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0
    
    rev_color = "highlight-green" if rev_growth > 0 else "highlight-red"
    profit_color = "highlight-green" if profit_growth > 0 else "highlight-red"
    
    st.markdown(f"""
    <div class="conclusion-box">
        <div class="title">💡 تحلیل کلی</div>
        <div class="text">
            • <strong>رشد درآمد</strong>: 
            <span class="{rev_color}">{rev_growth:+.1f}%</span> 
            (از {fmt(prev_rev)} به {fmt(latest_rev)})
            <br>
            • <strong>رشد سود</strong>: 
            <span class="{profit_color}">{profit_growth:+.1f}%</span>
            (از {fmt(prev_profit)} به {fmt(latest_profit)})
            <br>
            • <strong>تعداد دوره‌های مالی</strong>: {len(periods)} دوره
            <br>
            • <strong>تعداد سال‌های تحلیل فصلی</strong>: {len(seasonal_data)} سال
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="conclusion-box">
        <div class="title">💡 تحلیل کلی</div>
        <div class="text">
            برای تحلیل روند به حداقل ۲ دوره سالانه نیاز است.
            <br>
            • <strong>تعداد دوره‌های مالی</strong>: {len(periods)} دوره
            <br>
            • <strong>تعداد سال‌های تحلیل فصلی</strong>: {len(seasonal_data)} سال
        </div>
    </div>
    """, unsafe_allow_html=True)

# بهترین/بدترین فصل کلی
if seasonal_data:
    season_stats = {}
    for season in ["Q1", "Q2", "Q3", "Q4"]:
        values = []
        for y in seasonal_data:
            val = seasonal_data[y][season]
            if val is not None and val > 0:
                values.append(val)
        if values:
            season_stats[season] = sum(values) / len(values)
    
    if season_stats:
        best_season = max(season_stats, key=season_stats.get)
        worst_season = min(season_stats, key=season_stats.get)
        
        st.markdown(f"""
        <div class="conclusion-box" style="border-color: #16a34a; background: #f0fdf4; margin-top: 0.5rem;">
            <div class="title" style="color: #166534;">🏆 نتیجه‌گیری فصلی</div>
            <div class="text">
                • <strong>بهترین فصل کلی</strong>: <span class="highlight-green">{get_season_label(best_season)}</span> 
                با میانگین {fmt(season_stats[best_season])} میلیارد ریال
                <br>
                • <strong>بدترین فصل کلی</strong>: <span class="highlight-red">{get_season_label(worst_season)}</span> 
                با میانگین {fmt(season_stats[worst_season])} میلیارد ریال
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# فوتر
# ============================================================
st.markdown(f"""
<div class="footer">
    📊 گزارش تحلیل بنیادی جامع • {company["symbol"]} • 
    تاریخ چاپ: {get_current_jalali_date()} • 
    نسخه ۲.۰
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# دکمه پرینت در پایین
# ============================================================
st.markdown("""
<div style="text-align: center; padding: 15px 0; margin-top: 10px;" class="no-print">
    <button onclick="window.print()" class="print-button">
        🖨️ پرینت گزارش جامع
    </button>
</div>
""", unsafe_allow_html=True)