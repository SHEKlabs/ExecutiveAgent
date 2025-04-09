# ExecutiveAgent

ExecutiveAgent is a personal executive assistant application that helps users manage their projects through a web interface. It provides features for creating, viewing, updating, and deleting projects, as well as filtering and searching capabilities, and now includes a natural language chatbot interface.

## Project Structure

```
ExecutiveAgent/
├── src/                    # Main Python code
│   ├── ExecAgent_MAIN.py   # Main Flask application
│   ├── database.py         # Database connection and operations
│   ├── project.py          # Project-related functions
│   └── chatbot.py          # AI chatbot integration
├── tests/                  # Test scripts
│   ├── test_project.py     # Tests for project functionality
│   └── test_chatbot.py     # Tests for chatbot functionality
├── supabase/               # Supabase configuration
│   └── supabase_client.py  # Supabase client configuration
├── webapp/                 # Web interface files
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styles
│   └── app.js              # JavaScript for UI interactions
├── .env.example            # Template for environment variables
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for web development)
- Supabase account with a configured project
- OpenAI API key for chatbot functionality

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

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Configure Supabase:
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
- Chat with an AI assistant to help manage projects
- Use natural language to search and filter projects
- Get project data formatted in a readable format

## Using the Chatbot

The chatbot interface allows you to interact with your projects using natural language. You can:

- Ask to see all projects
- Filter projects using natural language (e.g., "Show me AI projects owned by Abhishek")
- Get project information in a clean format
- Ask general questions about project management

Example queries:
- "Show all projects"
- "Find projects with tag #AI"
- "What projects are owned by Abhishek?"
- "Show me projects in the Labs category"

## Future Enhancements

- User authentication
- Project task management
- Calendar integration
- AI-powered project recommendations
- Email notifications
- Enhanced chatbot capabilities with task automation
- Voice interface for the chatbot

# Create a .env file with your Supabase credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

4. Run the application
```bash
cd src
python -m flask run
```

## Usage

### Project List

- View all projects in the main interface
- Use the search box to find projects by name or description
- Click on the Filter dropdown to filter by category, tag, or owner
- Add multiple filter values and choose between matching all or any criteria

### Using the Chat Assistant

The Project Assistant chatbot supports natural language queries like:
- "Show all projects"
- "Find projects with tag #AI"
- "Show projects owned by Abhishek"
- "Find projects with tags #Foundation or #code"
- "Show me projects in the AI category with tags #Agent"

## Architecture

- **Backend**: Python Flask API
- **Database**: Supabase
- **Frontend**: HTML/CSS/JavaScript with Bootstrap

## Development

The codebase is organized into several key components:

- `src/ExecAgent_MAIN.py`: Main Flask application with API endpoints
- `src/project.py`: Project management and filter logic
- `src/chatbot.py`: Natural language processing for the chat interface
- `src/database.py`: Database connection and query operations
- `webapp/`: Frontend code (HTML, CSS, JavaScript)
