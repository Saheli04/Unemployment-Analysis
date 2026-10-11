
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Unemployment Analytics | India",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "outputs" / "cleaned_unemployment_data.csv"


# --------------------------------------------------
# CUSTOM STYLING — PROFESSIONAL DARK THEME
# --------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #0B1220;
        --panel: #162238;
        --border: #2B3A52;
        --text: #F1F5F9;
        --muted: #A8B7CC;
        --teal: #2DD4BF;
        --amber: #FBBF24;
        --coral: #FB7185;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 18, 32, 0.95);
    }

    [data-testid="stSidebar"] {
        background: #101A2B;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: var(--text) !important;
        font-size: 2.35rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: var(--text) !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }

    p, label, .stCaption {
        color: var(--muted);
    }

    .subtitle {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
        margin-top: -8px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #192840, #121D30);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 22px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
        min-height: 135px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
    }

    [data-testid="stPlotlyChart"] {
        background: #111C2E;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 12px 8px 4px 8px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    [data-testid="stExpander"] {
        background: #111C2E;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        background: var(--teal);
        color: #0B1220;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.55rem 1rem;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background: #5EEAD4;
        color: #0B1220;
        border: none;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: #162238;
        border-color: #3A4B65;
    }

    hr {
        border-color: var(--border);
        margin-top: 1.4rem;
        margin-bottom: 1.4rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Estimated Unemployment Rate (%)"] = pd.to_numeric(
        data["Estimated Unemployment Rate (%)"], errors="coerce"
    )
    data["Estimated Employed"] = pd.to_numeric(
        data["Estimated Employed"], errors="coerce"
    )
    data["Estimated Labour Participation Rate (%)"] = pd.to_numeric(
        data["Estimated Labour Participation Rate (%)"], errors="coerce"
    )
    data = data.dropna(
        subset=["Date", "Region", "Area", "Estimated Unemployment Rate (%)"]
    )
    data["Year-Month"] = data["Date"].dt.to_period("M").astype(str)
    return data


if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Run main.py first, then check that "
        "outputs/cleaned_unemployment_data.csv exists."
    )
    st.stop()

df = load_data(DATA_PATH)

