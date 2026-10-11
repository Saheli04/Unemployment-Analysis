
# ============================================================
# UNEMPLOYMENT ANALYSIS WITH PYTHON
# Project: Unemployment Analysis in India
# ============================================================

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------
# 1. PROJECT CONFIGURATION
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Unemployment in India.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
PLOT_DIR = OUTPUT_DIR / "plots"

OUTPUT_DIR.mkdir(exist_ok=True)
PLOT_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["figure.dpi"] = 110

print("=" * 65)
print("       UNEMPLOYMENT ANALYSIS WITH PYTHON")
print("=" * 65)

# ------------------------------------------------------------
# 2. LOAD THE DATASET
# ------------------------------------------------------------

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Place 'Unemployment in India.csv' beside main.py."
    )

df = pd.read_csv(DATA_PATH)

print("\n[1] ORIGINAL DATASET")
print("-" * 45)
print("Dataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst five rows:")
print(df.head().to_string(index=False))

print("\nOriginal data types:")
print(df.dtypes)

# ------------------------------------------------------------
# 3. DATA CLEANING
# ------------------------------------------------------------

# Remove accidental spaces from column names.
df.columns = df.columns.str.strip()

# Remove rows that are entirely empty.
original_rows = len(df)
df = df.dropna(how="all").copy()
blank_rows_removed = original_rows - len(df)

# Remove leading and trailing spaces from text columns.
for column in df.columns:
    if df[column].dtype == object or isinstance(
        df[column].dtype, pd.StringDtype
    ):
        if df[column].dtype != "datetime64[ns]":
            df[column] = df[column].str.strip()

# Convert date strings into proper datetime values.
df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# Convert measurement columns to numeric.
numeric_columns = [
    "Estimated Unemployment Rate (%)",
    "Estimated Employed",
    "Estimated Labour Participation Rate (%)"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Count duplicate rows before removing them.
duplicate_count = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

# Check missing values after removing blank rows.
missing_before_imputation = df.isna().sum()

print("\n[2] DATA CLEANING")
print("-" * 45)
print("Completely blank rows removed:", blank_rows_removed)
print("Duplicate rows removed:", duplicate_count)
print("\nMissing values before imputation:")
print(missing_before_imputation)

# Fill missing categories only when appropriate.
for column in ["Region", "Frequency", "Area"]:
    df[column] = df[column].fillna("Unknown")

# Median imputation for missing measurements.
# This is a practical fallback, not a claim that the values
# are known. We also retain a missingness report.
for column in numeric_columns:
    if df[column].isna().any():
        median_value = df[column].median()
        if pd.notna(median_value):
            df[column] = df[column].fillna(median_value)

# Remove rows with invalid dates, since time-series analysis
# cannot use them.
invalid_dates = int(df["Date"].isna().sum())
df = df.dropna(subset=["Date"]).copy()

# Add useful time-related columns.
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Month Name"] = df["Date"].dt.strftime("%b")
df["Year-Month"] = df["Date"].dt.to_period("M").astype(str)

# Save cleaned data.
cleaned_path = OUTPUT_DIR / "cleaned_unemployment_data.csv"
df.to_csv(cleaned_path, index=False)

# Save a cleaning summary.
cleaning_summary = pd.DataFrame({
    "Metric": [
        "Original rows",
        "Completely blank rows removed",
        "Duplicate rows removed",
        "Rows with invalid dates removed",
        "Final rows",
        "Final columns"
    ],
    "Value": [
        original_rows,
        blank_rows_removed,
        duplicate_count,
        invalid_dates,
        len(df),
        len(df.columns)
    ]
})
cleaning_summary.to_csv(
    OUTPUT_DIR / "cleaning_summary.csv", index=False
)

print("\nCleaned dataset shape:", df.shape)
print("Cleaned dataset saved to:", cleaned_path)

# ------------------------------------------------------------
# 4. DATA EXPLORATION
# ------------------------------------------------------------

print("\n[3] EXPLORATORY DATA ANALYSIS")
print("-" * 45)

print("\nDate range:")
print("Start:", df["Date"].min().date())
print("End:  ", df["Date"].max().date())

print("\nRegions:", df["Region"].nunique())
print("Areas:", df["Area"].unique())

print("\nDescriptive statistics:")
print(df[numeric_columns].describe().round(2))

df[numeric_columns].describe().round(2).to_csv(
    OUTPUT_DIR / "descriptive_statistics.csv"
)

print("\nRecords by area:")
print(df["Area"].value_counts())

print("\nRecords by region:")
print(df["Region"].value_counts().head(10))

print("\nMissing values after cleaning:")
print(df.isna().sum())

# ------------------------------------------------------------
# 5. PREPARE MONTHLY SUMMARIES
# ------------------------------------------------------------

# The source contains separate region/area estimates.
# This calculates a simple mean across available observations.
# It is NOT a population-weighted official national estimate.
monthly = (
    df.groupby("Year-Month", as_index=False)
    .agg(
        Average_Unemployment=(
            "Estimated Unemployment Rate (%)", "mean"
        ),
        Average_Labour_Participation=(
            "Estimated Labour Participation Rate (%)", "mean"
        ),
        Average_Employment=("Estimated Employed", "mean"),
        Number_of_Observations=(
            "Estimated Unemployment Rate (%)", "count"
        )
    )
)

monthly["Date"] = pd.to_datetime(
    monthly["Year-Month"] + "-01"
)
monthly = monthly.sort_values("Date")

monthly.to_csv(
    OUTPUT_DIR / "monthly_unemployment_summary.csv",
    index=False
)

# ------------------------------------------------------------
# 6. VISUALIZATION 1: OVERALL UNEMPLOYMENT DISTRIBUTION
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))
sns.histplot(
    data=df,
    x="Estimated Unemployment Rate (%)",
    bins=25,
    kde=True
)
plt.title("Distribution of Estimated Unemployment Rates")
plt.xlabel("Estimated unemployment rate (%)")
plt.ylabel("Number of observations")
plt.tight_layout()
plt.savefig(PLOT_DIR / "01_unemployment_distribution.png")
plt.close()

