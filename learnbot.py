import streamlit as st
import requests
import threading
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyBpO2gLWWCPasnY2mpoWK0359Zfb-P4kY0")

app = Flask(__name__, static_folder="frontend/dist", static_url_path="/")
CORS(app)

class LearnBot:
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        self.scores = {}
    
    def ask_gemini(self, prompt, mode):
        if mode == "simple":
            instruction = f"Explain '{prompt}' in a fun and easy way for children with examples."
        elif mode == "advanced":
            instruction = f"Provide an in-depth explanation of '{prompt}' with real-world applications."
        else:
            instruction = f"You are LearnBot, an educational assistant give easy answers and explain them in points. Explain: {prompt}"
        response = self.model.generate_content(instruction)
        return response.text
    
    def generate_quiz(self, topic):
        quiz_prompt = f"Create a multiple-choice quiz question based on this topic: {topic}. Give four options and indicate the correct one."
        return self.model.generate_content(quiz_prompt).text
    
    def generate_feedback(self, user_answer, correct_answer):
        feedback_prompt = f"Provide constructive feedback for a user who answered '{user_answer}' instead of the correct answer '{correct_answer}'. Be encouraging and explain why the correct answer is better."
        return self.model.generate_content(feedback_prompt).text

learnbot = LearnBot()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    mode = data.get("mode", "normal")
    
    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = learnbot.ask_gemini(message, mode)
    return jsonify({"reply": response})

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route("/scoreboard", methods=["GET"])
def get_scores():
    return jsonify(learnbot.scores)

@app.route("/update_score", methods=["POST"])
def update_score():
    data = request.json
    user = data.get("user", "Guest")
    score = data.get("score", 0)
    learnbot.scores[user] = learnbot.scores.get(user, 0) + score
    return jsonify({"message": "Score updated successfully!", "scores": learnbot.scores})

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()

st.set_page_config(page_title="LearnBot AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.sidebar.image("https://source.unsplash.com/200x200/?robot,ai", use_column_width=True)
st.sidebar.title("🤖 LearnBot AI")
st.sidebar.markdown("### Your AI-powered personalized learning assistant!")
st.sidebar.markdown("---")

scoreboard = requests.get("http://localhost:5000/scoreboard").json()
for user, score in scoreboard.items():
    st.sidebar.text(f"{user}: {score} pts")

st.sidebar.markdown("---")
st.sidebar.text_area("💬 Leave your feedback:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

st.title("🚀 LearnBot AI Chat")
st.markdown("### An interactive AI-powered assistant for learning concepts effortlessly.")

message = st.text_area("Enter your query:", height=100, placeholder="Type your question here...")
mode = st.radio("Select explanation mode:", ["normal", "simple", "advanced"], horizontal=True)
submit_button = st.button("💡 Ask LearnBot")

if submit_button:
    if message:
        with st.spinner("🤖 Generating response..."):
            response = requests.post("http://localhost:5000/chat", json={"message": message, "mode": mode})
            if response.status_code == 200:
                st.success("✅ Response Generated!")
                answer = response.json()["reply"]
                st.write(answer)
                
                st.markdown("---")
                st.subheader("🎯 Quick Quiz!")
                quiz_question = learnbot.generate_quiz(message)
                st.markdown(quiz_question)
                
                user_answer = st.text_input("Your Answer:")
                if st.button("Submit Answer"):
                    correct_answer = "(Assume correct answer from generated quiz)"  # Needs to be extracted from quiz_question
                    feedback = learnbot.generate_feedback(user_answer, correct_answer)
                    st.success("✅ Answer submitted!")
                    st.write("📝 Feedback:", feedback)
                    requests.post("http://localhost:5000/update_score", json={"user": "Guest", "score": 10})
                    st.experimental_rerun()
            else:
                st.error("❌ Error: " + response.json().get("error", "Unknown error"))
    else:
        st.warning("⚠️ Please enter a query before submitting.")

st.markdown("---")
st.markdown("© 2025 LearnBot AI | Built with Streamlit and Flask. AI can make mistakes, please verify the information.")
st.markdown("By YashwanthDS")
