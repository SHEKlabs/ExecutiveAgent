# main.py
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import gsheets
import chatbot

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    
    # For now, we’ll only use the "Projects" data from Google Sheets
    projects = sheets.get_projects()  # returns a list or summary string
    
    # Build a prompt for the LLM
    prompt = f"User asked: {user_input}\n\nHere are the current projects from my Google Sheets:\n{projects}\n\nPlease provide a helpful response."
    
    # You can choose model 'gpt-4' if you have access, otherwise 'gpt-3.5-turbo'
    response = chatbot.get_response(prompt, model="gpt-3.5-turbo")
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
