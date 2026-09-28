import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

print("Loading data for machine learning pipeline...")

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
df = pd.read_sql(query, conn)
conn.close()

df["signup_date"] = pd.to_datetime(df["signup_date"])
ref_date = pd.to_datetime("2026-01-01")
df["tenure_days"] = (ref_date - df["signup_date"]).dt.days
df["tenure_days"] = df["tenure_days"].apply(lambda x: max(x, 1))
df["support_ticket_ratio"] = df["support_tickets_opened"] / df["tenure_days"]
df["engagement_score"] = df["logins_last_30_days"] - (df["payment_failures"] * 5)

# 3. Define Target (y) and Features (X)
y = df["churned"]
X = df.drop(columns=["user_id", "signup_date", "churned"])

# Convert categorical text columns (like plan_type and acquisition_channel) into numbers
X = pd.get_dummies(X, drop_first=True)

print(f"Dataset prepared with {X.shape[1]} features for training.")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Training XGBoost Classifier...")
model = XGBClassifier(random_state=42, eval_metric="logloss")
model.fit(X_train, y_train)

y_pred_proba = model.predict_proba(X_test)[:, 1]
auc_score = roc_auc_score(y_test, y_pred_proba)

print(f"\n--- Model Results ---")
print(f"Test Set ROC-AUC Score: {auc_score:.4f}")