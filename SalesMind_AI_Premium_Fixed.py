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
# LOAD DATA
# =========================================================

FILE_PATH = "data/AI_Sales_Analytics_Sales_Data.xlsx"

try:

    df = pd.read_excel(FILE_PATH)

except FileNotFoundError:

    st.error(f"Excel file not found: {FILE_PATH}")
    st.stop()

except Exception as e:

    st.error(f"Could not read Excel file: {e}")
    st.stop()


# =========================================================
# NORMALIZE COLUMNS
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace(" ", "_")
)

required_columns = [
    "Order_Date",
    "Category",
    "Region",
    "Sales",
    "Profit"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:

    st.error("Some required columns are missing.")

    st.write("Missing:", missing)

    st.write("Available columns:", df.columns.tolist())

    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

df["Sales"] = pd.to_numeric(
    df["Sales"],
    errors="coerce"
).fillna(0)

df["Profit"] = pd.to_numeric(
    df["Profit"],
    errors="coerce"
).fillna(0)

df = df.dropna(subset=["Order_Date"])


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## ◈ SalesMind")

    st.caption("AI-Powered Sales Intelligence")

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
        '<div class="section-label">Filters</div>',
        unsafe_allow_html=True
    )

    regions = ["All"] + sorted(
        df["Region"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_region = st.selectbox(
        "Region",
        regions
    )

    categories = ["All"] + sorted(
        df["Category"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_category = st.selectbox(
        "Category",
        categories
    )

    st.divider()

    st.caption("● Data source connected")

    st.caption(
        f"{len(df):,} records loaded"
    )


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df.copy()

if selected_region != "All":

    filtered_df = filtered_df[
        filtered_df["Region"].astype(str)
        == selected_region
    ]

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Category"].astype(str)
        == selected_category
    ]


# =========================================================
# HEADER
# =========================================================

header_col1, header_col2 = st.columns(
    [5, 1]
)

with header_col1:

    st.markdown(
        '<div class="section-label">SALES INTELLIGENCE</div>',
        unsafe_allow_html=True
    )

    st.title("Good afternoon 👋")

    st.markdown(
        "### Here's what is happening with your sales."
    )

with header_col2:

    st.markdown(
        """
        <div style="
            text-align:right;
            padding-top:25px;
            color:#86efac;
            font-size:13px;
            font-weight:600;
        ">
        ● SYSTEM ONLINE
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Profit"].sum()

orders = len(filtered_df)

profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)

average_order = (
    total_sales / orders
    if orders != 0
    else 0
)


# =========================================================
# KPI CARDS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "TOTAL REVENUE",
        f"₹{total_sales:,.0f}"
    )

with c2:

    st.metric(
        "TOTAL PROFIT",
        f"₹{total_profit:,.0f}"
    )

with c3:

    st.metric(
        "PROFIT MARGIN",
        f"{profit_margin:.1f}%"
    )

with c4:

    st.metric(
        "TOTAL ORDERS",
        f"{orders:,}"
    )


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# MAIN ANALYTICS AREA
# =========================================================

chart_col, ai_col = st.columns(
    [2.2, 1]
)


# =========================================================
# SALES TREND
# =========================================================

with chart_col:

    st.markdown(
        '<div class="section-label">PERFORMANCE</div>',
        unsafe_allow_html=True
    )

    st.subheader("Revenue trend")

    monthly_sales = (
        filtered_df
        .groupby(
            filtered_df["Order_Date"]
            .dt.to_period("M")
        )["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales["Order_Date"] = (
        monthly_sales["Order_Date"]
        .astype(str)
    )

    if not monthly_sales.empty:

        fig = px.area(
            monthly_sales,
            x="Order_Date",
            y="Sales",
            markers=True
        )

        fig.update_traces(
            line=dict(width=3, color="#818cf8"),
            fillcolor="rgba(129,140,248,0.16)",
            marker=dict(size=7, color="#a5b4fc", line=dict(width=2, color="#0b1020")),
            hovertemplate="%{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>"
        )
        polish_chart(fig, height=345)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False}
        )


# =========================================================
# AI INSIGHT CARD
# =========================================================

with ai_col:

    with st.container(border=True):

        st.caption("✦ AI INSIGHT")

        st.markdown(
            '<span class="ai-live-badge"><span class="ai-live-dot"></span>NEMOTRON • ONLINE</span>',
            unsafe_allow_html=True
        )

        st.markdown("### Sales intelligence")

        st.write(
            "SalesMind combines deterministic sales calculations with "
            "NVIDIA Nemotron to turn your numbers into clear business insights."
        )

        st.divider()

        st.markdown("**Ask SalesMind**")

        st.caption(
            "Compare categories, regions and trends, investigate profit "
            "performance, and surface what is driving the numbers."
        )
# =========================================================
# CATEGORY + REGION
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)


with left:

    st.markdown(
        '<div class="section-label">PRODUCT MIX</div>',
        unsafe_allow_html=True
    )

    st.subheader("Sales by category")

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        color="Sales",
        color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
        text_auto=".2s"
    )

    fig_category.update_traces(
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>"
    )
    polish_chart(fig_category, height=315)
    fig_category.update_coloraxes(showscale=False)

    st.plotly_chart(
        fig_category,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False}
    )


with right:

    st.markdown(
        '<div class="section-label">GEOGRAPHY</div>',
        unsafe_allow_html=True
    )

    st.subheader("Sales by region")

    region_sales = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        color="Sales",
        color_continuous_scale=["#164e63", "#0891b2", "#67e8f9"],
        text_auto=".2s"
    )

    fig_region.update_traces(
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<extra></extra>"
    )
    polish_chart(fig_region, height=315)
    fig_region.update_coloraxes(showscale=False)

    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False}
    )


# =========================================================
# 3D SALES LANDSCAPE
# =========================================================

if not filtered_df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">3D OVERVIEW</div>', unsafe_allow_html=True)
    st.subheader("Sales landscape")
    st.caption("Interactive 3D view of sales across categories and regions.")

    landscape = (
        filtered_df
        .groupby(["Category", "Region"], as_index=False)["Sales"]
        .sum()
    )

    if not landscape.empty:
        fig_3d = px.scatter_3d(
            landscape,
            x="Category",
            y="Region",
            z="Sales",
            size="Sales",
            color="Category",
            hover_data={"Sales": ":,.0f"},
            opacity=0.88
        )
        fig_3d.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.25)")),
            hovertemplate=(
                "<b>Category:</b> %{x}<br>"
                "<b>Region:</b> %{y}<br>"
                "<b>Sales:</b> ₹%{z:,.0f}<extra></extra>"
            )
        )
        fig_3d.update_layout(
            height=430,
            margin=dict(l=0, r=0, t=8, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showbackground=False, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
                yaxis=dict(showbackground=False, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
                zaxis=dict(showbackground=False, gridcolor="rgba(255,255,255,0.06)", color="#94a3b8"),
                camera=dict(eye=dict(x=1.55, y=1.55, z=1.15))
            ),
            font=dict(family="Inter, sans-serif", color="#94a3b8"),
            legend=dict(font=dict(color="#cbd5e1"))
        )
        st.plotly_chart(
            fig_3d,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": True}
        )


# =========================================================
# ASK AI
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

question = st.text_input(
    "Ask a question",
    placeholder='Try: "Which category generates the most profit?"',
    label_visibility="collapsed",
    key="salesmind_ai_question"
)

if question:
    with st.spinner("Analyzing your sales data..."):

        result = analyze_question(
            filtered_df,
            question
        )

    # AI Answer
    st.markdown("### 🤖 SalesMind AI")

    st.success(result["answer"])

    # Evidence
    if result["evidence"]:

        with st.expander("🔎 Show me why", expanded=True):

            for item in result["evidence"]:
                st.markdown(f"• {item}")

    # Chart
    if result["chart_data"] is not None:

        chart_data = result["chart_data"]

        if result["chart_type"] == "bar":

            x_col = chart_data.columns[0]
            y_col = chart_data.columns[1]

            fig_ai = px.bar(
                chart_data,
                x=x_col,
                y=y_col,
                title=result["title"]
            )

        elif result["chart_type"] == "line":

            fig_ai = px.line(
                chart_data,
                x="Order_Date",
                y="Sales",
                markers=True,
                title=result["title"]
            )

        polish_chart(fig_ai, height=350)
        fig_ai.update_traces(
            marker_line_width=0,
            opacity=0.92
        )
        st.plotly_chart(
            fig_ai,
            use_container_width=True,
            config={"displayModeBar": False, "scrollZoom": False}
        )


# =========================================================
# DATA EXPLORER
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("🗃️ View underlying sales data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        padding:30px 0 10px 0;
        color:#475569;
        font-size:12px;
    ">
        SalesMind AI • Intelligent Sales Analytics
    </div>
    """,
    unsafe_allow_html=True
)
