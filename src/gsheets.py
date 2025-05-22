# gsheets.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheets_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    print("Google Sheets credentials path:", creds_path)
    print("File exists?", os.path.exists(creds_path))
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(credentials)
    return client

def get_projects():
    try:
        client = get_google_sheets_client()
        sheet_id = os.getenv("SHEET_ID")
        sheet = client.open_by_key(sheet_id)
        # Access the "Projects" worksheet/tab
        projects_tab = sheet.worksheet("Projects")
        
        # Retrieve all values including header row
        all_values = projects_tab.get_all_values()
        
        if not all_values:
            return "No projects found."
        
        # First row as header (column names)
        header = all_values[0]
        # Remaining rows as data
        data_rows = all_values[1:]
        
        # Build an output string with entire raw data and column names
        output = "Entire Raw Data:\n"
        for idx, row in enumerate(all_values, start=1):
            output += f"{idx}. {row}\n"
            
        output += "\nColumn Names:\n" + ", ".join(header)
        
        return output
    except Exception as e:
        return f"Error retrieving projects: {e}"
