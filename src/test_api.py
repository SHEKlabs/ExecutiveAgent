import json
from ExecAgent_MAIN import app
import urllib.parse

def test_api_endpoints():
    """
    Test the API endpoints with the correct table name and field names
    """
    # Create a test client
    client = app.test_client()
    
    print("1. Testing GET /projects (all projects)")
    response = client.get('/projects')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Success! Retrieved {len(data)} projects")
    else:
        print(f"Failed with status code: {response.status_code}")
    
    print("\n2. Testing GET /projects?category=AI - Agent")
    # URL encode the category parameter
    category = urllib.parse.quote("AI - Agent")
    response = client.get(f'/projects?category={category}')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Success! Retrieved {len(data)} projects with category 'AI - Agent'")
        for project in data:
            print(f"- {project['Project']}")
    else:
        print(f"Failed with status code: {response.status_code}")
        print(f"Error: {response.data.decode('utf-8')}")
    
    print("\n3. Testing GET /projects?tag=%23AI")  # %23 is URL encoded #
    response = client.get('/projects?tag=%23AI')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Success! Retrieved {len(data)} projects with tag '#AI'")
        for project in data:
            print(f"- {project['Project']}")
    else:
        print(f"Failed with status code: {response.status_code}")
        print(f"Error: {response.data.decode('utf-8')}")
    
    print("\n4. Testing GET /projects/9 (Executive Agent)")
    response = client.get('/projects/9')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Success! Retrieved project with ID 9:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Failed with status code: {response.status_code}")
    
    print("\n5. Testing GET /projects?owner=Abhishek Raol")
    # URL encode the owner parameter
    owner = urllib.parse.quote("Abhishek Raol")
    response = client.get(f'/projects?owner={owner}')
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"Success! Retrieved {len(data)} projects owned by 'Abhishek Raol'")
    else:
        print(f"Failed with status code: {response.status_code}")

if __name__ == "__main__":
    test_api_endpoints() 