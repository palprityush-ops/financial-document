import streamlit as st
from api.client import get_invoice_by_id

st.title("Invoice Detail")
st.caption("Detailed risk assessment and explainable rule breakdown.")

st.markdown("---")

# ----------------------------
# Check Session State
# ----------------------------

if "selected_invoice" not in st.session_state:
    st.warning("No invoice selected from Explorer.")
    st.stop()

invoice_id = st.session_state["selected_invoice"]

data = get_invoice_by_id(invoice_id)

if "error" in data:
    st.error(f"API Error: {data['error']}")
    st.stop()

# ----------------------------
# Risk Header Section (Dominant)
# ----------------------------

risk_score = data.get("risk_score", 0)
risk_level = data.get("risk_level", "unknown")
confidence = data.get("confidence_score", "N/A")

# Risk color logic
if risk_level == "high":
    risk_color = "#DC2626"  # red
elif risk_level == "medium":
    risk_color = "#F59E0B"  # amber
else:
    risk_color = "#16A34A"  # green

st.markdown(
    f"""
    <div style="
        background-color:#111827;
        padding:30px;
        border-radius:12px;
        margin-bottom:25px;">
        
        <h1 style="margin:0; font-size:42px; color:{risk_color};">
            {risk_score}
        </h1>
        
        <p style="margin:5px 0; font-size:18px;">
            Risk Level: <b>{risk_level.upper()}</b>
        </p>
        
        <p style="margin:0; color:gray;">
            Confidence Score: {confidence}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Risk Triggers Section
# ----------------------------

st.subheader("Risk Triggers")

risk_reasons = data.get("risk_reasons", [])

if risk_reasons:
    for reason in risk_reasons:
        st.markdown(
            f"""
            <div style="
                border-left:4px solid {risk_color};
                background-color:#1F2937;
                padding:14px;
                border-radius:8px;
                margin-bottom:12px;">
                
                <b>{reason.get('rule')}</b><br>
                Contribution: +{reason.get('impact')} points
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No rule triggers recorded.")

st.markdown("---")

# ----------------------------
# Extracted Invoice Information
# ----------------------------

st.subheader("Extracted Invoice Information")

excluded_fields = ["risk_reasons"]

display_data = {
    k: v for k, v in data.items() if k not in excluded_fields
}

col1, col2 = st.columns(2)

items = list(display_data.items())

for i, (key, value) in enumerate(items):
    label = key.replace("_", " ").title()
    
    if i % 2 == 0:
        col1.write(f"**{label}**")
        col1.write(value)
    else:
        col2.write(f"**{label}**")
        col2.write(value)