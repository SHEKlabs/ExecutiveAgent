# gsheets.py
import os
import json
from dotenv import load_dotenv
import sys
import traceback
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

def get_google_sheets_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    print("Google Sheets credentials path:", creds_path)
    print("File exists?", os.path.exists(creds_path))
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(credentials)
    return client

def get_projects():
    """
    Retrieve projects data from Google Sheets.
    This is a simplified version for demonstration purposes.
    
    Returns:
        list: A list of project dictionaries, or an empty list if there's an error.
    """
    # Get credentials path from environment
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    print("Google Sheets credentials path:", creds_path)
    
    try:
        # This is a placeholder. In a real application, you would:
        # 1. Use credentials to authenticate with Google Sheets API
        # 2. Access a specific spreadsheet
        # 3. Read and process data
        
        # For now, return some sample data
        sample_projects = [
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
        
        return sample_projects
    
    except Exception as e:
        print(f"Error retrieving projects: {str(e)}")
        # Print the full traceback for debugging
        traceback.print_exc()
        return []
