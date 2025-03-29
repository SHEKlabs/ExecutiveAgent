from flask import Flask, request, jsonify
from project import ProjectManager
import json
from chatbot import Chatbot
import asyncio

app = Flask(__name__)
project_manager = ProjectManager()
chatbot = Chatbot()

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
    return response

# Routes for project operations
@app.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects or filter by query parameters"""
    filters = {}
    
    # Get all filter parameters
    category = request.args.get('category')
    owner = request.args.get('owner')
    tags = request.args.get('tags')
    contributors = request.args.get('contributors')
    
    # Build filters dictionary
    if category:
        filters['category'] = category
    if owner:
        filters['owner'] = owner
    if tags:
        filters['tags'] = [tag.strip() for tag in tags.split(',')]
    if contributors:
        filters['contributors'] = [contributor.strip() for contributor in contributors.split(',')]
    
    # Use the filter_projects method if we have any filters
    if filters:
        projects = project_manager.filter_projects(filters)
    else:
        projects = project_manager.get_all_projects()
    
    return jsonify(projects)

@app.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a specific project by ID"""
    project = project_manager.get_project_by_id(project_id)
    if project:
        return jsonify(project)
    return jsonify({"error": "Project not found"}), 404

@app.route('/projects', methods=['POST'])
def add_project():
    """Add a new project"""
    project_data = request.json
    if not project_data:
        return jsonify({"error": "Invalid project data"}), 400
    
    result = project_manager.add_project(project_data)
    return jsonify(result), 201

@app.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update an existing project"""
    updated_data = request.json
    if not updated_data:
        return jsonify({"error": "Invalid project data"}), 400
    
    project = project_manager.get_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    result = project_manager.update_project(project_id, updated_data)
    return jsonify(result)

@app.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    project = project_manager.get_project_by_id(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    result = project_manager.delete_project(project_id)
    return jsonify({"message": "Project deleted successfully"})

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat interactions with the AI assistant
    
    This endpoint processes messages from the user, extracts filter criteria,
    and returns appropriate responses including formatted project data.
    """
    # Get the message from the request
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message parameter"}), 400
    
    user_message = data.get('message')
    print(f"DEBUG: Received chat message: {user_message}")
    
    # Check for common project queries that we can handle directly without AI
    lower_message = user_message.lower()
    
    # Check if user is asking for all projects
    if any(phrase in lower_message for phrase in ['show all projects', 'list all projects', 'get all projects']):
        print("DEBUG: Handling 'show all projects' request")
        # Get all projects
        projects = project_manager.get_all_projects()
        formatted_projects = project_manager.format_projects_for_chat(projects)
        
        return jsonify({
            "response": "Here are all projects:",
            "projects": projects,
            "formatted_projects": formatted_projects
        })
    
    # Check for hashtags in the message (special handling for tag-based queries)
    if '#' in lower_message:
        print("DEBUG: Detected hashtag in message, special handling")
        hashtags = []
        for word in lower_message.split():
            if word.startswith('#'):
                hashtags.append(word)
            elif '#' in word:
                hashtag_part = word[word.find('#'):]
                hashtags.append(hashtag_part)
        
        if hashtags:
            print(f"DEBUG: Found hashtags: {hashtags}")
            # Get projects with these tags
            filters = {'tags': hashtags}
            projects = project_manager.filter_projects(filters)
            formatted_projects = project_manager.format_projects_for_chat(projects)
            
            return jsonify({
                "response": f"Here are projects with tag(s) {', '.join(hashtags)}:",
                "projects": projects,
                "formatted_projects": formatted_projects
            })
    
    # Extract filter criteria from the message using ProjectManager's method
    filters = project_manager.extract_filters_from_text(user_message)
    
    # Check if the message is asking for projects with specific filters
    if filters:
        print(f"DEBUG: Handling message with filters: {filters}")
        # Get projects matching the filters
        projects = project_manager.filter_projects(filters)
        
        # Format projects for chat display
        formatted_projects = project_manager.format_projects_for_chat(projects)
        
        print(f"DEBUG: Found {len(projects)} projects matching filters")
        
        return jsonify({
            "response": "Here are the projects matching your criteria:",
            "projects": projects,
            "formatted_projects": formatted_projects,
            "filters_applied": filters
        })
    
    # Extract filter criteria using Chatbot's method as a fallback
    chatbot_filters = chatbot.extract_filter_criteria(user_message)
    if chatbot_filters and chatbot_filters != filters:
        print(f"DEBUG: Using chatbot filters: {chatbot_filters}")
        # Get projects matching the filters
        projects = project_manager.filter_projects(chatbot_filters)
        
        # Format projects for chat display
        formatted_projects = project_manager.format_projects_for_chat(projects)
        
        print(f"DEBUG: Found {len(projects)} projects matching chatbot filters")
        
        return jsonify({
            "response": "Here are the projects matching your criteria:",
            "projects": projects,
            "formatted_projects": formatted_projects,
            "filters_applied": chatbot_filters
        })
    
    # If no filters were found or it's a different type of query,
    # pass it to the chatbot for processing
    try:
        print("DEBUG: No filters found, passing to chatbot")
        # Create event loop for async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Process message with chatbot
        bot_response = loop.run_until_complete(chatbot.process_message(user_message))
        
        return jsonify({
            "response": bot_response
        })
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return jsonify({
            "error": error_msg
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 