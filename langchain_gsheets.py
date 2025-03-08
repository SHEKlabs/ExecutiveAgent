# langchain_gsheets.py
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain.tools import Tool
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Try to import FAISS with a fallback mechanism
try:
    from langchain_community.vectorstores import FAISS
    FAISS_AVAILABLE = True
except ImportError:
    print("FAISS not available, will use simple search instead")
    FAISS_AVAILABLE = False
from pydantic import BaseModel, Field

class GoogleSheetsConnector:
    def __init__(self):
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.sheet_id = os.getenv("SHEET_ID")
        self.client = self._get_google_sheets_client()
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.documents = []

    def _get_google_sheets_client(self):
        print("Google Sheets credentials path:", self.creds_path)
        print("File exists?", os.path.exists(self.creds_path))
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.creds_path, self.scope)
        return gspread.authorize(credentials)

    def load_projects_as_documents(self):
        """Load the projects sheet as langchain documents"""
        try:
            # Use gspread directly since GoogleSheetsLoader is unavailable
            sheet = self.client.open_by_key(self.sheet_id)
            projects_tab = sheet.worksheet("Projects")
            
            # Get all values including headers
            all_values = projects_tab.get_all_values()
            
            if not all_values or len(all_values) <= 1:  # Check if we only have headers or no data
                print("No data found in Projects sheet")
                return []
                
            # Convert to documents
            headers = all_values[0]
            documents = []
            
            for i, row in enumerate(all_values[1:], start=2):  # Start from index 2 for row numbers
                # Create a dictionary representation of the row
                row_dict = dict(zip(headers, row))
                
                # Create a formatted string representation of the row data
                content = f"Row {i}:\n"
                for header, value in row_dict.items():
                    content += f"{header}: {value}\n"
                
                # Create a Document object
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": f"Google Sheets - {self.sheet_id}",
                        "worksheet": "Projects",
                        "row": i
                    }
                )
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"Error loading documents from Google Sheets: {e}")
            return []

    def create_vector_store(self):
        """Create a vector store from the Google Sheets data"""
        documents = self.load_projects_as_documents()
        
        if not documents:
            print("No documents found to create vector store")
            return None
        
        # Split documents if they're too large
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
        splits = text_splitter.split_documents(documents)
        
        if FAISS_AVAILABLE:
            # Create vector store with FAISS
            try:
                self.vector_store = FAISS.from_documents(splits, self.embeddings)
                print("Vector store created successfully with FAISS")
                return self.vector_store
            except Exception as e:
                print(f"Error creating FAISS vector store: {e}")
                print("Falling back to simple document store")
        else:
            print("FAISS not available, using simple document store instead")
        
        # Fallback: just store the documents directly
        self.documents = splits
        return None

    def get_projects_raw(self, query=None):
        """
        Get raw project data as a formatted string.
        
        Args:
            query: Optional query parameter (ignored but required for LangChain tool compatibility)
        
        Returns:
            Formatted string with project data
        """
        try:
            sheet = self.client.open_by_key(self.sheet_id)
            projects_tab = sheet.worksheet("Projects")
            
            # Retrieve all values including header row
            all_values = projects_tab.get_all_values()
            
            if not all_values:
                return "No projects found."
            
            # First row as header (column names)
            header = all_values[0]
            # Remaining rows as data
            data_rows = all_values[1:]
            
            # Format the output in a more readable way for humans
            output = "# Projects List\n\n"
            
            # Add a table of projects
            for i, row in enumerate(data_rows, start=1):
                row_dict = dict(zip(header, row))
                output += f"## {i}. {row_dict.get('Project', f'Project {i}')}\n"
                output += f"- **Category:** {row_dict.get('Category/Section', 'N/A')}\n"
                output += f"- **Owner:** {row_dict.get('Owner', 'N/A')}\n"
                output += f"- **Tags:** {row_dict.get('Tag', 'N/A')}\n"
                if row_dict.get('Connected Project'):
                    output += f"- **Connected Project:** {row_dict.get('Connected Project')}\n"
                output += "\n"
            
            return output
        except Exception as e:
            return f"Error retrieving projects: {e}"

    def get_projects_tool(self):
        """Create a LangChain tool for accessing projects data"""
        return Tool(
            name="GetProjects",
            func=self.get_projects_raw,
            description="Retrieves project data from Google Sheets. Use this tool when you need information about projects or when asked to show all projects."
        )

    def search_projects(self, query, k=3):
        """
        Search for project information based on a query
        
        Args:
            query: Search query text
            k: Number of results to return (default: 3)
            
        Returns:
            Formatted string with search results
        """
        # Try to use vector store if available
        if FAISS_AVAILABLE and not hasattr(self, 'vector_store') or not self.vector_store:
            self.create_vector_store()
            
        if FAISS_AVAILABLE and hasattr(self, 'vector_store') and self.vector_store:
            # Vector search with FAISS
            docs = self.vector_store.similarity_search(query, k=k)
            results = [doc.page_content for doc in docs]
            return "\n\n".join(results)
        else:
            # Fallback to simple keyword search if FAISS is not available
            if not hasattr(self, 'documents') or not self.documents:
                documents = self.load_projects_as_documents()
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=100,
                )
                self.documents = text_splitter.split_documents(documents)
            
            if not self.documents:
                return "No project data available to search."
            
            # Simple keyword matching
            matches = []
            query_terms = query.lower().split()
            
            for doc in self.documents:
                score = 0
                content = doc.page_content.lower()
                for term in query_terms:
                    if term in content:
                        score += 1
                
                if score > 0:
                    matches.append((doc, score))
            
            # Sort by score and take top k
            matches.sort(key=lambda x: x[1], reverse=True)
            top_matches = matches[:k] if len(matches) >= k else matches
            
            results = [match[0].page_content for match in top_matches]
            
            if not results:
                return f"No matching projects found for query: {query}"
                
            return "\n\n".join(results)

    def search_projects_tool(self):
        """Create a LangChain tool for searching projects"""
        return Tool(
            name="SearchProjects",
            func=self.search_projects,
            description="Search for specific project information. Input should be a detailed query about what project information you're looking for."
        )