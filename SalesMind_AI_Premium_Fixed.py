import os
import streamlit as st
import pandas as pd
import plotly.express as px
from ai_analyst import analyze_question

# =========================================================
# CHART SYSTEM — ANIMATED / DEPTH STYLING
# =========================================================

def polish_chart(fig, height=330, show_legend=False):
    """Apply the shared SalesMind visual system to Plotly charts."""
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=14, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        showlegend=show_legend,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#0b1020",
            bordercolor="rgba(129,140,248,0.35)",
            font=dict(color="#f8fafc", family="Inter, sans-serif")
        ),
        transition=dict(duration=650, easing="cubic-in-out")
    )
    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color="#64748b")
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.055)",
        zeroline=False,
        tickfont=dict(color="#64748b")
    )
    return fig




# =========================================================
# PAGE CONFIG
# =========================================================
# Nebius × NVIDIA Global AI Hackathon build: keep the core demo
# focused on AI-powered sales analytics, Nemotron reasoning,
# and a polished interactive experience.

st.set_page_config(
    page_title="SalesMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

# =========================================================
# CUSTOM CSS — PREMIUM SALES INTELLIGENCE UI
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* =========================================================
   GLOBAL
   ========================================================= */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(99,102,241,0.10),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(139,92,246,0.08),
            transparent 28%
        ),
        #070a11;

    color: #f8fafc;
}

/* Remove Streamlit chrome */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

/* =========================================================
   MAIN CONTENT
   ========================================================= */

.block-container {
    max-width: 1480px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* =========================================================
   TYPOGRAPHY
   ========================================================= */

h1 {
    font-weight: 800 !important;
    letter-spacing: -1.8px;
    color: #f8fafc !important;
}

h2 {
    font-weight: 750 !important;
    letter-spacing: -0.8px;
    color: #f8fafc !important;
}

h3 {
    font-weight: 700 !important;
    color: #f8fafc !important;
}

p {
    color: #94a3b8;
}

/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(10,13,22,0.98),
            rgba(7,10,17,0.98)
        );

    border-right: 1px solid rgba(255,255,255,0.06);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Sidebar text */

[data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
}

/* Sidebar select boxes */

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
}

/* =========================================================
   SECTION LABELS
   ========================================================= */

.section-label {
    color: #818cf8;

    text-transform: uppercase;

    letter-spacing: 1.8px;

    font-size: 10px;

    font-weight: 800;

    margin-bottom: 8px;
}

/* =========================================================
   KPI CARDS
   ========================================================= */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.065),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.075);

    border-radius: 18px;

    padding: 20px 22px;

    min-height: 112px;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.22),
        inset 0 1px 0 rgba(255,255,255,0.025);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}

[data-testid="stMetric"]:hover {

    transform: translateY(-3px);

    border-color:
        rgba(129,140,248,0.35);

    box-shadow:
        0 18px 45px rgba(0,0,0,0.32),
        0 0 25px rgba(99,102,241,0.06);
}

[data-testid="stMetricLabel"] {

    color: #64748b !important;

    font-size: 0.72rem !important;

    font-weight: 700 !important;

    letter-spacing: 0.7px;

    text-transform: uppercase;
}

[data-testid="stMetricValue"] {

    color: #f8fafc !important;

    font-size: 1.65rem !important;

    font-weight: 750 !important;

    letter-spacing: -0.8px;
}

/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {

    background:
        rgba(255,255,255,0.035);

    color: #e2e8f0;

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 10px;

    font-weight: 600;

    transition: all 0.2s ease;
}

.stButton > button:hover {

    background:
        rgba(99,102,241,0.12);

    border-color:
        rgba(129,140,248,0.45);

    color: #ffffff;

    transform: translateY(-1px);
}

/* =========================================================
   INPUTS
   ========================================================= */

[data-testid="stTextInput"] input {

    background:
        rgba(255,255,255,0.035) !important;

    color: #f8fafc !important;

    border: 1px solid rgba(255,255,255,0.08) !important;

    border-radius: 12px !important;

    padding: 14px 16px !important;

    font-size: 14px !important;

    transition: all 0.2s ease;
}