# ------------------------------------------------------------
# 7. VISUALIZATION 2: UNEMPLOYMENT TREND OVER TIME
# ------------------------------------------------------------

plt.figure(figsize=(13, 6))
sns.lineplot(
    data=monthly,
    x="Date",
    y="Average_Unemployment",
    marker="o",
    linewidth=2.5
)

# COVID-19 period reference line.
plt.axvline(
    pd.Timestamp("2020-03-01"),
    color="red",
    linestyle="--",
    label="March 2020: start of COVID-period comparison"
)

plt.title("Average Observed Unemployment Rate Over Time")
plt.xlabel("Month")
plt.ylabel("Mean unemployment rate (%)")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOT_DIR / "02_monthly_unemployment_trend.png")
plt.close()

# ------------------------------------------------------------
# 8. VISUALIZATION 3: RURAL VS URBAN
# ------------------------------------------------------------

area_summary = (
    df.groupby("Area", as_index=False)
    ["Estimated Unemployment Rate (%)"]
    .mean()
    .sort_values("Estimated Unemployment Rate (%)", ascending=False)
)

area_summary.to_csv(
    OUTPUT_DIR / "rural_urban_comparison.csv", index=False
)

plt.figure(figsize=(9, 6))
sns.barplot(
    data=area_summary,
    x="Area",
    y="Estimated Unemployment Rate (%)"
)
plt.title("Average Observed Unemployment: Rural vs Urban")
plt.xlabel("Area")
plt.ylabel("Mean unemployment rate (%)")
plt.tight_layout()
plt.savefig(PLOT_DIR / "03_rural_urban_comparison.png")
plt.close()

# ------------------------------------------------------------
# 9. VISUALIZATION 4: REGION-WISE COMPARISON
# ------------------------------------------------------------

region_summary = (
    df.groupby("Region", as_index=False)
    ["Estimated Unemployment Rate (%)"]
    .mean()
    .sort_values("Estimated Unemployment Rate (%)", ascending=False)
)

region_summary.to_csv(
    OUTPUT_DIR / "region_wise_unemployment.csv", index=False
)

plt.figure(figsize=(12, 9))
sns.barplot(
    data=region_summary,
    y="Region",
    x="Estimated Unemployment Rate (%)"
)
plt.title("Average Observed Unemployment Rate by Region")
plt.xlabel("Mean unemployment rate (%)")
plt.ylabel("Region")
plt.tight_layout()
plt.savefig(PLOT_DIR / "04_region_wise_unemployment.png")
plt.close()

# ------------------------------------------------------------
# 10. VISUALIZATION 5: LABOUR PARTICIPATION
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df,
    x="Estimated Labour Participation Rate (%)",
    y="Estimated Unemployment Rate (%)",
    hue="Area",
    alpha=0.75
)
plt.title("Unemployment vs Labour Participation")
plt.xlabel("Estimated labour participation rate (%)")
plt.ylabel("Estimated unemployment rate (%)")
plt.tight_layout()
plt.savefig(PLOT_DIR / "05_unemployment_vs_participation.png")
plt.close()

correlation = df[numeric_columns].corr(numeric_only=True)

correlation.to_csv(
    OUTPUT_DIR / "correlation_matrix.csv"
)

