import html
import inspect
import os
import hashlib
from datetime import datetime
from io import BytesIO, StringIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ai_analyst
from ai_analyst import analyze_question

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SalesMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto",
)

FILE_PATH = "data/AI_Sales_Analytics_Sales_Data.xlsx"
OPTIONAL_DIMENSIONS = ["Product", "Salesperson", "Customer_Type"]

# =========================================================
# DESIGN TOKENS
# =========================================================
# Deep-sea teal surfaces, saffron for revenue and emphasis,
# mint for profit and gains, coral for losses.

C = {
    "bg": "#061225",
    "bg2": "#08172D",
    "surface": "#0D1D38",
    "surface2": "#12294B",
    "line": "#172C4D",
    "line2": "#29466E",
    "text": "#F0F5FF",
    "muted": "#9BAFCE",
    "saffron": "#287BFF",
    "mint": "#10D6B0",
    "coral": "#FF668A",
}

FONT_DISPLAY = "'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif"
FONT_BODY = "'Instrument Sans', 'Segoe UI', system-ui, sans-serif"

ROOT_VARS = (
    ":root{"
    + "".join(f"--{k}:{v};" for k, v in C.items())
    + f"--display:{FONT_DISPLAY};--body:{FONT_BODY};"
    + "}"
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&display=swap');

/*VARS*/

/* ---------- base ---------- */

html, body, .stApp,
.stApp [data-testid="stMarkdownContainer"],
.stApp label, .stApp input, .stApp textarea, .stApp button,
[data-testid="stSidebar"] {
    font-family: var(--body);
}

.stApp { background: var(--bg); color: var(--text); }

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    visibility: hidden;
}
header[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1280px;
    padding: 3.25rem 2.5rem 4rem;
}

button:focus-visible, [role="tab"]:focus-visible, a:focus-visible { outline: 2px solid var(--saffron) !important; outline-offset: 2px; }

/* ---------- headline ---------- */

.sm-headline {
    font-family: var(--display);
    font-weight: 600;
    font-size: clamp(1.9rem, 3.6vw, 3rem);
    line-height: 1.08;
    letter-spacing: -0.025em;
    color: var(--text);
    max-width: 26em;
    margin: 0;
}
.sm-scope {
    color: var(--muted);
    font-size: 1rem;
    margin: 0.9rem 0 0;
    max-width: 52em;
}

/* ---------- ask ---------- */

.st-key-ask { margin-top: 2rem; }

[data-testid="stForm"] { border: 0; padding: 0; background: transparent; }
[data-testid="InputInstructions"] { display: none; }

.st-key-ask [data-testid="stTextInputRootElement"] {
    background: var(--surface);
    border: 1px solid var(--line2);
    border-radius: 14px;
    height: 3.5rem;
    box-shadow: none;
}
.st-key-ask [data-testid="stTextInputRootElement"]:focus-within {
    border-color: var(--saffron);
    box-shadow: 0 0 0 3px rgba(244, 183, 64, 0.18);
}
.st-key-ask [data-testid="stTextInputRootElement"] > div { background: transparent; border: 0; }
.st-key-ask [data-testid="stTextInputRootElement"] input {
    background: transparent;
    color: var(--text);
    border: 0;
    box-shadow: none;
    height: 100%;
    padding: 0 1.2rem;
    font-size: 1.05rem;
}
.st-key-ask [data-testid="stTextInputRootElement"] input::placeholder { color: var(--muted); opacity: 0.85; }