RATE = "Estimated Unemployment Rate (%)"
EMPLOYED = "Estimated Employed"
PARTICIPATION = "Estimated Labour Participation Rate (%)"


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------
st.markdown(
    """
    <div style="background: linear-gradient(115deg, #172943, #111C2E);
                border: 1px solid #2B3A52;
                border-left: 5px solid #2DD4BF;
                border-radius: 18px;
                padding: 25px 28px;
                margin-bottom: 24px;">
        <div style="color: #2DD4BF;
                    font-size: 12px;
                    font-weight: 700;
                    letter-spacing: 2px;
                    margin-bottom: 8px;">
            ECONOMIC INSIGHTS · INDIA
        </div>
        <h1 style="margin: 0; color: #F1F5F9; font-size: 32px;">
            Unemployment Analytics
        </h1>
        <p style="color: #A8B7CC; margin: 10px 0 0 0; font-size: 15px;">
            Explore labour market patterns, regional differences,
            and the March–June 2020 period.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.divider()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.title("🎛️ Dashboard Filters")

regions = sorted(df["Region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Select regions",
    options=regions,
    default=regions,
)

areas = sorted(df["Area"].dropna().unique().tolist())
selected_areas = st.sidebar.multiselect(
    "Select area",
    options=areas,
    default=areas,
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["Region"].isin(selected_regions)
    & df["Area"].isin(selected_areas)
    & (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.warning("No data matches these filters. Change your selections.")
    st.stop()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------
average_rate = filtered[RATE].mean()
median_rate = filtered[RATE].median()
average_participation = filtered[PARTICIPATION].mean()
region_count = filtered["Region"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Unemployment", f"{average_rate:.2f}%")
c2.metric("Median Unemployment", f"{median_rate:.2f}%")
c3.metric("Labour Participation", f"{average_participation:.2f}%")
c4.metric("Regions Covered", f"{region_count}")

st.caption(
    f"Showing {len(filtered):,} region-area observations "
    f"from {start_date} to {end_date}. Rates are unweighted averages "
    "of the selected observations, not official national estimates."
)
st.divider()


# --------------------------------------------------
# PROFESSIONAL CHART THEME
# --------------------------------------------------
chart_layout = dict(
    template="plotly_dark",
    paper_bgcolor="#111C2E",
    plot_bgcolor="#111C2E",
    font=dict(
        family="Inter, sans-serif",
        color="#F1F5F9",
        size=12,
    ),
    title_font=dict(size=17, color="#F1F5F9"),
    margin=dict(l=20, r=25, t=65, b=30),
    hoverlabel=dict(
        bgcolor="#23334B",
        font_color="#FFFFFF",
        bordercolor="#2DD4BF",
    ),
    xaxis=dict(
        gridcolor="#26364D",
        zerolinecolor="#3A4B65",
    ),
    yaxis=dict(
        gridcolor="#26364D",
        zerolinecolor="#3A4B65",
    ),
)

# --------------------------------------------------
# UNEMPLOYMENT TREND
# --------------------------------------------------
st.subheader("📈 Unemployment Trend Over Time")

monthly = (
    filtered.groupby("Year-Month", as_index=False)
    .agg(
        Average_Unemployment=(RATE, "mean"),
        Average_Participation=(PARTICIPATION, "mean"),
    )
)

fig_trend = px.line(
    monthly,
    x="Year-Month",
    y="Average_Unemployment",
    markers=True,
    title="Monthly Average Unemployment Rate",
    labels={
        "Year-Month": "Month",
        "Average_Unemployment": "Unemployment Rate (%)",
    },
)
fig_trend.update_traces(
    line=dict(color="#2DD4BF", width=3.5),
    marker=dict(
        size=7,
        color="#2DD4BF",
        line=dict(color="#F1F5F9", width=1),
    ),
    hovertemplate="%{x}<br>Unemployment: %{y:.2f}%<extra></extra>",
)
fig_trend.update_layout(**chart_layout)
st.plotly_chart(fig_trend, use_container_width=True)

left, right = st.columns(2)

# --------------------------------------------------
# RURAL VS URBAN
# --------------------------------------------------
with left:
    st.subheader("🏙️ Rural vs Urban")

    area_summary = (
        filtered.groupby("Area", as_index=False)
        .agg(Average_Unemployment=(RATE, "mean"))
    )

    fig_area = px.bar(
        area_summary,
        x="Area",
        y="Average_Unemployment",
        color="Area",
        text_auto=".2f",
        title="Average Unemployment by Area",
        labels={
            "Area": "Area",
            "Average_Unemployment": "Unemployment Rate (%)",
        },
        color_discrete_sequence=["#38bdf8", "#f59e0b"],
    )
    fig_area.update_layout(**chart_layout, showlegend=False)
    st.plotly_chart(fig_area, use_container_width=True)

# --------------------------------------------------
# REGION COMPARISON
# --------------------------------------------------
with right:
    st.subheader("🗺️ Regional Comparison")

    region_summary = (
        filtered.groupby("Region", as_index=False)
        .agg(Average_Unemployment=(RATE, "mean"))
        .sort_values("Average_Unemployment", ascending=True)
    )

    fig_region = px.bar(
        region_summary,
        x="Average_Unemployment",
        y="Region",
        orientation="h",
        title="Average Unemployment by Region",
        labels={
            "Average_Unemployment": "Unemployment Rate (%)",
            "Region": "Region",
        },
        color="Average_Unemployment",
        color_continuous_scale="Teal",
    )
    fig_region.update_layout(**chart_layout, height=650)
    st.plotly_chart(fig_region, use_container_width=True)

# --------------------------------------------------
# DISTRIBUTION
# --------------------------------------------------
st.subheader("📊 Unemployment Rate Distribution")

fig_hist = px.histogram(
    filtered,
    x=RATE,
    nbins=30,
    marginal="box",
    title="Distribution of Observed Unemployment Rates",
    labels={RATE: "Unemployment Rate (%)"},
    color_discrete_sequence=["#38bdf8"],
)
fig_hist.update_layout(**chart_layout)
st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------------------------------
# EMPLOYMENT VS PARTICIPATION
# --------------------------------------------------
st.subheader("🔎 Employment and Labour Participation")

fig_scatter = px.scatter(
    filtered,
    x=PARTICIPATION,
    y=RATE,
    color="Area",
    hover_name="Region",
    size=EMPLOYED,
    size_max=24,
    title="Unemployment vs Labour Participation",
    labels={
        PARTICIPATION: "Labour Participation Rate (%)",
        RATE: "Unemployment Rate (%)",
        EMPLOYED: "Estimated Employed",
    },
)
fig_scatter.update_layout(**chart_layout)
st.plotly_chart(fig_scatter, use_container_width=True)

# --------------------------------------------------
# COVID PERIOD COMPARISON
# --------------------------------------------------
st.subheader("🦠 Pre-COVID vs COVID-Period Observations")

filtered["Period"] = filtered["Date"].apply(
    lambda d: "Pre-COVID (through Feb 2020)"
    if d < pd.Timestamp("2020-03-01")
    else "COVID period (Mar-Jun 2020)"
)

covid_summary = (
    filtered.groupby("Period", as_index=False)
    .agg(
        Average_Unemployment=(RATE, "mean"),
        Average_Participation=(PARTICIPATION, "mean"),
    )
)

fig_covid = px.bar(
    covid_summary,
    x="Period",
    y="Average_Unemployment",
    color="Period",
    text_auto=".2f",
    title="Observed Unemployment Before and During March–June 2020",
    labels={"Average_Unemployment": "Unemployment Rate (%)"},
    color_discrete_sequence=["#38bdf8", "#fb7185"],
)
fig_covid.update_layout(**chart_layout, showlegend=False)
st.plotly_chart(fig_covid, use_container_width=True)

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------
with st.expander("📄 Explore the filtered dataset"):
    st.dataframe(
        filtered.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv,
        file_name="filtered_unemployment_data.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "Project: Unemployment Analysis with Python | "
    "Tools: Python, Pandas, Plotly and Streamlit | "
    "Data period: May 2019 – June 2020"
)