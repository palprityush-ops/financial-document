import streamlit as st
import pandas as pd
from api.client import get_all_invoices

st.title("Invoice Explorer")
st.caption("Search, filter and inspect processed invoices.")

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
# Executive Summary Row
# -------------------------

total = len(df)
high = len(df[df["risk"] == "high"])
medium = len(df[df["risk"] == "medium"])
low = len(df[df["risk"] == "low"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total)
col2.metric("High", high)
col3.metric("Medium", medium)
col4.metric("Low", low)

st.markdown("---")

# -------------------------
# Filters
# -------------------------

col1, col2 = st.columns(2)

with col1:
    risk_filter = st.selectbox(
        "Filter by Risk Level",
        ["All", "low", "medium", "high"]
    )

with col2:
    search_query = st.text_input("Search by Bill Number or File")

# Apply risk filter
if risk_filter != "All":
    df = df[df["risk"] == risk_filter]

# Apply search
if search_query:
    df = df[
        df.apply(
            lambda row: search_query.lower() in str(row).lower(),
            axis=1
        )
    ]

st.markdown("---")

# -------------------------
# Clean Table Display
# -------------------------

st.subheader("Invoice Records")

display_columns = [
    "source_file",
    "bill_number",
    "invoice_date",
    "grand_total",
    "confidence",
    "risk",
]

df_display = df[display_columns]

def highlight_risk(val):
    if val == "high":
        return "background-color: #DC2626; color: white;"
    elif val == "medium":
        return "background-color: #F59E0B; color: black;"
    elif val == "low":
        return "background-color: #16A34A; color: white;"
    return ""

styled_df = df_display.style.applymap(
    highlight_risk,
    subset=["risk"]
)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=400
)

st.markdown("---")

# -------------------------
# Select for Detail
# -------------------------

st.subheader("Inspect Invoice")

selected_bill = st.selectbox(
    "Select Bill Number",
    df["bill_number"].tolist()
)

if st.button("View Invoice Detail"):
    st.session_state["selected_invoice"] = selected_bill
    st.switch_page("pages/3_Invoice_Detail.py")