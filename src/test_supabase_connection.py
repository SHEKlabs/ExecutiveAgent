import json
from database import SupabaseClient

def test_retrieve_projects():
    """
    Test function to retrieve and display data from the PM - Projects - AR table
    """
    # Create a database client instance
    db_client = SupabaseClient()
    
    # Set the specific table name
    table_name = 'PM - Projects - AR'
    
    # Retrieve all data from the table
    print(f"Retrieving all projects from '{table_name}'...")
    result = db_client.get_data(table_name)
    
    # Check if data was successfully retrieved
    if result and hasattr(result, 'data'):
        # Format and print the data
        formatted_data = json.dumps(result.data, indent=2)
        print(f"Retrieved {len(result.data)} projects:")
        print(formatted_data)
        return True
    else:
        print("Failed to retrieve data or no data available")
        return False

if __name__ == "__main__":
    test_retrieve_projects() 