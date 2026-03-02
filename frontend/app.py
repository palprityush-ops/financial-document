import streamlit as st
from utils.theme import apply_dark_theme

st.set_page_config(
    page_title="Evidentia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_dark_theme()

st.sidebar.markdown(
    """
    <h2 style='margin-bottom:0;'>EVIDENTIA</h2>
    <p style='color:gray; font-size:14px;'>
    Financial Risk Intelligence System
    </p>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Rule-Based Risk Intelligence Engine\n\n" "Transparent • Explainable • Auditable"
)

st.title(" Risk Command Center")
st.caption("Executive overview of financial risk exposure.")

st.markdown("---")
st.write("Use the sidebar to navigate.")
