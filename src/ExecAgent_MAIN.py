from flask import Flask, request, jsonify
from project import ProjectManager
import json

app = Flask(__name__)
project_manager = ProjectManager()

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
    category = request.args.get('category')
    tag = request.args.get('tag')
    owner = request.args.get('owner')
    
    if category:
        projects = project_manager.get_projects_by_category(category)
    elif tag:
        projects = project_manager.get_projects_by_tag(tag)
    elif owner:
        projects = project_manager.get_projects_by_owner(owner)
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

if __name__ == '__main__':
    app.run(debug=True, port=5000) 