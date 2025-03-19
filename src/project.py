from database import SupabaseClient

class ProjectManager:
    def __init__(self):
        self.db_client = SupabaseClient()
        self.table_name = 'PM - Projects - AR'
    
    def get_all_projects(self):
        """
        Retrieve all projects from the database
        
        Returns:
            List of project dictionaries
        """
        result = self.db_client.get_data(self.table_name)
        return result.data
    
    def get_projects_by_category(self, category):
        """
        Retrieve projects filtered by category
        
        Args:
            category (str): The category to filter by
            
        Returns:
            List of project dictionaries matching the category
        """
        # Note: Using 'cs' operator since Category/Section is an array in the table
        filters = [('"Category/Section"', 'cs', [category])]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def get_projects_by_tag(self, tag):
        """
        Retrieve projects that contain a specific tag
        
        Args:
            tag (str): The tag to filter by
            
        Returns:
            List of project dictionaries with the specified tag
        """
        # Note: Tag is stored as an array in the table
        filters = [('Tag', 'cs', [tag])]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def get_projects_by_owner(self, owner):
        """
        Retrieve projects filtered by owner
        
        Args:
            owner (str): The owner to filter by
            
        Returns:
            List of project dictionaries matching the owner
        """
        filters = [('Owner', 'eq', owner)]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def get_project_by_id(self, project_id):
        """
        Retrieve a specific project by its ID
        
        Args:
            project_id (str/int): The ID of the project to retrieve
            
        Returns:
            Project dictionary or None if not found
        """
        filters = [('id', 'eq', project_id)]
        result = self.db_client.get_data(self.table_name, filters=filters)
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    
    def add_project(self, project_data):
        """
        Add a new project to the database
        
        Args:
            project_data (dict): The project data to insert
            
        Returns:
            Inserted project data
        """
        result = self.db_client.insert_data(self.table_name, project_data)
        return result.data
    
    def update_project(self, project_id, updated_data):
        """
        Update an existing project
        
        Args:
            project_id (str/int): The ID of the project to update
            updated_data (dict): The updated project data
            
        Returns:
            Updated project data
        """
        filters = [('id', 'eq', project_id)]
        result = self.db_client.update_data(self.table_name, updated_data, filters)
        return result.data
    
    def delete_project(self, project_id):
        """
        Delete a project by its ID
        
        Args:
            project_id (str/int): The ID of the project to delete
            
        Returns:
            Result of the delete operation
        """
        filters = [('id', 'eq', project_id)]
        result = self.db_client.delete_data(self.table_name, filters)
        return result.data 