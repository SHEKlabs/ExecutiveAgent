# ExecutiveAgent

ExecutiveAgent is a personal executive assistant application that helps users manage their projects through a web interface. It provides features for creating, viewing, updating, and deleting projects, as well as filtering and searching capabilities.

## Project Structure

```
ExecutiveAgent/
├── src/                    # Main Python code
│   ├── ExecAgent_MAIN.py   # Main Flask application
│   ├── database.py         # Database connection and operations
│   └── project.py          # Project-related functions
├── tests/                  # Test scripts
│   └── test_project.py     # Tests for project functionality
├── supabase/               # Supabase configuration
│   └── supabase_client.py  # Supabase client configuration
├── webapp/                 # Web interface files
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styles
│   └── app.js              # JavaScript for UI interactions
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for web development)
- Supabase account with a configured project

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd ExecutiveAgent
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure Supabase:
   - Ensure your Supabase project is set up with a 'projects' table
   - Verify that the credentials in `supabase/supabase_client.py` are correct

## Running the Application

1. Start the Python backend:
   ```
   python src/ExecAgent_MAIN.py
   ```

2. Open the web interface:
   - Navigate to the `webapp` directory
   - Open `index.html` in a web browser
   - Alternatively, use a simple HTTP server:
     ```
     cd webapp
     python -m http.server 8000
     ```
   - Then open `http://localhost:8000` in your browser

## Testing

Run the tests using pytest:
```
pytest tests/
```

## Features

- View all projects in a list
- Filter projects by category, tag, or owner
- Search projects by name or description
- Add new projects
- View detailed information about a project
- Delete projects

## Future Enhancements

- User authentication
- Project task management
- Calendar integration
- AI-powered project recommendations
- Email notifications
