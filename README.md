# ExecutiveAgent
An Executive Assistant with a LLM interface that accesses the users calendar and google sheets to manage the users daily tasks, their projects and schedule. Will eventually work with other users ExecutiveAgents for scheduling and project management. 

# When I push the code to the repo, .gitignore doesn't include everything. Files not pushed (see below, unless .gitignore is pused also, then look at that) 

#Mose importantly, .env is not pushed. ANd will need to be setup when you run this code on a local server, or set it up for another user. This is what it looks like:
# .env file
OPENAI_API_KEY=your_openai_api_key_here
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

