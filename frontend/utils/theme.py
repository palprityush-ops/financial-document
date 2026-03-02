import streamlit as st


def apply_dark_theme():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0E1117;
            color: white;
        }

        .block-container {
            padding-top: 2rem;
        }

        section[data-testid="stSidebar"] {
            background-color: #111827;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
