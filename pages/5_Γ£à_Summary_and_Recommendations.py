import sys
from pathlib import Path

# Make sure the project root (parent of this pages/ folder) is on sys.path,
# so the `utils` package can always be found regardless of the working
# directory the hosting platform launches Streamlit from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from utils.data_loader import clean_data, kpi_card_css, kpi, PRIMARY, ACCENT

st.set_page_config(page_title="Stage 3 · Summary & Recommendations", page_icon="✅", layout="wide")
kpi_card_css()

st.title("✅ Stage 3 · Summary and Recommendations")
st.caption("Bringing the three analyses together into concrete actions for hotel management.")

df, _, _ = clean_data()

# quick recompute of headline numbers so this page is self-contained
share = df["hotel"].value_counts(normalize=True).mul(100).round(1)
cancel_by_hotel = df.groupby("hotel")["is_canceled"].mean().mul(100).round(1)
overall_cancel = df["is_canceled"].mean() * 100

st.header("1. Key findings")

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("#### 🏨 Hotel type & seasonality")
    st.markdown(f"""
- **{share.idxmax()}** takes the larger share of bookings ({share.max()}%
  vs {share.min()}% for {share.idxmin()}).
- **Resort Hotel** demand peaks sharply in **summer**; **City Hotel** demand is steadier year-round
  with a dip around **January**.
    """)
with f2:
    st.markdown("#### 📅 Stay duration")
    st.markdown(f"""
- Overall cancellation rate is **{overall_cancel:.1f}%**, higher for
  **{cancel_by_hotel.idxmax()}** ({cancel_by_hotel.max()}%) than
  **{cancel_by_hotel.idxmin()}** ({cancel_by_hotel.min()}%).
- Cancellation rate **rises with length of stay** for both hotel types — longer bookings are
  meaningfully more likely to fall through.
    """)
with f3:
    st.markdown("#### ⏳ Lead time")
    st.markdown("""
- Same-day / short-lead bookings cancel **least** often.
- Cancellation risk climbs steadily with lead time, rising sharply for bookings made **many months
  in advance** — most visibly for the more leisure-driven hotel type.
    """)

st.markdown("---")
st.header("2. Recommendations")

st.subheader("A. Hotel type & seasonality")
st.markdown("""
1. **Grow the less-popular hotel type** with targeted off-peak packages and channel-specific
   promotions (e.g. corporate rate cards, weekend city-break bundles) rather than generic
   discounting, to close the demand gap without eroding margin on the stronger property.
2. **Capitalise on peak seasons** by tightening cancellation terms and raising rates during each
   hotel's known busy months (Resort Hotel summer, City Hotel's steadier peak periods), while using
   the shoulder months either side to smooth demand with earlier, lighter promotions.
""")

st.subheader("B. Stay duration & cancellations")
st.markdown("""
3. **Introduce length-of-stay-tiered cancellation policies** — e.g. free cancellation up to 48 hours
   before arrival for short stays, but a partial non-refundable deposit for stays of 7+ nights, where
   cancellation risk is highest. This directly targets the segment shown to cancel most, without
   penalising the low-risk short-stay majority.
4. Consider **modest early-payment incentives** (small rate discount) for long-stay bookings that
   accept a non-refundable or partially-refundable rate, converting some of that cancellation risk
   into guaranteed revenue upfront.
""")

st.subheader("C. Lead time & cancellations")
st.markdown("""
5. **Automated reminder/confirmation touchpoints** for bookings made far in advance — e.g. an email
   or SMS confirmation request at the 90-day and 30-day marks — to catch and address wavering plans
   before they turn into last-minute cancellations.
6. **Small deposits scaled to lead time** for bookings placed many months out, mirroring the airline/
   travel industry practice of asking for a deposit that increases commitment without requiring full
   prepayment.
7. Where a long-lead booking does need to change, **actively offer date-rescheduling instead of
   cancellation** (e.g. via a self-service portal) — this preserves the revenue instead of losing it
   outright.
""")

st.markdown("---")
st.header("3. Highest-impact recommendation")

st.success("""
**Tiered cancellation policy by length of stay (Recommendation 3) is likely to have the single
biggest impact.**

The stay-duration analysis showed a clear, consistent, positive relationship between length of stay
and cancellation rate across *both* hotel types — this is the most direct and controllable lever
available, because cancellation *terms* are something the hotel sets itself, unlike broader seasonal
demand patterns. Combined with lead-time-based deposits (Recommendation 6) targeting the segment
shown to be both highest-value (longer, further-out bookings) and highest-risk, this pair of policy
changes attacks the two dimensions — **duration and lead time** — that this analysis found to be the
strongest, most visible predictors of cancellation in the data.
""")

st.caption(
    "All figures on this page are computed live from the cleaned dataset "
    f"({df.shape[0]:,} bookings) — see the Data Preprocessing page for the full cleaning log."
)