[data-testid="stTextInput"] input:focus {

    border-color:
        rgba(129,140,248,0.55) !important;

    box-shadow:
        0 0 0 3px rgba(99,102,241,0.08) !important;
}

[data-testid="stTextInput"] input::placeholder {

    color: #64748b !important;
}

/* =========================================================
   SELECT BOXES
   ========================================================= */

[data-baseweb="select"] > div {

    background:
        rgba(255,255,255,0.035);

    border:
        1px solid rgba(255,255,255,0.08);

    border-radius: 10px;
}

/* =========================================================
   AI INSIGHT CARD
   ========================================================= */

.ai-card {

    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(139,92,246,0.16),
            transparent 40%
        ),
        linear-gradient(
            145deg,
            rgba(99,102,241,0.13),
            rgba(255,255,255,0.025)
        );

    border:
        1px solid rgba(129,140,248,0.20);

    border-radius: 20px;

    padding: 25px;

    min-height: 270px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.25),
        inset 0 1px 0 rgba(255,255,255,0.035);

    position: relative;

    overflow: hidden;
}

.ai-card::before {

    content: "";

    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(129,140,248,0.7),
            transparent
        );
}

.ai-badge {

    display: inline-flex;

    align-items: center;

    padding: 6px 10px;

    border-radius: 999px;

    background:
        rgba(129,140,248,0.10);

    border:
        1px solid rgba(129,140,248,0.18);

    color: #a5b4fc;

    font-size: 10px;

    font-weight: 800;

    letter-spacing: 0.8px;
}

.ai-title {

    font-size: 20px;

    font-weight: 750;

    letter-spacing: -0.5px;

    margin-top: 16px;

    color: #f8fafc;
}

.ai-text {

    color: #a8b3c5;

    line-height: 1.7;

    margin-top: 12px;

    font-size: 13px;
}

/* =========================================================
   ASK AI CARD
   ========================================================= */

.ask-card {

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.045),
            rgba(255,255,255,0.018)
        );

    border:
        1px solid rgba(255,255,255,0.075);

    border-radius: 20px;

    padding: 25px;

    margin-top: 15px;

    box-shadow:
        0 15px 45px rgba(0,0,0,0.20);
}

.ask-title {

    font-size: 21px;

    font-weight: 750;

    letter-spacing: -0.5px;

    color: #f8fafc;

    margin-bottom: 5px;
}

.ask-subtitle {

    color: #64748b;

    font-size: 13px;

    margin-bottom: 18px;
}

/* =========================================================
   EXPANDERS
   ========================================================= */

[data-testid="stExpander"] {

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 14px;

    overflow: hidden;
}

[data-testid="stExpander"] summary {

    color: #cbd5e1 !important;

    font-weight: 600;
}

/* =========================================================
   ALERTS
   ========================================================= */

[data-testid="stAlert"] {

    border-radius: 14px;

    border: 1px solid rgba(255,255,255,0.07);
}

/* =========================================================
   DATAFRAME
   ========================================================= */

[data-testid="stDataFrame"] {

    border-radius: 14px;

    overflow: hidden;

    border: 1px solid rgba(255,255,255,0.07);
}

/* =========================================================
   DIVIDERS
   ========================================================= */

hr {

    border: none !important;

    border-top:
        1px solid rgba(255,255,255,0.06) !important;

    margin-top: 1.5rem;

    margin-bottom: 1.5rem;
}

/* =========================================================
   PLOTLY CONTAINERS
   ========================================================= */

[data-testid="stPlotlyChart"] {

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.028),
            rgba(255,255,255,0.012)
        );

    border:
        1px solid rgba(255,255,255,0.055);

    border-radius: 18px;

    padding: 8px;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.16);
}

/* =========================================================
   SCROLLBAR
   ========================================================= */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #070a11;
}

