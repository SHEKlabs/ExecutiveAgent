import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.project import ProjectManager

class TestProjectManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.project_manager = ProjectManager()
        
        # Sample project data for testing
        self.sample_project = {
            'id': '1',
            'name': 'Test Project',
            'description': 'Test project description',
            'category': 'Development',
            'tags': ['python', 'test'],
            'owner': 'test_user'
        }
    
    @patch('src.project.SupabaseClient')
    def test_get_all_projects(self, mock_client):
        """Test retrieving all projects"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.data = [self.sample_project]
        mock_instance.get_data.return_value = mock_response
        
        # Call the function
        projects = self.project_manager.get_all_projects()
        
        # Assertions
        mock_instance.get_data.assert_called_once_with('projects')
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['name'], 'Test Project')
    
    @patch('src.project.SupabaseClient')
    def test_get_projects_by_category(self, mock_client):
        """Test retrieving projects by category"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.data = [self.sample_project]
        mock_instance.get_data.return_value = mock_response
        
        # Call the function
        projects = self.project_manager.get_projects_by_category('Development')
        
        # Assertions
        mock_instance.get_data.assert_called_once_with(
            'projects', 
            filters=[('category', 'eq', 'Development')]
        )
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['category'], 'Development')
    
    @patch('src.project.SupabaseClient')
    def test_get_projects_by_tag(self, mock_client):
        """Test retrieving projects by tag"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.data = [self.sample_project]
        mock_instance.get_data.return_value = mock_response
        
        # Call the function
        projects = self.project_manager.get_projects_by_tag('python')
        
        # Assertions
        mock_instance.get_data.assert_called_once_with(
            'projects', 
            filters=[('tags', 'cs', ['python'])]
        )
        self.assertEqual(len(projects), 1)
        self.assertIn('python', projects[0]['tags'])
    
    @patch('src.project.SupabaseClient')
    def test_get_projects_by_owner(self, mock_client):
        """Test retrieving projects by owner"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.data = [self.sample_project]
        mock_instance.get_data.return_value = mock_response
        
        # Call the function
        projects = self.project_manager.get_projects_by_owner('test_user')
        
        # Assertions
        mock_instance.get_data.assert_called_once_with(
            'projects', 
            filters=[('owner', 'eq', 'test_user')]
        )
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['owner'], 'test_user')
    
    @patch('src.project.SupabaseClient')
    def test_add_project(self, mock_client):
        """Test adding a new project"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_response.data = [self.sample_project]
        mock_instance.insert_data.return_value = mock_response
        
        # Call the function
        result = self.project_manager.add_project(self.sample_project)
        
        # Assertions
        mock_instance.insert_data.assert_called_once_with('projects', self.sample_project)
        self.assertEqual(result[0]['name'], 'Test Project')
    
    @patch('src.project.SupabaseClient')
    def test_update_project(self, mock_client):
        """Test updating an existing project"""
        # Setup mock
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        updated_project = self.sample_project.copy()
        updated_project['name'] = 'Updated Project'
        mock_response.data = [updated_project]
        mock_instance.update_data.return_value = mock_response
        
        # Call the function
        result = self.project_manager.update_project('1', {'name': 'Updated Project'})
        
        # Assertions
        mock_instance.update_data.assert_called_once_with(
            'projects', 
            {'name': 'Updated Project'}, 
            [('id', 'eq', '1')]
        )
        self.assertEqual(result[0]['name'], 'Updated Project')

if __name__ == '__main__':
    unittest.main() 