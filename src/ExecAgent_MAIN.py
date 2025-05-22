# MAIN.py
from dotenv import load_dotenv
load_dotenv()  # Load env variables immediately

import os
import sys

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates.execAgent_promptLibrary import get_prompt
print("Loaded GOOGLE_SHEETS_CREDENTIALS:", os.environ.get("GOOGLE_SHEETS_CREDENTIALS"))

# Use relative imports when running as a module
try:
    from . import gsheets
    from . import chatbot
except ImportError:
    import gsheets
    import chatbot

from flask import Flask, render_template, request, jsonify

# Set the template folder explicitly
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

def test_projects_data():
    # Retrieve projects data from Google Sheets and print it for testing purposes.
    projects_data = gsheets.get_projects()
    print("Test: Retrieved projects data:")
    print(projects_data)
    return projects_data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    
    # Retrieve and print projects data for testing.
    projects = test_projects_data()
    
    # Use our prompt library to generate the full prompt.
    full_prompt = get_prompt("show_projects", user_query=user_input, projects=projects)
    
    # Get response from OpenAI using GPT-4.
    response = chatbot.get_response(full_prompt, model="gpt-4")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
