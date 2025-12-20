import streamlit as st
import requests
import uuid  # Thread ID එකක් සෑදීමට අවශ්‍ය වේ

st.set_page_config(page_title="LangGraph Agent UI", layout="centered")

# Docker හරහා run කරන විට localhost වෙනුවට 0.0.0.0 හෝ 127.0.0.1 පාවිච්චි කරන්න
API_URL = "http://127.0.0.1:8000/chat"

# --- Session State මඟින් Thread ID එක කළමනාකරණය ---
# මෙය වරක් සෑදූ පසු browser tab එක වසන තුරු වෙනස් නොවේ
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

st.title("LangGraph Chatbot Agent")
st.write(f"Thread ID: `{st.session_state.thread_id}`") # ID එක පෙන්වීමට (Optional)

# System Prompt එක code එක ඇතුළේම ලබා දීම (UI එකෙන් සැඟවීමට)
given_system_prompt = "You are a helpful assistant with access to a Google Search tool via Tavily. You MUST use the search tool to find the latest information. Do NOT answer from your own memory if the question is about current events or real-time data. Always search first, then answer."

MODEL_NAMES = [
    "llama-3.3-70b-versatile",  
    "mixtral-8x7b-32768"
]
selected_model = st.selectbox("Select Model:", MODEL_NAMES)

user_input = st.text_area("Enter your message(s):", height=150, placeholder="Type your message here...")

if st.button("Submit"):
    if user_input.strip():
        try:
            # Backend එක බලාපොරොත්තු වන නව Payload එක (thread_id සහිතව)
            payload = {
                "messages": [user_input], 
                "model_name": selected_model, 
                "system_prompt": given_system_prompt,
                "thread_id": st.session_state.thread_id # Session ID එක යැවීම
            }
            
            with st.spinner("Thinking..."):
                response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                # Backend එක දැන් එවන්නේ කෙලින්ම පිළිතුර (String එකක්) නිසා
                response_text = response.json()
                
                if isinstance(response_text, dict) and "error" in response_text:
                    st.error(response_text["error"])
                else:
                    st.subheader("Agent Response:")
                    st.markdown(response_text) # අවසාන පිළිතුර පෙන්වීම
            else:
                st.error(f"Request failed with status code {response.status_code}.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a message before clicking 'Submit'.")