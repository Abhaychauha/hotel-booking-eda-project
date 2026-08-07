import sys
from pathlib import Path

# Make sure the project root (this file's own folder) is on sys.path, so the
# `utils` package can always be found regardless of the working directory
# the hosting platform launches Streamlit from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from utils.data_loader import load_raw_data, clean_data, kpi_card_css, kpi, PRIMARY, ACCENT

st.set_page_config(
    page_title="Hotel Business Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

kpi_card_css()

# ---------------------------------------------------------------- HERO -----
st.markdown(f"""
<div style="background: linear-gradient(120deg, {PRIMARY} 0%, #2E5578 100%);
            padding: 42px 40px; border-radius: 14px; margin-bottom: 28px;">
    <p style="color:{ACCENT}; letter-spacing:0.12em; font-size:13px; font-weight:700;
              text-transform:uppercase; margin-bottom:6px;">
        Data Visualization Project · 2017 – 2019
    </p>
    <h1 style="color:white; margin:0; font-size:38px;">Investigating Hotel Business Performance</h1>
    <p style="color:#DCE4EC; font-size:16px; max-width:720px; margin-top:14px;">
        A data-driven look at booking and cancellation behaviour across a City Hotel and a Resort
        Hotel, built to turn ~119,000 raw booking records into decisions a hotel manager can act on.
    </p>
</div>
""", unsafe_allow_html=True)

raw_df = load_raw_data()
clean_df, log, summary = clean_data()

c1, c2, c3, c4 = st.columns(4)
kpi("Raw bookings loaded", f"{summary['start_rows']:,}", c1)
kpi("Bookings after cleaning", f"{summary['end_rows']:,}", c2)
kpi("Overall cancellation rate", f"{clean_df['is_canceled'].mean()*100:.1f}%", c3)
kpi("Period covered", "2017 – 2019", c4)

st.markdown("### ")

# --------------------------------------------------------- STAGE 0 ---------
st.header("Stage 0 · Problem Statement")

st.markdown("""
**1. Why does understanding customer booking behaviour matter?**

For a hotel, revenue is only ever *provisional* until a guest actually checks in — every confirmed
booking carries a real risk of being cancelled, and a cancelled room close to the arrival date is
usually lost revenue that can't be resold in time. Understanding *what* drives guests to book, and
*what* drives them to cancel, lets a hotel move from reacting to cancellations after the fact to
managing the risk in advance. Concretely, this kind of analysis can improve decisions on:
""")

d1, d2 = st.columns(2)
with d1:
    st.markdown("""
- **Staffing & inventory** — knowing which months and hotel types are busiest
- **Pricing & overbooking strategy** — anticipating how much cancellation risk to price in
- **Deposit & cancellation policy design** — tightening terms where cancellation risk is highest
    """)
with d2:
    st.markdown("""
- **Marketing spend** — growing demand for the weaker-performing hotel type or off-peak months
- **Guest communication** — reminders or check-ins for bookings most likely to fall through
- **Revenue forecasting** — building more realistic, cancellation-adjusted forecasts
    """)

st.markdown("**2. The three business questions this project answers:**")
st.markdown("""
1. **Hotel type popularity** — Which hotel type (City or Resort) do customers book most often, and how does demand move through the year?
2. **Stay duration vs. cancellation** — Does the length of a guest's stay affect how likely the booking is to be cancelled?
3. **Lead time vs. cancellation** — Does the gap between booking and arrival (lead time) affect the cancellation rate?
""")

st.info(
    "**Objective:** Produce a single, evidence-backed analysis of the 2017–2019 booking dataset "
    "that answers the three questions above with clear visualisations, and translate each finding "
    "into a concrete, actionable recommendation for hotel management. "
    "The deliverable is this interactive dashboard, walking through data cleaning, analysis and "
    "final recommendations stage by stage."
)

st.markdown("---")
st.markdown("### How this dashboard is organised")

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.markdown("""
**🧹 Stage 1 — Data Preprocessing**
Overview of the raw dataset, missing values, duplicates, inconsistent categories and anomalies —
with the reasoning behind every cleaning decision.
    """)
with nav2:
    st.markdown("""
**📊 Stage 2 — Data Analysis**
Three dedicated pages, one per business question: hotel type & seasonality, stay duration &
cancellation, and lead time & cancellation.
    """)
with nav3:
    st.markdown("""
**✅ Stage 3 — Summary & Recommendations**
Key findings pulled together into prioritised, actionable recommendations for hotel management.
    """)

st.caption("Use the sidebar to move between stages. All charts and figures below are computed live from the uploaded dataset.")
