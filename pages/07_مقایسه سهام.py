import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="مقایسه شرکت‌ها", layout="wide")
from utils.styles import apply_styles
apply_styles()


st.markdown("""
<style>
    .main .block-container { direction: rtl; padding-top: 1.2rem; max-width: 100%; }

    /* عناوین */
    h1 { font-size: 1.7rem !important; font-weight: 700 !important; color: #1e293b; }
    h2, h3 { font-size: 1.25rem !important; font-weight: 600 !important; color: #334155; }

    /* جدول زیباتر */
    .stTable, table {
        direction: rtl;
        text-align: center;
        border-collapse: collapse;
        width: 100%;
        font-size: 0.92rem;
    }
    .stTable th, table th {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 10px !important;
        border: none !important;
        white-space: nowrap;
    }
    .stTable td, table td {
        padding: 10px 8px !important;
        border-bottom: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
    }
    .stTable tr:nth-child(even) td, table tr:nth-child(even) td {
        background: #f8fafc !important;
    }
    .stTable tr:hover td, table tr:hover td {
        background: #eff6ff !important;
    }

    /* دکمه‌های سورت زیباتر */
    div[data-testid="stHorizontalBlock"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.55rem 0.4rem !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
        transition: all 0.2s ease;
        width: 100%;
        min-height: 42px;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    div[data-testid="stHorizontalBlock"] button:active {
        transform: translateY(0);
    }

    /* کپشن‌ها */
    .stCaption { color: #64748b; font-size: 0.88rem; }

    /* فاصله نمودارها */
    .js-plotly-plot { border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
</style>
""", unsafe_allow_html=True)

st.title("مقایسه شرکت‌ها")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#ea580c", "#7c3aed", "#0891b2", "#db2777", "#0d9488"]

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
        ORDER BY p.year_solar DESC, p.period_type DESC
    """, (company_id,)).fetchall()
    conn.close()
    return rows

def get_all_monthly_sales(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT year_solar, month, domestic_sales, export_sales, total_sales
        FROM monthly_sales WHERE company_id = ?
        ORDER BY year_solar, month
    """, (company_id,)).fetchall()
    conn.close()
    return rows

