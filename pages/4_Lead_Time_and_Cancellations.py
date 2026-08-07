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

st.set_page_config(page_title="Stage 2.3 · Lead Time & Cancellations", page_icon="⏳", layout="wide")
kpi_card_css()

st.title("⏳ Stage 2.3 · Impact of Lead Time on Cancellation Rate")
st.caption("Business question: Does lead time (the gap between booking and arrival) affect the cancellation rate?")

df, _, _ = clean_data()

st.markdown("""
> **Lead time**, in this dataset, is the number of days between the date a booking was made and the
> guest's arrival date. A lead time of 0 means a same-day booking; a lead time of 300 means the room
> was booked about ten months in advance.
""")

# ---- bucket lead time for a readable, robust trend line -------------------
bins = [-1, 0, 7, 30, 90, 180, 365, 10000]
labels = ["Same day", "1–7 days", "8–30 days", "31–90 days", "91–180 days", "181–365 days", "365+ days"]
df["lead_time_bucket"] = pd.cut(df["lead_time"], bins=bins, labels=labels)

lt_group = df.groupby(["lead_time_bucket", "hotel"], observed=True).agg(
    bookings=("is_canceled", "size"),
    cancel_rate=("is_canceled", "mean")
).reset_index()
lt_group["cancel_rate_pct"] = (lt_group["cancel_rate"] * 100).round(1)

st.header("Cancellation rate by lead time")

fig = px.line(lt_group, x="lead_time_bucket", y="cancel_rate_pct", color="hotel", markers=True,
              color_discrete_map={"City Hotel": CITY_COLOR, "Resort Hotel": RESORT_COLOR},
              labels={"lead_time_bucket": "Lead time (days before arrival)", "cancel_rate_pct": "Cancellation rate (%)"},
              title="Cancellation rate by lead time bucket, per hotel type",
              category_orders={"lead_time_bucket": labels})
fig.update_layout(height=440, margin=dict(t=50, l=10, r=10, b=10), legend_title="")
st.plotly_chart(fig, use_container_width=True)

with st.expander("See underlying bucket-level figures"):
    st.dataframe(lt_group.rename(columns={"cancel_rate_pct": "cancel_rate_%"}), use_container_width=True, hide_index=True)

# ---- lowest / highest lead-time cancellation points ------------------
lowest = lt_group.loc[lt_group.groupby("hotel", observed=True)["cancel_rate_pct"].idxmin()]
highest = lt_group.loc[lt_group.groupby("hotel", observed=True)["cancel_rate_pct"].idxmax()]

st.subheader("Where is cancellation lowest and highest?")
l1, l2 = st.columns(2)
with l1:
    st.markdown("**Lowest cancellation rate**")
    st.dataframe(lowest[["hotel", "lead_time_bucket", "cancel_rate_pct"]], hide_index=True, use_container_width=True)
with l2:
    st.markdown("**Highest cancellation rate**")
    st.dataframe(highest[["hotel", "lead_time_bucket", "cancel_rate_pct"]], hide_index=True, use_container_width=True)

st.markdown("""
Cancellation is **lowest for same-day / very short lead-time bookings** — a guest booking a room for
tonight or tomorrow is, almost by definition, committed to staying. It's **highest for the longest
lead times (181+ days out)**, especially for whichever hotel type shows the steepest rise below.
""")

st.markdown("---")

st.header("Comparing the two hotel types")

# compute simple "spread" (max - min cancel rate) per hotel to describe stability
spread = lt_group.groupby("hotel")["cancel_rate_pct"].agg(["min", "max"])
spread["range"] = (spread["max"] - spread["min"]).round(1)
more_stable = spread["range"].idxmin()
more_volatile = spread["range"].idxmax()

s1, s2 = st.columns(2)
kpi(f"{more_stable} cancellation range", f"{spread.loc[more_stable, 'range']} pts across lead times", s1)
kpi(f"{more_volatile} cancellation range", f"{spread.loc[more_volatile, 'range']} pts across lead times", s2)

st.markdown(f"""
**{more_stable}** stays comparatively more stable across lead times — its cancellation rate moves
within a narrower band regardless of how far ahead the booking was made. **{more_volatile}**, on the
other hand, rises much more sharply as lead time increases.

A plausible explanation: **{more_volatile}** bookings made far in advance are more often *leisure/
holiday plans* — inherently more likely to change over many months (different dates chosen, a
different destination booked, plans falling through) — whereas **{more_stable}**'s demand
(often business-oriented or short-notice city travel) is driven by needs that are firmer once a
booking is placed, regardless of how far out it was made.
""")
