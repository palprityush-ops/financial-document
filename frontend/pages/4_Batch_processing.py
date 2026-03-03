import streamlit as st
from api.client import upload_invoice, run_batch

st.title("Batch Processing")
st.caption("Operational control panel for invoice ingestion and risk analysis.")

st.markdown("---")

# -----------------------------
# Upload Section
# -----------------------------

st.subheader("Upload Single Invoice")

uploaded_file = st.file_uploader("Upload invoice file", type=["pdf", "json", "xml"])

if uploaded_file is not None:
    if st.button("Process Invoice"):
        with st.spinner("Processing invoice..."):
            result = upload_invoice(uploaded_file)
        
        if "error" in result:
            st.error(f"Upload Error: {result['error']}")
        else:
            st.success("Invoice processed successfully.")
            st.json(result)

st.markdown("---")

# -----------------------------
# Batch Processing Section
# -----------------------------

st.subheader("Run Batch Analysis")

st.write("Trigger risk analysis for all pending invoices.")

if st.button("Run Batch Processing"):
    with st.spinner("Running batch analysis..."):
        batch_result = run_batch()
    
    if "error" in batch_result:
        st.error(f"Batch Error: {batch_result['error']}")
    else:
        st.success("Batch processing completed.")
        st.json(batch_result)