# ExecAgent_MAIN.py
from dotenv import load_dotenv
load_dotenv()  # Load env variables immediately

import os
import sys

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from templates.execAgent_promptLibrary import get_prompt
print(f"Supabase URL: {os.environ.get('SUPABASE_URL')}")
print(f"Projects Table: {os.environ.get('PROJECTS_TABLE', 'projects')}")

# Use relative imports when running as a module
try:
    from . import database
    from . import chatbot
except ImportError:
    import database
    import chatbot

from flask import Flask, render_template, request, jsonify

# Set the template folder explicitly
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Supabase client
supabase_client = None
try:
    supabase_client = database.SupabaseClient()
    print("Supabase client initialized successfully in main")
except Exception as e:
    print(f"Error initializing Supabase client: {str(e)}")

def get_projects(filters=None):
    """Get projects from Supabase"""
    if supabase_client:
        return supabase_client.get_projects(filters)
    else:
        # Fallback to sample data if Supabase client not available
        return [
            {
                "name": "Executive Agent",
                "category": "AI Projects",
                "owner": "Abhishek",
                "tags": ["AI", "Agent", "Assistant"],
                "description": "A personal executive assistant powered by AI"
            },
            {
                "name": "Data Pipeline",
                "category": "Data Engineering",
                "owner": "Sarah",
                "tags": ["ETL", "Data", "Pipeline"],
                "description": "Data processing pipeline for analytics"
            }
        ]

@app.route("/")
def index():
    # Get all projects
    projects = get_projects()
    # Get Supabase information
    supabase_url = os.environ.get("SUPABASE_URL", "")
    projects_table = os.environ.get("PROJECTS_TABLE", "projects")
    # Extract project name from URL (e.g., https://xyz.supabase.co -> xyz)
    supabase_project = supabase_url.split("//")[1].split(".")[0] if supabase_url else ""
    return render_template("index.html", 
                         projects=projects,
                         supabase_table=projects_table,
                         supabase_project=supabase_project)

@app.route("/projects")
def get_projects_endpoint():
    """API endpoint to get projects"""
    projects = get_projects()
    return jsonify({"projects": projects})

@app.route("/projects/<project_name>", methods=["PUT"])
def update_project(project_name):
    """API endpoint to update a project"""
    try:
        # Get the updates from the request JSON
        updates = request.get_json()
        
        if not updates:
            return jsonify({"success": False, "error": "No updates provided"}), 400
        
        # Remove any id field to prevent updates
        if 'id' in updates:
            del updates['id']
        
        if supabase_client:
            result = supabase_client.update_project(project_name, updates)
            if result["success"]:
                return jsonify(result)
            else:
                return jsonify(result), 500
        else:
            return jsonify({"success": False, "error": "Database not available"}), 500
            
    except Exception as e:
        print(f"Error in update_project route: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    
    # Get projects for the chatbot context
    projects = get_projects()
    
    # Use our prompt library to generate the full prompt
    full_prompt = get_prompt("show_projects", user_query=user_input, projects=projects)
    
    # Get response from OpenAI
    response = chatbot.get_response(full_prompt, model="gpt-4")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
