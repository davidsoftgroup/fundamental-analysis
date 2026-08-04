# -*- coding: utf-8 -*-
import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, init_db

st.set_page_config(page_title="مقایسه فصلی", layout="wide")

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

st.title("مقایسه فصلی")
st.caption("فصل‌ها از تفاضل دوره‌های تجمعی استخراج می‌شوند: فصل۱=۳ماهه | فصل۲=۶−۳ | فصل۳=۹−۶ | فصل۴=۱۲−۹")

init_db()

MONTH_NAMES = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#ea580c", "#7c3aed", "#0891b2"]
Q_LABELS = {1: "فصل ۱", 2: "فصل ۲", 3: "فصل ۳", 4: "فصل ۴"}
TABLE_COLS = ["سال", "فصل ۱", "فصل ۲", "فصل ۳", "فصل ۴"]

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
        ORDER BY p.year_solar, p.period_type
    """, (company_id,)).fetchall()
    conn.close()
    return rows

def safe_num(v):
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None

def safe_div(a, b):
    try:
        if a is None or b is None or float(b) == 0:
            return None
        return float(a) / float(b)
    except Exception:
        return None

def op_profit(row):
    np_ = safe_num(row["net_profit"])
    if np_ is None:
        return None
    other = safe_num(row["other_income"]) or 0.0
    non_op = safe_num(row["non_operating_income"]) or 0.0
    return np_ - other - non_op

def subtract(a, b):
    if a is None or b is None:
        return None
    return a - b

def extract_quarters_for_year(year_rows):
    by_type = {}
    for r in year_rows:
        by_type[int(r["period_type"])] = r

    def get_field(ptype, field_fn):
        r = by_type.get(ptype)
        if not r:
            return None
        return field_fn(r)

    rev = {t: get_field(t, lambda r: safe_num(r["operating_revenue"])) for t in [3, 6, 9, 12]}
    op = {t: get_field(t, op_profit) for t in [3, 6, 9, 12]}
    np_ = {t: get_field(t, lambda r: safe_num(r["net_profit"])) for t in [3, 6, 9, 12]}
    cogs = {t: get_field(t, lambda r: safe_num(r["cogs"])) for t in [3, 6, 9, 12]}

    q_rev = {
        1: rev[3],
        2: subtract(rev[6], rev[3]),
        3: subtract(rev[9], rev[6]),
        4: subtract(rev[12], rev[9]),
    }
    q_op = {
        1: op[3],
        2: subtract(op[6], op[3]),
        3: subtract(op[9], op[6]),
        4: subtract(op[12], op[9]),
    }
    q_np = {
        1: np_[3],
        2: subtract(np_[6], np_[3]),
        3: subtract(np_[9], np_[6]),
        4: subtract(np_[12], np_[9]),
    }
    q_cogs = {
        1: cogs[3],
        2: subtract(cogs[6], cogs[3]),
        3: subtract(cogs[9], cogs[6]),
        4: subtract(cogs[12], cogs[9]),
    }

    period_for_q = {1: 3, 2: 6, 3: 9, 4: 12}
    quarters = {}
    for q in [1, 2, 3, 4]:
        ptype = period_for_q[q]
        r = by_type.get(ptype)
        recv = safe_num(r["trade_receivables"]) if r else None
        cur = safe_num(r["current_assets"]) if r else None
        inv = safe_num(r["inventory"]) if r else None
        eq = safe_num(r["equity"]) if r else None

        revenue = q_rev[q]
        op_p = q_op[q]

        quarters[q] = {
            "revenue": revenue,
            "cogs": q_cogs[q],
            "op_profit": op_p,
            "net_profit": q_np[q],
            "margin": safe_div(op_p, revenue),
            "recv_ratio": safe_div(recv, cur),
            "inventory": inv,
            "equity": eq,
            "trade_receivables": recv,
            "current_assets": cur,
            "has_source": r is not None,
        }
    return quarters

def build_quarterly_data(periods):
    by_year = {}
    for r in periods:
        y = int(r["year_solar"])
        by_year.setdefault(y, []).append(r)

    result = {}
    for y, rows in sorted(by_year.items()):
        result[y] = extract_quarters_for_year(rows)
    return result

def fmt(v):
    if v is None:
        return "—"
    try:
        return "{:,.0f}".format(float(v))
    except Exception:
        return "—"

def fmt_pct(v):
    if v is None:
        return "—"
    try:
        return "{:.1f}%".format(float(v) * 100)
    except Exception:
        return "—"

def render_table(title, rows, columns):
    html = [
        '<div style="margin: 1rem 0 1.5rem 0;">',
        '<div style="background: linear-gradient(90deg, #475569, #94a3b8);',
        ' color: white; font-weight: 600; font-size: 0.95rem;',
        ' padding: 0.7rem 1rem; border-radius: 12px 12px 0 0;',
        ' text-align: center; font-family: Vazirmatn, Tahoma, sans-serif;">',
        title,
        '</div>',
        '<div style="overflow-x: auto; border: 1px solid #e2e8f0;',
        ' border-top: none; border-radius: 0 0 12px 12px;',
        ' box-shadow: 0 2px 8px rgba(15,23,42,0.06);">',
        '<table style="width:100%; border-collapse: collapse; direction: rtl;',
        ' text-align: center; font-size: 13px; font-family: Vazirmatn, Tahoma, sans-serif;">',
        '<thead><tr style="background: #f1f5f9;">'
    ]
    for col in columns:
        html.append(
            '<th style="padding: 10px 12px; border-bottom: 2px solid #cbd5e1;'
            ' color: #334155; font-weight: 600; white-space: nowrap;">{}</th>'.format(col)
        )
    html.append('</tr></thead><tbody>')

    for i, row in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
        year_val = str(row.get("سال", ""))
        if year_val.startswith("رشد"):
            bg = "#fef9c3"
        html.append('<tr style="background: {};">'.format(bg))
        for col in columns:
            val = row.get(col, "—")
            weight = "font-weight: 600;" if col == "سال" else ""
            html.append(
                '<td style="padding: 9px 12px; border-bottom: 1px solid #e2e8f0;'
                ' color: #0f172a; {}">{}</td>'.format(weight, val)
            )
        html.append('</tr>')

    html.append('</tbody></table></div></div>')
    st.markdown("".join(html), unsafe_allow_html=True)

def make_line_chart(title, years, series_dict, y_is_pct=False):
    fig = go.Figure()
    for i, (name, vals) in enumerate(series_dict.items()):
        y = []
        for v in vals:
            if v is None:
                y.append(None)
            elif y_is_pct:
                y.append(v * 100)
            else:
                y.append(v)
        fig.add_trace(go.Scatter(
            x=[str(y_) for y_ in years],
            y=y,
            mode="lines+markers",
            name=name,
            line=dict(color=COLORS[i % len(COLORS)], width=2.5),
            marker=dict(size=8),
            connectgaps=False,
        ))
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        height=380,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="سال", gridcolor="#f1f5f9"),
        yaxis=dict(
            title="درصد" if y_is_pct else "مبلغ",
            gridcolor="#f1f5f9",
            zeroline=True,
            zerolinecolor="#cbd5e1",
        ),
        hovermode="x unified",
    )
    return fig

def make_grouped_bar(title, categories, series_dict, y_is_pct=False):
    fig = go.Figure()
    for i, (name, vals) in enumerate(series_dict.items()):
        y = []
        for v in vals:
            if v is None:
                y.append(None)
            elif y_is_pct:
                y.append(v * 100)
            else:
                y.append(v)
        if y_is_pct:
            texts = ["{:.1f}".format(v) if v is not None else "" for v in y]
        else:
            texts = [fmt(v) if v is not None else "" for v in vals]
        fig.add_trace(go.Bar(
            name=str(name),
            x=categories,
            y=y,
            marker_color=COLORS[i % len(COLORS)],
            text=texts,
            textposition="outside",
        ))
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        barmode="group",
        height=400,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(title="فصل"),
        yaxis=dict(title="درصد" if y_is_pct else "مبلغ", gridcolor="#f1f5f9"),
    )
    return fig

# ============================================================
# انتخاب شرکت
# ============================================================
companies = get_companies()
if not companies:
    st.warning("هنوز شرکتی ثبت نشده است.")
    st.stop()

placeholder = "— یک شرکت انتخاب کنید —"
options = {placeholder: None}
for c in companies:
    label = "{} — {}".format(c["symbol"], c["name_fa"] or "")
    options[label] = c

selected = st.selectbox("انتخاب شرکت:", options=list(options.keys()))

if selected == placeholder or options[selected] is None:
    st.info("برای مشاهده مقایسه فصلی، ابتدا یک شرکت انتخاب کنید.")
    st.stop()

company = options[selected]
company_id = company["id"]
fiscal_m = int(company["fiscal_end_month"] or 12)
fiscal_d = int(company["fiscal_end_day"] or 29)

st.success("شرکت: **{}** | پایان سال مالی: {} {}".format(
    company["symbol"], fiscal_d, MONTH_NAMES.get(fiscal_m, fiscal_m)
))

periods = get_periods(company_id)
if not periods:
    st.warning("برای این شرکت هنوز صورت مالی ثبت نشده است.")
    st.stop()

qdata = build_quarterly_data(periods)
years = sorted(qdata.keys())

if not years:
    st.warning("داده فصلی قابل استخراج نیست.")
    st.stop()

st.markdown("---")

# ============================================================
# فیلتر سال‌ها
# ============================================================
c1, c2 = st.columns([3, 1])
with c1:
    selected_years = st.multiselect(
        "سال‌های مورد نظر:",
        options=years,
        default=years[-min(4, len(years)):]
    )
with c2:
    st.write("")
    show_yoy = st.checkbox("نمایش رشد سالانه (YoY)", value=True)

if not selected_years:
    st.info("حداقل یک سال انتخاب کنید.")
    st.stop()

selected_years = sorted(selected_years)

# ============================================================
# جدول درآمد
# ============================================================
rows_rev = []
for y in selected_years:
    row = {"سال": str(y)}
    for q in [1, 2, 3, 4]:
        row[Q_LABELS[q]] = fmt(qdata[y][q]["revenue"])
    rows_rev.append(row)

if show_yoy and len(selected_years) >= 2:
    for i, y in enumerate(selected_years):
        if i == 0:
            continue
        prev = selected_years[i - 1]
        yoy_row = {"سال": "رشد {} به {}".format(y, prev)}
        for q in [1, 2, 3, 4]:
            cur_v = qdata[y][q]["revenue"]
            prev_v = qdata[prev][q]["revenue"]
            g = safe_div(subtract(cur_v, prev_v), prev_v)
            yoy_row[Q_LABELS[q]] = fmt_pct(g)
        rows_rev.append(yoy_row)

render_table("درآمد عملیاتی فصلی", rows_rev, TABLE_COLS)

# ============================================================
# جدول حاشیه سود
# ============================================================
rows_m = []
for y in selected_years:
    row = {"سال": str(y)}
    for q in [1, 2, 3, 4]:
        row[Q_LABELS[q]] = fmt_pct(qdata[y][q]["margin"])
    rows_m.append(row)

render_table("حاشیه سود خالص عملیاتی فصلی", rows_m, TABLE_COLS)

# ============================================================
# جداول بیشتر
# ============================================================
with st.expander("جدول سود خالص عملیاتی فصلی", expanded=False):
    rows_op = []
    for y in selected_years:
        row = {"سال": str(y)}
        for q in [1, 2, 3, 4]:
            row[Q_LABELS[q]] = fmt(qdata[y][q]["op_profit"])
        rows_op.append(row)
    render_table("سود خالص عملیاتی فصلی", rows_op, TABLE_COLS)

with st.expander("جدول نسبت مطالبات (مانده پایان دوره)", expanded=False):
    rows_r = []
    for y in selected_years:
        row = {"سال": str(y)}
        for q in [1, 2, 3, 4]:
            row[Q_LABELS[q]] = fmt_pct(qdata[y][q]["recv_ratio"])
        rows_r.append(row)
    render_table("نسبت مطالبات به دارایی جاری", rows_r, TABLE_COLS)
    st.caption("نسبت مطالبات از مانده ترازنامه همان دوره تجمعی است (تفریق فصلی نمی‌شود).")

st.markdown("---")
st.subheader("نمودارها")

rev_series = {}
margin_series = {}
op_series = {}
for q in [1, 2, 3, 4]:
    rev_series[Q_LABELS[q]] = [qdata[y][q]["revenue"] for y in selected_years]
    margin_series[Q_LABELS[q]] = [qdata[y][q]["margin"] for y in selected_years]
    op_series[Q_LABELS[q]] = [qdata[y][q]["op_profit"] for y in selected_years]

st.plotly_chart(
    make_line_chart("روند درآمد عملیاتی فصلی در سال‌های مختلف", selected_years, rev_series),
    use_container_width=True
)

st.plotly_chart(
    make_line_chart("روند حاشیه سود فصلی", selected_years, margin_series, y_is_pct=True),
    use_container_width=True
)

st.plotly_chart(
    make_line_chart("روند سود خالص عملیاتی فصلی", selected_years, op_series),
    use_container_width=True
)

st.markdown("---")
st.subheader("مقایسه فصول در هر سال")

bar_rev = {}
bar_margin = {}
for y in selected_years:
    bar_rev[str(y)] = [qdata[y][q]["revenue"] for q in [1, 2, 3, 4]]
    bar_margin[str(y)] = [qdata[y][q]["margin"] for q in [1, 2, 3, 4]]

cats = [Q_LABELS[q] for q in [1, 2, 3, 4]]

st.plotly_chart(
    make_grouped_bar("درآمد عملیاتی به تفکیک فصل و سال", cats, bar_rev),
    use_container_width=True
)

st.plotly_chart(
    make_grouped_bar("حاشیه سود به تفکیک فصل و سال", cats, bar_margin, y_is_pct=True),
    use_container_width=True
)

with st.expander("راهنمای محاسبه فصل‌ها"):
    st.markdown("""
**استخراج فصل خالص از دوره‌های تجمعی:**

| فصل | فرمول |
|-----|--------|
| فصل ۱ | مقدار ۳ ماهه |
| فصل ۲ | مقدار ۶ ماهه − مقدار ۳ ماهه |
| فصل ۳ | مقدار ۹ ماهه − مقدار ۶ ماهه |
| فصل ۴ | مقدار ۱۲ ماهه − مقدار ۹ ماهه |

- اگر یکی از دو دوره لازم موجود نباشد، آن فصل خالی (`—`) نمایش داده می‌شود.
- اقلام ترازنامه (مطالبات، موجودی و ...) مانده پایان دوره هستند و تفریق نمی‌شوند.
- فصل‌ها نسبت به **شروع سال مالی همان شرکت** هستند، نه لزوماً فصول تقویم شمسی.
""")