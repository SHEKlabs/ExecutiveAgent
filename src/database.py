import os
from supabase import create_client
import json
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        # Get Supabase credentials from environment variables
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        projects_table = os.environ.get("PROJECTS_TABLE", "projects")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")
        
        print(f"Initializing Supabase client with URL: {supabase_url}")
        # Create a new client instance
        self.client = create_client(supabase_url, supabase_key)
        self.projects_table = projects_table
        print("Supabase client initialized successfully")
        
        # Field mapping between database and frontend - Updated to match actual column names
        self.db_to_frontend = {
            "Project": "name",
            "Category/Section": "category",
            "Owner": "owner",
            "Tags": "tags",  # Changed from "Tag" to "Tags"
            "Connected Projects": "connected_project",  # Changed from "Connected Project"
            "Contributors": "contributors",
            "Description": "description"
        }
        
        self.frontend_to_db = {
            "name": "Project",
            "category": "Category/Section",
            "owner": "Owner",
            "tags": "Tags",  # Changed from "Tag" to "Tags"
            "connected_project": "Connected Projects",  # Changed from "Connected Project"
            "contributors": "Contributors",
            "description": "Description"
        }
    
    def get_projects(self, filters=None):
        """
        Get all projects from Supabase
        """
        try:
            print(f"Getting projects from table: {self.projects_table}")
            query = self.client.table(self.projects_table).select('*')
            
            if filters:
                for column, operator, value in filters:
                    query = query.filter(column, operator, value)
            
            result = query.execute()
            print(f"Raw result from Supabase: {result.data[:2] if result.data else 'No data'}")  # Print first 2 items for debugging
            
            if result.data:
                # Convert field names from DB to frontend format
                result.data = self.map_db_to_frontend(result.data)
                print(f"Mapped data: {result.data[:2] if result.data else 'No data'}")  # Print first 2 mapped items
            
            return result.data
        except Exception as e:
            print(f"Error fetching projects: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            traceback.print_exc()  # Print full traceback
            # Return sample data as fallback
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
    
    def map_db_to_frontend(self, data_list):
        """Map database field names to frontend field names"""
        if not data_list:
            return data_list
            
        result = []
        for item in data_list:
            new_item = {}
            # Keep id as is
            if 'id' in item:
                new_item['id'] = item['id']
                
            # Map other fields
            for db_field, frontend_field in self.db_to_frontend.items():
                if db_field in item:
                    new_item[frontend_field] = item[db_field]
            
            # Keep any other fields not in the mapping
            for key, value in item.items():
                if key not in self.db_to_frontend and key != 'id':
                    new_item[key] = value
                    
            result.append(new_item)
            
        return result
        
    def map_frontend_to_db(self, data):
        """Map frontend field names to database field names"""
        if not data:
            return data
            
        result = {}
        
        # Map fields
        for frontend_field, db_field in self.frontend_to_db.items():
            if frontend_field in data:
                result[db_field] = data[frontend_field]
        
        # Keep any other fields not in the mapping
        for key, value in data.items():
            if key not in self.frontend_to_db:
                result[key] = value
                
        return result 