def get_recurring_by_year(company_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT year_solar, SUM(amount) as total
        FROM non_operating_items
        WHERE company_id = ? AND is_recurring = 1
        GROUP BY year_solar ORDER BY year_solar
    """, (company_id,)).fetchall()
    conn.close()
    return {r["year_solar"]: float(r["total"] or 0) for r in rows}

def safe_div(a, b):
    try:
        if a is None or b is None or float(b) == 0:
            return None
        return float(a) / float(b)
    except Exception:
        return None

def calc_metrics(row):
    revenue = row["operating_revenue"]
    other_inc = row["other_income"] or 0
    non_op = row["non_operating_income"] or 0
    net_profit = row["net_profit"]
    receivables = row["trade_receivables"]
    current_assets = row["current_assets"]
    comprehensive = row["comprehensive_income"]
    dividend = row["approved_dividend"]
    op_profit = None
    if net_profit is not None:
        op_profit = float(net_profit) - float(other_inc) - float(non_op)
    net_margin = safe_div(op_profit, revenue)
    recv_ratio = safe_div(receivables, current_assets)
    div_ratio = safe_div(dividend, comprehensive)
    return op_profit, net_margin, recv_ratio, div_ratio

def get_first_quarter_months(fiscal_end_month):
    start = (fiscal_end_month % 12) + 1
    return [((start - 1 + i) % 12) + 1 for i in range(3)]

def calc_forward_estimates(company, periods, monthly_rows):
    result = {
        "has_data": False, "target_year": None,
        "sales_final": None, "margin_avg": None,
        "est_profit": None, "est_recurring_non_op": None,
        "est_dividend": None, "payout_avg": None,
        "pe_forward": None, "pd_forward": None, "ps_forward": None,
        "margin_annual": None, "margin_last": None,
    }
    if not periods and not monthly_rows:
        return result

    fiscal_end_month = company["fiscal_end_month"] or 12
    market_value = company["market_value"]

    years_in_periods = [r["year_solar"] for r in periods] if periods else []
    years_in_monthly = [r["year_solar"] for r in monthly_rows] if monthly_rows else []
    all_years = sorted(set(years_in_periods + years_in_monthly))
    if not all_years:
        return result

    last_year = max(all_years)
    has_annual_last = any(r["year_solar"] == last_year and r["period_type"] == 12 for r in periods)
    target_year = last_year + 1 if has_annual_last else last_year
    result["target_year"] = target_year

    q1 = None
    for r in periods:
        if r["year_solar"] == target_year and r["period_type"] == 3:
            q1 = r
            break
    q1_months = get_first_quarter_months(fiscal_end_month)
    sales_m1 = sales_m2 = None

    if q1 and q1["operating_revenue"] and q1["operating_revenue"] > 0:
        rev = float(q1["operating_revenue"])
        sales_m1 = (rev / 3) * 12
        month_sales = {}
        for r in monthly_rows:
            if r["year_solar"] == target_year and r["month"] in q1_months:
                tot = r["total_sales"]
                if tot is None:
                    tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
                if tot and tot > 0:
                    month_sales[r["month"]] = float(tot)
        if month_sales:
            last_val = month_sales[max(month_sales.keys())]
            sum_existing = sum(month_sales.values())
            sales_m2 = (last_val * (12 - len(month_sales))) + sum_existing
        else:
            sales_m2 = sales_m1
    else:
        month_sales = {}
        for r in monthly_rows:
            if r["year_solar"] == target_year and r["month"] in q1_months:
                tot = r["total_sales"]
                if tot is None:
                    tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
                if tot and tot > 0:
                    month_sales[r["month"]] = float(tot)
        if not month_sales:
            return result
        n = len(month_sales)
        sales_m1 = (sum(month_sales.values()) / n) * 12
        last_val = month_sales[max(month_sales.keys())]
        sum_existing = sum(month_sales.values())
        sales_m2 = (last_val * (12 - n)) + sum_existing

    sales_final = min(sales_m1, sales_m2) if sales_m1 and sales_m2 else (sales_m1 or sales_m2)
    result["sales_final"] = sales_final

    margin_annual = margin_last = None
    for r in periods:
        if r["year_solar"] == target_year - 1 and r["period_type"] == 12:
            _, margin, _, _ = calc_metrics(r)
            if margin is not None:
                margin_annual = margin
            break
    candidates = [r for r in periods if r["year_solar"] <= target_year]
    if candidates:
        non_annual = [r for r in candidates if r["period_type"] != 12]
        last_period = max(non_annual or candidates, key=lambda x: (x["year_solar"], x["period_type"]))
        _, margin, _, _ = calc_metrics(last_period)
        if margin is not None:
            margin_last = margin

    result["margin_annual"] = margin_annual
    result["margin_last"] = margin_last
    if margin_annual is not None and margin_last is not None:
        margin_avg = (margin_annual + margin_last) / 2
    else:
        margin_avg = margin_annual if margin_annual is not None else margin_last
    if margin_avg is None or sales_final is None:
        return result
    result["margin_avg"] = margin_avg

    est_profit = sales_final * margin_avg
    recurring_map = get_recurring_by_year(company["id"])
    relevant = [y for y in sorted(recurring_map.keys()) if y < target_year]
    est_recurring = None
    if len(relevant) >= 2:
        v1, v2 = recurring_map[relevant[-2]], recurring_map[relevant[-1]]
        g = (v2 - v1) / v1 if v1 != 0 else 0
        est_recurring = v2 * (1 + g)
    elif len(relevant) == 1:
        est_recurring = recurring_map[relevant[-1]]
    result["est_recurring_non_op"] = est_recurring
    if est_recurring is not None:
        est_profit = est_profit + est_recurring
    result["est_profit"] = est_profit

    payouts = []
    for y in [target_year - 1, target_year - 2]:
        for r in periods:
            if r["year_solar"] == y and r["period_type"] == 12:
                div, comp = r["approved_dividend"], r["comprehensive_income"]
                if div is not None and comp is not None and float(comp) != 0:
                    payouts.append(float(div) / float(comp))
                break
    payout_avg = sum(payouts) / len(payouts) if payouts else None
    result["payout_avg"] = payout_avg
    if payout_avg is not None and est_profit is not None:
        result["est_dividend"] = est_profit * payout_avg

    if market_value and est_profit and est_profit > 0:
        result["pe_forward"] = market_value / est_profit
    if market_value and result.get("est_dividend") and result["est_dividend"] > 0:
        result["pd_forward"] = market_value / result["est_dividend"]
    if market_value and sales_final and sales_final > 0:
        result["ps_forward"] = market_value / sales_final

    result["has_data"] = True
    return result

def fmt(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):,.0f}"
    except Exception:
        return "—"

def fmt_pct(v):
    if v is None:
        return "—"
    try:
        return f"{float(v)*100:.1f}%"
    except Exception:
        return "—"

def fmt_ratio(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):.2f}"
    except Exception:
        return "—"

def pe_label(pe):
    if pe is None:
        return "—"
    if pe < 5:
        return f"{pe:.2f} (مناسب)"
    if pe <= 7:
        return f"{pe:.2f} (متوسط)"
    return f"{pe:.2f} (بالا)"

# ============================================================
# انتخاب شرکت‌ها
# ============================================================
companies = get_companies()
if not companies:
    st.warning("هنوز شرکتی ثبت نشده است.")
    st.stop()

options = {f"{c['symbol']} — {c['name_fa'] or ''}": c for c in companies}
selected_labels = st.multiselect(
    "شرکت‌های مورد نظر برای مقایسه (حداقل ۲ شرکت):",
    options=list(options.keys()),
    default=list(options.keys())[: min(3, len(options))]
)

if len(selected_labels) < 2:
    st.info("حداقل دو شرکت انتخاب کنید.")
    st.stop()

selected_companies = [options[lb] for lb in selected_labels]

# ============================================================
# محاسبه داده
# ============================================================
rows_data = []
for comp in selected_companies:
    periods = get_periods(comp["id"])
    monthly = get_all_monthly_sales(comp["id"])
    fwd = calc_forward_estimates(comp, periods, monthly)
    latest_margin = latest_recv = None
    if periods:
        _, latest_margin, latest_recv, _ = calc_metrics(periods[0])
    rows_data.append({
        "نماد": comp["symbol"],
        "نام": comp["name_fa"] or "—",
        "صنعت": comp["industry"] or "—",
        "ارزش بازار": comp["market_value"],
        "برآورد فروش": fwd.get("sales_final"),
        "میانگین حاشیه": fwd.get("margin_avg"),
        "برآورد سود": fwd.get("est_profit"),
        "برآورد سود تقسیمی": fwd.get("est_dividend"),
        "P/E Forward": fwd.get("pe_forward"),
        "P/D Forward": fwd.get("pd_forward"),
        "P/S Forward": fwd.get("ps_forward"),
        "حاشیه آخرین دوره": latest_margin,
        "نسبت مطالبات": latest_recv,
    })

df = pd.DataFrame(rows_data)

# ============================================================
# جدول مقایسه
# ============================================================

st.subheader("جدول مقایسه")

if "sort_by" not in st.session_state:
    st.session_state.sort_by = None
    st.session_state.sort_asc = True

def toggle_sort(col_name):
    if st.session_state.sort_by == col_name:
        st.session_state.sort_asc = not st.session_state.sort_asc
    else:
        st.session_state.sort_by = col_name
        st.session_state.sort_asc = True

st.markdown("**مرتب‌سازی جدول** — روی هر دکمه کلیک کنید (کلیک دوباره = نزولی):")
b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
with b1:
    if st.button("P/E Forward", key="btn_pe"):
        toggle_sort("P/E Forward")
with b2:
    if st.button("برآورد سود", key="btn_profit"):
        toggle_sort("برآورد سود")
with b3:
    if st.button("ارزش بازار", key="btn_mv"):
        toggle_sort("ارزش بازار")
with b4:
    if st.button("میانگین حاشیه", key="btn_margin"):
        toggle_sort("میانگین حاشیه")
with b5:
    if st.button("P/S Forward", key="btn_ps"):
        toggle_sort("P/S Forward")
with b6:
    if st.button("P/D Forward", key="btn_pd"):
        toggle_sort("P/D Forward")
with b7:
    if st.button("برآورد فروش", key="btn_sales"):
        toggle_sort("برآورد فروش")

def safe_sort(dataframe, column, ascending=True):
    temp = dataframe.copy()
    values = []
    for v in temp[column]:
        if v is None:
            values.append(1e18 if ascending else -1e18)
        else:
            try:
                values.append(float(v))
            except Exception:
                values.append(1e18 if ascending else -1e18)
    temp["_sort_key"] = values
    temp = temp.sort_values("_sort_key", ascending=ascending).reset_index(drop=True)
    return temp.drop(columns=["_sort_key"])

df_view = df.copy()
if st.session_state.sort_by is not None:
    df_view = safe_sort(df_view, st.session_state.sort_by, st.session_state.sort_asc)
    direction = "صعودی ↑" if st.session_state.sort_asc else "نزولی ↓"
    st.caption(f"مرتب‌شده بر اساس: **{st.session_state.sort_by}** — {direction}")

table_data = []
for _, row in df_view.iterrows():
    table_data.append({
        "نماد": row["نماد"],
        "نام": row["نام"],
        "صنعت": row["صنعت"],
        "ارزش بازار": fmt(row["ارزش بازار"]),
        "برآورد فروش": fmt(row["برآورد فروش"]),
        "میانگین حاشیه": fmt_pct(row["میانگین حاشیه"]),
        "برآورد سود": fmt(row["برآورد سود"]),
        "سود تقسیمی": fmt(row["برآورد سود تقسیمی"]),
        "P/E Forward": pe_label(row["P/E Forward"]),
        "P/D Forward": fmt_ratio(row["P/D Forward"]),
        "P/S Forward": fmt_ratio(row["P/S Forward"]),
        "حاشیه آخرین دوره": fmt_pct(row["حاشیه آخرین دوره"]),
        "نسبت مطالبات": fmt_pct(row["نسبت مطالبات"]),
    })

st.table(pd.DataFrame(table_data))
st.caption("P/E: مناسب < ۵  |  متوسط ۵ تا ۷  |  بالا > ۷")

# ============================================================
# نمودارها — هر کدام در یک سطر کامل و بزرگ‌تر
# ============================================================
st.markdown("---")
st.subheader("نمودارهای مقایسه‌ای")

symbols = df_view["نماد"].tolist()
bar_colors = [COLORS[i % len(COLORS)] for i in range(len(symbols))]

CHART_HEIGHT = 480
CHART_LAYOUT = dict(
    height=CHART_HEIGHT,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=50, r=30, t=60, b=50),
    font=dict(family="Tahoma, sans-serif", size=13),
    title_font=dict(size=16, color="#1e293b"),
    xaxis=dict(tickfont=dict(size=13)),
    yaxis=dict(tickfont=dict(size=12), gridcolor="#f1f5f9"),
    bargap=0.35,
)

# --- P/E Forward ---
pe_vals = df_view["P/E Forward"].tolist()
fig1 = go.Figure(go.Bar(
    x=symbols,
    y=[v if v is not None else 0 for v in pe_vals],
    marker_color=bar_colors,
    text=[fmt_ratio(v) for v in pe_vals],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig1.update_layout(title="مقایسه P/E Forward", yaxis_title="P/E", **CHART_LAYOUT)
st.plotly_chart(fig1, use_container_width=True)

# --- میانگین حاشیه ---
fig2 = go.Figure(go.Bar(
    x=symbols,
    y=[(v * 100) if v is not None else 0 for v in df_view["میانگین حاشیه"]],
    marker_color=bar_colors,
    text=[fmt_pct(v) for v in df_view["میانگین حاشیه"]],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig2.update_layout(title="مقایسه میانگین حاشیه سود", yaxis_title="حاشیه (%)", **CHART_LAYOUT)
st.plotly_chart(fig2, use_container_width=True)

# --- برآورد سود ---
fig3 = go.Figure(go.Bar(
    x=symbols,
    y=[v if v is not None else 0 for v in df_view["برآورد سود"]],
    marker_color=bar_colors,
    text=[fmt(v) for v in df_view["برآورد سود"]],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig3.update_layout(title="مقایسه برآورد سود نهایی", yaxis_title="میلیارد ریال", **CHART_LAYOUT)
st.plotly_chart(fig3, use_container_width=True)

# --- ارزش بازار ---
fig4 = go.Figure(go.Bar(
    x=symbols,
    y=[v if v is not None else 0 for v in df_view["ارزش بازار"]],
    marker_color=bar_colors,
    text=[fmt(v) for v in df_view["ارزش بازار"]],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig4.update_layout(title="مقایسه ارزش بازار", yaxis_title="میلیارد ریال", **CHART_LAYOUT)
st.plotly_chart(fig4, use_container_width=True)

# --- P/S Forward ---
fig5 = go.Figure(go.Bar(
    x=symbols,
    y=[v if v is not None else 0 for v in df_view["P/S Forward"]],
    marker_color=bar_colors,
    text=[fmt_ratio(v) for v in df_view["P/S Forward"]],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig5.update_layout(title="مقایسه P/S Forward", yaxis_title="P/S", **CHART_LAYOUT)
st.plotly_chart(fig5, use_container_width=True)

# --- P/D Forward ---
fig6 = go.Figure(go.Bar(
    x=symbols,
    y=[v if v is not None else 0 for v in df_view["P/D Forward"]],
    marker_color=bar_colors,
    text=[fmt_ratio(v) for v in df_view["P/D Forward"]],
    textposition="outside",
    textfont=dict(size=13, color="#334155"),
    marker_line=dict(width=0),
))
fig6.update_layout(title="مقایسه P/D Forward", yaxis_title="P/D", **CHART_LAYOUT)
st.plotly_chart(fig6, use_container_width=True)