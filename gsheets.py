# gsheets.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheets_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(credentials)
    return client

def get_projects():
    try:
        client = get_google_sheets_client()
        sheet_id = os.getenv("SHEET_ID")
        sheet = client.open_by_key(sheet_id)
        # Assume "Projects" is the title of the tab
        projects_tab = sheet.worksheet("Projects")
        projects_data = projects_tab.get_all_records()
        
        # Format the data as a string summary
        if not projects_data:
            return "No projects found."
        
        summary = ""
        for idx, project in enumerate(projects_data, 1):
            summary += f"{idx}. {project.get('Project Name', 'Unnamed Project')} - {project.get('Status', 'No status')}\n"
        
        return summary
    except Exception as e:
        return f"Error retrieving projects: {e}"