::-webkit-scrollbar-thumb {

    background:
        rgba(129,140,248,0.25);

    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {

    background:
        rgba(129,140,248,0.45);
}

/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 900px) {

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;
    }

}


/* =========================================================
   PREMIUM MOTION + DEPTH
   ========================================================= */

.stApp::before {
    content: "";
    position: fixed;
    inset: -20%;
    pointer-events: none;
    background:
        radial-gradient(circle at 18% 18%, rgba(99,102,241,0.10), transparent 24%),
        radial-gradient(circle at 82% 22%, rgba(56,189,248,0.07), transparent 22%),
        radial-gradient(circle at 55% 92%, rgba(139,92,246,0.06), transparent 25%);
    filter: blur(8px);
    animation: ambientFloat 14s ease-in-out infinite alternate;
    z-index: 0;
}

.block-container {
    position: relative;
    z-index: 1;
}

@keyframes ambientFloat {
    from { transform: translate3d(-1%, -1%, 0) scale(1); }
    to   { transform: translate3d(1%, 1%, 0) scale(1.035); }
}

[data-testid="stPlotlyChart"] {
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 18px;
    padding: 6px;
    background: linear-gradient(145deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012));
    box-shadow: 0 18px 45px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.025);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

[data-testid="stPlotlyChart"]:hover {
    transform: translateY(-2px);
    border-color: rgba(129,140,248,0.20);
    box-shadow: 0 22px 55px rgba(0,0,0,0.25), 0 0 30px rgba(99,102,241,0.055);
}

/* AI response emphasis */
.ai-live-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border-radius: 999px;
    border: 1px solid rgba(74,222,128,0.18);
    background: rgba(74,222,128,0.06);
    color: #86efac;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.7px;
}

.ai-live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 12px rgba(74,222,128,0.75);
    animation: pulseDot 1.8s ease-in-out infinite;
}

@keyframes pulseDot {
    0%, 100% { opacity: 0.55; transform: scale(0.85); }
    50% { opacity: 1; transform: scale(1.15); }
}

/* Responsive spacing */
@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# UPLOAD + DATA PREPARATION
# =========================================================

from io import BytesIO
import re

def read_uploaded_file(uploaded):
    """Read an uploaded Excel or CSV file without assuming its column names."""
    raw = uploaded.getvalue()
    filename = uploaded.name.lower()

    if filename.endswith(".csv"):
        try:
            return pd.read_csv(BytesIO(raw))
        except UnicodeDecodeError:
            return pd.read_csv(BytesIO(raw), encoding="latin-1")
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(raw))
    raise ValueError("Please upload an Excel (.xlsx, .xls) or CSV (.csv) file.")


def clean_header(value):
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


COLUMN_ALIASES = {
    "Sales": [
        "sales", "sale", "revenue", "total_revenue", "total_sales",
        "net_sales", "gross_sales", "sales_amount", "revenue_amount",
        "total_amount", "amount", "order_value", "total", "bill_amount",
        "total_bill", "net_amount", "selling_price"
    ],
    "Profit": [
        "profit", "net_profit", "gross_profit", "profit_amount",
        "earnings", "net_earnings"
    ],
    "Cost": [
        "cost", "total_cost", "cost_price", "expenses", "expense",
        "total_expenses", "purchase_cost"
    ],
    "Order_Date": [
        "order_date", "date", "transaction_date", "purchase_date",
        "sale_date", "invoice_date", "bill_date", "created_at",
        "datetime", "timestamp"
    ],
    "Category": [
        "category", "product_category", "item_category", "segment",
        "department", "type", "food_category", "menu_category"
    ],
    "Region": [
        "region", "city", "state", "location", "area", "branch",
        "store_location", "territory"
    ],
    "Product": [
        "product", "product_name", "item", "item_name", "dish",
        "dish_name", "menu_item", "service", "service_name",
        "sku", "product_id"
    ],
    "Quantity": [
        "quantity", "qty", "units", "units_sold", "items_sold",
        "order_quantity", "count"
    ],
    "Order_ID": [
        "order_id", "invoice_id", "transaction_id", "bill_no",
        "bill_number", "receipt_id", "booking_id"
    ],
    "Customer": [
        "customer", "customer_name", "customer_id", "client",
        "client_name", "buyer"
    ],
}


