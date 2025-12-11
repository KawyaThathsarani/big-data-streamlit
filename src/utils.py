import streamlit as st


def custom_style():
    """Add custom CSS for UI improvement"""
    st.markdown("""
    <style>
        .main { background-color: #faf5ff; }
        h1, h2, h3 { color: #5a189a; }
    </style>
    """, unsafe_allow_html=True)
