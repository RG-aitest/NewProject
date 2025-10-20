import streamlit as st
import requests
import json
#from AIBot import agent  # for Direct mode
import os

# Load config
import json

if "input_box" not in st.session_state:
    st.session_state.input_box = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with open("config.json", "r") as f:
    config = json.load(f)

FRONTEND_MODE = config.get("FrontendMode", "API")
BACKEND_URL = config.get("BackendURL", "http://localhost:8000/ask")

st.set_page_config(page_title="IntelligentBot AI Agent", layout="centered")
st.title("🌊 IntelligentBot: Sustainability Agent")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask a question:", key="input_box")

if st.button("Send") or query:
    if query:
        with st.spinner("Thinking..."):
            if FRONTEND_MODE == "API":
                try:
                    resp = requests.post(BACKEND_URL, json={"query": query}, timeout=200)
                    answer = resp.json().get("answer", "No response from backend.")
                except Exception as e:
                    answer = f"API call failed: {e}"
            else:
                answer = agent.run(input=query)

        # Update history (keep last 3 interactions)
        st.session_state.history.append(("You", query))
        st.session_state.history.append(("Agent", answer))
        st.session_state.history = st.session_state.history[-6:]

        # Clear input box
#        st.session_state.input_box = ""

# Display chat history
for speaker, msg in st.session_state.history:
    if speaker == "You":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Agent:** {msg}")