plt.figure(figsize=(8, 6))
sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    vmin=-1,
    vmax=1
)
plt.title("Correlation Between Numeric Variables")
plt.tight_layout()
plt.savefig(PLOT_DIR / "06_correlation_heatmap.png")
plt.close()

# ------------------------------------------------------------
# 11. COVID-19 IMPACT ANALYSIS
# ------------------------------------------------------------

# Define the comparison windows explicitly.
# Pre-COVID: through February 2020.
# COVID period: March through June 2020 in this dataset.
pre_covid = df[df["Date"] < "2020-03-01"].copy()

covid_period = df[
    (df["Date"] >= "2020-03-01")
    & (df["Date"] <= "2020-06-30")
].copy()

def summarize_period(data, label):
    return {
        "Period": label,
        "Start_Date": (
            data["Date"].min().date() if not data.empty else None
        ),
        "End_Date": (
            data["Date"].max().date() if not data.empty else None
        ),
        "Observations": len(data),
        "Mean_Unemployment_Rate": (
            data["Estimated Unemployment Rate (%)"].mean()
            if not data.empty else np.nan
        ),
        "Median_Unemployment_Rate": (
            data["Estimated Unemployment Rate (%)"].median()
            if not data.empty else np.nan
        ),
        "Mean_Labour_Participation": (
            data["Estimated Labour Participation Rate (%)"].mean()
            if not data.empty else np.nan
        ),
        "Mean_Estimated_Employed": (
            data["Estimated Employed"].mean()
            if not data.empty else np.nan
        )
    }

covid_summary = pd.DataFrame([
    summarize_period(pre_covid, "Pre-COVID (through Feb 2020)"),
    summarize_period(covid_period, "COVID period (Mar-Jun 2020)")
])

covid_summary.to_csv(
    OUTPUT_DIR / "covid_period_comparison.csv", index=False
)

print("\n[4] COVID-19 PERIOD COMPARISON")
print("-" * 45)
print(covid_summary.round(2).to_string(index=False))

if not pre_covid.empty and not covid_period.empty:
    pre_mean = pre_covid[
        "Estimated Unemployment Rate (%)"
    ].mean()
    covid_mean = covid_period[
        "Estimated Unemployment Rate (%)"
    ].mean()

    change_pp = covid_mean - pre_mean

    print(f"\nPre-COVID mean: {pre_mean:.2f}%")
    print(f"COVID-period mean: {covid_mean:.2f}%")
    print(f"Difference: {change_pp:+.2f} percentage points")

    if pre_mean != 0:
        percent_change = (change_pp / pre_mean) * 100
        print(f"Relative change: {percent_change:+.2f}%")

# Plot period comparison.
plt.figure(figsize=(9, 6))
sns.barplot(
    data=covid_summary,
    x="Period",
    y="Mean_Unemployment_Rate"
)
plt.title("Mean Observed Unemployment: Pre-COVID vs COVID Period")
plt.xlabel("")
plt.ylabel("Mean unemployment rate (%)")
plt.xticks(rotation=10)
plt.tight_layout()
plt.savefig(PLOT_DIR / "07_covid_period_comparison.png")
plt.close()

# ------------------------------------------------------------
# 12. MONTHLY PATTERNS / LIMITED SEASONAL EXPLORATION
# ------------------------------------------------------------

df["Calendar Month"] = df["Date"].dt.month_name()

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

month_summary = (
    df.groupby("Calendar Month")[
        "Estimated Unemployment Rate (%)"
    ]
    .agg(["mean", "median", "count"])
    .reindex(month_order)
    .dropna(how="all")
    .reset_index()
)

month_summary.columns = [
    "Month", "Mean_Unemployment", "Median_Unemployment", "Count"
]

month_summary.to_csv(
    OUTPUT_DIR / "calendar_month_summary.csv", index=False
)