[data-testid="stFormSubmitButton"] button {
    height: 3.5rem;
    border-radius: 14px;
    background: var(--saffron);
    border: 0;
    color: #1B1503;
    font-weight: 600;
    font-size: 1.02rem;
}
[data-testid="stFormSubmitButton"] button:hover { background: #FFC85C; color: #1B1503; }
[data-testid="stFormSubmitButton"] button p { color: #1B1503; }

.st-key-chips {
    flex-direction: row !important;
    flex-wrap: wrap;
    gap: 0.5rem !important;
    margin-top: 0.35rem;
}
.st-key-chips > div { width: auto !important; flex: 0 0 auto; }
.st-key-chips button {
    background: transparent;
    border: 1px solid var(--line2);
    border-radius: 999px;
    min-height: 2.1rem;
    padding: 0.2rem 0.95rem;
    color: var(--muted);
}
.st-key-chips button p { font-size: 0.88rem; color: inherit; }
.st-key-chips button:hover {
    border-color: var(--saffron);
    color: var(--text);
    background: rgba(244, 183, 64, 0.08);
}

/* ---------- answer ---------- */

.st-key-answer {
    margin-top: 1.5rem;
    background: var(--surface);
    border: 1px solid var(--line2);
    border-left: 3px solid var(--saffron);
    border-radius: 14px;
    padding: 1.4rem 1.6rem 1.2rem;
    animation: sm-in 0.25s ease-out both;
}
.st-key-answer .a-question { color: var(--muted); font-size: 0.92rem; margin: 0; }
.st-key-answer-text [data-testid="stMarkdownContainer"] p {
    font-family: var(--display);
    font-weight: 500;
    font-size: clamp(1.25rem, 2vw, 1.65rem);
    line-height: 1.35;
    letter-spacing: -0.01em;
    color: var(--text);
    margin: 0.2rem 0 0.8rem;
    max-width: 40em;
}
.a-evidence-title, .a-chart-title {
    font-family: var(--display);
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--text);
    margin: 0.4rem 0 0.35rem;
}
.a-evidence { margin: 0; padding-left: 1.1rem; color: var(--muted); font-size: 0.92rem; line-height: 1.7; }
.st-key-answer-clear button {
    min-height: 1.9rem;
    padding: 0.1rem 0.7rem;
    background: transparent;
    border: 1px solid var(--line2);
    border-radius: 999px;
    color: var(--muted);
}
.st-key-answer-clear button p { font-size: 0.82rem; color: inherit; }
.st-key-answer-clear button:hover { border-color: var(--saffron); color: var(--text); }

/* ---------- KPI band ---------- */

.kpis {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    margin: 2.5rem 0 1.5rem;
    border-top: 1px solid var(--line2);
    border-bottom: 1px solid var(--line);
}
.kpi { padding: 1.3rem 1.5rem 1.2rem 0; position: relative; }
.kpi + .kpi { padding-left: 1.5rem; border-left: 1px solid var(--line); }
.kpi-label { color: var(--muted); font-size: 0.92rem; font-weight: 500; }
.kpi-value {
    font-family: var(--display);
    font-weight: 600;
    font-size: clamp(1.7rem, 2.6vw, 2.35rem);
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin: 0.25rem 0 0.2rem;
    color: var(--text);
    font-variant-numeric: tabular-nums;
}
.kpi-delta { font-size: 0.86rem; font-weight: 600; min-height: 1.3rem; }
.kpi-delta span { color: var(--muted); font-weight: 400; margin-left: 0.35rem; }
.kpi-delta.up { color: var(--mint); }
.kpi-delta.down { color: var(--coral); }
.kpi-delta.flat { color: var(--muted); font-weight: 400; }
.kpi-spark { display: block; width: 100%; height: 38px; margin-top: 0.8rem; animation: sm-reveal 1s ease-out both; }

/* ---------- sections ---------- */

.sec { margin: 0 0 0.5rem; }
.sec h3 {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.22rem;
    letter-spacing: -0.01em;
    color: var(--text);
    margin: 0;
    padding: 0;
}
.sec p { color: var(--muted); font-size: 0.92rem; margin: 0.2rem 0 0; }

.highlights { list-style: none; margin: 0.9rem 0 0; padding: 0; }
.highlights li {
    display: grid;
    grid-template-columns: 0.6rem 1fr;
    column-gap: 0.8rem;
    padding: 0.85rem 0;
    border-bottom: 1px solid var(--line);
    color: var(--text);
    font-size: 0.97rem;
    line-height: 1.5;
}
.highlights li:first-child { padding-top: 0.2rem; }
.highlights li:last-child { border-bottom: 0; }
.highlights .dot { width: 0.6rem; height: 0.6rem; border-radius: 50%; margin-top: 0.45rem; }
.dot.good { background: var(--mint); }
.dot.bad { background: var(--coral); }
.dot.note { background: var(--saffron); }

/* ---------- leaderboard ---------- */

.lb { margin-top: 0.8rem; }
.lb-row {
    display: grid;
    grid-template-columns: minmax(0, 1.25fr) minmax(0, 1.5fr) auto 4.2rem;
    align-items: center;
    column-gap: 0.9rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--line);
    font-size: 0.94rem;
}
.lb-row:last-child { border-bottom: 0; }
.lb-name { color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lb-bar { height: 8px; background: var(--line); border-radius: 4px; overflow: hidden; }
.lb-bar span { display: block; height: 100%; background: var(--saffron); border-radius: 4px; }
.lb-val { color: var(--text); font-variant-numeric: tabular-nums; text-align: right; min-width: 4.8rem; }
.lb-m { font-size: 0.86rem; font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }
.lb-m.up { color: var(--mint); }
.lb-m.down { color: var(--coral); }

/* ---------- sidebar ---------- */

[data-testid="stSidebar"] {
    background: var(--bg2);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.2rem; }

.brand { display: flex; align-items: center; gap: 0.7rem; margin: 0 0 0.2rem; }
.brand svg { flex: none; }
.brand-name { font-family: var(--display); font-weight: 700; font-size: 1.35rem; letter-spacing: -0.02em; color: var(--text); }
.brand-sub { color: var(--muted); font-size: 0.85rem; margin: 0 0 1.4rem; }

.side-title {
    font-family: var(--display);
    font-weight: 600;
    font-size: 0.98rem;
    color: var(--text);
    margin: 0.6rem 0 0.3rem;
}
.side-status { color: var(--muted); font-size: 0.84rem; line-height: 1.5; margin-top: 1rem; }
.side-status b { color: var(--text); font-weight: 600; }
.ai-state { display: flex; gap: 0.55rem; align-items: flex-start; }
.ai-state i { flex: none; width: 0.55rem; height: 0.55rem; border-radius: 50%; margin-top: 0.4rem; background: var(--mint); }
.ai-state.off i { background: var(--saffron); }

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
    background: var(--surface);
    border-color: var(--line2);
    border-radius: 10px;
}
[data-testid="stSidebar"] [data-testid="stDateInput"] input { font-size: 0.86rem; }
[data-baseweb="tag"] { background: rgba(244, 183, 64, 0.16) !important; border-radius: 6px; }
[data-baseweb="tag"] span { color: var(--saffron) !important; }
[data-testid="stSidebar"] .stButton button {
    background: transparent;
    border: 1px solid var(--line2);
    border-radius: 10px;
    color: var(--muted);
    width: 100%;
}
[data-testid="stSidebar"] .stButton button:hover { border-color: var(--saffron); color: var(--text); }

/* ---------- tabs ---------- */

[role="tablist"], [data-baseweb="tab-list"] { gap: 1.6rem; border-bottom: 1px solid var(--line); }
[data-testid="stTab"], button[data-baseweb="tab"] { padding: 0.7rem 0; background: transparent; }
[data-testid="stTab"] p, button[data-baseweb="tab"] p {
    font-family: var(--display);
    font-weight: 600;
    font-size: 1.02rem;
    color: var(--muted) !important;
}
[data-testid="stTab"][aria-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--text) !important; }
[data-testid="stTab"]:hover p, button[data-baseweb="tab"]:hover p { color: var(--text) !important; }
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"] {
    background: var(--saffron) !important;
    background-color: var(--saffron) !important;
    height: 3px !important;
}
[data-baseweb="tab-border"] { display: none; }

/* ---------- misc ---------- */

[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 12px; background: transparent; }
[data-testid="stDownloadButton"] button {
    background: transparent;
    border: 1px solid var(--line2);
    border-radius: 10px;
    color: var(--text);
}
[data-testid="stDownloadButton"] button:hover { border-color: var(--saffron); }

.empty {
    border: 1px dashed var(--line2);
    border-radius: 14px;
    padding: 2.2rem 1.6rem;
    margin-top: 2rem;
    color: var(--muted);
}
.empty b { display: block; font-family: var(--display); font-size: 1.2rem; color: var(--text); font-weight: 600; margin-bottom: 0.3rem; }

.sm-foot { color: var(--muted); font-size: 0.84rem; margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--line); }

/* ---------- motion ---------- */

@keyframes sm-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes sm-reveal { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}

/* ---------- responsive ---------- */

@media (max-width: 900px) {
    .block-container { padding: 2.2rem 1.1rem 3rem; }
    .kpis { grid-template-columns: repeat(2, 1fr); }
    .kpi:nth-child(3) { padding-left: 0; border-left: 0; }
    .kpi:nth-child(n+3) { border-top: 1px solid var(--line); }
    .lb-row { grid-template-columns: minmax(0, 1fr) auto 4rem; }
    .lb-bar { display: none; }
}
@media (max-width: 480px) {
    .kpis { grid-template-columns: 1fr; }
    .kpi, .kpi + .kpi { padding-left: 0; border-left: 0; }
    .kpi + .kpi { border-top: 1px solid var(--line); }
}

