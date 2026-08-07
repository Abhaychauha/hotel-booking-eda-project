import sys
from pathlib import Path

# Make sure the project root (parent of this pages/ folder) is on sys.path,
# so the `utils` package can always be found regardless of the working
# directory the hosting platform launches Streamlit from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import clean_data, kpi_card_css, kpi, CITY_COLOR, RESORT_COLOR

st.set_page_config(page_title="Stage 2.2 · Stay Duration & Cancellations", page_icon="📅", layout="wide")
kpi_card_css()

st.title("📅 Stage 2.2 · Impact of Stay Duration on Cancellation Rate")
st.caption("Business question: Does the length of stay affect the booking cancellation rate?")

df, _, _ = clean_data()

# ---- Q1: cancellation rate by hotel type -----------------------------
st.header("Cancellation rate by hotel type")

rate_by_hotel = df.groupby("hotel")["is_canceled"].mean().reset_index()
rate_by_hotel["is_canceled"] = (rate_by_hotel["is_canceled"] * 100).round(1)

c1, c2 = st.columns([1.2, 1])
with c1:
    fig = px.bar(rate_by_hotel, x="hotel", y="is_canceled", color="hotel",
                 color_discrete_map={"City Hotel": CITY_COLOR, "Resort Hotel": RESORT_COLOR},
                 text="is_canceled", labels={"is_canceled": "Cancellation rate (%)"},
                 title="Overall cancellation rate by hotel type")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=380, showlegend=False, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    higher = rate_by_hotel.loc[rate_by_hotel["is_canceled"].idxmax()]
    lower = rate_by_hotel.loc[rate_by_hotel["is_canceled"].idxmin()]
    kpi(f"{higher['hotel']} cancellation rate", f"{higher['is_canceled']}%", c2)
    st.markdown("")
    kpi(f"{lower['hotel']} cancellation rate", f"{lower['is_canceled']}%", c2)
    st.markdown(f"""
**{higher['hotel']}** is cancelled more often than **{lower['hotel']}**, by roughly
**{higher['is_canceled'] - lower['is_canceled']:.1f} percentage points**.
    """)

st.markdown("---")

# ---- Q2 + Q3: cancellation rate vs. length of stay -----------------------
st.header("Cancellation rate vs. total length of stay")

df["total_nights_capped"] = df["total_nights"].clip(upper=14)  # cap for a readable x-axis
stay_group = df.groupby(["total_nights_capped", "hotel"]).agg(
    bookings=("is_canceled", "size"),
    cancel_rate=("is_canceled", "mean")
).reset_index()
stay_group = stay_group[stay_group["bookings"] >= 30]  # drop noisy, low-volume tail
stay_group["cancel_rate_pct"] = (stay_group["cancel_rate"] * 100).round(1)

fig = px.line(stay_group, x="total_nights_capped", y="cancel_rate_pct", color="hotel", markers=True,
              color_discrete_map={"City Hotel": CITY_COLOR, "Resort Hotel": RESORT_COLOR},
              labels={"total_nights_capped": "Total length of stay (nights, capped at 14+)",
                      "cancel_rate_pct": "Cancellation rate (%)"},
              title="Cancellation rate by length of stay, per hotel type")
fig.update_layout(height=440, margin=dict(t=50, l=10, r=10, b=10), legend_title="")
st.plotly_chart(fig, use_container_width=True)
st.caption("Stay lengths with fewer than 30 bookings at that exact night-count are excluded to avoid noisy, unreliable rates.")

st.subheader("Describing the trend")
st.markdown("""
- For **both hotel types**, the cancellation rate **rises as the length of stay increases** —
  short 1–2 night stays are cancelled least often, while longer stays (7+ nights) show a
  noticeably higher cancellation rate.
- The relationship is **positive** (longer stay → higher cancellation risk) rather than flat or negative.
- **City Hotel** cancellation rates climb somewhat faster with stay length than **Resort Hotel**,
  suggesting City Hotel guests booking longer stays are relatively less certain of their plans —
  possibly extended business trips or provisional city breaks that are easier to cancel or rebook
  elsewhere.
""")

st.subheader("Why might longer stays be cancelled more often?")
st.markdown("""
1. **Greater planning uncertainty** — the more nights booked, the more that could change (work
   schedules, group travel plans, budget) between booking and arrival, increasing the odds *something*
   disrupts the trip.
2. **Lower switching cost / softer terms** — longer, often more expensive bookings are more likely to
   be made with flexible or refundable rates precisely because the guest wants a safety net, making
   cancellation easier and cheaper for them.
3. **Bulk/group or exploratory bookings** — long stays are sometimes placed speculatively (e.g. holding
   a room while final holiday dates are confirmed) and cancelled once real plans firm up.
""")
