import streamlit as st
import requests
import os

# Assuming FastAPI is running on localhost:8000
API_URL = os.getenv("API_URL", "http://localhost:8000") # Use environment variable for API URL

st.set_page_config(page_title="Airline Support AI", page_icon="✈️")

st.title("✈️ AI-Powered Airline Customer Support")
st.markdown("Welcome to the AI-powered support system. Ask about flight status, baggage policies, or general information.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = requests.post(f"{API_URL}/chat", json={"query": prompt})
            if response.status_code == 200:
                answer = response.json().get("response", "No response received.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}\nEnsure the FastAPI server is running at {API_URL}/")
