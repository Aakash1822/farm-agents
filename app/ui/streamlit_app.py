import streamlit as st
import requests
import uuid

API_BASE = st.session_state.get("api_base", "http://localhost:8000")

st.title("Kisan Saarthi — Farmer Assistant")

st.markdown("Enter your OpenAI API key to use your own quota (optional). Leave blank to use server/mock responses.")
api_key = st.text_input("OpenAI API Key", type="password")

user_id = st.text_input("User ID", value=st.session_state.get("user_id", "farmer1"))
session_id = st.text_input("Session ID", value=st.session_state.get("session_id", str(uuid.uuid4())))

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_area("Ask your question", height=120)

if st.button("Send") and query.strip():
    payload = {
        "query": query,
        "user_id": user_id,
        "session_id": session_id,
        "language": "hi",
    }
    if api_key:
        payload["api_key"] = api_key

    try:
        resp = requests.post(f"{API_BASE}/api/v1/ask", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        assistant = data.get("response")
    except Exception as e:
        assistant = f"Error: {e}"

    st.session_state.history.append({"role": "user", "message": query})
    st.session_state.history.append({"role": "assistant", "message": assistant})

for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['message']}")
    else:
        st.markdown(f"**Assistant:** {msg['message']}")

st.markdown("---")
st.markdown("Powered by Kisan Saarthi. For production, run the backend and optionally provide OpenAI keys.")
