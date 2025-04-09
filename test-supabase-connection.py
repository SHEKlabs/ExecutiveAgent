import sys
import os
import requests
import json

# Path setup to access the project modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

from database import SupabaseClient
from project import ProjectManager

def test_get_projects():
    """Test retrieving all projects"""
    project_manager = ProjectManager()
    projects = project_manager.get_all_projects()
    
    print(f"Retrieved {len(projects)} projects")
    
    # Print first project as sample
    if projects:
        print("\nSample project:")
        print(json.dumps(projects[0], indent=2))
    
    return projects

def test_update_description(project_id, new_description):
    """Test updating a project description"""
    project_manager = ProjectManager()
    
    # Get the project first to show before/after
    project_before = project_manager.get_project_by_id(project_id)
    
    print(f"\nProject before update:")
    print(f"ID: {project_before['id']}")
    print(f"Name: {project_before['name']}")
    print(f"Description: {project_before.get('description', 'No description')}")
    
    # Update the project
    result = project_manager.update_project(project_id, {"description": new_description})
    
    # Get the updated project
    project_after = project_manager.get_project_by_id(project_id)
    
    print(f"\nProject after update:")
    print(f"ID: {project_after['id']}")
    print(f"Name: {project_after['name']}")
    print(f"Description: {project_after.get('description', 'No description')}")
    
    return result

def test_api_update(project_id, new_description):
    """Test updating a project via the API"""
    url = f"http://localhost:5001/projects/{project_id}"
    headers = {"Content-Type": "application/json"}
    data = {"description": new_description}
    
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"\nAPI Update Response Status: {response.status_code}")
        print(f"API Update Response: {json.dumps(response.json(), indent=2)}")
        
        return response.json()
    except Exception as e:
        print(f"Error updating project via API: {str(e)}")
        return None

if __name__ == "__main__":
    # Get all projects
    projects = test_get_projects()
    
    if not projects:
        print("No projects found. Exiting.")
        sys.exit(1)
    
    # Get the first project ID
    first_project_id = projects[0]['id']
    
    # Test updating the description directly
    print("\n=== Testing Direct Update ===")
    test_update_description(first_project_id, "Updated description from test script")
    
    # Test updating via API
    print("\n=== Testing API Update ===")
    test_api_update(first_project_id, "Updated description from API test") 