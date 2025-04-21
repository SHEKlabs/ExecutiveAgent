# ExecutiveAgent
An Executive Assistant with a LLM interface that accesses the users calendar and google sheets to manage the users daily tasks, their projects and schedule. Will eventually work with other users ExecutiveAgents for scheduling and project management. 

# When I push the code to the repo, .gitignore doesn't include everything. Files not pushed (see below, unless .gitignore is pused also, then look at that) 

#Mose importantly, .env is not pushed. ANd will need to be setup when you run this code on a local server, or set it up for another user. This is what it looks like:
# .env file
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_SHEETS_CREDENTIALS=path/to/your/credentials.json #This comes from the google authentication stuff, generating a key then JSON key file I think. 
NOTION_TOKEN=your_notion_integration_token  # for future use
SHEET_ID=your_google_sheet_id_here 

#### GITHUB COMMITS!!!!!!!!!! ################
######### PUSHING STUFF TO GITHUB FROM IDE (for reference when you push your code changes)
# Initialize a new Git repository (if you haven't already)
git init

# OR.... Verify you're in the correct repository directory:
pwd 

# Check the current branch:
git status

# This should show you're on the framework_supabase branch. If not, switch to it with:
git checkout framework_supabase     (Or whatever branch you want to be on...)

# Check what files have been changed, again:
git status

# Add all files to Git
git add .

# Exclude sensitive files (if u need to)
echo ".env" >> .gitignore
echo "credentials/*" >> .gitignore
echo "__pycache__/" >> .gitignore

# Create your first commit
git commit -m "Your commit message describing the changes"

# Push to the framework_supabase branch. There are 3 different ways:
#1:
git push origin framework_supabase
#2: If you need to replace all code completely (force push)
    # Be careful with force push as it will overwrite remote history:
git push -f origin framework_supabase
#3: Push to the framework_supabase branch with upstream tracking (This differs from -f push. The -u flag sets up
    # tracking between local and remote branches):It should say "Your branch is up to date with 'origin framework_supabase'."
    # (Same for both -u and -f)
    # BENEFIT OF -u: For future pushes, you can now simply use: git push
git push -u origin framework_supabase

# Verify the push was successful:
git status

### This was another method from earlier... ?
# Link to your GitHub repository (replace with your repo URL) --- not sure what this is???
git remote add origin https://github.com/yourusername/ExecutiveAgent.git

# Push your code to GitHub
git push -u origin main
And if you wanna push to the fresh_langchain branch, you use:
git push -u origin fresh_langchain
###############

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

