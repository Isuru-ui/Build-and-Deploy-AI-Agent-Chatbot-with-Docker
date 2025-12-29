import streamlit as st
import requests
import uuid
import time

st.set_page_config(page_title="LangGraph Chatbot", layout="centered")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

API_URL = "http://localhost:8000/chat"

st.title("🤖 LangGraph AI Agent")
st.write("I will help you find any information.")

with st.sidebar:
    st.header("Settings")
    MODEL_NAMES = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
    selected_model = st.selectbox("Select Model:", MODEL_NAMES)
    
    user_prompt = st.text_area(
        "Define your AI Agent:", 
        placeholder="You are a helpful assistant with access to Google Search.",
        height=150
    )
    
    system_prompt = user_prompt if user_prompt else "You are a helpful assistant with access to Google Search via Tavily."

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "messages": [prompt], 
        "model_name": selected_model, 
        "system_prompt": system_prompt,
        "thread_id": st.session_state.thread_id 
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=60)
                if response.status_code == 200:
                    res_data = response.json()
                    ai_msg = res_data.get("messages", [])[-1].get("content", "")
                    if ai_msg:
                        st.markdown(ai_msg)
                        st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                else:
                    st.error(f"Backend Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error("The backend is not ready yet. Please try again in a few seconds.")