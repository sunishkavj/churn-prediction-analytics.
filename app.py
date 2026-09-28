import streamlit as st
import sqlite3
import pandas as pd


st.set_page_config(page_title="Churn Analytics Dashboard", layout="wide")
st.title("🔄 Customer Churn & Retention Dashboard")
st.markdown("Identify high-risk accounts and analyze revenue impact.")


@st.cache_data
def load_data():
    conn = sqlite3.connect("data/churn.db")
    query = """
    SELECT 
        u.user_id,
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
    return df

df = load_data()


total_users = len(df)
churn_rate = df['churned'].mean() * 100
total_mrr = df[df['churned'] == 0]['mrr'].sum()
mrr_lost = df[df['churned'] == 1]['mrr'].sum()


col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{total_users:,}")
col2.metric("Overall Churn Rate", f"{churn_rate:.1f}%")
col3.metric("Active MRR", f"${total_mrr:,.0f}")
col4.metric("MRR Lost to Churn", f"${mrr_lost:,.0f}")

st.divider()

st.subheader("🚨 High-Risk Customer Explorer")
st.write("Filter customers based on their usage behavior to identify retention targets.")

min_logins = st.slider("Max Logins in Last 30 Days (Low Engagement)", 0, 30, 5)
show_payment_failures = st.checkbox("Only show accounts with payment failures")


filtered_df = df[(df['logins_last_30_days'] <= min_logins) & (df['churned'] == 0)]
if show_payment_failures:
    filtered_df = filtered_df[filtered_df['payment_failures'] > 0]

st.dataframe(
    filtered_df[['user_id', 'plan_type', 'mrr', 'logins_last_30_days', 'payment_failures']], 
    use_container_width=True
)

st.caption(f"Showing {len(filtered_df)} at-risk active customers based on current filters.")