"""
Shared data utilities for the Hotel Business Analytics app.

Centralising loading + cleaning here means every page works off the exact
same, already-cached DataFrame, and the cleaning logic (with the reasoning
behind each decision) only has to be written once.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "hotel_bookings_data.csv")

PRIMARY = "#1F3B57"     # deep navy (headers, text)
ACCENT = "#C9922F"      # warm gold (highlights)
CITY_COLOR = "#2E6F95"  # City Hotel
RESORT_COLOR = "#C9922F"  # Resort Hotel
BG_SOFT = "#F7F5F0"

MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


@st.cache_data(show_spinner=False)
def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df


@st.cache_data(show_spinner=False)
def clean_data():
    """
    Runs the full Stage 1 cleaning pipeline and returns:
      - cleaned DataFrame
      - a dict-based audit log describing every decision (for display)
    """
    df = load_raw_data().copy()
    log = []

    start_rows = len(df)

    # --- 1. Missing values -------------------------------------------------
    missing_before = df.isnull().sum()
    missing_cols = missing_before[missing_before > 0]

    # company: >90% missing -> guest simply wasn't booking on behalf of a
    # company. Missing here is informative, not an error, so we encode it
    # as its own category rather than dropping rows or columns.
    if "company" in df.columns:
        n = df["company"].isnull().sum()
        df["company"] = df["company"].apply(lambda x: "None" if pd.isnull(x) else "Corporate")
        log.append({
            "column": "company",
            "missing": int(n),
            "pct": round(100 * n / start_rows, 1),
            "action": "Recoded to a flag: 'None' (no company) vs 'Corporate' (company on file).",
            "reasoning": "A missing company almost always means the guest booked as an individual, "
                         "not that data was lost. Treating it as its own category preserves that signal."
        })

    # agent: missing -> booking wasn't placed through a travel agent.
    if "agent" in df.columns:
        n = df["agent"].isnull().sum()
        df["agent"] = df["agent"].apply(lambda x: "None" if pd.isnull(x) else "Agent")
        log.append({
            "column": "agent",
            "missing": int(n),
            "pct": round(100 * n / start_rows, 1),
            "action": "Recoded to a flag: 'None' (direct booking) vs 'Agent' (booked via agent).",
            "reasoning": "Same logic as company: absence is meaningful (a direct booking), so it "
                         "is encoded rather than imputed with a fake agent ID."
        })

    # children: a handful of missing values -> almost certainly 0 children,
    # since every other guest-count field for those rows is filled in.
    if "children" in df.columns:
        n = df["children"].isnull().sum()
        df["children"] = df["children"].fillna(0)
        log.append({
            "column": "children",
            "missing": int(n),
            "pct": round(100 * n / start_rows, 1),
            "action": "Filled with 0.",
            "reasoning": "Only a few rows affected, and adults/babies are populated for them - "
                         "the simplest, least distorting assumption is that no children were on the booking."
        })

    # city: small number of missing values -> unknown origin, kept as its
    # own category so we don't silently drop rows.
    if "city" in df.columns:
        n = df["city"].isnull().sum()
        df["city"] = df["city"].fillna("Unknown")
        log.append({
            "column": "city",
            "missing": int(n),
            "pct": round(100 * n / start_rows, 1),
            "action": "Filled with 'Unknown'.",
            "reasoning": "Guest origin isn't used in the three business questions this project "
                         "answers, so rows are kept and just labelled rather than discarded."
        })

    # --- 2. Duplicate rows ---------------------------------------------------
    dup_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    log.append({
        "column": "(entire row)",
        "missing": dup_count,
        "pct": round(100 * dup_count / start_rows, 1),
        "action": f"Dropped {dup_count:,} exact duplicate rows.",
        "reasoning": "A booking dataset shouldn't contain two 100%-identical records; these are "
                     "treated as accidental duplication (e.g. re-exported data) and removed."
    })

    # --- 3. Inconsistent categorical values --------------------------------
    undefined_meal = int((df["meal"] == "Undefined").sum()) if "meal" in df.columns else 0
    if "meal" in df.columns:
        df["meal"] = df["meal"].replace("Undefined", "No Meal")
        log.append({
            "column": "meal",
            "missing": undefined_meal,
            "pct": round(100 * undefined_meal / start_rows, 1),
            "action": "Recoded 'Undefined' to 'No Meal'.",
            "reasoning": "'Undefined' and 'No Meal'/'SC' (self-catering) describe the same "
                         "real-world situation - no meal plan purchased - so they are merged into "
                         "one consistent category instead of left as an ambiguous label."
        })

    # --- 4. Anomalies --------------------------------------------------------
    # Negative ADR is not a valid price; extreme ADR (>3 IQR-style cutoff,
    # using a fixed generous cap) is very likely a data-entry error.
    adr_negative = int((df["adr"] < 0).sum())
    adr_extreme = int((df["adr"] > 2000).sum())
    df = df[(df["adr"] >= 0) & (df["adr"] <= 2000)]
    log.append({
        "column": "adr",
        "missing": adr_negative + adr_extreme,
        "pct": round(100 * (adr_negative + adr_extreme) / start_rows, 1),
        "action": f"Removed {adr_negative} negative-ADR rows and {adr_extreme} extreme (>2000) ADR rows.",
        "reasoning": "A negative price is impossible, and a single-night rate above 2000 is far "
                     "outside normal hotel pricing - both look like data-entry errors that would "
                     "distort average pricing and revenue figures."
    })

    # Bookings with zero total guests (adults + children + babies == 0)
    zero_guests = int(((df["adults"] + df["children"] + df["babies"]) == 0).sum())
    df = df[(df["adults"] + df["children"] + df["babies"]) > 0]
    log.append({
        "column": "adults / children / babies",
        "missing": zero_guests,
        "pct": round(100 * zero_guests / start_rows, 1),
        "action": f"Removed {zero_guests} rows with zero total guests.",
        "reasoning": "A hotel booking with nobody staying isn't a valid booking record - most "
                     "likely a logging error - so these rows are excluded from analysis."
    })

    # --- Derived / helper columns used throughout the app -------------------
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_weekdays_nights"]
    df["total_guests"] = df["adults"] + df["children"] + df["babies"]
    df["is_canceled_label"] = df["is_canceled"].map({0: "Not Cancelled", 1: "Cancelled"})
    df["arrival_date_month"] = pd.Categorical(df["arrival_date_month"], categories=MONTH_ORDER, ordered=True)

    end_rows = len(df)
    summary = {
        "start_rows": start_rows,
        "end_rows": end_rows,
        "rows_removed": start_rows - end_rows,
        "pct_removed": round(100 * (start_rows - end_rows) / start_rows, 2),
        "missing_cols": missing_cols,
    }

    return df, log, summary


def kpi_card_css():
    st.markdown(f"""
    <style>
    .kpi-box {{
        background-color: white;
        border: 1px solid #E7E2D8;
        border-left: 5px solid {ACCENT};
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: {PRIMARY};
        margin: 0;
    }}
    .kpi-label {{
        font-size: 13px;
        color: #6B6558;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 0;
    }}
    </style>
    """, unsafe_allow_html=True)


def kpi(label, value, col):
    col.markdown(f"""
    <div class="kpi-box">
        <p class="kpi-label">{label}</p>
        <p class="kpi-value">{value}</p>
    </div>
    """, unsafe_allow_html=True)
