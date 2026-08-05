import streamlit as st
import sys
import os
import pandas as pd
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="داشبورد", layout="wide", initial_sidebar_state="expanded")
from utils.styles import apply_styles
apply_styles()

st.markdown("""
<style>
    .main .block-container { direction: rtl; padding-top: 1.2rem; max-width: 1200px; }

    div[data-testid="stMetric"] {
        direction: rtl;
        text-align: center;
        background: #f8f9fb;
        border: 1px solid #e8ecf1;
        border-radius: 10px;
        padding: 10px 8px;
        min-height: 78px;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.88rem !important;
        color: #475569 !important;
        font-weight: 600 !important;
        white-space: nowrap;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }

    .stTable, table { direction: rtl; text-align: center;font-size: 1.22rem }
    .stExpander { direction: rtl; }

    h1 { font-size: 2.55rem !important; color: #0f172a !important; font-weight: 700 !important; }
    h2, h3 { color: #1e293b !important; font-size: 2.10rem !important; }
    .stCaption { color: #64748b !important; font-size: 0.82rem !important; }

    /* فاصله بین ردیف‌های متریک */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.6rem !important;
        margin-bottom: 0.35rem !important;
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
        FROM monthly_sales
        WHERE company_id = ?
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
        GROUP BY year_solar
        ORDER BY year_solar
    """, (company_id,)).fetchall()
    conn.close()
    return {r["year_solar"]: float(r["total"] or 0) for r in rows}

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
    months = []
    for i in range(3):
        m = ((start - 1 + i) % 12) + 1
        months.append(m)
    return months

