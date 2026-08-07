import sys
from pathlib import Path

# Make sure the project root (parent of this pages/ folder) is on sys.path,
# so the `utils` package can always be found regardless of the working
# directory the hosting platform launches Streamlit from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_raw_data, clean_data, kpi_card_css, kpi, PRIMARY, ACCENT

st.set_page_config(page_title="Stage 1 · Data Preprocessing", page_icon="🧹", layout="wide")
kpi_card_css()

st.title("🧹 Stage 1 · Data Preprocessing")

raw_df = load_raw_data()
clean_df, log, summary = clean_data()

# =========================================================== 1.1 =========
st.header("1.1 Data Overview")

c1, c2, c3, c4 = st.columns(4)
kpi("Rows (raw)", f"{raw_df.shape[0]:,}", c1)
kpi("Columns", f"{raw_df.shape[1]}", c2)
kpi("Period covered", "Jul 2015 – Aug 2017 arrivals*", c3)
kpi("Hotel types", "City · Resort", c4)
st.caption("*Booking dates span 2017–2019 in the dataset export; arrival dates in the raw file follow the same multi-year window used throughout this analysis.")

st.markdown("""
The dataset holds one row per booking, with columns covering **who** booked (customer type, repeat
guest status), **when** (arrival year/month/week/day, lead time), **what** they booked (hotel type,
meal plan, room requests), **how** (market segment, distribution channel, agent/company), and the
**outcome** (`is_canceled`, `reservation_status`).

The columns most relevant to this project's three business questions are:
""")

rel1, rel2, rel3 = st.columns(3)
with rel1:
    st.markdown("**Hotel type & seasonality**\n- `hotel`\n- `arrival_date_month`\n- `arrival_date_year`")
with rel2:
    st.markdown("**Stay duration**\n- `stays_in_weekend_nights`\n- `stays_in_weekdays_nights`\n- `is_canceled`")
with rel3:
    st.markdown("**Lead time**\n- `lead_time`\n- `is_canceled`\n- `hotel`")

with st.expander("Preview raw data (first 20 rows)"):
    st.dataframe(raw_df.head(20), use_container_width=True)

with st.expander("Column data types"):
    dtype_df = pd.DataFrame({"column": raw_df.columns, "dtype": raw_df.dtypes.astype(str).values})
    st.dataframe(dtype_df, use_container_width=True, hide_index=True)

st.markdown("---")

# =========================================================== 1.2 =========
st.header("1.2 Data Assessment & Cleaning Decisions")
st.markdown("Every issue found in the raw data is listed below, together with the action taken and the reasoning behind it.")

# --- Missing values ---------------------------------------------------
st.subheader("A. Missing values")

miss = summary["missing_cols"].sort_values(ascending=False)
miss_df = pd.DataFrame({
    "column": miss.index,
    "missing_count": miss.values,
    "missing_%": (miss.values / summary["start_rows"] * 100).round(1)
})

mcol1, mcol2 = st.columns([1, 1.3])
with mcol1:
    st.dataframe(miss_df, use_container_width=True, hide_index=True)
with mcol2:
    fig = px.bar(miss_df, x="missing_%", y="column", orientation="h",
                 color_discrete_sequence=[ACCENT],
                 labels={"missing_%": "% of rows missing", "column": ""},
                 title="Share of missing values by column")
    fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=320,
                       margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

for entry in [l for l in log if l["column"] in miss_df["column"].values]:
    st.markdown(f"**`{entry['column']}`** — {entry['missing']:,} missing ({entry['pct']}%). "
                f"**Action:** {entry['action']} — *{entry['reasoning']}*")

st.markdown("---")

# --- Duplicates ---------------------------------------------------------
st.subheader("B. Duplicate rows")
dup_entry = [l for l in log if l["column"] == "(entire row)"][0]
d1, d2 = st.columns([1, 2])
with d1:
    kpi_card_css()
    kpi("Exact duplicate rows found", f"{dup_entry['missing']:,}", d1)
with d2:
    st.markdown(f"**Action:** {dup_entry['action']} ({dup_entry['pct']}% of the raw dataset)")
    st.markdown(f"*{dup_entry['reasoning']}*")

st.markdown("---")

# --- Inconsistent values -------------------------------------------------
st.subheader("C. Inconsistent / unclear categorical values")
meal_entry = [l for l in log if l["column"] == "meal"][0]

mc1, mc2 = st.columns(2)
with mc1:
    raw_meal_counts = raw_df["meal"].value_counts().reset_index()
    raw_meal_counts.columns = ["meal", "count"]
    fig = px.bar(raw_meal_counts, x="meal", y="count", color_discrete_sequence=[PRIMARY],
                 title="Meal category — before cleaning")
    fig.update_layout(height=320, margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
with mc2:
    clean_meal_counts = clean_df["meal"].value_counts().reset_index()
    clean_meal_counts.columns = ["meal", "count"]
    fig = px.bar(clean_meal_counts, x="meal", y="count", color_discrete_sequence=[ACCENT],
                 title="Meal category — after cleaning")
    fig.update_layout(height=320, margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown(f"**`meal` = 'Undefined'** — {meal_entry['missing']:,} rows ({meal_entry['pct']}%). "
            f"**Action:** {meal_entry['action']} — *{meal_entry['reasoning']}*")

st.markdown("---")

# --- Anomalies -------------------------------------------------------------
st.subheader("D. Anomalies")

adr_entry = [l for l in log if l["column"] == "adr"][0]
guest_entry = [l for l in log if "guests" in l["column"] or "children" in l["column"] and "adults" in l["column"]]
guest_entry = [l for l in log if l["column"] == "adults / children / babies"][0]

a1, a2 = st.columns(2)
with a1:
    fig = px.box(raw_df, y="adr", points=False, color_discrete_sequence=[PRIMARY],
                 title="Average Daily Rate (adr) — raw distribution")
    fig.update_layout(height=340, margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Action:** {adr_entry['action']}")
    st.markdown(f"*{adr_entry['reasoning']}*")

with a2:
    zero_guest_raw = int(((raw_df["adults"] + raw_df["children"].fillna(0) + raw_df["babies"]) == 0).sum())
    zg_df = pd.DataFrame({
        "category": ["Zero total guests", "Valid bookings"],
        "count": [zero_guest_raw, raw_df.shape[0] - zero_guest_raw]
    })
    fig = px.pie(zg_df, names="category", values="count", hole=0.55,
                 color_discrete_sequence=[ACCENT, "#E7E2D8"],
                 title="Bookings recording zero total guests")
    fig.update_layout(height=340, margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Action:** {guest_entry['action']}")
    st.markdown(f"*{guest_entry['reasoning']}*")

st.markdown("---")

# --- Net effect -------------------------------------------------------------
st.subheader("Net effect of cleaning")
n1, n2, n3 = st.columns(3)
kpi("Rows before cleaning", f"{summary['start_rows']:,}", n1)
kpi("Rows after cleaning", f"{summary['end_rows']:,}", n2)
kpi("Rows removed", f"{summary['rows_removed']:,} ({summary['pct_removed']}%)", n3)

st.success(
    f"After removing duplicates and clear anomalies (and recoding rather than deleting for "
    f"informative missingness), **{summary['end_rows']:,} bookings** ({100 - summary['pct_removed']:.1f}% "
    f"of the raw file) remain as the analysis-ready dataset used in every chart from Stage 2 onward."
)

with st.expander("Preview cleaned data (first 20 rows)"):
    st.dataframe(clean_df.head(20), use_container_width=True)
