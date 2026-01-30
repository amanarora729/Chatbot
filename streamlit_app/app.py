import streamlit as st
import requests
import uuid

# Backend API URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Humanli.ai Chatbot", layout="wide")

st.title("Humanli.ai - Website RAG Chatbot")
st.markdown("Enter a URL to crawl, then ask questions about its content.")

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for URL Input
with st.sidebar:
    st.header("1. Index Website")
    url_input = st.text_input("Enter Website URL", placeholder="https://example.com")
    if st.button("Crawl & Index"):
        if url_input:
            with st.spinner(f"Crawling {url_input}..."):
                try:
                    response = requests.post(f"{API_URL}/crawl", json={"url": url_input})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Success! {data['message']}")
                    else:
                        st.error(f"Error: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend. Is it running?")
        else:
            st.warning("Please enter a URL.")

# Chat Interface
st.header("2. Ask Questions")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about the website..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt,
                    "session_id": st.session_state.session_id
                }
                response = requests.post(f"{API_URL}/chat", json=payload)
                
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer received.")
                    st.markdown(answer)
                    # Add assistant message to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend.")