/* ---------- SalesMind Advisor: reference-inspired navy / electric-blue UI ---------- */
.stApp {
    background:
      radial-gradient(ellipse at 85% 0%, rgba(27, 89, 220, .16), transparent 34%),
      radial-gradient(ellipse at 15% 70%, rgba(10, 199, 198, .06), transparent 35%),
      var(--bg);
}
.block-container { max-width: 1500px; padding-top: 2rem; }
.sm-headline { font-size: clamp(1.8rem, 3vw, 2.65rem); letter-spacing: -.035em; }
.sm-scope { margin-top: .45rem; }
.kpis {
    gap: 1rem; border: 0; margin: 1.6rem 0 1.7rem;
    grid-template-columns: repeat(4, minmax(0, 1fr));
}
.kpi {
    min-width: 0; padding: 1.15rem 1.2rem 1rem !important;
    background: linear-gradient(145deg, rgba(17, 39, 73, .98), rgba(10, 27, 53, .98));
    border: 1px solid rgba(70, 111, 175, .27); border-radius: 17px;
    box-shadow: 0 10px 28px rgba(0,0,0,.13); overflow: hidden;
    transition: transform .18s ease, border-color .18s ease;
}
.kpi:hover { transform: translateY(-2px); border-color: rgba(45, 126, 255, .7); }
.kpi + .kpi { border-left: 1px solid rgba(70, 111, 175, .27); }
.kpi-label { color: #AFC1E1; font-size: .88rem; }
.kpi-value { font-size: clamp(1.45rem, 2vw, 2rem); }
.kpi-spark { height: 32px; margin-top: .45rem; }
.sec { padding: .15rem 0; }
.sec h3 { font-size: 1.12rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08162B 0%, #071326 100%);
    border-right: 1px solid #172D51;
}
.brand svg { filter: drop-shadow(0 0 8px rgba(32, 200, 255, .22)); }
.brand-name { font-size: 1.25rem; }
.side-title { color: #DCE8FF; }
.st-key-ask [data-testid="stTextInputRootElement"]:focus-within {
    border-color: #287BFF; box-shadow: 0 0 0 3px rgba(40,123,255,.18);
}
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(100deg, #246BFF, #4858E8); color: white;
    box-shadow: 0 5px 18px rgba(40, 100, 255, .18);
}
[data-testid="stFormSubmitButton"] button p { color: white; }
[data-testid="stFormSubmitButton"] button:hover { background: linear-gradient(100deg, #3780FF, #5A68F5); color: white; }
.st-key-chips button:hover { border-color: #287BFF; background: rgba(40,123,255,.10); }
.st-key-answer { border-left-color: #10D6B0; background: linear-gradient(135deg, #0D2541, #0B1B34); }
.st-key-answer-clear button:hover { border-color: #287BFF; }
[data-testid="stExpander"] { background: rgba(10, 28, 54, .55); border-color: #1D365C; }
[data-testid="stDownloadButton"] button:hover { border-color: #287BFF; }
[role="tablist"], [data-baseweb="tab-list"] { gap: 1.15rem; border-bottom-color: #1A3155; }
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"] { background: #287BFF !important; background-color: #287BFF !important; }
.empty { background: rgba(12, 31, 59, .6); border-color: #2B4771; }
@media (max-width: 900px) {
    .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 480px) {
    .kpis { grid-template-columns: 1fr; }
}
""".replace("/*VARS*/", ROOT_VARS)

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def stretch(fn):
    """Full-width kwargs that work on both old and new Streamlit."""
    if "width" in inspect.signature(fn).parameters:
        return {"width": "stretch"}
    return {"use_container_width": True}


def _indian_group(n):
    s = str(int(n))
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def inr(x, compact=True):
    """Format rupees with Indian digit grouping (lakh / crore)."""
    if x is None or pd.isna(x):
        return "–"
    sign = "−" if x < 0 else ""
    a = abs(float(x))
    if compact and a >= 1e7:
        return f"{sign}₹{a / 1e7:.2f}\u00a0Cr"
    if compact and a >= 1e5:
        return f"{sign}₹{a / 1e5:.2f}\u00a0L"
    return f"{sign}₹{_indian_group(round(a))}"


_RUPEE = __import__("re").compile(r"₹(-?[\d,]+)(\.\d+)?")


def localize_rupees(text):
    """Re-group rupee amounts from the analysis engine into lakh / crore style."""

    def swap(match):
        whole = match.group(1).replace(",", "")
        if not whole.lstrip("-").isdigit():
            return match.group(0)
        sign = "-" if whole.startswith("-") else ""
        return f"₹{sign}{_indian_group(int(whole.lstrip('-')))}{match.group(2) or ''}"

    return _RUPEE.sub(swap, str(text))


def inr_tick(x):
    a = abs(x)
    sign = "−" if x < 0 else ""
    if a >= 1e7:
        return f"{sign}₹{round(a / 1e7, 2):g} Cr"
    if a >= 1e5:
        return f"{sign}₹{round(a / 1e5, 2):g} L"
    if a >= 1e3:
        return f"{sign}₹{round(a / 1e3, 1):g}K"
    return f"{sign}₹{round(a):g}"


def nice_ticks(lo, hi, n=4):
    """Round tick values so money axes read in lakh / crore."""
    lo = min(lo, 0)
    span = max(hi - lo, 1)
    raw = span / n
    mag = 10 ** (len(str(int(raw))) - 1) if raw >= 1 else 1
    for mult in (1, 2, 2.5, 5, 10):
        step = mult * mag
        if step >= raw:
            break
    start = (lo // step) * step
    vals, v = [], start
    while True:
        vals.append(v)
        if v >= hi:
            break
        v += step
    return vals, [inr_tick(t) for t in vals]


def greeting():
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        now = datetime.now()
    if now.hour < 12:
        return "Good morning"
    if now.hour < 17:
        return "Good afternoon"
    return "Good evening"


def fmt_date(ts):
    return f"{ts.day} {ts:%b %Y}"


def esc(text):
    return html.escape(str(text))


def show_chart(fig):
    st.plotly_chart(
        fig,
        key=f"salesmind_chart_{id(fig)}",
        theme=None,
        config={"displayModeBar": False, "scrollZoom": False},
        **stretch(st.plotly_chart),
    )


def style_fig(fig, height, legend=False):
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=4, t=8, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=C["muted"], size=12),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(color=C["text"], size=12), bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=C["surface2"], bordercolor=C["line2"],
            font=dict(color=C["text"], family=FONT_BODY, size=13),
        ),
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig


def section(title, subtitle=""):
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="sec"><h3>{esc(title)}</h3>{sub}</div>',
        unsafe_allow_html=True,
    )


def list_text(items, all_label):
    items = list(items)
    if not items:
        return all_label
    if len(items) <= 3:
        return ", ".join(items[:-1]) + (" and " if len(items) > 1 else "") + items[-1]
    return f"{len(items)} selections"


# =========================================================
# UNIVERSAL DATA INPUT + COLUMN MAPPING
# =========================================================

ALIASES = {
    "date": ["date", "order_date", "order date", "transaction_date", "transaction date", "invoice_date", "timestamp", "month", "period"],
    "sales": ["sales", "revenue", "total_revenue", "total revenue", "amount", "sales_amount", "gross_sales", "turnover", "income", "total_amount", "price_total"],
    "profit": ["profit", "net_profit", "net profit", "gross_profit", "gross profit", "earnings", "contribution"],
    "cost": ["cost", "costs", "total_cost", "total cost", "expenses", "expense", "total_expenses", "total expenses", "cogs", "cost_of_goods_sold"],
    "region": ["region", "territory", "market", "location", "area", "state", "country", "city", "branch"],
    "category": ["category", "product_category", "product category", "department", "segment", "business_unit", "business unit", "type"],
    "product": ["product", "product_name", "product name", "item", "item_name", "service", "sku"],
    "salesperson": ["salesperson", "sales_person", "sales person", "representative", "rep", "employee", "agent", "owner"],
    "customer": ["customer_type", "customer type", "customer_segment", "customer segment", "customer", "client", "account"],
}


def _norm_col(value):
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _guess_column(columns, aliases, numeric_only=False, df=None):
    normalized = {_norm_col(c): c for c in columns}
    for alias in aliases:
        key = _norm_col(alias)
        if key in normalized:
            col = normalized[key]
            if not numeric_only or pd.to_numeric(df[col], errors="coerce").notna().any():
                return col
    if numeric_only and df is not None:
        candidates = [c for c in columns if pd.to_numeric(df[c], errors="coerce").notna().mean() > 0.6]
        return candidates[0] if candidates else None
    return None


def _read_uploaded(uploaded):
    name = uploaded.name.lower()
    raw = uploaded.getvalue()
    if name.endswith(".csv"):
        try:
            return pd.read_csv(BytesIO(raw))
        except UnicodeDecodeError:
            return pd.read_csv(BytesIO(raw), encoding="latin-1")
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(raw))
    raise ValueError("Please upload an Excel (.xlsx, .xls) or CSV (.csv) file.")


@st.cache_data(show_spinner=False)
def load_data(path, mtime):
    return pd.read_excel(path)

st.markdown('<h1 class="sm-headline">Your business, understood.</h1><p class="sm-scope">Your sales, profit, and growth opportunities — brought together in one AI-powered business overview.</p>', unsafe_allow_html=True)

upload_col, info_col = st.columns([2, 1], gap="large")
with upload_col:
    uploaded_file = st.file_uploader("Upload your business data", type=["xlsx", "xls", "csv"], help="Excel and CSV files are supported. Your file is analysed in this app session.")
with info_col:
    st.markdown("<div class='empty'><b>Bring your own data</b><br>Retail, e-commerce, services, restaurants, operations, and more. Column names do not need to match the sample dataset.</div>", unsafe_allow_html=True)

try:
    if uploaded_file is not None:
        source_df = _read_uploaded(uploaded_file)
        source_name = uploaded_file.name
    elif os.path.exists(FILE_PATH):
        source_df = load_data(FILE_PATH, os.path.getmtime(FILE_PATH))
        source_name = os.path.basename(FILE_PATH) + " (sample dataset)"
    else:
        st.info("Upload an Excel or CSV file to begin. Your existing sample dataset can also be placed at `data/AI_Sales_Analytics_Sales_Data.xlsx`.")
        st.stop()
except Exception as exc:
    st.error(f"Could not read this file: {exc}")
    st.stop()

if source_df.empty or len(source_df.columns) == 0:
    st.error("This file has no rows or columns to analyse.")
    st.stop()
source_df = source_df.copy()
source_df.columns = [str(c).strip() for c in source_df.columns]
columns = list(source_df.columns)
numeric_candidates = [c for c in columns if pd.to_numeric(source_df[c], errors="coerce").notna().mean() > 0.5]
if not numeric_candidates:
    st.error("I couldn't find numeric columns in this file. Please upload a sheet containing amounts, quantities, costs, or other numeric business metrics.")
    st.dataframe(source_df.head(20), use_container_width=True)
    st.stop()

with st.expander("Review detected columns", expanded=uploaded_file is not None):
    st.caption(f"File: {source_name} · {len(source_df):,} rows · {len(columns):,} columns. Confirm the mapping so calculations use the right fields.")
    m1, m2, m3 = st.columns(3)
    date_guess = _guess_column(columns, ALIASES["date"])
    sales_guess = _guess_column(columns, ALIASES["sales"], True, source_df) or numeric_candidates[0]
    profit_guess = _guess_column(columns, ALIASES["profit"], True, source_df)
    cost_guess = _guess_column(columns, ALIASES["cost"], True, source_df)
    category_guess = _guess_column(columns, ALIASES["category"])
    region_guess = _guess_column(columns, ALIASES["region"])
    product_guess = _guess_column(columns, ALIASES["product"])
    salesperson_guess = _guess_column(columns, ALIASES["salesperson"])
    customer_guess = _guess_column(columns, ALIASES["customer"])
    no_mapping = "— Not available —"
    with m1:
        date_col = st.selectbox("Date / period column", [no_mapping] + columns, index=(columns.index(date_guess)+1 if date_guess in columns else 0), key="map_date")
        sales_col = st.selectbox("Revenue / sales column", numeric_candidates, index=(numeric_candidates.index(sales_guess) if sales_guess in numeric_candidates else 0), key="map_sales")
        profit_options = [no_mapping] + numeric_candidates
        profit_col = st.selectbox("Profit column (if present)", profit_options, index=(profit_options.index(profit_guess) if profit_guess in profit_options else 0), key="map_profit")
    with m2:
        cost_options = [no_mapping] + numeric_candidates
        cost_col = st.selectbox("Cost / expenses column", cost_options, index=(cost_options.index(cost_guess) if cost_guess in cost_options else 0), key="map_cost")
        category_col = st.selectbox("Category / segment column", [no_mapping] + columns, index=(columns.index(category_guess)+1 if category_guess in columns else 0), key="map_category")
        region_col = st.selectbox("Region / location column", [no_mapping] + columns, index=(columns.index(region_guess)+1 if region_guess in columns else 0), key="map_region")
    with m3:
        product_col = st.selectbox("Product / item column", [no_mapping] + columns, index=(columns.index(product_guess)+1 if product_guess in columns else 0), key="map_product")
        salesperson_col = st.selectbox("Salesperson / owner column", [no_mapping] + columns, index=(columns.index(salesperson_guess)+1 if salesperson_guess in columns else 0), key="map_salesperson")
        customer_col = st.selectbox("Customer / client column", [no_mapping] + columns, index=(columns.index(customer_guess)+1 if customer_guess in columns else 0), key="map_customer")

# Convert arbitrary source columns into the canonical fields used by the existing dashboard.
df = source_df.copy()
df["Sales"] = pd.to_numeric(source_df[sales_col], errors="coerce").fillna(0)
profit_available = profit_col != no_mapping
cost_available = cost_col != no_mapping
if profit_available:
    df["Profit"] = pd.to_numeric(source_df[profit_col], errors="coerce")
    profit_source_note = f"Profit taken from '{profit_col}'."
elif cost_available:
    df["Profit"] = df["Sales"] - pd.to_numeric(source_df[cost_col], errors="coerce").fillna(0)
    profit_available = True
    profit_source_note = f"Estimated as mapped revenue '{sales_col}' minus mapped costs '{cost_col}'. This is only as accurate as those columns."
else:
    df["Profit"] = 0.0
    profit_source_note = "Profit is unavailable: map a profit column or a cost/expenses column to calculate it. The zero placeholder is not a real profit result."

if date_col != no_mapping:
    df["Order_Date"] = pd.to_datetime(source_df[date_col], errors="coerce")
    has_dates = df["Order_Date"].notna().any()
else:
    df["Order_Date"] = pd.Timestamp("2000-01-01")
    has_dates = False
if not has_dates:
    df["Order_Date"] = pd.Timestamp("2000-01-01")

for canonical, selected in [("Category", category_col), ("Region", region_col), ("Product", product_col), ("Salesperson", salesperson_col), ("Customer_Type", customer_col)]:
    if selected != no_mapping:
        df[canonical] = source_df[selected].fillna("Unknown").astype(str)
    else:
        df[canonical] = "All data"

if cost_available:
    df["Cost"] = pd.to_numeric(source_df[cost_col], errors="coerce").fillna(0)

if not profit_available:
    st.warning("Profit cannot be calculated from this file yet. Choose a profit column or a cost/expenses column in **Review detected columns**. Revenue alone is not profit.")
    st.markdown("### Dataset overview")
    ov1, ov2, ov3 = st.columns(3)
    ov1.metric("Rows", f"{len(source_df):,}")
    ov2.metric("Columns", f"{len(source_df.columns):,}")
    ov3.metric("Missing cells", f"{int(source_df.isna().sum().sum()):,}")
    st.dataframe(source_df.head(100), use_container_width=True, hide_index=True)
    st.download_button("Download cleaned preview as CSV", source_df.to_csv(index=False).encode("utf-8"), file_name="salesmind_data_preview.csv", mime="text/csv")
    st.markdown("### Ask the business advisor")
    generic_question = st.text_input("Ask about this dataset", placeholder="Summarize this business, identify risks, or suggest what to investigate next", key="generic_business_q")
    if st.button("Analyse dataset", type="primary", key="generic_analyse") and generic_question.strip():
        with st.spinner("Reviewing the dataset and asking Nemotron for insights…"):
            generic_result = analyze_question(source_df, generic_question.strip())
        st.markdown(generic_result.get("answer", "No answer returned."))
        for evidence_item in generic_result.get("evidence", []):
            st.write(f"• {evidence_item}")
        if generic_result.get("ai_error"):
            st.caption("Nemotron was unavailable for this request; showing the local analysis instead.")
    st.stop()
else:
    st.caption(f"**Profit calculation:** {profit_source_note}")
if not has_dates:
    st.info("No usable date column was selected. Date trends are disabled; the dashboard will show the overall dataset rather than a time series.")

# Drop rows without a usable revenue value only if at least one valid value exists.
df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
if df["Sales"].notna().any():
    df = df[df["Sales"].notna()].copy()
else:
    df["Sales"] = 0.0
if df.empty:
    st.error("No rows have usable values in the selected revenue/sales column.")
    st.stop()
df["Sales"] = df["Sales"].fillna(0)
df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
if profit_available:
    df["Profit"] = df["Profit"].fillna(0)
else:
    df["Profit"] = 0.0
if not has_dates:
    MIN_DATE = MAX_DATE = pd.Timestamp("2000-01-01").date()
else:
    df = df.dropna(subset=["Order_Date"])
    if df.empty:
        st.error("The selected date column has no valid dates. Choose another date column or set it to Not available.")
        st.stop()
    MIN_DATE = df["Order_Date"].min().date()
    MAX_DATE = df["Order_Date"].max().date()

ALL_REGIONS = sorted(df["Region"].astype(str).unique().tolist())
ALL_CATEGORIES = sorted(df["Category"].astype(str).unique().tolist())
DIMENSIONS = [c for c in OPTIONAL_DIMENSIONS if c in df.columns and df[c].nunique() > 1 and not (df[c] == "All data").all()]

# =========================================================
# SIDEBAR
# =========================================================

def reset_filters():
    st.session_state["f_dates"] = (MIN_DATE, MAX_DATE)
    st.session_state["f_regions"] = []
    st.session_state["f_cats"] = []


BRAND_MARK = (
    '<svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">'
    f'<rect x="1" y="1" width="28" height="28" rx="8" fill="{C["surface2"]}" stroke="{C["line2"]}"/>'
    f'<path d="M7 20 L13 13 L17 17 L23 9" fill="none" stroke="{C["saffron"]}" stroke-width="2.4" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    f'<circle cx="23" cy="9" r="2.3" fill="{C["mint"]}"/></svg>'
)

with st.sidebar:
    st.markdown(
        f'<div class="brand">{BRAND_MARK}<span class="brand-name">SalesMind</span></div>'
        '<p class="brand-sub">Business intelligence for any spreadsheet</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-title">Filters</div>', unsafe_allow_html=True)

    date_value = st.date_input(
        "Date range" if has_dates else "Date (not supplied)",
        value=(MIN_DATE, MAX_DATE),
        min_value=MIN_DATE,
        max_value=MAX_DATE,
        format="DD/MM/YYYY",
        key="f_dates",
    )
    sel_regions = st.multiselect(
        "Region", ALL_REGIONS, placeholder="All regions", key="f_regions"
    )
    sel_cats = st.multiselect(
        "Category", ALL_CATEGORIES, placeholder="All categories", key="f_cats"
    )

    if isinstance(date_value, (tuple, list)) and len(date_value) == 2:
        start_date, end_date = date_value
    else:
        start_date, end_date = MIN_DATE, MAX_DATE
        st.caption("Pick an end date to apply the date filter.")

    st.button("Reset filters", on_click=reset_filters)

# =========================================================
# FILTER
# =========================================================

mask = ((df["Order_Date"] >= pd.Timestamp(start_date)) & (
    df["Order_Date"] < pd.Timestamp(end_date) + pd.Timedelta(days=1)
)) if has_dates else pd.Series(True, index=df.index)
if sel_regions:
    mask &= df["Region"].isin(sel_regions)
if sel_cats:
    mask &= df["Category"].isin(sel_cats)
d = df[mask]

AI_ON = ai_analyst.client is not None

with st.sidebar:
    ai_line = (
        "<b>AI explanations on.</b> Numbers are calculated from your data, then explained by NVIDIA Nemotron."
        if AI_ON
        else "<b>AI explanations off.</b> Configure NVIDIA_API_KEY in your local .env to enable AI explanations. Calculated answers still work."
    )
    st.markdown(
        f'<div class="side-status ai-state{"" if AI_ON else " off"}"><i></i><div>{ai_line}</div></div>'
        f'<div class="side-status"><b>{len(d):,}</b> of {len(df):,} records match these filters.</div>',
        unsafe_allow_html=True,
    )

# =========================================================
# NUMBERS
# =========================================================

total_sales = float(d["Sales"].sum())
total_profit = float(d["Profit"].sum())
orders = len(d)
margin = total_profit / total_sales * 100 if total_sales else 0.0
aov = total_sales / orders if orders else 0.0

scope_regions = list_text(sel_regions, "all regions")
scope_cats = list_text(sel_cats, "all categories")
scope = (
    f"Showing {scope_regions} and {scope_cats}, "
    f"{fmt_date(pd.Timestamp(start_date))} to {fmt_date(pd.Timestamp(end_date))}."
)

# =========================================================
# HEADLINE
# =========================================================

if d.empty:
    st.markdown(
        f'<h1 class="sm-headline">{greeting()}.</h1>'
        '<div class="empty"><b>No records match these filters</b>'
        "Widen the date range, or clear the region and category filters.</div>",
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(
    f'<h1 class="sm-headline">Business Overview</h1>'
    f'<p class="sm-scope">Here’s what’s happening with your sales · {inr(total_sales)} revenue across {orders:,} records · {margin:.1f}% profit margin</p>'
    f'<p class="sm-scope">{esc(scope)}</p>',
    unsafe_allow_html=True,
)

# =========================================================
# ASK
# =========================================================

SUGGESTIONS = [
    "Summarize business performance",
    "What are the main risks and opportunities?",
]
if profit_available:
    SUGGESTIONS.extend(["What is the profit margin?", "Where are we losing money?"])
if region_col != no_mapping:
    SUGGESTIONS.append(f"Which {str(region_col).replace('_', ' ')} has the highest sales?")
elif category_col != no_mapping:
    SUGGESTIONS.append(f"Which {str(category_col).replace('_', ' ')} has the highest sales?")
if has_dates:
    SUGGESTIONS.append("Show monthly sales trend")
if product_col != no_mapping and profit_available:
    SUGGESTIONS.append(f"What are the top 5 {str(product_col).replace('_', ' ')} by profit?")


def submit_question():
    st.session_state["active_q"] = st.session_state.get("q_input", "").strip()


def pick_question(text):
    st.session_state["q_input"] = text
    st.session_state["active_q"] = text


def clear_question():
    st.session_state["q_input"] = ""
    st.session_state["active_q"] = ""


@st.cache_data(show_spinner="Analyzing your sales data…", ttl=3600)
def run_analysis(question, signature, _frame):
    return analyze_question(_frame, question)


with st.container(key="ask"):
    with st.form("ask_form", border=False):
        col_input, col_btn = st.columns([6, 1], vertical_alignment="center")
        with col_input:
            st.text_input(
                "Ask a question about your business data",
                key="q_input",
                placeholder="Ask about performance, profitability, risks, trends, or growth opportunities",
                label_visibility="collapsed",
            )
        with col_btn:
            st.form_submit_button(
                "Ask", on_click=submit_question, **stretch(st.form_submit_button)
            )

    with st.container(key="chips"):
        for i, text in enumerate(SUGGESTIONS):
            st.button(text, key=f"chip_{i}", on_click=pick_question, args=(text,))

active_q = st.session_state.get("active_q", "")

if active_q:
    dataset_fingerprint = hashlib.sha256(
        (source_name + str(len(df)) + "|" + "|".join(map(str, df.columns)) + "|" +
         str(pd.util.hash_pandas_object(df.astype(str), index=True).sum())).encode("utf-8")
    ).hexdigest()[:20]
    signature = (
        dataset_fingerprint, str(start_date), str(end_date),
        tuple(sorted(sel_regions)), tuple(sorted(sel_cats))
    )
    result = run_analysis(active_q, signature, d)

    with st.container(key="answer"):
        head_l, head_r = st.columns([8, 1], vertical_alignment="center")
        with head_l:
            st.markdown(
                f'<p class="a-question">{esc(active_q)}</p>', unsafe_allow_html=True
            )
        with head_r:
            with st.container(key="answer-clear"):
                st.button("Clear", on_click=clear_question)

        with st.container(key="answer-text"):
            st.markdown(localize_rupees(result["answer"]))

        evidence = result.get("evidence") or []
        if evidence:
            items = "".join(f"<li>{esc(localize_rupees(e))}</li>" for e in evidence)
            st.markdown(
                '<p class="a-evidence-title">How this was calculated</p>'
                f'<ul class="a-evidence">{items}</ul>',
                unsafe_allow_html=True,
            )

        chart_data = result.get("chart_data")
        single_bar = result.get("chart_type") == "bar" and chart_data is not None and len(chart_data) < 2
        if chart_data is not None and len(chart_data) > 0 and not single_bar:
            cols = list(chart_data.columns)
            kind = result.get("chart_type")
            if kind == "line" and {"Order_Date", "Sales"} <= set(cols):
                x_col, y_col = "Order_Date", "Sales"
            else:
                x_col, y_col = cols[0], cols[1]

            xs = chart_data[x_col].astype(str).tolist()
            ys = chart_data[y_col].astype(float).tolist()
            labels = [inr(v) for v in ys]

            fig_ai = go.Figure()
            if kind == "line":
                fig_ai.add_trace(go.Scatter(
                    x=xs, y=ys, mode="lines+markers",
                    line=dict(color=C["saffron"], width=2.5),
                    marker=dict(size=6, color=C["saffron"]),
                    customdata=labels,
                    hovertemplate="%{x}<br>%{customdata}<extra></extra>",
                ))
            else:
                fig_ai.add_trace(go.Bar(
                    x=xs, y=ys,
                    marker=dict(color=[C["saffron"] if v >= 0 else C["coral"] for v in ys]),
                    text=labels, textposition="outside", cliponaxis=False,
                    textfont=dict(color=C["text"], size=12),
                    customdata=labels,
                    hovertemplate="%{x}<br>%{customdata}<extra></extra>",
                ))
            tv, tt = nice_ticks(min(ys), max(ys))
            style_fig(fig_ai, 320)
            top = max(tv) + (max(tv) - min(tv)) * (0.1 if kind != "line" else 0.02)
            fig_ai.update_yaxes(
                tickvals=tv, ticktext=tt, gridcolor=C["line"], zeroline=False,
                showline=False, tickfont=dict(color=C["muted"]), range=[min(tv), top],
            )
            fig_ai.update_xaxes(showgrid=False, linecolor=C["line2"], tickfont=dict(color=C["muted"]))

            st.markdown(
                f'<p class="a-chart-title">{esc(result.get("title", ""))}</p>',
                unsafe_allow_html=True,
            )
            show_chart(fig_ai)

# =========================================================
# KPI BAND
# =========================================================

monthly = (
    d.assign(Month=d["Order_Date"].dt.to_period("M"))
    .groupby("Month")
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Sales", "size"))
    .reset_index()
)
monthly["Margin"] = monthly["Profit"] / monthly["Sales"].where(monthly["Sales"] != 0) * 100
monthly["Date"] = monthly["Month"].dt.to_timestamp()

# Compare the latest complete month with the one before it.
cmp_cur, cmp_prev, cmp_label = None, None, ""
if len(monthly) >= 2:
    last_period = monthly["Month"].iloc[-1]
    partial = d["Order_Date"].max().normalize() < last_period.end_time.normalize()
    if partial and len(monthly) >= 3:
        cmp_cur, cmp_prev = len(monthly) - 2, len(monthly) - 3
    else:
        cmp_cur, cmp_prev = len(monthly) - 1, len(monthly) - 2
    cmp_label = (
        f"{monthly['Date'].iloc[cmp_cur]:%b} vs {monthly['Date'].iloc[cmp_prev]:%b}"
    )


def delta_html(column, points=False):
    if cmp_cur is None:
        return '<div class="kpi-delta flat">Needs two months of data to compare</div>'
    cur = monthly[column].iloc[cmp_cur]
    prev = monthly[column].iloc[cmp_prev]
    if pd.isna(cur) or pd.isna(prev):
        return '<div class="kpi-delta flat">&nbsp;</div>'
    if points:
        change, text = cur - prev, f"{cur - prev:+.1f} pts"
    else:
        if prev == 0:
            return '<div class="kpi-delta flat">&nbsp;</div>'
        change = (cur - prev) / abs(prev) * 100
        text = f"{change:+.1f}%"
    tone = "up" if change > 0.05 else "down" if change < -0.05 else "flat"
    text = text.replace("-", "−")
    return f'<div class="kpi-delta {tone}">{text}<span>{cmp_label}</span></div>'


def spark_svg(values, color, uid, fill=0.28):
    vals = [v for v in values if pd.notna(v)]
    if len(vals) < 2:
        return '<svg class="kpi-spark" viewBox="0 0 120 38" aria-hidden="true"></svg>'
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pts = [
        (i / (len(vals) - 1) * 120, 34 - (v - lo) / span * 30)
        for i, v in enumerate(vals)
    ]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,38 {line} 120,38"
    return (
        '<svg class="kpi-spark" viewBox="0 0 120 38" preserveAspectRatio="none" aria-hidden="true">'
        f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{fill}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon points="{area}" fill="url(#g{uid})"/>'
        f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2" '
        'vector-effect="non-scaling-stroke" stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def kpi_cell(label, value, delta, spark):
    return (
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{delta}{spark}</div>'
    )


kpi_html = (
    '<div class="kpis">'
    + kpi_cell("Revenue", inr(total_sales), delta_html("Sales"),
               spark_svg(monthly["Sales"], C["saffron"], 1))
    + kpi_cell("Profit", inr(total_profit), delta_html("Profit"),
               spark_svg(monthly["Profit"], C["mint"], 2))
    + kpi_cell("Profit margin", f"{margin:.1f}%", delta_html("Margin", points=True),
               spark_svg(monthly["Margin"], C["muted"], 3, 0.10))
    + kpi_cell("Records", f"{orders:,}", delta_html("Orders"),
               spark_svg(monthly["Orders"], C["muted"], 4, 0.10))
    + "</div>"
)
st.markdown(kpi_html, unsafe_allow_html=True)

# =========================================================
# HIGHLIGHTS (calculated, not AI)
# =========================================================


def build_highlights():
    items = []

    losses = d[d["Profit"] < 0]
    if len(losses):
        items.append((
            "bad",
            f"{len(losses):,} records ({len(losses) / orders * 100:.1f}%) show negative profit, "
            f"costing {inr(abs(losses['Profit'].sum()))} in total.",
        ))
    else:
        items.append(("good", "No records show negative profit."))

    by_cat = d.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    by_cat = by_cat[by_cat["Sales"] > 0]
    by_cat["Margin"] = by_cat["Profit"] / by_cat["Sales"] * 100
    if len(by_cat) >= 2:
        low, high = by_cat["Margin"].idxmin(), by_cat["Margin"].idxmax()
        items.append((
            "bad" if by_cat.loc[low, "Margin"] < margin else "note",
            f"{low} has the thinnest margin at {by_cat.loc[low, 'Margin']:.1f}%, "
            f"against {margin:.1f}% overall.",
        ))
        items.append((
            "good",
            f"{high} earns the best margin at {by_cat.loc[high, 'Margin']:.1f}%.",
        ))

    by_region = d.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    if len(by_region) >= 2 and total_sales > 0:
        items.append((
            "note",
            f"{by_region.index[0]} brings in {by_region.iloc[0] / total_sales * 100:.0f}% "
            "of revenue, the most of any region.",
        ))

    if len(monthly) >= 2:
        best = monthly.loc[monthly["Sales"].idxmax()]
        items.append((
            "note",
            f"{best['Date']:%B %Y} was the strongest month, with {inr(best['Sales'])} in revenue.",
        ))

    return items[:5]


# =========================================================
# TABS
# =========================================================

tab_overview, tab_breakdown, tab_data = st.tabs(["Overview", "Breakdown", "Data"])


def grouped_bars(group_col):
    g = (
        d.groupby(group_col)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=True)
        .reset_index()
    )
    names = g[group_col].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=names, x=g["Profit"], name="Profit", orientation="h",
        marker=dict(color=[C["mint"] if v >= 0 else C["coral"] for v in g["Profit"]]),
        text=[inr(v) for v in g["Profit"]], textposition="outside", cliponaxis=False,
        textfont=dict(color=C["muted"], size=12),
        customdata=[inr(v) for v in g["Profit"]],
        hovertemplate="%{y}<br>Profit %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=names, x=g["Sales"], name="Revenue", orientation="h",
        marker=dict(color=C["saffron"]),
        text=[inr(v) for v in g["Sales"]], textposition="outside", cliponaxis=False,
        textfont=dict(color=C["text"], size=12),
        customdata=[inr(v) for v in g["Sales"]],
        hovertemplate="%{y}<br>Revenue %{customdata}<extra></extra>",
    ))
    tv, tt = nice_ticks(min(g["Profit"].min(), 0), g["Sales"].max())
    style_fig(fig, 110 + 74 * len(names), legend=True)
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08, margin=dict(l=4, r=24, t=8, b=4), legend=dict(traceorder="reversed"))
    fig.update_xaxes(
        tickvals=tv, ticktext=tt, gridcolor=C["line"], zeroline=False,
        tickfont=dict(color=C["muted"]), range=[min(tv), max(max(tv), g["Sales"].max() * 1.0) * 1.22],
    )
    fig.update_yaxes(showgrid=False, tickfont=dict(color=C["text"], size=13), automargin=True)
    return fig


with tab_overview:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    trend_col, notes_col = st.columns([2.2, 1], gap="large")

    with trend_col:
        section("Revenue and profit by month", "Monthly totals for the filters you chose")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly["Date"], y=monthly["Sales"], name="Revenue",
            mode="lines+markers" if len(monthly) < 3 else "lines",
            line=dict(color=C["saffron"], width=2.5, shape="spline", smoothing=0.5),
            fill="tozeroy", fillcolor="rgba(244,183,64,0.10)",
            customdata=[inr(v) for v in monthly["Sales"]],
            hovertemplate="Revenue %{customdata}<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly["Date"], y=monthly["Profit"], name="Profit",
            mode="lines+markers" if len(monthly) < 3 else "lines",
            line=dict(color=C["mint"], width=2.5, shape="spline", smoothing=0.5),
            customdata=[inr(v) for v in monthly["Profit"]],
            hovertemplate="Profit %{customdata}<extra></extra>",
        ))
        if len(monthly) >= 3:
            peak = monthly.loc[monthly["Sales"].idxmax()]
            fig_trend.add_trace(go.Scatter(
                x=[peak["Date"]], y=[peak["Sales"]], mode="markers+text",
                marker=dict(size=9, color=C["saffron"], line=dict(color=C["bg"], width=2)),
                text=[f"Peak {inr(peak['Sales'])}"], textposition="top center",
                textfont=dict(color=C["text"], size=12),
                hoverinfo="skip", showlegend=False, cliponaxis=False,
            ))
        tv, tt = nice_ticks(
            min(monthly["Profit"].min(), 0), monthly["Sales"].max() * 1.12
        )
        style_fig(fig_trend, 380, legend=True)
        fig_trend.update_layout(hovermode="x unified")
        fig_trend.update_yaxes(
            tickvals=tv, ticktext=tt, gridcolor=C["line"], zeroline=False,
            tickfont=dict(color=C["muted"]), range=[min(tv), max(tv)],
        )
        fig_trend.update_xaxes(
            showgrid=False, linecolor=C["line2"], tickformat="%b %y",
            hoverformat="%B %Y", tickfont=dict(color=C["muted"]),
        )
        show_chart(fig_trend)

    with notes_col:
        section("What stands out", "Calculated directly from your data")
        rows = "".join(
            f'<li><span class="dot {tone}"></span><span>{esc(text)}</span></li>'
            for tone, text in build_highlights()
        )
        st.markdown(f'<ul class="highlights">{rows}</ul>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
    cat_col, reg_col = st.columns(2, gap="large")
    with cat_col:
        section("Category performance", "Revenue and profit")
        show_chart(grouped_bars("Category"))
    with reg_col:
        section("Region performance", "Revenue and profit")
        show_chart(grouped_bars("Region"))


def leaderboard(column, limit=8):
    g = (
        d.groupby(column)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
        .head(limit)
        .reset_index()
    )
    top = g["Sales"].max() or 1
    rows = []
    for _, r in g.iterrows():
        m = r["Profit"] / r["Sales"] * 100 if r["Sales"] else 0
        tone = "up" if m >= 0 else "down"
        m_text = f"{m:+.1f}%".replace("-", "−")
        rows.append(
            '<div class="lb-row">'
            f'<div class="lb-name" title="{esc(r[column])}">{esc(r[column])}</div>'
            f'<div class="lb-bar"><span style="width:{max(r["Sales"], 0) / top * 100:.1f}%"></span></div>'
            f'<div class="lb-val">{inr(r["Sales"])}</div>'
            f'<div class="lb-m {tone}">{m_text}</div></div>'
        )
    return f'<div class="lb">{"".join(rows)}</div>'


with tab_breakdown:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    cells = (
        d.groupby(["Region", "Category"])
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )
    cells["Margin"] = cells["Profit"] / cells["Sales"].where(cells["Sales"] != 0) * 100
    grid = cells.pivot(index="Region", columns="Category", values="Margin")
    region_order = (
        d.groupby("Region")["Sales"].sum().sort_values(ascending=False).index.tolist()
    )
    grid = grid.reindex(region_order)

    if grid.shape[0] * grid.shape[1] >= 2:
        section(
            "Profit margin by region and category",
            "Greener cells beat your overall margin. Red cells fall below it.",
        )
        z = grid.values
        text = [[f"{v:.1f}%" if pd.notna(v) else "" for v in row] for row in z]
        fig_heat = go.Figure(go.Heatmap(
            z=z, x=grid.columns.tolist(), y=grid.index.tolist(),
            text=text, texttemplate="%{text}",
            textfont=dict(color="#FFFFFF", size=14),
            zmid=margin, xgap=3, ygap=3, showscale=False,
            colorscale=[[0, "#C9503F"], [0.5, "#1D3A3E"], [1, "#2FA67F"]],
            hovertemplate="%{y}, %{x}<br>Margin %{z:.1f}%<extra></extra>",
        ))
        style_fig(fig_heat, 90 + 62 * grid.shape[0])
        fig_heat.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=C["text"], size=13))
        fig_heat.update_xaxes(showgrid=False, side="top", tickfont=dict(color=C["text"], size=13))
        show_chart(fig_heat)

    if DIMENSIONS:
        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
        lb_cols = st.columns(min(len(DIMENSIONS), 2), gap="large")
        for col, dim in zip(lb_cols, DIMENSIONS[:2]):
            with col:
                plural = {"Product": "products", "Salesperson": "salespeople", "Customer_Type": "customer types"}
                label = plural.get(dim, dim.replace("_", " ").lower())
                section(
                    f"Top {label} by revenue",
                    "Bar shows revenue. The figure on the right is profit margin.",
                )
                st.markdown(leaderboard(dim), unsafe_allow_html=True)

with tab_data:
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    shown = d.sort_values("Order_Date", ascending=False).copy()
    shown.columns = [c.replace("_", " ") for c in shown.columns]

    top_l, top_r = st.columns([4, 1], vertical_alignment="center")
    with top_l:
        section("Records", f"{len(shown):,} records match the current filters")
    with top_r:
        st.download_button(
            "Download filtered CSV",
            data=shown.to_csv(index=False).encode("utf-8"),
            file_name="salesmind_analysis.csv",
            mime="text/csv",
            **stretch(st.download_button),
        )

    st.dataframe(
        shown,
        hide_index=True,
        column_config={
            "Order Date": st.column_config.DateColumn("Order Date", format="DD MMM YYYY"),
            "Sales": st.column_config.NumberColumn("Sales", format="₹%.2f"),
            "Profit": st.column_config.NumberColumn("Profit", format="₹%.2f"),
            **(
                {"Cost": st.column_config.NumberColumn("Cost", format="₹%.2f")}
                if "Cost" in shown.columns else {}
            ),
        },
        **stretch(st.dataframe),
    )

st.markdown(
    '<div class="sm-foot">Calculated metrics come from your mapped columns. Profit is only valid when a profit or cost column is supplied. '
    "AI explains results and recommendations; verify strategic decisions against your business context.</div>",
    unsafe_allow_html=True,
)
