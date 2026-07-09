import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import create_engine

# =====================================
# Generate synthetic email activity data
# =====================================

np.random.seed(42)

# Normal email activity
data = pd.DataFrame({
    "user_id": np.random.randint(1, 20, 1000),
    "hour": np.random.randint(8, 20, 1000),
    "email_count": np.random.randint(1, 15, 1000),
    "attachments": np.random.randint(0, 3, 1000),
    "country": np.random.choice(["PL", "DE", "UA"], 1000)
})

# Suspicious email activity
anomalies = pd.DataFrame({
    "user_id": np.random.randint(1, 20, 50),
    "hour": np.random.choice([1, 2, 3, 4], 50),
    "email_count": np.random.randint(50, 200, 50),
    "attachments": np.random.randint(5, 10, 50),
    "country": np.random.choice(["CN", "IN"], 50)
})

# Combine datasets
data = pd.concat([data, anomalies], ignore_index=True)

# =====================================
# Data preprocessing
# =====================================

# Encode categorical features
data_encoded = pd.get_dummies(
    data,
    columns=["country"]
)

# =====================================
# Anomaly detection
# =====================================

model = IsolationForest(
    contamination=0.05,
    random_state=42
)

model.fit(data_encoded)

# Predict anomalies
data["anomaly"] = model.predict(data_encoded)

# Calculate anomaly score
data["risk_score"] = model.decision_function(data_encoded)

print("\nFirst records of the generated dataset:")
print(data.head())

print("\nTop suspicious events:")
print(
    data.sort_values(
        "risk_score"
    ).head(10)
)

# =====================================
# Behavior analysis
# =====================================

# Average user activity
user_stats = data.groupby("user_id").agg({
    "hour": "mean",
    "email_count": "mean"
}).rename(columns={
    "hour": "avg_hour",
    "email_count": "avg_emails"
})

# Merge user statistics
data = data.merge(
    user_stats,
    on="user_id"
)

# Calculate deviations from normal behavior
data["hour_diff"] = abs(
    data["hour"] - data["avg_hour"]
)

data["email_diff"] = abs(
    data["email_count"] - data["avg_emails"]
)

print("\nBehavior analysis:")
print(
    data.sort_values(
        "email_diff",
        ascending=False
    ).head(10)
)
# =====================================
# Final risk calculation
# =====================================

# Normalize behavior deviation values
data["email_diff_norm"] = (
    data["email_diff"] / data["email_diff"].max()
)

data["hour_diff_norm"] = (
    data["hour_diff"] / data["hour_diff"].max()
)

# Convert anomaly labels to binary values
data["anomaly_flag"] = data["anomaly"].apply(
    lambda value: 1 if value == -1 else 0
)

# Calculate final risk score
data["final_risk"] = (
    data["anomaly_flag"] * 0.5 +
    (-data["risk_score"]) * 0.3 +
    data["email_diff_norm"] * 0.1 +
    data["hour_diff_norm"] * 0.1
)

# Sort events by risk score
top_risk = data.sort_values(
    "final_risk",
    ascending=False
)

print("\nTop High-Risk Events:")

print(
    top_risk[
        [
            "user_id",
            "hour",
            "email_count",
            "country",
            "final_risk"
        ]
    ].head(10)
)

# =====================================
# Save results to PostgreSQL
# =====================================

engine = create_engine(
    "postgresql://postgres:tfh64es13@localhost:5432/email_db"
)

data.to_sql(
    "email_logs",
    engine,
    if_exists="replace",
    index=False
)

print("\nData successfully saved to PostgreSQL.")

# =====================================
# Export dataset
# =====================================

data.to_csv(
    "data/generated_data.csv",
    index=False
)

print("\nCSV file successfully exported.")