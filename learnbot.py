import streamlit as st
import google.generativeai as genai

# Set your Gemini API key
genai.configure(api_key="AIzaSyBpO2gLWWCPasnY2mpoWK0359Zfb-P4kY0")

# Load model
model = genai.GenerativeModel('gemini-pro')

# App Title
st.set_page_config(page_title="LearnBot", layout="centered")
st.title("🤖 LearnBot - Your AI Tutor")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Simple mode toggle
mode = st.checkbox("Enable Simple Mode")

# User input
user_input = st.text_input("Ask me anything:")

if user_input:
    # Save user message
    st.session_state.messages.append(("You", user_input))

    # Construct prompt
    if mode:
        prompt = f"Explain '{user_input}' in the easiest way possible. Use simple words and examples. Avoid complications."
    else:
        prompt = user_input

    # Get Gemini response
    try:
        response = model.generate_content(prompt)
        bot_reply = response.text.strip()
    except Exception as e:
        bot_reply = f"❌ Error: {str(e)}"

    # Save bot reply
    st.session_state.messages.append(("LearnBot", bot_reply))

# Display chat history
for sender, message in st.session_state.messages:
    if sender == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 LearnBot:** {message}")
