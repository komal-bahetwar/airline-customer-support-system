import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Airline Customer Support",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI-Powered Airline Customer Support")

st.write("Ask any airline-related question.")

question = st.text_input("Enter your question")

if st.button("Test Backend"):
    try:
        response = requests.get(f"{BACKEND_URL}/")

        if response.status_code == 200:
            st.json(response.json())
        else:
            st.error("Backend error")
    except Exception as e:
        st.error(f"Cannot connect to backend.\n{e}")