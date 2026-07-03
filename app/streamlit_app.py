import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


# ПІДКЛЮЧЕННЯ ДО БАЗИ ДАНИХ


engine = create_engine(
    "postgresql://postgres:tfh64es13@localhost:5432/email_db"
)


# ЗАВАНТАЖЕННЯ ДАНИХ


data = pd.read_sql(
    "SELECT * FROM email_logs",
    engine
)


# ЗАГОЛОВОК


st.title("📊 Система аналізу безпеки електронної пошти")

st.markdown("""
Дана система виконує аналіз активності користувачів електронної пошти,
виявляє аномальні події та оцінює рівень ризику за допомогою алгоритмів
машинного навчання.
""")


# МЕТРИКИ


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Кількість подій",
    len(data)
)

col2.metric(
    "Кількість аномалій",
    len(data[data["anomaly"] == -1])
)

col3.metric(
    "Середній ризик",
    round(data["final_risk"].mean(), 2)
)

col4.metric(
    "Максимальний ризик",
    round(data["final_risk"].max(), 2)
)


# ФІЛЬТРИ


st.sidebar.header("Фільтри")

min_emails = st.sidebar.slider(
    "Мінімальна кількість листів",
    0,
    200,
    50
)

night_only = st.sidebar.checkbox(
    "Тільки нічна активність"
)

countries = st.sidebar.multiselect(
    "Країни",
    options=data["country"].unique(),
    default=data["country"].unique()
)

users = st.sidebar.multiselect(
    "Користувачі",
    options=data["user_id"].unique(),
    default=data["user_id"].unique()
)

min_risk = st.sidebar.slider(
    "Мінімальний рівень ризику",
    0.0,
    1.0,
    0.0
)


# ФІЛЬТРАЦІЯ


filtered = data[
    (data["email_count"] >= min_emails) &
    (data["country"].isin(countries)) &
    (data["user_id"].isin(users)) &
    (data["final_risk"] >= min_risk)
]

if night_only:
    filtered = filtered[
        (filtered["hour"] >= 0) &
        (filtered["hour"] <= 5)
    ]

st.info(
    f"Кількість записів після фільтрації: {len(filtered)}"
)


# ТАБЛИЦЯ


st.subheader("📋 Відфільтровані дані")

st.dataframe(filtered[[
    "user_id",
    "hour",
    "email_count",
    "attachments",
    "country",
    "final_risk"
]])


# ТОП РИЗИКІВ


st.subheader("🔥 Найбільш ризиковані події")

top_risk = filtered.sort_values(
    "final_risk",
    ascending=False
).head(10)

st.dataframe(top_risk[[
    "user_id",
    "hour",
    "email_count",
    "country",
    "final_risk"
]])


# АКТИВНІСТЬ КОРИСТУВАЧІВ


st.subheader(
    "📈 Кількість електронних листів по користувачах"
)

chart_data = filtered.groupby(
    "user_id"
)["email_count"].sum()

st.bar_chart(chart_data)


# РОЗПОДІЛ РИЗИКУ


st.subheader("📊 Розподіл рівня ризику")

risk_data = filtered.sort_values(
    "final_risk"
)

st.bar_chart(
    risk_data.set_index("user_id")["final_risk"]
)


# СТАТИСТИКА ПО КРАЇНАХ


st.subheader("🌍 Кількість подій по країнах")

country_count = filtered.groupby(
    "country"
)["email_count"].count()

st.bar_chart(country_count)


# НІЧНА АКТИВНІСТЬ


st.subheader("🌙 Нічна активність користувачів")

night_data = filtered[
    filtered["hour"] < 6
]

night_users = night_data.groupby(
    "user_id"
)["email_count"].sum().sort_values(
    ascending=False
)

st.bar_chart(
    night_users.head(10)
)


# ЕКСПОРТ CSV


st.subheader("⬇️ Експорт даних")

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Завантажити CSV файл",
    data=csv,
    file_name="email_security_data.csv",
    mime="text/csv"
)