def map_business_columns(source):
    """Add stable internal column names while retaining the original columns."""
    frame = source.copy()
    original_names = list(frame.columns)
    cleaned_to_original = {}
    for col in original_names:
        cleaned_to_original.setdefault(clean_header(col), col)

    mapped = {}
    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in cleaned_to_original:
                mapped[standard_name] = cleaned_to_original[alias]
                break

    # If no known revenue label exists, use a numeric column only when its
    # name strongly suggests a monetary amount. Do not guess from arbitrary IDs.
    if "Sales" not in mapped:
        monetary_words = ("revenue", "sales", "amount", "total", "price", "bill", "value")
        candidates = [
            col for col in original_names
            if any(word in clean_header(col) for word in monetary_words)
            and pd.api.types.is_numeric_dtype(frame[col])
        ]
        if candidates:
            mapped["Sales"] = candidates[0]

    for standard_name, original_name in mapped.items():
        if standard_name not in frame.columns:
            frame[standard_name] = frame[original_name]

    return frame, mapped


def detect_business_type(columns):
    names = " ".join(clean_header(c) for c in columns)
    restaurant_terms = (
        "dish", "menu", "food", "table", "waiter", "restaurant",
        "cuisine", "recipe", "ingredient", "order_type"
    )
    retail_terms = ("sku", "inventory", "stock", "product", "supplier")
    if any(term in names for term in restaurant_terms):
        return "Restaurant"
    if any(term in names for term in retail_terms):
        return "Small / Retail Business"
    if len(columns) >= 12:
        return "Large Business"
    return "Small Business"


def prepare_dataframe(source):
    frame, mapping = map_business_columns(source)
    if frame.empty:
        raise ValueError("The uploaded file contains no data rows.")

    # Convert mapped metrics to numbers, tolerating currency symbols and commas.
    for col in ("Sales", "Profit", "Cost", "Quantity"):
        if col in frame.columns:
            values = frame[col].astype(str).str.replace(",", "", regex=False)
            values = values.str.replace(r"[₹$€£]", "", regex=True).str.strip()
            frame[col] = pd.to_numeric(values, errors="coerce")

    if "Order_Date" in frame.columns:
        frame["Order_Date"] = pd.to_datetime(frame["Order_Date"], errors="coerce", dayfirst=True)

    # Remove completely empty rows; retain rows with missing optional metrics.
    frame = frame.dropna(how="all").copy()
    if frame.empty:
        raise ValueError("No usable records were found in this file.")

    return frame, mapping


# =========================================================
# SIDEBAR — WORKSPACE + BUSINESS PROFILE
# =========================================================

with st.sidebar:
    st.markdown("## ◈ SalesMind")
    st.caption("AI-Powered Business Intelligence")
    st.divider()

    st.markdown(
        '<div class="section-label">Workspace</div>',
        unsafe_allow_html=True
    )
    st.markdown("📊 **Overview**")
    st.markdown("📈 Analytics")
    st.markdown("🤖 AI Analyst")
    st.markdown("🗃️ Data Explorer")
    st.divider()

    st.markdown(
        '<div class="section-label">Your business</div>',
        unsafe_allow_html=True
    )
    business_profile = st.selectbox(
        "Business type",
        ["Auto-detect", "Restaurant", "Small Business", "Large Business"],
        help="Choose a profile or let SalesMind infer it from your spreadsheet columns."
    )

    uploaded_file = st.file_uploader(
        "Upload business data",
        type=["csv", "xlsx", "xls"],
        help="Upload a sales, orders, restaurant, retail, or business spreadsheet."
    )

    st.divider()
    st.caption("Supported formats: CSV, XLSX, XLS")


