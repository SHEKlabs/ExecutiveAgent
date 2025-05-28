Updated: May 28, 2025, 4:45 PM, Pacific Standard Time

# ExecutiveAgent

## Instructions: How to Clone, Push, and Set Up the Codebase

### 1. Cloning the Repository from GitHub

1. Open your terminal.
2. Navigate to the directory where you want to store the project (e.g., `cd ~/CODE/`).
3. Run:
   ```bash
   git clone https://github.com/SHEKlabs/ExecutiveAgent.git
   cd ExecutiveAgent
   ```

### 2. Pushing Your Code to GitHub

1. Make sure you are in the `ExecutiveAgent` directory.
2. Check the status of your changes:
   ```bash
   git status
   ```
3. Add all changes:
   ```bash
   git add .
   ```
4. Commit your changes:
   ```bash
   git commit -m "Describe your changes here"
   ```
5. Pull the latest changes from the remote (to avoid conflicts):
   ```bash
   git pull origin main --rebase
   ```
6. Push your changes to GitHub:
   ```bash
   git push origin main
   ```

### 3. Setting Up and Running the Codebase (with Virtual Environment)

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up your `.env` file:**
   - Create a file named `.env` in the project root (same folder as `requirements.txt`).
   - Add your Supabase and OpenAI credentials. Example:
     ```env
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_anon_key
     PROJECTS_TABLE=Projects-Abhishek_Raol
     OPENAI_API_KEY=your_openai_api_key
     ```
   - **Note:** The `.env` file is never pushed to GitHub (see `.gitignore`).
4. **Run the web app:**
   ```bash
   python src/ExecAgent_MAIN.py
   ```
5. **Open your browser and go to:**
   [http://127.0.0.1:5001/](http://127.0.0.1:5001/)

---

# Features
- Executive Assistant chatbot with LLM interface
- Project list and details fetched from Supabase
- Modern web UI with chat and project management

# Codebase
An Executive Assistant with a LLM interface that accesses the users calendar and google sheets to manage the users daily tasks, their projects and schedule. Will eventually work with other users ExecutiveAgents for scheduling and project management. 

# When I push the code to the repo, .gitignore doesn't include everything. Files not pushed (see below, unless .gitignore is pused also, then look at that) 

#Mose importantly, .env is not pushed. ANd will need to be setup when you run this code on a local server, or set it up for another user. This is what it looks like:
# .env file
OPENAI_API_KEY=your_openai_api_key
GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json #This comes from the google authentication stuff, generating a key then JSON key file I think. 
NOTION_TOKEN=your_notion_integration_token  # for future use
SHEET_ID=your_google_sheet_id_here 


# .gitignore:

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environment directories
venv/
ENV/
env/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# IDE or Editor directories
.idea/
.vscode/

# Local environment variables file
.env

# Credentials folder (to protect sensitive JSON keys, etc.)
credentials/