def calc_forward_estimates(company, periods, monthly_rows):
    result = {
        "has_data": False,
        "target_year": None,
        "q1_revenue": None,
        "months_used": [],
        "sales_method1": None,
        "sales_method2": None,
        "sales_final": None,
        "margin_annual": None,
        "margin_last": None,
        "margin_avg": None,
        "est_profit": None,
        "est_recurring_non_op": None,
        "recurring_growth": None,
        "payout_avg": None,
        "est_dividend": None,
        "pe_forward": None,
        "pd_forward": None,
        "ps_forward": None,
        "message": ""
    }

    if not periods and not monthly_rows:
        result["message"] = "داده کافی برای برآورد وجود ندارد."
        return result

    fiscal_end_month = company["fiscal_end_month"] or 12
    market_value = company["market_value"]

    years_in_periods = [r["year_solar"] for r in periods] if periods else []
    years_in_monthly = [r["year_solar"] for r in monthly_rows] if monthly_rows else []
    all_years = sorted(set(years_in_periods + years_in_monthly))

    if not all_years:
        result["message"] = "هیچ داده‌ای ثبت نشده است."
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
    sales_m1 = None
    sales_m2 = None
    months_used = []

    if q1 and q1["operating_revenue"] and q1["operating_revenue"] > 0:
        rev = float(q1["operating_revenue"])
        result["q1_revenue"] = rev
        sales_m1 = (rev / 3) * 12

        month_sales = {}
        for r in monthly_rows:
            if r["year_solar"] == target_year and r["month"] in q1_months:
                tot = r["total_sales"]
                if tot is None:
                    tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
                if tot and tot > 0:
                    month_sales[r["month"]] = float(tot)
                    months_used.append(r["month"])

        if month_sales:
            last_m = max(month_sales.keys())
            last_val = month_sales[last_m]
            sum_existing = sum(month_sales.values())
            remaining = 12 - len(month_sales)
            sales_m2 = (last_val * remaining) + sum_existing
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
                    months_used.append(r["month"])

        if not month_sales:
            result["message"] = f"برای سال {target_year} نه گزارش سه‌ماهه و نه فروش ماهانه سه ماه اول وجود ندارد."
            return result

        n = len(month_sales)
        avg_month = sum(month_sales.values()) / n
        sales_m1 = avg_month * 12
        last_m = max(month_sales.keys())
        last_val = month_sales[last_m]
        sum_existing = sum(month_sales.values())
        remaining = 12 - n
        sales_m2 = (last_val * remaining) + sum_existing
        result["q1_revenue"] = sum_existing

    result["months_used"] = sorted(months_used)
    result["sales_method1"] = sales_m1
    result["sales_method2"] = sales_m2
    sales_final = min(sales_m1, sales_m2) if sales_m1 and sales_m2 else (sales_m1 or sales_m2)
    result["sales_final"] = sales_final

    margin_annual = None
    for r in periods:
        if r["year_solar"] == target_year - 1 and r["period_type"] == 12:
            _, margin, _, _ = calc_metrics(r)
            if margin is not None:
                margin_annual = margin
            break

    margin_last = None
    candidates = [r for r in periods if r["year_solar"] <= target_year]
    if candidates:
        non_annual = [r for r in candidates if r["period_type"] != 12]
        if non_annual:
            last_period = max(non_annual, key=lambda x: (x["year_solar"], x["period_type"]))
        else:
            last_period = max(candidates, key=lambda x: (x["year_solar"], x["period_type"]))
        _, margin, _, _ = calc_metrics(last_period)
        if margin is not None:
            margin_last = margin

    result["margin_annual"] = margin_annual
    result["margin_last"] = margin_last

    if margin_annual is not None and margin_last is not None:
        margin_avg = (margin_annual + margin_last) / 2
    elif margin_annual is not None:
        margin_avg = margin_annual
    elif margin_last is not None:
        margin_avg = margin_last
    else:
        result["message"] = "حاشیه سود سال قبل یا فصل آخر موجود نیست."
        return result

    result["margin_avg"] = margin_avg

    est_profit = sales_final * margin_avg
    result["est_profit"] = est_profit

    recurring_map = get_recurring_by_year(company["id"])
    relevant = [y for y in sorted(recurring_map.keys()) if y < target_year]
    est_recurring = None
    recurring_growth = None
    if len(relevant) >= 2:
        v1 = recurring_map[relevant[-2]]
        v2 = recurring_map[relevant[-1]]
        recurring_growth = (v2 - v1) / v1 if v1 != 0 else 0
        est_recurring = v2 * (1 + recurring_growth)
    elif len(relevant) == 1:
        est_recurring = recurring_map[relevant[-1]]
        recurring_growth = 0

    result["est_recurring_non_op"] = est_recurring
    result["recurring_growth"] = recurring_growth

    if est_recurring is not None and est_profit is not None:
        est_profit = est_profit + est_recurring
        result["est_profit"] = est_profit

    payouts = []
    for y in [target_year - 1, target_year - 2]:
        for r in periods:
            if r["year_solar"] == y and r["period_type"] == 12:
                div = r["approved_dividend"]
                comp = r["comprehensive_income"]
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

def fmt(val):
    if val is None:
        return "—"
    try:
        return f"{float(val):,.0f}"
    except Exception:
        return "—"

def fmt_pct(val):
    if val is None:
        return "—"
    try:
        return f"{float(val)*100:.1f}%"
    except Exception:
        return "—"

def fmt_ratio(val):
    if val is None:
        return "—"
    try:
        return f"{float(val):.2f}"
    except Exception:
        return "—"

# ============================================================
# انتخاب شرکت
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

company_options = {f"{c['symbol']} — {c['name_fa'] or ''}": c for c in filtered}
selected_label = st.selectbox("انتخاب شرکت", options=list(company_options.keys()))
company = company_options[selected_label]
company_id = company["id"]

st.markdown("---")

# ============================================================
# اطلاعات کلی
# ============================================================
st.subheader(f"{company['symbol']}  ·  {company['name_fa'] or ''}")