# =========================================================
# EMPTY STATE
# =========================================================

if uploaded_file is None:
    st.markdown(
        '<div class="section-label">SALES INTELLIGENCE</div>',
        unsafe_allow_html=True
    )
    st.title("Your business, understood.")
    st.markdown(
        "### Upload a spreadsheet to turn everyday business data into clear decisions."
    )
    st.markdown("")
    intro1, intro2, intro3 = st.columns(3)
    with intro1:
        st.markdown("#### 📂 Any spreadsheet")
        st.caption("Start with an Excel or CSV export. No fixed template required.")
    with intro2:
        st.markdown("#### 🧠 Business-aware")
        st.caption("Identify useful sales, product, date, customer and cost fields.")
    with intro3:
        st.markdown("#### ✦ AI advisor")
        st.caption("Explore performance, ask questions and get practical next steps.")
    st.info("Use the upload control in the sidebar to get started.")
    st.stop()


# =========================================================
# LOAD + VALIDATE UPLOADED DATA
# =========================================================

try:
    source_df = read_uploaded_file(uploaded_file)
    df, mapped_columns = prepare_dataframe(source_df)
except Exception as exc:
    st.error(f"Could not prepare this file: {exc}")
    st.stop()

detected_profile = detect_business_type(source_df.columns)
active_profile = detected_profile if business_profile == "Auto-detect" else business_profile

# Ensure the AI analyst receives the stable canonical field names when available.
has_revenue = "Sales" in df.columns and df["Sales"].notna().any()
has_profit = "Profit" in df.columns and df["Profit"].notna().any()
has_cost = "Cost" in df.columns and df["Cost"].notna().any()
has_dates = "Order_Date" in df.columns and df["Order_Date"].notna().any()

if has_revenue:
    df["Sales"] = df["Sales"].fillna(0)
if has_profit:
    df["Profit"] = df["Profit"].fillna(0)
if has_cost:
    df["Cost"] = df["Cost"].fillna(0)

# Find the best descriptive dimension for product/category analysis.
dimension_candidates = ["Product", "Category", "Customer", "Region"]
available_dimensions = [
    col for col in dimension_candidates
    if col in df.columns and df[col].notna().any()
]
primary_dimension = (
    "Product" if active_profile == "Restaurant" and "Product" in available_dimensions
    else "Category" if "Category" in available_dimensions
    else available_dimensions[0] if available_dimensions
    else None
)

# Sidebar filters are shown only when their columns exist.
with st.sidebar:
    st.markdown(
        '<div class="section-label">Filters</div>',
        unsafe_allow_html=True
    )
    filtered_df = df.copy()

    if "Region" in df.columns and df["Region"].notna().any():
        region_values = ["All"] + sorted(df["Region"].dropna().astype(str).unique().tolist())
        selected_region = st.selectbox("Location / region", region_values)
        if selected_region != "All":
            filtered_df = filtered_df[filtered_df["Region"].astype(str) == selected_region]

    if "Category" in df.columns and df["Category"].notna().any():
        category_values = ["All"] + sorted(df["Category"].dropna().astype(str).unique().tolist())
        selected_category = st.selectbox("Category", category_values)
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["Category"].astype(str) == selected_category]

    st.divider()
    st.caption("● Data source connected")
    st.caption(f"{len(df):,} records loaded")
    st.caption(f"Detected: {detected_profile}")


# =========================================================
# HEADER
# =========================================================

header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.markdown(
        '<div class="section-label">BUSINESS INTELLIGENCE</div>',
        unsafe_allow_html=True
    )
    st.title("Good evening 👋")
    st.markdown(f"### Your {active_profile.lower()} performance, at a glance.")
