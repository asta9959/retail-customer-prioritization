"""
Customer Segmentation Dashboard
--------------------------------
Interactive Streamlit app for exploring RFM-based customer segments.

Run with:
    streamlit run dashboard.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from pathlib import Path

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Retail Customer Prioritization ",
    layout="wide"
)


# ============================================================
# SEGMENT DEFINITIONS
# ============================================================

SEGMENT_ORDER = [
    "High-Value & Active",
    "Regular Buyers",
    "High-Value One-Time Buyer",
    "Recent Low-Engagement",
    "Dormant Customers"
]


SEGMENT_COLORS = {
    "High-Value & Active": "#2E86AB",
    "Regular Buyers": "#43AA8B",
    "High-Value One-Time Buyer": "#F18F01",
    "Recent Low-Engagement": "#C73E1D",
    "Dormant Customers": "#7B2CBF",
}


SEGMENT_ACTIONS = {
    "High-Value & Active":
        "Focus on retention, loyalty rewards, early access, and premium offers.",

    "Regular Buyers":
        "Use cross-selling and upselling campaigns to increase purchase value and frequency.",

    "High-Value One-Time Buyer":
        "Encourage repeat purchases using personalized offers and follow-up campaigns.",

    "Recent Low-Engagement":
        "Use targeted re-engagement campaigns and personalized offers to increase activity.",

    "Dormant Customers":
        "Use low-cost re-engagement campaigns and prioritize high-potential customers for win-back efforts.",
}


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "outputs" / "customer_segments.csv"
    df = pd.read_csv(data_path)
    return df


df = load_data()


# ============================================================
# PAGE TITLE
# ============================================================

st.title("📊 Retail Customer Prioritization")

st.caption(
    "RFM (Recency, Frequency, Monetary) + K-Means clustering "
    "on the UCI Online Retail dataset. "
    "Use the filters on the left to explore each segment."
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Filters")

selected_segments = st.sidebar.multiselect(
    "Segment",
    options=SEGMENT_ORDER,
    default=SEGMENT_ORDER
)


# Monetary range

min_monetary = float(df["Monetary"].min())  
max_monetary = float(df["Monetary"].max())

monetary_range = st.sidebar.slider(
    "Monetary range (£)",
    min_monetary,
    max_monetary,
    (min_monetary, max_monetary)
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df[
    df["Segment"].isin(selected_segments)
    & df["Monetary"].between(
        monetary_range[0],
        monetary_range[1]
    )
]


# ============================================================
# KPI ROW
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Customers (filtered)",
    f"{len(filtered):,}"
)

col2.metric(
    "Total Revenue (filtered)",
    f"£{filtered['Monetary'].sum():,.0f}"
)

if len(filtered) > 0:

    col3.metric(
        "Avg Order Frequency",
        f"{filtered['Frequency'].mean():.1f}"
    )

    col4.metric(
        "Avg Recency (days)",
        f"{filtered['Recency'].mean():.0f}"
    )

else:

    col3.metric(
        "Avg Order Frequency",
        "0.0"
    )

    col4.metric(
        "Avg Recency (days)",
        "0"
    )


st.divider()


# ============================================================
# CHARTS
# ============================================================

left, right = st.columns(2)


# ------------------------------------------------------------
# Customer Count by Segment
# ------------------------------------------------------------

with left:

    seg_counts = (
        filtered["Segment"]
        .value_counts()
        .reindex(
            [
                s for s in SEGMENT_ORDER
                if s in selected_segments
            ],
            fill_value=0
        )
    )

    fig_pie = px.pie(
        values=seg_counts.values,
        names=seg_counts.index,
        color=seg_counts.index,
        color_discrete_map=SEGMENT_COLORS,
        title="Customer Count by Segment"
    )

    st.plotly_chart(
        fig_pie,
        width="stretch"
    )


# ------------------------------------------------------------
# Total Revenue by Segment
# ------------------------------------------------------------

with right:

    seg_rev = (
        filtered
        .groupby("Segment")["Monetary"]
        .sum()
        .reindex(
            [
                s for s in SEGMENT_ORDER
                if s in selected_segments
            ],
            fill_value=0
        )
    )

    fig_bar = px.bar(
        x=seg_rev.index,
        y=seg_rev.values,
        color=seg_rev.index,
        color_discrete_map=SEGMENT_COLORS,
        title="Total Revenue by Segment (£)",
        labels={
            "x": "Segment",
            "y": "Revenue (£)"
        }
    )

    st.plotly_chart(
        fig_bar,
        width="stretch"
    )


# ============================================================
# 3D RFM SCATTER PLOT
# ============================================================

if len(filtered) > 0:

    fig_scatter = px.scatter_3d(
        filtered,
        x="Recency",
        y="Frequency",
        z="Monetary",
        color="Segment",
        color_discrete_map=SEGMENT_COLORS,
        opacity=0.6,
        title="Customers in RFM Space",
        height=600
    )

    st.plotly_chart(
        fig_scatter,
        width="stretch"
    )

else:

    st.info(
        "No customers match the selected filters. "
        "Please select at least one segment or adjust the monetary range."
    )


# ============================================================
# SEGMENT RECOMMENDATIONS
# ============================================================

st.divider()

st.subheader("Recommended Action per Segment")


for seg in [
    s for s in SEGMENT_ORDER
    if s in selected_segments
]:

    seg_df = filtered[
        filtered["Segment"] == seg
    ]

    with st.container(border=True):

        st.markdown(
            f"**{seg}** — {SEGMENT_ACTIONS[seg]}"
        )

        if len(seg_df) > 0:

            st.caption(
                f"{len(seg_df):,} customers · "
                f"avg recency {seg_df['Recency'].mean():.0f} days · "
                f"avg frequency {seg_df['Frequency'].mean():.1f} orders · "
                f"avg spend £{seg_df['Monetary'].mean():,.0f}"
            )

        else:

            st.caption(
                "No customers in this segment match the current filters."
            )


# ============================================================
# CUSTOMER-LEVEL DATA
# ============================================================

st.divider()

st.subheader("Customer-Level Data")

st.dataframe(
    filtered
    .sort_values(
        "Monetary",
        ascending=False
    )
    .reset_index(drop=True),
    width="stretch"
)