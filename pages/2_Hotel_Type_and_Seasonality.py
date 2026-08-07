import sys
from pathlib import Path

# Make sure the project root (parent of this pages/ folder) is on sys.path,
# so the `utils` package can always be found regardless of the working
# directory the hosting platform launches Streamlit from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import clean_data, kpi_card_css, kpi, PRIMARY, ACCENT, CITY_COLOR, RESORT_COLOR, MONTH_ORDER

st.set_page_config(page_title="Stage 2.1 · Hotel Type & Seasonality", page_icon="🏨", layout="wide")
kpi_card_css()

st.title("🏨 Stage 2.1 · Monthly Booking Analysis by Hotel Type")
st.caption("Business question: Which hotel type do customers book most often, and how does demand move through the year?")

df, _, _ = clean_data()

# ---- Q1: share of bookings ------------------------------------------------
st.header("Which hotel type is booked more often?")

share = df["hotel"].value_counts().reset_index()
share.columns = ["hotel", "bookings"]
share["pct"] = (share["bookings"] / share["bookings"].sum() * 100).round(1)

c1, c2 = st.columns([1, 1.4])
with c1:
    fig = px.pie(share, names="hotel", values="bookings", hole=0.55,
                 color="hotel", color_discrete_map={"City Hotel": CITY_COLOR, "Resort Hotel": RESORT_COLOR},
                 title="Share of total bookings by hotel type")
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=380, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    top = share.iloc[0]
    other = share.iloc[1]
    kA, kB = st.columns(2)
    kpi(f"{top['hotel']} bookings", f"{top['bookings']:,} ({top['pct']}%)", kA)
    kpi(f"{other['hotel']} bookings", f"{other['bookings']:,} ({other['pct']}%)", kB)
    st.markdown(f"""
**{top['hotel']}** is booked more often, accounting for **{top['pct']}%** of all bookings in the
cleaned dataset, roughly **{top['pct'] - other['pct']:.0f} percentage points** ahead of
**{other['hotel']}** ({other['pct']}%). City Hotels typically draw a broader mix of business and
short-break travellers year-round, which is consistent with the higher volume seen here.
    """)

st.markdown("---")

# ---- Q2 + Q3: monthly bookings & seasonality --------------------------
st.header("Monthly bookings per hotel type")

monthly = df.groupby(["arrival_date_month", "hotel"], observed=True).size().reset_index(name="bookings")
monthly["arrival_date_month"] = pd.Categorical(monthly["arrival_date_month"], categories=MONTH_ORDER, ordered=True)
monthly = monthly.sort_values("arrival_date_month")

fig = px.line(monthly, x="arrival_date_month", y="bookings", color="hotel", markers=True,
              color_discrete_map={"City Hotel": CITY_COLOR, "Resort Hotel": RESORT_COLOR},
              labels={"arrival_date_month": "Arrival month", "bookings": "Number of bookings"},
              title="Bookings per month, by hotel type (all years combined)")
fig.update_layout(height=440, margin=dict(t=50, l=10, r=10, b=10), legend_title="")
st.plotly_chart(fig, use_container_width=True)

busiest = monthly.loc[monthly.groupby("hotel", observed=True)["bookings"].idxmax()]
quietest = monthly.loc[monthly.groupby("hotel", observed=True)["bookings"].idxmin()]

b1, b2 = st.columns(2)
with b1:
    st.markdown("**Busiest month per hotel type**")
    st.dataframe(busiest[["hotel", "arrival_date_month", "bookings"]].rename(
        columns={"arrival_date_month": "month"}), hide_index=True, use_container_width=True)
with b2:
    st.markdown("**Quietest month per hotel type**")
    st.dataframe(quietest[["hotel", "arrival_date_month", "bookings"]].rename(
        columns={"arrival_date_month": "month"}), hide_index=True, use_container_width=True)

st.subheader("What might explain this seasonal pattern?")
st.markdown("""
- **Resort Hotel** demand rises sharply through the **summer months (July–August)**, matching the
  classic leisure/holiday season — families and couples travelling during school holidays and warmer
  weather.
- **City Hotel** demand stays comparatively steadier across the year, with a dip in **January and
  the winter months**, consistent with a heavier mix of business travel, conferences and weekend
  city breaks that don't depend as much on holiday seasons.
- The **quietest periods for both hotel types cluster around January**, right after the December
  holiday season, a common lull in both leisure and corporate travel.
""")

st.subheader("What could a hotel do with this trend?")
st.markdown("""
- **Dynamic staffing & pricing** — scale up staffing and nightly rates for the Resort Hotel ahead of
  its summer peak, and run off-peak promotions in the shoulder months to smooth demand.
- **Cross-property packages** — bundle City Hotel + Resort Hotel stays to shift some summer overflow
  demand toward the City property, and vice-versa in the City Hotel's slower months.
- **Targeted marketing spend** — front-load marketing budget into the months just before each
  hotel's known low season, rather than spreading it evenly across the year.
""")
