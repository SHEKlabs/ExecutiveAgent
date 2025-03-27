from project import ProjectManager
import sys
import webbrowser
from urllib.parse import quote

def print_projects(projects):
    """Print projects in a readable format"""
    if not projects:
        print("\nNo projects found matching the criteria.")
        return
    
    print(f"\nFound {len(projects)} project(s):")
    print("-" * 80)
    for project in projects:
        print(f"ID: {project.get('id', 'N/A')}")
        print(f"Name: {project.get('name', 'N/A')}")
        print(f"Category: {project.get('category', 'N/A')}")
        print(f"Owner: {project.get('owner', 'N/A')}")
        print(f"Tags: {', '.join(project.get('tags', []))}")
        print(f"Contributors: {', '.join(project.get('contributors', []))}")
        print("-" * 80)

def get_filter_value(filter_type):
    """Get filter value from user input"""
    if filter_type in ['tags', 'category']:
        print(f"\nEnter {filter_type} (comma-separated):")
        value = input().strip()
        return [v.strip() for v in value.split(',') if v.strip()]
    else:
        print(f"\nEnter {filter_type}:")
        return input().strip()

def get_filter_url(filters):
    """Generate URL for filtered results"""
    base_url = "http://localhost:5001/projects"
    params = []
    
    if 'category' in filters:
        # Join categories with comma for the URL
        category_str = ','.join(filters['category'])
        params.append(f"category={quote(category_str)}")
    
    if 'owner' in filters:
        params.append(f"owner={quote(filters['owner'])}")
    
    if 'tags' in filters:
        # Join tags with comma for the URL
        tags_str = ','.join(filters['tags'])
        params.append(f"tags={quote(tags_str)}")
    
    if 'connected_project' in filters:
        # Join connected projects with comma for the URL
        connected_str = ','.join(filters['connected_project'])
        params.append(f"connected_project={quote(connected_str)}")
    
    if params:
        url = f"{base_url}?{'&'.join(params)}"
    else:
        url = base_url
    
    return url

def ask_to_open_browser(url):
    """Ask user if they want to open results in browser"""
    print(f"\nView these results in browser?")
    print(f"URL: {url}")
    choice = input("Open in browser? (y/n): ").strip().lower()
    if choice == 'y':
        webbrowser.open(url)
        print("Opened in browser!")
    else:
        print("Browser not opened.")

def get_filters():
    """Get multiple filters from user"""
    filters = {}
    
    while True:
        print("\nAdd Filter:")
        print("1. Category")
        print("2. Owner")
        print("3. Tags")
        print("4. Connected Project")
        print("5. Done adding filters")
        print("6. Cancel")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '5':
            break
        elif choice == '6':
            return None
        
        try:
            if choice == '1':
                value = get_filter_value('category')
                if value:
                    filters['category'] = value
            elif choice == '2':
                value = get_filter_value('owner')
                if value:
                    filters['owner'] = value
            elif choice == '3':
                values = get_filter_value('tags')
                if values:
                    filters['tags'] = values
            elif choice == '4':
                values = get_filter_value('connected_project')
                if values:
                    filters['connected_project'] = values
            else:
                print("\nInvalid choice. Please try again.")
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")
    
    return filters if filters else None

def main():
    project_manager = ProjectManager()
    
    while True:
        print("\nProject Filter Menu:")
        print("1. Add Multiple Filters")
        print("2. Show All Projects")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        try:
            if choice == '1':
                filters = get_filters()
                if filters:
                    projects = project_manager.filter_projects(filters)
                    url = get_filter_url(filters)
                    print_projects(projects)
                    ask_to_open_browser(url)
            elif choice == '2':
                projects = project_manager.get_all_projects()
                url = get_filter_url({})
                print_projects(projects)
                ask_to_open_browser(url)
            elif choice == '3':
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main() 