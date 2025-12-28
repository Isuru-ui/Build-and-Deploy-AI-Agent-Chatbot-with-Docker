import streamlit as st
import requests
import uuid

st.set_page_config(page_title="LangGraph Chatbot", layout="centered")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

API_URL = "http://127.0.0.1:8000/chat"

st.title("🤖 LangGraph AI Agent")
st.write("I will help you find any information.")

with st.sidebar:
    st.header("Settings")
    MODEL_NAMES = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
    selected_model = st.selectbox("Select Model:", MODEL_NAMES)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4()) 
        st.rerun()

given_system_prompt = "You are a helpful assistant with access to a Google Search tool via Tavily."

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
        "system_prompt": given_system_prompt,
        "thread_id": st.session_state.thread_id 
    }

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    response_data = response.json()
                    
                    ai_content = response_data.get("messages", [])[-1].get("content", "")
                    
                    if ai_content:
                        st.markdown(ai_content)
                        st.session_state.messages.append({"role": "assistant", "content": ai_content})
                    else:
                        st.warning("No AI response was received.")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"There is an error in the connection: {e}")