with header_col2:
    st.markdown(
        """
        <div style="text-align:right;padding-top:25px;color:#86efac;font-size:13px;font-weight:600;">
        ● DATA CONNECTED
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(
    f"File: {uploaded_file.name}  ·  {len(df):,} rows  ·  {len(source_df.columns):,} original columns"
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = float(filtered_df["Sales"].fillna(0).sum()) if has_revenue else None
total_profit = float(filtered_df["Profit"].fillna(0).sum()) if has_profit else None
total_cost = float(filtered_df["Cost"].fillna(0).sum()) if has_cost else None
record_count = len(filtered_df)

order_count = (
    filtered_df["Order_ID"].nunique()
    if "Order_ID" in filtered_df.columns
    else record_count
)
average_order = total_sales / order_count if total_sales is not None and order_count else None
profit_margin = (
    total_profit / total_sales * 100
    if total_profit is not None and total_sales not in (None, 0)
    else None
)

kpi_items = []
if total_sales is not None:
    kpi_items.append(("TOTAL REVENUE", f"₹{total_sales:,.0f}"))
if total_profit is not None:
    kpi_items.append(("TOTAL PROFIT", f"₹{total_profit:,.0f}"))
if profit_margin is not None:
    kpi_items.append(("PROFIT MARGIN", f"{profit_margin:.1f}%"))
if total_cost is not None and total_profit is None:
    kpi_items.append(("TOTAL COST", f"₹{total_cost:,.0f}"))
if average_order is not None:
    kpi_items.append(("AVERAGE ORDER", f"₹{average_order:,.0f}"))
kpi_items.append(("RECORDS", f"{record_count:,}"))

kpi_cols = st.columns(min(4, len(kpi_items)))
for index, (label, value) in enumerate(kpi_items[:4]):
    with kpi_cols[index]:
        st.metric(label, value)

if not has_revenue:
    st.warning(
        "I couldn't confidently identify a revenue or sales column. "
        "Your data is loaded, but revenue-based KPIs and charts are unavailable. "
        "Check that your spreadsheet has a column such as Revenue, Sales, Amount or Total."
    )


# =========================================================
# PERFORMANCE + PROACTIVE BUSINESS REVIEW
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)
chart_col, ai_col = st.columns([2.2, 1])

with chart_col:
    st.markdown('<div class="section-label">PERFORMANCE</div>', unsafe_allow_html=True)
    st.subheader("Revenue trend")

    if has_revenue and has_dates:
        dated = filtered_df.dropna(subset=["Order_Date"]).copy()
        if not dated.empty:
            monthly_sales = (
                dated.groupby(dated["Order_Date"].dt.to_period("M"))["Sales"]
                .sum().reset_index()
            )
            monthly_sales["Order_Date"] = monthly_sales["Order_Date"].astype(str)
            fig = px.area(monthly_sales, x="Order_Date", y="Sales", markers=True)
            fig.update_traces(
                line=dict(width=3, color="#818cf8"),
                fillcolor="rgba(129,140,248,0.16)",
                marker=dict(size=7, color="#a5b4fc", line=dict(width=2, color="#0b1020")),
                hovertemplate="%{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>"
            )
            polish_chart(fig, height=345)
            st.plotly_chart(
                fig, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False},
                key="salesmind_revenue_trend"
            )
        else:
            st.info("A date column was detected, but it contains no usable dates.")
    elif has_revenue:
        st.info("Revenue is available. Add a date column (for example Order Date or Transaction Date) to see a trend.")
    else:
        st.info("A revenue trend will appear when Sales, Revenue, Amount or a similar column is available.")

with ai_col:
    with st.container(border=True):
        st.caption("✦ AI BUSINESS ADVISOR")
        st.markdown(
            '<span class="ai-live-badge"><span class="ai-live-dot"></span>NVIDIA NEMOTRON • OPTIONAL</span>',
            unsafe_allow_html=True
        )
        st.markdown("### Business intelligence")
        st.write(
            f"SalesMind has loaded your {active_profile.lower()} dataset and is using "
            "locally calculated metrics as the evidence base for its analysis."
        )
        st.divider()
        if st.button("Generate business review", use_container_width=True):
            with st.spinner("Reviewing your business data..."):
                try:
                    review = analyze_question(
                        filtered_df,
                        "Give me an executive summary of this business data, its strongest observed patterns, risks, and three practical actions to improve performance."
                    )
                    st.session_state["salesmind_business_review"] = review
                except Exception as exc:
                    st.session_state["salesmind_business_review"] = {
                        "answer": "The business review could not be generated.",
                        "evidence": [str(exc)[:300]]
                    }

        if "salesmind_business_review" in st.session_state:
            review = st.session_state["salesmind_business_review"]
            st.success(review.get("answer", "No review was returned."))
        if review.get("ai_error"):
            st.warning("AI provider error:")
            st.code(review["ai_error"])
        if review.get("evidence"):
            with st.expander("Review evidence"):
                for evidence_item in review["evidence"]:
                    st.write(f"• {evidence_item}")
        else:
            st.caption("Generate a review to receive an evidence-based summary and practical next steps.")


# =========================================================
# PRODUCT / CATEGORY / LOCATION ANALYTICS
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-label">PRODUCT MIX</div>', unsafe_allow_html=True)
    st.subheader("Performance by product or category")
    if has_revenue and primary_dimension:
        grouped = (
            filtered_df.groupby(primary_dimension, dropna=False)["Sales"]
            .sum().reset_index().sort_values("Sales", ascending=False).head(12)
        )
        grouped[primary_dimension] = grouped[primary_dimension].fillna("Unknown").astype(str)
        fig_group = px.bar(
            grouped, x=primary_dimension, y="Sales",
            color="Sales",
            color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
            text_auto=".2s"
        )
        fig_group.update_traces(
            marker_line_width=0, opacity=0.92,
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
        )
        polish_chart(fig_group, height=315)
        fig_group.update_coloraxes(showscale=False)
        st.plotly_chart(
            fig_group, use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
            key="salesmind_product_mix"
        )
    elif primary_dimension:
        counts = filtered_df[primary_dimension].fillna("Unknown").astype(str).value_counts().head(12).reset_index()
        counts.columns = [primary_dimension, "Records"]
        fig_count = px.bar(counts, x=primary_dimension, y="Records", text_auto=True)
        polish_chart(fig_count, height=315)
        st.plotly_chart(
            fig_count, use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
            key="salesmind_dimension_counts"
        )
    else:
        st.info("Add a product, item, category, customer or similar column to see a breakdown.")

with right:
    st.markdown('<div class="section-label">BUSINESS BREAKDOWN</div>', unsafe_allow_html=True)
    if active_profile == "Restaurant":
        st.subheader("Popular menu items")
        item_col = "Product" if "Product" in filtered_df.columns else primary_dimension
        if item_col:
            if "Quantity" in filtered_df.columns and filtered_df["Quantity"].notna().any():
                item_data = (
                    filtered_df.groupby(item_col, dropna=False)["Quantity"]
                    .sum().sort_values(ascending=False).head(10).reset_index()
                )
                y_label = "Quantity"
            elif has_revenue:
                item_data = (
                    filtered_df.groupby(item_col, dropna=False)["Sales"]
                    .sum().sort_values(ascending=False).head(10).reset_index()
                )
                y_label = "Sales"
            else:
                item_data = filtered_df[item_col].fillna("Unknown").astype(str).value_counts().head(10).reset_index()
                item_data.columns = [item_col, "Orders"]
                y_label = "Orders"
            item_data[item_col] = item_data[item_col].fillna("Unknown").astype(str)
            fig_items = px.bar(item_data, x=item_col, y=y_label, text_auto=".2s")
            polish_chart(fig_items, height=315)
            st.plotly_chart(
                fig_items, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False},
                key="salesmind_restaurant_items"
            )
        else:
            st.info("Add an item, dish or product column to identify popular menu items.")
    elif "Region" in filtered_df.columns and has_revenue:
        st.subheader("Revenue by location")
        region_data = (
            filtered_df.groupby("Region", dropna=False)["Sales"]
            .sum().sort_values(ascending=False).head(10).reset_index()
        )
        region_data["Region"] = region_data["Region"].fillna("Unknown").astype(str)
        fig_region = px.bar(
            region_data, x="Region", y="Sales", color="Sales",
            color_continuous_scale=["#164e63", "#0891b2", "#67e8f9"],
            text_auto=".2s"
        )
        polish_chart(fig_region, height=315)
        fig_region.update_coloraxes(showscale=False)
        st.plotly_chart(
            fig_region, use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
            key="salesmind_location_breakdown"
        )
    elif "Customer" in filtered_df.columns:
        st.subheader("Customer activity")
        customer_counts = filtered_df["Customer"].fillna("Unknown").astype(str).value_counts().head(10).reset_index()
        customer_counts.columns = ["Customer", "Records"]
        fig_customer = px.bar(customer_counts, x="Customer", y="Records", text_auto=True)
        polish_chart(fig_customer, height=315)
        st.plotly_chart(
            fig_customer, use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False},
            key="salesmind_customer_activity"
        )
    else:
        st.subheader("Data overview")
        st.metric("Usable records", f"{len(filtered_df):,}")
        st.caption("A location, customer or product field will unlock a more detailed breakdown.")


# =========================================================
# ASK SALESMIND AI
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">ASK YOUR DATA</div>', unsafe_allow_html=True)
st.subheader("What would you like to understand?")
question = st.text_input(
    "Ask a question",
    placeholder='Try: "Which product has the highest revenue?" or "How can I improve my business?"',
    label_visibility="collapsed",
    key="salesmind_ai_question"
)

if question:
    with st.spinner("Analysing your business data..."):
        try:
            result = analyze_question(filtered_df, question)
        except Exception as exc:
            result = {
                "answer": "I couldn't complete that analysis. Check the dataset columns and try again.",
                "evidence": [str(exc)[:300]],
                "chart_data": None,
                "chart_type": None,
                "title": "Analysis unavailable"
            }

    st.markdown("### 🤖 SalesMind AI")
    st.success(result.get("answer", "No answer was returned."))

    if result.get("evidence"):
        with st.expander("🔎 Show supporting evidence", expanded=True):
            for item in result["evidence"]:
                st.markdown(f"• {item}")

    chart_data = result.get("chart_data")
    chart_type = result.get("chart_type")
    if isinstance(chart_data, pd.DataFrame) and not chart_data.empty:
        if chart_type == "line" and {"Order_Date", "Sales"}.issubset(chart_data.columns):
            fig_ai = px.line(
                chart_data, x="Order_Date", y="Sales",
                markers=True, title=result.get("title", "Analysis")
            )
        elif chart_type == "bar" and chart_data.shape[1] >= 2:
            fig_ai = px.bar(
                chart_data, x=chart_data.columns[0], y=chart_data.columns[1],
                title=result.get("title", "Analysis")
            )
        else:
            fig_ai = None
        if fig_ai is not None:
            polish_chart(fig_ai, height=350)
            st.plotly_chart(
                fig_ai, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False},
                key="salesmind_ai_chart"
            )


# =========================================================
# DATA EXPLORER + DATA QUALITY
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗃️ Explore uploaded data"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with st.expander("🧹 Data quality and detected columns"):
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    quality_col1.metric("Missing cells", f"{int(source_df.isna().sum().sum()):,}")
    quality_col2.metric("Duplicate rows", f"{int(source_df.duplicated().sum()):,}")
    quality_col3.metric("Columns detected", f"{len(source_df.columns):,}")
    st.write("**Detected field mapping**")
    if mapped_columns:
        st.json({key: str(value) for key, value in mapped_columns.items()})
    else:
        st.info("No standard business fields were confidently detected. The original data is still available below.")
    st.write("**Original column names**")
    st.write([str(column) for column in source_df.columns])


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="text-align:center;padding:30px 0 10px 0;color:#475569;font-size:12px;">
        SalesMind AI • Intelligent Business Analytics
    </div>
    """,
    unsafe_allow_html=True
)
