import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chatbot import Chatbot
from project import ProjectManager

class TestChatbot:
    """Tests for the Chatbot class"""
    
    @patch('openai.OpenAI')
    def test_process_message(self, mock_openai):
        """Test that the chatbot can process messages"""
        # Set up the mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock the chat completions create method
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This is a test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        # Set up the mock chain
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_completions.create = MagicMock(return_value=mock_response)
        mock_chat.completions = mock_completions
        mock_client.chat = mock_chat
        
        # Create the chatbot
        chatbot = Chatbot()
        
        # Use synchronous test with event loop
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(chatbot.process_message("Hello, chatbot!"))
        
        # Check that the response is correct
        assert response == "This is a test response"
        
        # Check that the message was added to the conversation history
        assert len(chatbot.conversation_history) == 2
        assert chatbot.conversation_history[0]["role"] == "user"
        assert chatbot.conversation_history[0]["content"] == "Hello, chatbot!"
        assert chatbot.conversation_history[1]["role"] == "assistant"
        assert chatbot.conversation_history[1]["content"] == "This is a test response"
    
    def test_extract_filter_criteria(self):
        """Test that the chatbot can extract filter criteria from messages"""
        chatbot = Chatbot()
        
        # Test category extraction
        message = "Show me projects in category AI"
        filters = chatbot.extract_filter_criteria(message)
        assert "category" in filters
        assert filters["category"] == "AI"
        
        # Test owner extraction
        message = "Find projects owned by John"
        filters = chatbot.extract_filter_criteria(message)
        assert "owner" in filters
        assert filters["owner"] == "John"
        
        # Test tag extraction
        message = "Show projects with tags Machine Learning"
        filters = chatbot.extract_filter_criteria(message)
        assert "tags" in filters
        assert "Machine" in filters["tags"]
        assert "Learning" in filters["tags"]
        
        # Test multiple filters
        message = "Find projects in category AI with tags ML owned by John"
        filters = chatbot.extract_filter_criteria(message)
        assert "category" in filters
        assert "tags" in filters
        assert "owner" in filters
    
    def test_format_project_data(self):
        """Test that the chatbot can format project data"""
        chatbot = Chatbot()
        
        # Test with empty projects
        formatted = chatbot.format_project_data([])
        assert formatted == "No projects found matching your criteria."
        
        # Test with projects
        projects = [
            {
                "id": 1,
                "name": "Test Project",
                "description": "A test project",
                "category": "Test",
                "owner": "Test User",
                "tags": ["test", "example"]
            },
            {
                "id": 2,
                "name": "Another Project",
                "description": "Another test project",
                "category": "Example",
                "owner": "Another User",
                "tags": ["example", "test"]
            }
        ]
        
        formatted = chatbot.format_project_data(projects)
        
        # Check that the formatting is correct
        assert "Project 1:" in formatted
        assert "name: Test Project" in formatted
        assert "description: A test project" in formatted
        assert "category: Test" in formatted
        assert "owner: Test User" in formatted
        assert "tags: test, example" in formatted
        
        assert "Project 2:" in formatted
        assert "name: Another Project" in formatted
        assert "description: Another test project" in formatted
        assert "category: Example" in formatted
        assert "owner: Another User" in formatted
        assert "tags: example, test" in formatted


class TestProjectNLP:
    """Tests for the NLP features in ProjectManager"""
    
    def test_extract_filters_from_text(self):
        """Test extraction of filters from natural language text"""
        project_manager = ProjectManager()
        
        # Test category extraction
        text = "Show me projects in the AI category"
        filters = project_manager.extract_filters_from_text(text)
        assert "category" in filters
        assert "AI" in filters["category"]
        
        # Test owner extraction
        text = "Find projects owned by Abhishek"
        filters = project_manager.extract_filters_from_text(text)
        assert "owner" in filters
        assert "Abhishek" in filters["owner"]
        
        # Test multiple filters
        text = "Show me AI projects with tag Machine Learning"
        filters = project_manager.extract_filters_from_text(text)
        assert "category" in filters or "tags" in filters
    
    def test_format_projects_for_chat(self):
        """Test formatting of projects for chat display"""
        project_manager = ProjectManager()
        
        # Test with empty projects
        formatted = project_manager.format_projects_for_chat([])
        assert formatted == "No projects found matching your criteria."
        
        # Test with projects
        projects = [
            {
                "id": 1,
                "name": "Test Project",
                "description": "A test project",
                "category": "Test",
                "owner": "Test User",
                "tags": ["test", "example"]
            }
        ]
        
        formatted = project_manager.format_projects_for_chat(projects)
        
        # Check that the formatting is correct
        assert "Project 1:" in formatted
        assert "name: Test Project" in formatted
        assert "description: A test project" in formatted 