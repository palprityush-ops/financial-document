import streamlit as st
from api.client import get_all_invoices

st.title("🔎 Invoice Intelligence Detail")

if "selected_invoice" not in st.session_state:
    st.warning("No invoice selected.")
    st.stop()

invoice_id = st.session_state["selected_invoice"]

st.markdown(f"### Invoice ID: {invoice_id}")

# Later we will fetch by ID
st.write("Detailed risk breakdown will appear here.")
