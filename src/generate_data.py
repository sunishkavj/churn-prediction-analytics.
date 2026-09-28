import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
n_users = 5000

print("Generating synthetic SaaS customer data with behavioral signals...")

# 1. Users Data
user_ids = [f"USR_{i:04d}" for i in range(1, n_users + 1)]
signup_dates = [
    datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 365)))
    for _ in range(n_users)
]
channels = np.random.choice(
    ["Google Ads", "Organic", "LinkedIn", "Referral"],
    size=n_users,
    p=[0.4, 0.3, 0.2, 0.1],
)

users_df = pd.DataFrame(
    {
        "user_id": user_ids,
        "signup_date": signup_dates,
        "acquisition_channel" : channels,
    }
)

plans = np.random.choice(["Basic", "Pro", "Enterprise"], size=n_users, p=[0.6, 0.3, 0.1])
mrr_map = {"Basic": 15, "Pro": 49, "Enterprise": 199}
mrr = [mrr_map[p] for p in plans]
payment_failures = np.random.choice([0, 1], size=n_users, p=[0.85, 0.15])


logins = np.random.poisson(lam=15, size=n_users)  # average logins per month
support_tickets = np.random.poisson(lam=1.2, size=n_users)



churn_prob = np.ones(n_users) * 0.10  # Base churn probability


churn_prob += payment_failures * 0.40  

churn_prob += (logins < 5) * 0.35  

churn_prob -= (plans == "Enterprise") * 0.15  

churn_prob = np.clip(churn_prob, 0.01, 0.99)

churned = np.random.binomial(1, churn_prob)



subs_df = pd.DataFrame(
    {
        "user_id": user_ids,
        "plan_type": plans,
        "mrr": mrr,
        "payment_failures": payment_failures,
        "churned": churned,
    }
)

usage_df = pd.DataFrame(
    {
        "user_id": user_ids,
        "logins_last_30_days": logins,
        "support_tickets_opened": support_tickets,
    }
)


conn = sqlite3.connect("data/churn.db")
users_df.to_sql("users", conn, if_exists="replace", index=False)
subs_df.to_sql("subscriptions", conn, if_exists="replace", index=False)
usage_df.to_sql("usage_logs", conn, if_exists="replace", index=False)
conn.close()

print(
    "Database successfully created at data/churn.db with users, subscriptions,"
    " and usage_logs tables!"
)