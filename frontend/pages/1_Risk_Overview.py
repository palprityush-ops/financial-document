import streamlit as st
import pandas as pd
from api.client import get_all_invoices

st.title("📊 Risk Command Center")
st.caption("Executive overview of financial risk intelligence signals.")

st.markdown("---")

data = get_all_invoices()

if "error" in data:
    st.error(f"API Error: {data['error']}")
    st.stop()

if not data:
    st.warning("No invoices found.")
    st.stop()

df = pd.DataFrame(data)

# -------------------
# Executive Metrics
# -------------------

total_invoices = len(df)
high_risk = len(df[df["risk_level"] == "high"])
medium_risk = len(df[df["risk_level"] == "medium"])
low_risk = len(df[df["risk_level"] == "low"])
avg_risk_score = round(df["risk_score"].mean(), 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Invoices", total_invoices)
col2.metric("High Risk", high_risk)
col3.metric("Average Risk Score", avg_risk_score)
col4.metric("Medium Risk", medium_risk)

st.markdown("---")

# -------------------
# Risk Distribution
# -------------------

st.subheader("Risk Distribution")

risk_counts = df["risk_level"].value_counts()

st.bar_chart(risk_counts)
