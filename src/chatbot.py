import os
import json
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Chatbot:
    """ChatBot class to handle conversations with OpenAI's models"""
    
    def __init__(self):
        """Initialize the chatbot with OpenAI configuration"""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize the OpenAI client
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Default model
        self.model = "gpt-4"
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Store the last filter criteria
        self.last_filter = None

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history
        
        Args:
            role (str): The role of the message sender (system, user, or assistant)
            content (str): The content of the message
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def clear_history(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
    
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message and generate a response
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The chatbot's response
        """
        # Add the user message to the conversation history
        self.add_message("user", user_message)
        
        try:
            # Create the messages for the API call
            messages = self.conversation_history.copy()
            
            # Add system message for context if it's not already there
            if not any(msg["role"] == "system" for msg in messages):
                system_message = {
                    "role": "system", 
                    "content": (
                        "You are a helpful project management assistant. "
                        "You can help users find, filter, and manage projects. "
                        "When users ask about projects, try to extract filter criteria "
                        "like category, owner, tags, or contributors. "
                        "Format project data as 'Column: Values' for easy reading."
                    )
                }
                messages.insert(0, system_message)
            
            # Call the OpenAI API with the new format
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract the assistant's message
            assistant_message = response.choices[0].message.content
            
            # Add the assistant's response to the conversation history
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            return error_message
    
    def extract_filter_criteria(self, user_message: str) -> Dict[str, Any]:
        """
        Extract filter criteria from a user message
        
        Args:
            user_message (str): The user's message
            
        Returns:
            Dict: Dictionary containing extracted filter criteria
        """
        # Define keywords for each filter type
        filter_keywords = {
            'category': ['category', 'section', 'type', 'kind', 'group'],
            'owner': ['owner', 'owned by', 'belongs to', 'assigned to', 'by'],
            'tags': ['tag', 'tags', 'labeled', 'labelled', 'marked as'],
            'contributors': ['contributor', 'contributors', 'worked on by', 'team']
        }
        
        # Initialize empty filters dictionary
        filters = {}
        
        # First, check for hashtags in the original message (preserve case)
        hashtags = []
        for word in user_message.split():
            word_lower = word.lower()
            
            # Special handling for common terms
            if word_lower in ['#ai', 'ai', '#artificial', 'artificial intelligence']:
                hashtags.append('#AI')
                continue
                
            if word_lower in ['#ml', 'ml', '#machine', 'machine learning']:
                hashtags.append('#ML')
                continue
            
            # Handle normal hashtags
            if '#' in word:
                # If it's a pure hashtag, keep it as is
                if word.startswith('#'):
                    hashtags.append(word)
                else:
                    # Extract the part starting with #
                    hashtag_part = word[word.find('#'):]
                    hashtags.append(hashtag_part)
        
        if hashtags:
            filters['tags'] = hashtags
        
        # Check for specific owners directly in the message
        common_owners = ['Abhishek', 'Abhishek Raol', 'John', 'John Doe']
        for owner in common_owners:
            if owner in user_message:
                filters['owner'] = owner
                print(f"DEBUG: Found specific owner in message: {owner}")
                break

        # Convert message to lowercase for easier matching of other filter types
        message_lower = user_message.lower()
        
        # Check for each filter type (except tags, as we've handled hashtags already)
        for filter_type, keywords in filter_keywords.items():
            if filter_type == 'tags' and 'tags' in filters:
                # Skip tag extraction if we already found hashtags
                continue
                
            if filter_type == 'owner' and 'owner' in filters:
                # Skip owner extraction if we already found a specific owner
                continue
                
            for keyword in keywords:
                if keyword in message_lower:
                    # Find the position of the keyword
                    start_pos = message_lower.find(keyword)
                    # Extract the text after the keyword
                    after_keyword = message_lower[start_pos + len(keyword):].strip()
                    # Find the next filter keyword or end of string
                    next_keyword_pos = len(after_keyword)
                    for next_keyword in [k for f in filter_keywords.values() for k in f]:
                        pos = after_keyword.find(next_keyword)
                        if pos > 0 and pos < next_keyword_pos:
                            next_keyword_pos = pos
                    
                    # Extract the value for this filter
                    value = after_keyword[:next_keyword_pos].strip()
                    
                    # Clean up the value (remove punctuation, etc.)
                    value = value.strip(".,;: ")
                    
                    # Add to filters if value is not empty
                    if value:
                        if filter_type == 'tags':
                            # Special handling for tags
                            tag_words = value.split()
                            tag_values = []
                            
                            for word in tag_words:
                                if word.startswith('#'):
                                    tag_values.append(word)
                                elif '#' in word:
                                    # Extract the part starting with #
                                    hashtag_part = word[word.find('#'):]
                                    tag_values.append(hashtag_part)
                                else:
                                    tag_values.append(word)
                            
                            if tag_values:
                                filters['tags'] = tag_values
                            elif ',' in value or ' and ' in value:
                                # For list types, split by commas or 'and'
                                values = [v.strip() for v in value.replace(' and ', ',').split(',')]
                                filters['tags'] = values
                        elif filter_type == 'owner':
                            # Special handling for owner
                            # Check for known owners in the value
                            owner_found = False
                            for known_owner in common_owners:
                                if known_owner.lower() in value.lower() or value.lower() in known_owner.lower():
                                    filters['owner'] = known_owner
                                    owner_found = True
                                    break
                            
                            # If no known owner found, use the extracted value
                            if not owner_found:
                                if ',' in value or ' and ' in value:
                                    # For multiple owners, split by commas or 'and'
                                    values = [v.strip() for v in value.replace(' and ', ',').split(',')]
                                    filters['owner'] = values
                                else:
                                    filters['owner'] = value
                        elif filter_type in ['contributors']:
                            # For list types, split by commas or 'and'
                            values = [v.strip() for v in value.replace(' and ', ',').split(',')]
                            filters[filter_type] = values
                        else:
                            filters[filter_type] = value
                    
                    break
        
        # Special case handling for common tag terms without hashtags
        if 'tags' not in filters:
            common_tags = {
                'ai': '#AI',
                'artificial intelligence': '#AI',
                'ml': '#ML',
                'machine learning': '#ML',
                'agent': '#Agent',
                'code': '#code',
                'finance': '#finance',
                'labs': '#Labs'
            }
            
            for term, tag in common_tags.items():
                if term in message_lower:
                    if 'tags' not in filters:
                        filters['tags'] = []
                    filters['tags'].append(tag)
        
        # Store the extracted filters for future reference
        self.last_filter = filters if filters else self.last_filter
        
        print(f"DEBUG: Extracted filters from chatbot: {filters}")
        return filters
    
    def format_project_data(self, projects: List[Dict[str, Any]]) -> str:
        """
        Format project data for display in chat interface
        
        Args:
            projects (List[Dict]): List of project dictionaries
            
        Returns:
            str: Formatted project data as a string
        """
        if not projects:
            return "No projects found matching your criteria."
        
        formatted_output = []
        
        # Field display names (more user-friendly)
        field_display_names = {
            "name": "Name",
            "description": "Description",
            "category": "Category",
            "owner": "Owner",
            "tags": "Tags",
            "contributors": "Contributors",
            "connected_project": "Connected Project"
        }
        
        # Field display order (for consistent output)
        field_order = ["name", "description", "category", "owner", "tags", "contributors", "connected_project"]
        
        for i, project in enumerate(projects):
            project_lines = []
            
            # Add project number
            project_lines.append(f"Project {i+1}:")
            
            # First add fields in the preferred order
            for field in field_order:
                if field in project and project[field]:
                    display_name = field_display_names.get(field, field.title())
                    value = project[field]
                    
                    # Format list values
                    if isinstance(value, list):
                        value_str = ", ".join(str(item) for item in value)
                    else:
                        value_str = str(value)
                    
                    # Format the line as "Column: Values"
                    project_lines.append(f"  {display_name}: {value_str}")
            
            # Then add any other fields not in the order list
            for key, value in project.items():
                if key not in field_order and key not in ['id', 'created_at', 'updated_at'] and value:
                    display_name = field_display_names.get(key, key.title())
                    
                    # Format list values
                    if isinstance(value, list):
                        value_str = ", ".join(str(item) for item in value)
                    else:
                        value_str = str(value)
                    
                    # Format the line as "Column: Values"
                    project_lines.append(f"  {display_name}: {value_str}")
            
            # Add a separator between projects
            formatted_output.append("\n".join(project_lines))
        
        return "\n\n".join(formatted_output) 