def metric_card(title, value, bg="#f1f5f9", border="#cbd5e1", text="#0f172a"):
    st.markdown(f"""
    <div style="
        background:{bg};
        border:1.5px solid {border};
        border-radius:10px;
        padding:10px 8px;
        text-align:center;
        min-height:78px;
    ">
        <div style="font-size:0.88rem;font-weight:600;color:#64748b;margin-bottom:4px;">
            {title}
        </div>
        <div style="font-size:1.15rem;font-weight:700;color:{text};">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)

GRAY_BG = "#f1f5f9"
GRAY_BORDER = "#cbd5e1"
GRAY_TEXT = "#0f172a"

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("ارزش بازار", fmt(company["market_value"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
with c2:
    rank = company["rank_in_industry"] if company["rank_in_industry"] else "—"
    metric_card("رتبه در صنعت", str(rank), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
with c3:
    mn = MONTH_NAMES.get(company["fiscal_end_month"], "")
    fiscal = f"{company['fiscal_end_day'] or '—'} {mn}"
    metric_card("پایان سال مالی", fiscal, GRAY_BG, GRAY_BORDER, GRAY_TEXT)
with c4:
    metric_card("صنعت", company["industry"] or "—", GRAY_BG, GRAY_BORDER, GRAY_TEXT)

# ============================================================
# داده
# ============================================================
monthly_rows = get_all_monthly_sales(company_id)
periods = get_periods(company_id)

if monthly_rows:
    records = []
    for r in monthly_rows:
        tot = r["total_sales"]
        if tot is None:
            tot = (r["domestic_sales"] or 0) + (r["export_sales"] or 0)
        records.append({
            "سال": r["year_solar"], "ماه": r["month"],
            "داخلی": float(r["domestic_sales"] or 0),
            "صادراتی": float(r["export_sales"] or 0),
            "کل": float(tot or 0),
        })
    df_sales = pd.DataFrame(records)
    years_available = sorted(df_sales["سال"].unique())
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
    months_str = "، ".join(str(m) for m in fwd["months_used"]) if fwd["months_used"] else "گزارش سه‌ماهه"
    st.caption(f"سال هدف برآورد:   {fwd['target_year']}              ماه های : {months_str}")

    def metric_card(title, value, bg="#f1f5f9", border="#cbd5e1", text="#0f172a"):
        st.markdown(f"""
        <div style="
            background:{bg};
            border:1.5px solid {border};
            border-radius:10px;
            padding:10px 8px;
            text-align:center;
            min-height:78px;
        ">
            <div style="font-size:0.88rem;font-weight:600;color:#64748b;margin-bottom:4px;">
                {title}
            </div>
            <div style="font-size:1.15rem;font-weight:700;color:{text};">
                {value}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # رنگ پیش‌فرض خاکستری برای همه
    GRAY_BG = "#f1f5f9"
    GRAY_BORDER = "#cbd5e1"
    GRAY_TEXT = "#0f172a"

    # ---- ردیف ۱ ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("برآورد فروش نرمال", fmt(fwd["sales_method1"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col2:
        metric_card("برآورد فروش بر اساس ماه آخر", fmt(fwd["sales_method2"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col3:
        metric_card("برآورد غیرعملیاتی تکرارپذیر", fmt(fwd.get("est_recurring_non_op")), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col4:
        metric_card("برآورد سود نهایی", fmt(fwd["est_profit"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)

    # ---- ردیف ۲ ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("حاشیه سود سال قبل", fmt_pct(fwd["margin_annual"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col2:
        metric_card("حاشیه سود فصل آخر", fmt_pct(fwd["margin_last"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col3:
        metric_card("میانگین حاشیه سود", fmt_pct(fwd["margin_avg"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col4:
        metric_card("میانگین درصد تقسیم سود", fmt_pct(fwd["payout_avg"]), GRAY_BG, GRAY_BORDER, GRAY_TEXT)

    # ---- ردیف ۳ ----
    col1, col2, col3, col4 = st.columns(4)

    # فقط P/E شرط رنگی دارد
    pe = fwd.get("pe_forward")
    with col1:
        if pe is None:
            metric_card("P/E Forward", "—", GRAY_BG, GRAY_BORDER, GRAY_TEXT)
        else:
            if pe < 5:
                metric_card("P/E Forward", f"{pe:.2f}", "#dcfce7", "#16a34a", "#166534")  # سبز
            elif pe <= 7:
                metric_card("P/E Forward", f"{pe:.2f}", "#fef9c3", "#ca8a04", "#854d0e")  # زرد
            else:
                metric_card("P/E Forward", f"{pe:.2f}", "#fee2e2", "#dc2626", "#991b1b")  # قرمز

    with col2:
        metric_card("P/D Forward", fmt_ratio(fwd.get("pd_forward")), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col3:
        metric_card("سود تقسیمی برآوردی", fmt(fwd.get("est_dividend")), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
    with col4:
        metric_card("P/S Forward", fmt_ratio(fwd.get("ps_forward")), GRAY_BG, GRAY_BORDER, GRAY_TEXT)
# ============================================================
# نمودارها
# ============================================================
st.markdown("---")
st.subheader("نمودارها")

if years_available:
    selected_years = st.multiselect("سال‌های مورد نظر", options=years_available, default=list(years_available))
else:
    selected_years = []
    st.info("فروش ماهانه‌ای ثبت نشده است.")

df_chart = df_sales[df_sales["سال"].isin(selected_years)].copy() if selected_years and len(df_sales) > 0 else pd.DataFrame()

with st.expander("نمودار حاشیه سود بر اساس دوره", expanded=True):
    if periods:
        margin_records = []
        for r in periods:
            _, margin, _, _ = calc_metrics(r)
            if margin is not None and r["operating_revenue"]:
                end_m, end_d = r["end_month"], r["end_day"]
                label = f"{end_m:02d}/{end_d:02d}" if end_m and end_d else period_label(r["period_type"])
                margin_records.append({"سال": r["year_solar"], "برچسب": label, "حاشیه": margin * 100, "ترتیب": r["period_type"]})
        if margin_records:
            df_m = pd.DataFrame(margin_records).sort_values(["سال", "ترتیب"])
            fig = go.Figure()
            for y in sorted(df_m["سال"].unique()):
                d = df_m[df_m["سال"] == y]
                fig.add_trace(go.Scatter(
                    x=d["برچسب"].tolist(), y=d["حاشیه"].tolist(),
                    mode="lines+markers+text", name=str(y),
                    line=dict(width=2.5, color=color_map.get(y, "#333")),
                    marker=dict(size=8),
                    text=[f"{v:.1f}%" for v in d["حاشیه"]],
                    textposition="top center", textfont=dict(size=11),
                ))
            fig.update_layout(
                title="حاشیه سود خالص عملیاتی",
                xaxis=dict(title="دوره منتهی به", tickangle=-20),
                yaxis=dict(title="حاشیه سود (%)", ticksuffix="%", gridcolor="#eee"),
                legend=dict(orientation="h", y=1.12), height=400,
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=50, r=30, t=60, b=60),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داده حاشیه سود موجود نیست.")
    else:
        st.info("دوره مالی ثبت نشده است.")

with st.expander("نمودار نسبت مطالبات به دارایی جاری", expanded=True):
    if periods:
        recv_records = []
        for r in periods:
            _, _, recv_r, _ = calc_metrics(r)
            if recv_r is not None:
                end_m, end_d = r["end_month"], r["end_day"]
                label = f"{end_m:02d}/{end_d:02d}" if end_m and end_d else period_label(r["period_type"])
                recv_records.append({"سال": r["year_solar"], "برچسب": label, "نسبت": recv_r * 100, "ترتیب": r["period_type"]})
        if recv_records:
            df_r = pd.DataFrame(recv_records).sort_values(["سال", "ترتیب"])
            fig = go.Figure()
            for y in sorted(df_r["سال"].unique()):
                d = df_r[df_r["سال"] == y]
                fig.add_trace(go.Scatter(
                    x=d["برچسب"].tolist(), y=d["نسبت"].tolist(),
                    mode="lines+markers+text", name=str(y),
                    line=dict(width=2.5, color=color_map.get(y, "#333")),
                    marker=dict(size=8),
                    text=[f"{v:.1f}%" for v in d["نسبت"]],
                    textposition="top center", textfont=dict(size=11),
                ))
            fig.update_layout(
                title="نسبت مطالبات به دارایی جاری",
                xaxis=dict(title="دوره منتهی به", tickangle=-20),
                yaxis=dict(title="نسبت مطالبات (%)", ticksuffix="%", gridcolor="#eee"),
                legend=dict(orientation="h", y=1.12), height=400,
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=50, r=30, t=60, b=60),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("داده نسبت مطالبات موجود نیست.")
    else:
        st.info("دوره مالی ثبت نشده است.")

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
                x=df_y["ماه"].tolist(), y=df_y["کل"].tolist(),
                mode="lines+markers+text", name=str(y),
                line=dict(width=2.5, color=color_map.get(y, "#333")),
                marker=dict(size=7),
                text=[f"{v:,.0f}" for v in df_y["کل"]],
                textposition="top center", textfont=dict(size=9),
            ))
        fig.update_layout(
            title="فروش کل ماهانه",
            xaxis=dict(title="ماه", tickmode="array", tickvals=list(range(1, 13)),
                       ticktext=[MONTH_NAMES[i] for i in range(1, 13)]),
            yaxis=dict(title="میلیارد ریال", gridcolor="#eee"),
            legend=dict(orientation="h", y=1.12), height=400,
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=50, r=30, t=60, b=60),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("فروش ماهانه ثبت نشده است.")

with st.expander("نمودار فروش داخلی و صادراتی", expanded=False):
    if selected_years and len(df_chart) > 0:
        year_bar = st.selectbox("سال", options=selected_years, index=len(selected_years)-1, key="bar_year")
        df_bar = df_chart[df_chart["سال"] == year_bar].sort_values("ماه")
        nonzero = df_bar[df_bar["کل"] > 0]
        if len(nonzero) > 0:
            last_m = int(nonzero["ماه"].max())
            df_bar = df_bar[df_bar["ماه"] <= last_m]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in df_bar["ماه"]], y=df_bar["داخلی"].tolist(),
            name="داخلی", marker_color="#2563eb",
            text=[f"{v:,.0f}" for v in df_bar["داخلی"]], textposition="outside",
        ))
        fig.add_trace(go.Bar(
            x=[MONTH_NAMES[m] for m in df_bar["ماه"]], y=df_bar["صادراتی"].tolist(),
            name="صادراتی", marker_color="#ea580c",
            text=[f"{v:,.0f}" for v in df_bar["صادراتی"]], textposition="outside",
        ))
        fig.update_layout(
            barmode="group", title=f"فروش داخلی و صادراتی — {year_bar}",
            xaxis_title="ماه", yaxis_title="میلیارد ریال", height=400,
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.12),
            margin=dict(l=50, r=30, t=60, b=50),
        )
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
                    row_g[str(y)] = f"{val:,.0f}"
                    has_any = True
                else:
                    row_g[str(y)] = "—"
                if i > 0:
                    prev_y = y_sorted[i-1]
                    prev_s = df_chart[(df_chart["سال"] == prev_y) & (df_chart["ماه"] == m)]["کل"]
                    prev_val = float(prev_s.iloc[0]) if len(prev_s) > 0 else None
                    if val is not None and val > 0 and prev_val is not None and prev_val > 0:
                        growth = (val - prev_val) / prev_val * 100
                        row_g[f"رشد {y}"] = f"{growth:+.1f}%"
                    else:
                        row_g[f"رشد {y}"] = "—"
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
    latest = periods[0]
    op_p, margin, recv_r, div_r = calc_metrics(latest)
    st.caption(f"{latest['year_solar']} — {period_label(latest['period_type'], latest['end_day'], latest['end_month'])}")

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
        annual = [r for r in periods if r["period_type"] == 12]
        if annual:
            annual_sorted = sorted(annual, key=lambda x: x["year_solar"])
            years_a = [r["year_solar"] for r in annual_sorted]
            revenues = [r["operating_revenue"] or 0 for r in annual_sorted]
            op_profits = []
            for r in annual_sorted:
                op, _, _, _ = calc_metrics(r)
                op_profits.append(op if op is not None else 0)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=years_a, y=revenues, name="درآمد عملیاتی", marker_color="#2563eb"))
            fig.add_trace(go.Bar(x=years_a, y=op_profits, name="سود خالص عملیاتی", marker_color="#dc2626"))
            fig.update_layout(
                barmode="group", xaxis_title="سال", yaxis_title="میلیارد ریال",
                height=360, plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", y=1.12),
                margin=dict(l=40, r=30, t=40, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("دوره سالانه ثبت نشده است.")

    with st.expander("جدول کامل دوره‌های مالی", expanded=True):
        data = []
        for row in periods:
            op_p, margin, recv_r, div_r = calc_metrics(row)
            data.append({
                "سال": row["year_solar"],
                "دوره": period_label(row["period_type"], row["end_day"], row["end_month"]),
                "درآمد عملیاتی": fmt(row["operating_revenue"]),
                "سود خالص": fmt(row["net_profit"]),
                "سود خالص عملیاتی": fmt(op_p),
                "حاشیه سود": fmt_pct(margin),
                "نسبت مطالبات": fmt_pct(recv_r),
                "حقوق مالکانه": fmt(row["equity"]),
            })
        st.table(pd.DataFrame(data))

    with st.expander("جزئیات یک دوره", expanded=False):
        period_labels = [
            f"{r['year_solar']} - {period_label(r['period_type'], r['end_day'], r['end_month'])}"
            for r in periods
        ]
        chosen = st.selectbox("انتخاب دوره", options=period_labels)
        if chosen:
            idx = period_labels.index(chosen)
            row = periods[idx]
            op_p, margin, recv_r, div_r = calc_metrics(row)
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown("**سود و زیان**")
                st.write(f"درآمد عملیاتی: {fmt(row['operating_revenue'])}")
                st.write(f"بهای تمام‌شده: {fmt(row['cogs'])}")
                st.write(f"سایر درآمدها: {fmt(row['other_income'])}")
                st.write(f"سایر غیرعملیاتی: {fmt(row['non_operating_income'])}")
                st.write(f"سود خالص: {fmt(row['net_profit'])}")
                st.write(f"**سود عملیاتی: {fmt(op_p)}**")
                st.write(f"**حاشیه سود: {fmt_pct(margin)}**")
            with d2:
                st.markdown("**ترازنامه**")
                st.write(f"موجودی کالا: {fmt(row['inventory'])}")
                st.write(f"دریافتنی تجاری: {fmt(row['trade_receivables'])}")
                st.write(f"حقوق مالکانه: {fmt(row['equity'])}")
                st.write(f"دارایی جاری: {fmt(row['current_assets'])}")
                st.write(f"جمع دارایی‌ها: {fmt(row['total_assets'])}")
                st.write(f"**نسبت مطالبات: {fmt_pct(recv_r)}**")
            with d3:
                st.markdown("**سایر**")
                st.write(f"سود جامع: {fmt(row['comprehensive_income'])}")
                st.write(f"سود مصوب: {fmt(row['approved_dividend'])}")
                st.write(f"**نسبت سود مصوب: {fmt_pct(div_r)}**")