from pathlib import Path
import pandas as pd
import streamlit as st
import sys

# Page configuration
# Page configuration
st.set_page_config(page_title="Olist Dashboard", layout="wide")

# Path handling - Simplest for Streamlit Cloud
DATA_FILE = Path("data/processed/dashboard_orders.csv")

st.title("Olist KPI Dashboard")
st.markdown("---")

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    try:
        if not path.exists():
            st.error(f"### ❌ Data file not found\nExpected at: `{path}`")
            st.info("Check if the file is present in your GitHub repository folder: `data/processed/dashboard_orders.csv`")
            st.stop()
            
        # Use standard pandas engine for maximum compatibility on cloud environments
        df = pd.read_csv(path)

        # Ensure correct types for filtering
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
        df["order_gmv"] = pd.to_numeric(df["order_gmv"], errors="coerce").fillna(0.0)
        df["order_items"] = pd.to_numeric(df["order_items"], errors="coerce").fillna(0).astype(int)
        df["category"] = df["category"].fillna("unknown")

        return df
    except Exception as e:
        st.error(f"### ❌ Error loading data\n`{str(e)}`")
        st.exception(e)
        st.stop()

# Execution with error handling
try:
    df = load_data(DATA_FILE)
except Exception as e:
    st.error(f"### ❌ Unexpected error\n`{str(e)}`")
    st.stop()

# ----------------------------
# Sidebar filters
# ----------------------------
st.sidebar.header("Filters")

try:
    min_date = df["order_date"].min()
    max_date = df["order_date"].max()

    date_range = st.sidebar.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    categories = sorted(df["category"].dropna().unique())
    selected_categories = st.sidebar.multiselect(
        "Product category",
        options=categories,
        default=categories
    )

    # Apply filters safely
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
        mask = (
            (df["order_date"] >= start_date) &
            (df["order_date"] <= end_date) &
            (df["category"].isin(selected_categories))
        )
        df_filtered = df.loc[mask].copy()
    else:
        # If range incomplete, filter only by category
        df_filtered = df[df["category"].isin(selected_categories)].copy()

except Exception as e:
    st.sidebar.error(f"Error in filters: {e}")
    df_filtered = df.copy()

# ----------------------------
# KPIs
# ----------------------------
try:
    total_gmv = df_filtered["order_gmv"].sum()
    total_orders = df_filtered["order_id"].nunique()
    aov = total_gmv / total_orders if total_orders > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total GMV", f"${total_gmv:,.0f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("AOV", f"${aov:,.2f}")
except Exception as e:
    st.warning(f"Metrics error: {e}")

st.markdown("---")

# ----------------------------
# Chart 1 — Monthly GMV trend
# ----------------------------
try:
    monthly = (
        df_filtered.groupby("order_month", as_index=False)
        .agg(gmv=("order_gmv", "sum"), orders=("order_id", "nunique"))
        .sort_values("order_month")
    )

    st.subheader("Monthly GMV Trend")
    st.line_chart(monthly.set_index("order_month")[["gmv"]])
except Exception as e:
    st.error(f"Chart error: {e}")

# ----------------------------
# Chart 2 — Top categories by GMV
# ----------------------------
try:
    top_n = st.selectbox("Top N categories", [5, 10, 15, 20], index=1)

    cat_perf = (
        df_filtered.groupby("category", as_index=False)
        .agg(gmv=("order_gmv", "sum"), orders=("order_id", "nunique"))
        .sort_values("gmv", ascending=False)
        .head(top_n)
    )

    st.subheader("Top Categories by GMV")
    st.bar_chart(cat_perf.set_index("category")[["gmv"]])
except Exception as e:
    st.error(f"Categories error: {e}")

# ----------------------------
# Storytelling / Insights
# ----------------------------
st.markdown("---")
st.subheader("What this view tells you")

# Dynamic context check
selected_cat_count = len(selected_categories)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    st.write(
        f"- **Date window:** `{date_range[0]}` → `{date_range[1]}`"
        f"\n- **Categories selected:** {selected_cat_count}"
        f"\n- **Orders in scope:** {total_orders:,}"
    )
else:
    st.write(
        f"- **Date window:** (Select a range in the sidebar)"
        f"\n- **Categories selected:** {selected_cat_count}"
        f"\n- **Orders in scope:** {total_orders:,}"
    )

# Data-driven insights
if total_orders > 0:
    try:
        # Best month by GMV
        best_month_row = monthly.sort_values("gmv", ascending=False).head(1)
        best_month = best_month_row["order_month"].iloc[0]
        best_month_gmv = best_month_row["gmv"].iloc[0]

        # Top category by GMV
        top_cat = cat_perf.sort_values("gmv", ascending=False).head(1)
        top_cat_name = top_cat["category"].iloc[0]
        top_cat_gmv = top_cat["gmv"].iloc[0]

        st.write("### Key takeaways (data-backed)")
        st.write(
            f"1) **Peak month (GMV):** `{best_month}` with **${best_month_gmv:,.0f}** GMV."
        )
        st.write(
            f"2) **Top category (GMV):** `{top_cat_name}` with **${top_cat_gmv:,.0f}** GMV in the current filter."
        )
        st.write(
            "3) **AOV signal:** Use AOV to check whether growth comes from **more orders** or **higher basket size**."
        )
    except Exception:
        st.write("*(Insights unavailable for this selection)*")

st.markdown("### How to use this dashboard")
st.write(
    "- Start with **date range** to isolate a period (e.g., last quarter).\n"
    "- Use **category filter** to compare segments.\n"
    "- Watch how **GMV trend** changes and cross-check with **Top categories**.\n"
    "- Use **AOV** to understand if performance is driven by volume vs. value."
)

# ----------------------------
# Data preview
# ----------------------------
try:
    st.write(f"Showing **{df_filtered.shape[0]:,}** orders after filters.")
    st.dataframe(df_filtered.head(100), width="stretch")
except Exception as e:
    st.warning(f"Dataframe preview error: {e}")