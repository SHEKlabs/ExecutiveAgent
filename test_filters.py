import sys
import os
import json

# Add the current directory to sys.path to make imports work
sys.path.append(os.path.abspath('.'))

from src.project import ProjectManager

def test_filter_functionality():
    # Initialize the project manager
    project_manager = ProjectManager()
    
    print("\n===== TESTING MULTIPLE-VALUE FILTER FUNCTIONALITY =====")
    
    # First, get all projects to see what data we have to work with
    print("\n----- Getting all projects for reference -----")
    all_projects = project_manager.get_all_projects()
    print(f"Found {len(all_projects)} total projects")
    
    # Print a sample of the projects to see the structure
    if all_projects and len(all_projects) > 0:
        # Print sample of all projects to examine the data structure
        print("\nAll projects (brief overview):")
        for i, project in enumerate(all_projects):
            print(f"{i+1}. Title: {project.get('Project')}")
            print(f"   Categories: {project.get('Category/Section')}")
            print(f"   Tags: {project.get('Tag')}")
            print(f"   Owner: {project.get('Owner')}")
            print()
        
        # Extract real values from the data for better testing
        categories = set()
        tags = set()
        owners = set()
        
        for p in all_projects:
            if p.get('Category/Section'):
                if isinstance(p.get('Category/Section'), list):
                    categories.update(p.get('Category/Section', []))
                else:
                    categories.add(p.get('Category/Section'))
                    
            if p.get('Tag'):
                if isinstance(p.get('Tag'), list):
                    tags.update(p.get('Tag', []))
                else:
                    tags.add(p.get('Tag'))
                    
            if p.get('Owner'):
                owners.add(p.get('Owner'))
        
        print("\nAvailable categories:", list(categories))
        print("Available tags:", list(tags))
        print("Available owners:", list(owners))
        
        # Select filter values based on real data to ensure matches
        # Look for categories that appear in the actual data
        project_categories = {}
        for p in all_projects:
            if p.get('Category/Section') and isinstance(p.get('Category/Section'), list):
                for cat in p.get('Category/Section'):
                    if cat not in project_categories:
                        project_categories[cat] = []
                    project_categories[cat].append(p.get('Project'))
        
        print("\nCategories and projects that contain them:")
        for cat, projects in project_categories.items():
            print(f"{cat}: {projects}")
        
        # Create test values from real data - select values that actually exist in projects
        test_categories = list(project_categories.keys())[:2] if len(project_categories) >= 2 else list(project_categories.keys())
        
        # Get tags that actually exist in projects
        project_tags = {}
        for p in all_projects:
            if p.get('Tag') and isinstance(p.get('Tag'), list):
                for tag in p.get('Tag'):
                    if tag not in project_tags:
                        project_tags[tag] = []
                    project_tags[tag].append(p.get('Project'))
        
        print("\nTags and projects that contain them:")
        for tag, projects in project_tags.items():
            print(f"{tag}: {projects}")
        
        test_tags = list(project_tags.keys())[:2] if len(project_tags) >= 2 else list(project_tags.keys())
        test_owners = list(owners)[:2] if len(owners) >= 2 else list(owners)
    else:
        # Fallback test values if no projects exist
        test_categories = ["AI - Agent", "#Labs"]
        test_tags = ["#code", "#finance"]
        test_owners = ["Abhishek Raol", "John Doe"]
    
    # Test 1: Get projects by multiple categories
    print("\n1. Testing multiple categories:")
    print(f"   Searching for categories: {test_categories}")
    projects = project_manager.get_projects_by_category(test_categories)
    print(f"   Found {len(projects)} projects with categories {test_categories}")
    for i, project in enumerate(projects):
        if i < 5:  # Limit output to 5 projects
            print(f"   - {project.get('Project')} (Categories: {project.get('Category/Section')})")
        else:
            print(f"   ... and {len(projects) - 5} more projects")
            break
    
    # Test 2: Get projects by multiple tags
    print("\n2. Testing multiple tags:")
    print(f"   Searching for tags: {test_tags}")
    projects = project_manager.get_projects_by_tag(test_tags)
    print(f"   Found {len(projects)} projects with any of these tags: {test_tags}")
    for i, project in enumerate(projects):
        if i < 5:  # Limit output to 5 projects
            print(f"   - {project.get('Project')} (Tags: {project.get('Tag')})")
        else:
            print(f"   ... and {len(projects) - 5} more projects")
            break
    
    # Test 3: Get projects by multiple owners
    print("\n3. Testing multiple owners:")
    print(f"   Searching for owners: {test_owners}")
    projects = project_manager.get_projects_by_owner(test_owners)
    print(f"   Found {len(projects)} projects with owners: {test_owners}")
    for i, project in enumerate(projects):
        if i < 5:  # Limit output to 5 projects
            print(f"   - {project.get('Project')} (Owner: {project.get('Owner')})")
        else:
            print(f"   ... and {len(projects) - 5} more projects")
            break
    
    # Test 4: Combined filtering
    print("\n4. Testing combined filtering:")
    filter_criteria = {
        'category': test_categories,
        'tags': test_tags,
        'owner': test_owners
    }
    print(f"   Combined criteria: {json.dumps(filter_criteria, indent=2)}")
    projects = project_manager.filter_projects(filter_criteria)
    print(f"   Found {len(projects)} projects matching combined criteria")
    for i, project in enumerate(projects):
        if i < 5:  # Limit output to 5 projects
            print(f"   - {project.get('Project')}")
            print(f"     Categories: {project.get('Category/Section')}")
            print(f"     Tags: {project.get('Tag')}")
            print(f"     Owner: {project.get('Owner')}")
        else:
            print(f"   ... and {len(projects) - 5} more projects")
            break
    
    # Test 5: Filter by a single category (backward compatibility)
    if test_categories:
        print("\n5. Testing single category (backward compatibility):")
        single_category = test_categories[0]
        print(f"   Searching for category: {single_category}")
        projects = project_manager.get_projects_by_category(single_category)
        print(f"   Found {len(projects)} projects with category: {single_category}")
        for i, project in enumerate(projects):
            if i < 5:  # Limit output to 5 projects
                print(f"   - {project.get('Project')} (Categories: {project.get('Category/Section')})")
            else:
                print(f"   ... and {len(projects) - 5} more projects")
                break

    # Test 6: Custom combined filtering
    print("\n6. Custom test - Specific values from data:")
    # Pick filter values directly from what we see in the data
    specific_filter = {
        'category': ['AI - Agent', '#Labs'],  # From the first project
        'tags': ['#code', '#finance'],        # From the first project
        'owner': ['Abhishek Raol']            # Common owner
    }
    print(f"   Custom criteria: {json.dumps(specific_filter, indent=2)}")
    projects = project_manager.filter_projects(specific_filter)
    print(f"   Found {len(projects)} projects matching custom criteria")
    for i, project in enumerate(projects):
        if i < 5:  # Limit output to 5 projects
            print(f"   - {project.get('Project')}")
            print(f"     Categories: {project.get('Category/Section')}")
            print(f"     Tags: {project.get('Tag')}")
            print(f"     Owner: {project.get('Owner')}")
        else:
            print(f"   ... and {len(projects) - 5} more projects")
            break

if __name__ == "__main__":
    test_filter_functionality() 