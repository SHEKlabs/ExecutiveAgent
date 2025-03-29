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
            'tags': ['tag', 'tags', 'labeled', 'labelled', 'marked as', 'hashtag', 'hashtags'],
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
        found_owners = []
        for owner in common_owners:
            if owner in user_message:
                found_owners.append(owner)
                print(f"DEBUG: Found specific owner in message: {owner}")
        
        if found_owners:
            filters['owner'] = found_owners

        # Convert message to lowercase for easier matching of other filter types
        message_lower = user_message.lower()
        
        # Check for multiple filter mentions by finding all keyword occurrences
        filter_matches = {}
        for filter_type, keywords in filter_keywords.items():
            filter_matches[filter_type] = []
            for keyword in keywords:
                # Find all occurrences of this keyword
                start_pos = 0
                while True:
                    pos = message_lower.find(keyword, start_pos)
                    if pos == -1:
                        break
                    filter_matches[filter_type].append((pos, keyword))
                    start_pos = pos + len(keyword)
        
        # Sort all found positions across all filter types
        all_positions = []
        for filter_type, positions in filter_matches.items():
            for pos, keyword in positions:
                all_positions.append((pos, keyword, filter_type))
        
        # Sort by position in the message
        all_positions.sort()
        
        # Process each filter mention in order
        for i, (pos, keyword, filter_type) in enumerate(all_positions):
            # Skip if we already have this filter type from hashtags or specific owners
            if filter_type == 'tags' and 'tags' in filters:
                continue
            if filter_type == 'owner' and 'owner' in filters:
                continue
            
            # Find the end of this filter's value (either next filter or end of message)
            end_pos = len(message_lower)
            if i < len(all_positions) - 1:
                end_pos = all_positions[i+1][0]
            
            # Extract the text after the keyword up to the next filter or end
            after_keyword = message_lower[pos + len(keyword):end_pos].strip()
            
            # Clean up the value
            value = after_keyword.strip(".,;: ")
            
            if not value:
                continue
            
            # Process based on filter type
            if filter_type == 'tags':
                # Extract individual tags
                tag_values = []
                
                # Check for list indicators
                if ',' in value or ' and ' in value:
                    # Split by commas and 'and'
                    parts = value.replace(' and ', ',').split(',')
                    for part in parts:
                        clean_part = part.strip()
                        if clean_part:
                            if clean_part.startswith('#'):
                                tag_values.append(clean_part)
                            else:
                                # Add hashtag if missing
                                tag_values.append(f"#{clean_part}")
                else:
                    # Process individual words for hashtags
                    for word in value.split():
                        if word.startswith('#'):
                            tag_values.append(word)
                        elif '#' in word:
                            # Extract part starting with #
                            hashtag = word[word.find('#'):]
                            tag_values.append(hashtag)
                        else:
                            # Regular word, treat as tag
                            tag_values.append(f"#{word}")
                
                if tag_values:
                    if 'tags' not in filters:
                        filters['tags'] = []
                    filters['tags'].extend(tag_values)
                    # Remove duplicates
                    filters['tags'] = list(set(filters['tags']))
                    
            elif filter_type == 'owner':
                # Extract owners
                if ',' in value or ' and ' in value:
                    # Split by commas and 'and'
                    owners = [owner.strip() for owner in value.replace(' and ', ',').split(',')]
                    for owner in owners:
                        if owner:
                            # Check against known owners
                            for known_owner in common_owners:
                                if owner.lower() in known_owner.lower() or known_owner.lower() in owner.lower():
                                    if 'owner' not in filters:
                                        filters['owner'] = []
                                    if isinstance(filters['owner'], list):
                                        filters['owner'].append(known_owner)
                                    else:
                                        filters['owner'] = [filters['owner'], known_owner]
                                    break
                            else:
                                # No match with known owners
                                if 'owner' not in filters:
                                    filters['owner'] = []
                                if isinstance(filters['owner'], list):
                                    filters['owner'].append(owner)
                                else:
                                    filters['owner'] = [filters['owner'], owner]
                else:
                    # Single owner
                    # Check against known owners
                    for known_owner in common_owners:
                        if value.lower() in known_owner.lower() or known_owner.lower() in value.lower():
                            if 'owner' not in filters:
                                filters['owner'] = known_owner
                            elif isinstance(filters['owner'], list):
                                filters['owner'].append(known_owner)
                            else:
                                filters['owner'] = [filters['owner'], known_owner]
                            break
                    else:
                        # No match with known owners
                        if 'owner' not in filters:
                            filters['owner'] = value
                        elif isinstance(filters['owner'], list):
                            filters['owner'].append(value)
                        else:
                            filters['owner'] = [filters['owner'], value]
                            
            elif filter_type == 'category':
                # Extract categories
                if ',' in value or ' and ' in value:
                    # Split by commas and 'and'
                    categories = [cat.strip() for cat in value.replace(' and ', ',').split(',')]
                    if 'category' not in filters:
                        filters['category'] = categories
                    elif isinstance(filters['category'], list):
                        filters['category'].extend(categories)
                    else:
                        filters['category'] = [filters['category']] + categories
                else:
                    # Single category
                    if 'category' not in filters:
                        filters['category'] = value
                    elif isinstance(filters['category'], list):
                        filters['category'].append(value)
                    else:
                        filters['category'] = [filters['category'], value]
                    
            elif filter_type == 'contributors':
                # Extract contributors
                if ',' in value or ' and ' in value:
                    # Split by commas and 'and'
                    contributors = [c.strip() for c in value.replace(' and ', ',').split(',')]
                    if 'contributors' not in filters:
                        filters['contributors'] = contributors
                    elif isinstance(filters['contributors'], list):
                        filters['contributors'].extend(contributors)
                    else:
                        filters['contributors'] = [filters['contributors']] + contributors
                else:
                    # Single contributor
                    if 'contributors' not in filters:
                        filters['contributors'] = value
                    elif isinstance(filters['contributors'], list):
                        filters['contributors'].append(value)
                    else:
                        filters['contributors'] = [filters['contributors'], value]
        
        # Special case handling for common tag terms without hashtags
        common_tags = {
            'ai': '#AI',
            'artificial intelligence': '#AI',
            'ml': '#ML',
            'machine learning': '#ML',
            'agent': '#Agent',
            'code': '#code',
            'finance': '#finance',
            'labs': '#Labs',
            'foundation': '#Foundation'
        }
        
        for term, tag in common_tags.items():
            if term in message_lower:
                if 'tags' not in filters:
                    filters['tags'] = []
                elif not isinstance(filters['tags'], list):
                    filters['tags'] = [filters['tags']]
                # Add if not already present
                if tag not in filters['tags']:
                    filters['tags'].append(tag)
        
        # Ensure all filter values are lists for consistency
        for key in filters:
            if not isinstance(filters[key], list):
                filters[key] = [filters[key]]
        
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