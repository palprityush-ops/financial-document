# frontend/pages/2_Invoice_Explorer.py

import streamlit as st
import pandas as pd
from api.client import get_all_invoices

st.title("📁 Invoice Intelligence Explorer")
st.caption("Explore, filter, and inspect processed invoices.")

st.markdown("---")

data = get_all_invoices()

if "error" in data:
    st.error(f"API Error: {data['error']}")
    st.stop()

if not data:
    st.warning("No invoices found.")
    st.stop()

df = pd.DataFrame(data)

# -------------------------
# Filters Section
# -------------------------

col1, col2 = st.columns(2)

with col1:
    risk_filter = st.selectbox("Filter by Risk Level", ["All", "low", "medium", "high"])

with col2:
    search_query = st.text_input("Search by Invoice ID or Vendor")

# Apply Risk Filter
if risk_filter != "All":
    df = df[df["risk_level"] == risk_filter]

# Apply Search
if search_query:
    df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]

st.markdown("---")

# -------------------------
# Table Display
# -------------------------

st.subheader("Invoices")

st.dataframe(df[["invoice_id", "risk_score", "risk_level"]], use_container_width=True)

# -------------------------
# Select Invoice for Detail
# -------------------------

st.markdown("---")
st.subheader("Inspect Invoice")

selected_id = st.selectbox("Select Invoice ID", df["invoice_id"].tolist())

if st.button("View Details"):
    st.session_state["selected_invoice"] = selected_id
    st.switch_page("pages/3_Invoice_Detail.py")
