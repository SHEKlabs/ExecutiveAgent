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
    
    # Get match mode (default: match all criteria)
    match_all = request.args.get('match_all', 'true').lower() != 'false'
    
    # Build filters dictionary
    if category:
        filters['category'] = [cat.strip() for cat in category.split(',')]
    if owner:
        filters['owner'] = [own.strip() for own in owner.split(',')]
    if tags:
        filters['tags'] = [tag.strip() for tag in tags.split(',')]
    if contributors:
        filters['contributors'] = [contributor.strip() for contributor in contributors.split(',')]
    
    # Use the filter_projects method if we have any filters
    if filters:
        projects = project_manager.filter_projects(filters, match_all=match_all)
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

    # Check for general search queries
    search_keywords = ['search', 'find', 'look for', 'projects with', 'containing', 'related to']
    is_search_query = any(keyword in lower_message for keyword in search_keywords)
    
    if is_search_query:
        # Try to extract a search term
        search_term = None
        
        # First check for quoted terms
        import re
        quoted_terms = re.findall(r'"([^"]*)"', user_message)
        if quoted_terms:
            search_term = quoted_terms[0]
        else:
            # Otherwise extract words after search keywords
            for keyword in search_keywords:
                if keyword in lower_message:
                    # Find the position of the keyword
                    start_pos = lower_message.find(keyword) + len(keyword)
                    rest = lower_message[start_pos:].strip()
                    
                    # Take the first few words as the search term
                    words = rest.split()[:3]
                    if words:
                        search_term = ' '.join(words)
                    break
        
        if search_term:
            print(f"DEBUG: Extracted search term: {search_term}")
            # Use the text search method
            projects = project_manager.search_projects_by_text(search_term)
            formatted_projects = project_manager.format_projects_for_chat(projects)
            
            return jsonify({
                "response": f"Here are projects matching '{search_term}':",
                "projects": projects,
                "formatted_projects": formatted_projects
            })

    # Check for owner-specific searches
    known_owners = ['Abhishek', 'Abhishek Raol', 'John', 'John Doe']
    for owner in known_owners:
        if owner in user_message:
            print(f"DEBUG: Detected owner name in message: {owner}")
            # Special handling for owner queries
            projects = project_manager.get_projects_by_owner([owner])
            formatted_projects = project_manager.format_projects_for_chat(projects)
            
            return jsonify({
                "response": f"Here are projects owned by {owner}:",
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
    
    # Check if the user wants to match any or all filters
    match_all = True  # Default to matching all criteria
    if any(phrase in lower_message for phrase in ['any of', 'either', 'or', 'match any']):
        match_all = False
        print("DEBUG: User requested to match ANY criteria")
    
    # Check if the message is asking for projects with specific filters
    if filters:
        print(f"DEBUG: Handling message with filters: {filters}")
        # Get projects matching the filters
        projects = project_manager.filter_projects(filters, match_all=match_all)
        
        # Format projects for chat display
        formatted_projects = project_manager.format_projects_for_chat(projects)
        
        print(f"DEBUG: Found {len(projects)} projects matching filters")
        
        # Prepare a response that mentions what filters were applied
        filter_desc = []
        if 'owner' in filters:
            owner_val = filters['owner']
            if isinstance(owner_val, list):
                filter_desc.append(f"owner(s): {', '.join(owner_val)}")
            else:
                filter_desc.append(f"owner: {owner_val}")
                
        if 'tags' in filters:
            tags_val = filters['tags']
            if isinstance(tags_val, list):
                filter_desc.append(f"tag(s): {', '.join(tags_val)}")
            else:
                filter_desc.append(f"tag: {tags_val}")
                
        if 'category' in filters:
            cat_val = filters['category']
            if isinstance(cat_val, list):
                filter_desc.append(f"category/section: {', '.join(cat_val)}")
            else:
                filter_desc.append(f"category/section: {cat_val}")
                
        if 'contributors' in filters:
            contrib_val = filters['contributors']
            if isinstance(contrib_val, list):
                filter_desc.append(f"contributor(s): {', '.join(contrib_val)}")
            else:
                filter_desc.append(f"contributor: {contrib_val}")
        
        filter_description = ", ".join(filter_desc)
        match_type = "any of" if not match_all else "all of"
        response_msg = f"Here are the projects matching {match_type} your criteria ({filter_description}):"
        
        return jsonify({
            "response": response_msg,
            "projects": projects,
            "formatted_projects": formatted_projects,
            "filters_applied": filters,
            "match_all": match_all
        })
    
    # Extract filter criteria using Chatbot's method as a fallback
    chatbot_filters = chatbot.extract_filter_criteria(user_message)
    if chatbot_filters and chatbot_filters != filters:
        print(f"DEBUG: Using chatbot filters: {chatbot_filters}")
        # Get projects matching the filters
        projects = project_manager.filter_projects(chatbot_filters, match_all=match_all)
        
        # Format projects for chat display
        formatted_projects = project_manager.format_projects_for_chat(projects)
        
        print(f"DEBUG: Found {len(projects)} projects matching chatbot filters")
        
        # Prepare a response that mentions what filters were applied
        filter_desc = []
        if 'owner' in chatbot_filters:
            owner_val = chatbot_filters['owner']
            if isinstance(owner_val, list):
                filter_desc.append(f"owner(s): {', '.join(owner_val)}")
            else:
                filter_desc.append(f"owner: {owner_val}")
                
        if 'tags' in chatbot_filters:
            tags_val = chatbot_filters['tags']
            if isinstance(tags_val, list):
                filter_desc.append(f"tag(s): {', '.join(tags_val)}")
            else:
                filter_desc.append(f"tag: {tags_val}")
                
        if 'category' in chatbot_filters:
            cat_val = chatbot_filters['category']
            if isinstance(cat_val, list):
                filter_desc.append(f"category/section: {', '.join(cat_val)}")
            else:
                filter_desc.append(f"category/section: {cat_val}")
                
        if 'contributors' in chatbot_filters:
            contrib_val = chatbot_filters['contributors']
            if isinstance(contrib_val, list):
                filter_desc.append(f"contributor(s): {', '.join(contrib_val)}")
            else:
                filter_desc.append(f"contributor: {contrib_val}")
        
        filter_description = ", ".join(filter_desc)
        match_type = "any of" if not match_all else "all of"
        response_msg = f"Here are the projects matching {match_type} your criteria ({filter_description}):"
        
        return jsonify({
            "response": response_msg,
            "projects": projects,
            "formatted_projects": formatted_projects,
            "filters_applied": chatbot_filters,
            "match_all": match_all
        })
    
    # If this seems like a search query but we didn't find specific filters,
    # try a general text search with the main words from the query
    if is_search_query:
        # Extract the most significant words from the query
        import re
        # Remove common words and punctuation
        cleaned_text = re.sub(r'[^\w\s]', ' ', lower_message)
        words = cleaned_text.split()
        
        # Remove common stop words
        stop_words = ['search', 'find', 'for', 'the', 'and', 'with', 'projects', 'project', 'show', 'me', 'list', 'get', 'about']
        search_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        if search_words:
            search_term = ' '.join(search_words[:3])  # Use up to 3 words
            print(f"DEBUG: Using general text search with term: {search_term}")
            
            # Use the text search method
            projects = project_manager.search_projects_by_text(search_term)
            formatted_projects = project_manager.format_projects_for_chat(projects)
            
            return jsonify({
                "response": f"Here are projects related to '{search_term}':",
                "projects": projects,
                "formatted_projects": formatted_projects
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