plt.figure(figsize=(12, 6))
sns.barplot(
    data=month_summary,
    x="Month",
    y="Mean_Unemployment"
)
plt.title("Observed Unemployment by Calendar Month")
plt.xlabel("Calendar month")
plt.ylabel("Mean unemployment rate (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(PLOT_DIR / "08_calendar_month_patterns.png")
plt.close()

# IMPORTANT: this dataset spans only about 14 months.
# Monthly differences cannot establish a reliable recurring
# seasonal pattern from just one annual cycle.

# ------------------------------------------------------------
# 13. HIGHEST UNEMPLOYMENT OBSERVATIONS
# ------------------------------------------------------------

highest_unemployment = df.nlargest(
    10, "Estimated Unemployment Rate (%)"
)[[
    "Region", "Date", "Area",
    "Estimated Unemployment Rate (%)",
    "Estimated Labour Participation Rate (%)"
]]

highest_unemployment.to_csv(
    OUTPUT_DIR / "top_10_unemployment_observations.csv",
    index=False
)

print("\n[5] TOP 10 HIGHEST UNEMPLOYMENT OBSERVATIONS")
print("-" * 45)
print(highest_unemployment.to_string(index=False))

# ------------------------------------------------------------
# 14. RURAL/URBAN COVID-PERIOD COMPARISON
# ------------------------------------------------------------

df["COVID Period"] = np.where(
    df["Date"] < "2020-03-01",
    "Pre-COVID",
    "COVID period"
)

area_covid = (
    df[df["Date"] <= "2020-06-30"]
    .groupby(["Area", "COVID Period"], as_index=False)
    ["Estimated Unemployment Rate (%)"]
    .mean()
)

area_covid.to_csv(
    OUTPUT_DIR / "area_covid_comparison.csv", index=False
)

plt.figure(figsize=(10, 6))
sns.barplot(
    data=area_covid,
    x="Area",
    y="Estimated Unemployment Rate (%)",
    hue="COVID Period"
)
plt.title("Rural and Urban Unemployment: Period Comparison")
plt.xlabel("Area")
plt.ylabel("Mean unemployment rate (%)")
plt.tight_layout()
plt.savefig(PLOT_DIR / "09_area_covid_comparison.png")
plt.close()

# ------------------------------------------------------------
# 15. AUTOMATIC INSIGHTS AND POLICY CONSIDERATIONS
# ------------------------------------------------------------

insights = []

if not pre_covid.empty and not covid_period.empty:
    change = (
        covid_period["Estimated Unemployment Rate (%)"].mean()
        - pre_covid["Estimated Unemployment Rate (%)"].mean()
    )

    if change > 0:
        insights.append(
            f"The average observed unemployment rate was "
            f"{change:.2f} percentage points higher during "
            f"March-June 2020 than before March 2020."
        )
    elif change < 0:
        insights.append(
            f"The average observed unemployment rate was "
            f"{abs(change):.2f} percentage points lower during "
            f"March-June 2020 than before March 2020."
        )
    else:
        insights.append(
            "The two period averages were equal to the displayed precision."
        )

if not region_summary.empty:
    highest_region = region_summary.iloc[0]
    lowest_region = region_summary.iloc[-1]

    insights.append(
        f"{highest_region['Region']} had the highest mean observed "
        f"unemployment rate among regions in this dataset "
        f"({highest_region['Estimated Unemployment Rate (%)']:.2f}%)."
    )

    insights.append(
        f"{lowest_region['Region']} had the lowest mean observed "
        f"unemployment rate among regions in this dataset "
        f"({lowest_region['Estimated Unemployment Rate (%)']:.2f}%)."
    )

if not area_summary.empty:
    highest_area = area_summary.iloc[0]
    insights.append(
        f"The {highest_area['Area'].lower()} observations had the higher "
        f"mean unemployment rate in the rural/urban comparison "
        f"({highest_area['Estimated Unemployment Rate (%)']:.2f}%)."
    )

insights.extend([
    "Policy consideration: examine region-specific employment support "
    "rather than relying only on a single national average.",
    "Policy consideration: assess rural and urban workers separately "
    "when designing job placement, training and income-support programmes.",
    "Policy consideration: track unemployment alongside labour "
    "participation and employment estimates.",
    "Limitation: these comparisons show associations over time, not "
    "proof that COVID-19 alone caused every observed change.",
    "Limitation: the dataset ends in June 2020 and cannot measure "
    "the full long-term recovery.",
    "Limitation: monthly averages here are unweighted averages of "
    "the available region/area observations, not official national rates.",
    "Limitation: roughly 14 months of data are insufficient to establish "
    "reliable recurring annual seasonality."
])

insights_path = OUTPUT_DIR / "key_insights_and_policy_notes.txt"

with open(insights_path, "w", encoding="utf-8") as file:
    file.write("UNEMPLOYMENT ANALYSIS: KEY INSIGHTS\n")
    file.write("=" * 50 + "\n\n")
    for number, insight in enumerate(insights, start=1):
        file.write(f"{number}. {insight}\n\n")

print("\n[6] KEY INSIGHTS")
print("-" * 45)
for number, insight in enumerate(insights, start=1):
    print(f"{number}. {insight}\n")

# ------------------------------------------------------------
# 16. FINAL OUTPUT SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("ANALYSIS COMPLETED SUCCESSFULLY!")
print("=" * 65)

print("\nCleaned data:")
print(cleaned_path)

print("\nTables and reports:")
print(OUTPUT_DIR)

print("\nCharts:")
print(PLOT_DIR)

print("\nGenerated chart files:")
for plot_file in sorted(PLOT_DIR.glob("*.png")):
    print("-", plot_file.name)

print("\nOpen the outputs folder to review your results.")