from datetime import datetime
import pandas as pd
import sqlite3

print("Connecting to database and loading data via SQL...")
conn = sqlite3.connect("data/churn.db")

query = """
SELECT 
    u.user_id,
    u.signup_date,
    u.acquisition_channel,
    s.plan_type,
    s.mrr,
    s.payment_failures,
    s.churned,
    l.logins_last_30_days,
    l.support_tickets_opened
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
JOIN usage_logs l ON u.user_id = l.user_id
"""

df = pd.read_sql_query(query, conn)
conn.close()

df["signup_date"] = pd.to_datetime(df["signup_date"])

print("Engineering features...")

ref_date = pd.to_datetime("2026-01-01")
df["tenure_days"] = (ref_date - df["signup_date"]).dt.days

df["tenure_days"] = df["tenure_days"].apply(lambda x: max(x, 1))

df["support_ticket_ratio"] = df["support_tickets_opened"] / df["tenure_days"]

df["engagement_score"] = df["logins_last_30_days"] - (df["payment_failures"] * 5)

print("\n--- Data Head ---")
print(df.head())

print("\n--- DataFrame Info ---")
print(df.info())