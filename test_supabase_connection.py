import os
from dotenv import load_dotenv
from supabase import create_client
import json

# Load environment variables
load_dotenv()

print("=== Testing Supabase Connection ===")
print()

# Check environment variables
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
projects_table = os.environ.get("PROJECTS_TABLE", "projects")

print("Environment Variables:")
print(f"SUPABASE_URL: {'✓ Set' if supabase_url else '✗ Not set'}")
print(f"SUPABASE_KEY: {'✓ Set' if supabase_key else '✗ Not set'}")
print(f"PROJECTS_TABLE: {projects_table}")
print()

if not supabase_url or not supabase_key:
    print("❌ ERROR: Missing Supabase credentials!")
    print()
    print("Please create a .env file in the project root with:")
    print("SUPABASE_URL=your_supabase_project_url")
    print("SUPABASE_KEY=your_supabase_anon_key")
    print("PROJECTS_TABLE=projects")
    exit(1)

try:
    # Try to connect to Supabase
    print("Attempting to connect to Supabase...")
    client = create_client(supabase_url, supabase_key)
    print("✓ Connection successful!")
    print()
    
    # Try to fetch data from projects table
    print(f"Fetching data from '{projects_table}' table...")
    result = client.table(projects_table).select('*').execute()
    
    if result.data:
        print(f"✓ Found {len(result.data)} projects!")
        print()
        print("First 3 projects:")
        for i, project in enumerate(result.data[:3]):
            print(f"\nProject {i+1}:")
            for key, value in project.items():
                print(f"  {key}: {value}")
    else:
        print("⚠ No projects found in the table")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===") 