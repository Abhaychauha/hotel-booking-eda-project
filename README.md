# Investigate Hotel Business — Streamlit Dashboard

A multi-page Streamlit app covering all stages of the project brief:

- **Home (`app.py`)** — Stage 0: problem statement, business questions, objective.
- **1 · Data Preprocessing** — Stage 1: data overview, missing values, duplicates,
  inconsistent categories, and anomalies, each with the reasoning behind the fix.
- **2 · Hotel Type & Seasonality** — Stage 2.1: booking share and monthly trends by hotel type.
- **3 · Stay Duration & Cancellations** — Stage 2.2: cancellation rate vs. length of stay.
- **4 · Lead Time & Cancellations** — Stage 2.3: cancellation rate vs. booking lead time.
- **5 · Summary & Recommendations** — Stage 3: findings and prioritised recommendations.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app expects `data/hotel_bookings_data.csv` (already included) relative to the project root.
All cleaning and chart logic is cached with `st.cache_data`, so navigating between pages is instant
after the first load.

## Project structure

```
hotel_app/
├── app.py                                   # Home / Stage 0
├── pages/
│   ├── 1_🧹_Data_Preprocessing.py            # Stage 1
│   ├── 2_🏨_Hotel_Type_and_Seasonality.py    # Stage 2.1
│   ├── 3_📅_Stay_Duration_and_Cancellations.py  # Stage 2.2
│   ├── 4_⏳_Lead_Time_and_Cancellations.py   # Stage 2.3
│   └── 5_✅_Summary_and_Recommendations.py   # Stage 3
├── utils/
│   └── data_loader.py                        # shared loading, cleaning, styling
├── data/
│   └── hotel_bookings_data.csv
├── .streamlit/config.toml                    # theme
└── requirements.txt
```
