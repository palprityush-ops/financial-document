import streamlit as st
import pandas as pd
from api.client import get_all_invoices

st.title("Risk Overview")
st.caption("Executive summary of financial document risk exposure.")

st.markdown("---")

response = get_all_invoices()

if "error" in response:
    st.error(response["error"])
    st.stop()

data = response.get("data", [])

if not data:
    st.warning("No invoices available.")
    st.stop()

df = pd.DataFrame(data)

# -------------------------
# Executive Metrics
# -------------------------

total = len(df)
high = len(df[df["risk"] == "high"])
medium = len(df[df["risk"] == "medium"])
low = len(df[df["risk"] == "low"])

high_exposure = round((high / total) * 100, 2) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Invoices", total)
col2.metric("High Risk Invoices", high)
col3.metric("High Risk Exposure %", f"{high_exposure}%")
col4.metric("Average Confidence", round(df["confidence"].mean(), 2))

st.markdown("---")

# -------------------------
# Risk Distribution Chart
# -------------------------

st.subheader("Risk Distribution")

risk_counts = df["risk"].value_counts()
st.bar_chart(risk_counts)

st.markdown("---")

# -------------------------
# Recommended Review Panel
# -------------------------

st.subheader("Recommended Review")

if high > 0:
    st.error(f"{high} invoices require immediate review.")
elif medium > 0:
    st.warning(f"{medium} invoices require monitoring.")
else:
    st.success("No high-risk invoices detected.")