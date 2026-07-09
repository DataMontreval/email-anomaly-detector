import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# =====================================
# Database Connection
# =====================================

engine = create_engine(
   "postgresql://username:password@localhost:5432/email_db"
)

# =====================================
# Load Data
# =====================================

data = pd.read_sql(
    "SELECT * FROM email_logs",
    engine
)

# =====================================
# Dashboard Header
# =====================================

st.set_page_config(
    page_title="Email Anomaly Detection Dashboard",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Email Anomaly Detection Dashboard")

st.caption(
    "Corporate Email Security Monitoring using Isolation Forest"
)

st.markdown(
    """
This application demonstrates anomaly detection in corporate email activity
using Isolation Forest, behavioral analysis and PostgreSQL data storage.

The dashboard allows you to monitor suspicious events, analyze user activity
and identify high-risk email behavior.
"""
)

st.divider()

# =====================================
# Dashboard Metrics
# =====================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Events",
    len(data)
)

col2.metric(
    "Detected Anomalies",
    len(data[data["anomaly"] == -1])
)

col3.metric(
    "Average Risk",
    round(data["final_risk"].mean(), 2)
)

col4.metric(
    "Maximum Risk",
    round(data["final_risk"].max(), 2)
)

# =====================================
# Sidebar Filters
# =====================================

st.sidebar.header("Filters")

st.sidebar.markdown(
    "### Dataset Filters"
)

min_emails = st.sidebar.slider(
    "Minimum Email Count",
    min_value=0,
    max_value=200,
    value=50
)

night_only = st.sidebar.checkbox(
    "Night Activity Only"
)

countries = st.sidebar.multiselect(
    "Countries",
    options=data["country"].unique(),
    default=data["country"].unique()
)

users = st.sidebar.multiselect(
    "Users",
    options=data["user_id"].unique(),
    default=data["user_id"].unique()
)

min_risk = st.sidebar.slider(
    "Minimum Risk Score",
    min_value=0.0,
    max_value=1.0,
    value=0.0
)

# =====================================
# Apply Filters
# =====================================

filtered = data[
    (data["email_count"] >= min_emails)
    & (data["country"].isin(countries))
    & (data["user_id"].isin(users))
    & (data["final_risk"] >= min_risk)
]

if night_only:
    filtered = filtered[
        (filtered["hour"] >= 0)
        & (filtered["hour"] <= 5)
    ]

st.info(
    f"Filtered records: {len(filtered)}"
)
# =====================================
# Filtered Dataset
# =====================================

st.subheader("📋 Filtered Dataset")

st.dataframe(
    filtered[
        [
            "user_id",
            "hour",
            "email_count",
            "attachments",
            "country",
            "final_risk",
        ]
    ],
    use_container_width=True,
)

# =====================================
# Top High-Risk Events
# =====================================

st.subheader("🔥 Top High-Risk Events")

top_risk = (
    filtered.sort_values(
        "final_risk",
        ascending=False,
    )
    .head(10)
)

st.dataframe(
    top_risk[
        [
            "user_id",
            "hour",
            "email_count",
            "country",
            "final_risk",
        ]
    ],
    use_container_width=True,
)

# =====================================
# Email Activity by User
# =====================================

st.subheader("📈 Email Activity by User")

chart_data = (
    filtered.groupby("user_id")["email_count"]
    .sum()
)

st.bar_chart(chart_data)

# =====================================
# Risk Score Distribution
# =====================================

st.subheader("📊 Risk Score Distribution")

risk_data = filtered.sort_values(
    "final_risk"
)

st.bar_chart(
    risk_data.set_index("user_id")[
        "final_risk"
    ]
)

# =====================================
# Events by Country
# =====================================

st.subheader("🌍 Events by Country")

country_count = (
    filtered.groupby("country")["email_count"]
    .count()
)

st.bar_chart(country_count)

# =====================================
# Night Activity
# =====================================

st.subheader("🌙 Night Activity")

night_data = filtered[
    filtered["hour"] < 6
]

night_users = (
    night_data.groupby("user_id")[
        "email_count"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
)

st.bar_chart(
    night_users.head(10)
)
# =====================================
# Export Filtered Dataset
# =====================================

st.subheader("⬇️ Export Data")

st.markdown(
    """
Download the filtered dataset for further analysis
or reporting.
"""
)

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="email_security_data.csv",
    mime="text/csv",
)

st.divider()

# =====================================
# Footer
# =====================================

st.markdown(
    """
---
### About this project

This dashboard is part of the **Email Anomaly Detection System**.

The application demonstrates how machine learning can be used to detect
suspicious email activity based on behavioral analysis and anomaly detection.

**Technologies used:**

- Python
- Pandas
- Scikit-learn
- PostgreSQL
- Streamlit
- SQLAlchemy

Developed as a portfolio project for Data Analyst / Python Developer positions.
"""
)
