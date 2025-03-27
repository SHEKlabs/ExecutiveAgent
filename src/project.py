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
    
    def get_projects_by_category(self, categories):
        """
        Retrieve projects filtered by one or more categories
        
        Args:
            categories (str or list): The category or categories to filter by
            
        Returns:
            List of project dictionaries matching the categories
        """
        # Convert single category to list if needed
        if not isinstance(categories, list):
            categories = [categories]
            
        # Note: The exact column name in the database is "Category/Section"
        # Use 'containsAny' operator for jsonb array to match any of the categories
        filters = [('Category/Section', 'containsAny', categories)]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def get_projects_by_tag(self, tags):
        """
        Retrieve projects that contain any of the specified tags
        
        Args:
            tags (str or list): The tag or tags to filter by
            
        Returns:
            List of project dictionaries with any of the specified tags
        """
        # Convert single tag to list if needed
        if not isinstance(tags, list):
            tags = [tags]
            
        # Use 'containsAny' operator to match any of the tags
        filters = [('Tag', 'containsAny', tags)]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def get_projects_by_owner(self, owners):
        """
        Retrieve projects filtered by one or more owners
        
        Args:
            owners (str or list): The owner or owners to filter by
            
        Returns:
            List of project dictionaries matching any of the specified owners
        """
        # Convert single owner to list if needed
        if not isinstance(owners, list):
            owners = [owners]
            
        # For text columns like Owner, use 'in' operator with multiple values
        filters = [('Owner', 'in', owners)]
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
    
    def get_projects_by_contributors(self, contributors):
        """
        Retrieve projects that have any of the specified contributors
        
        Args:
            contributors (str or list): List of contributor names to filter by
            
        Returns:
            List of project dictionaries with any of the specified contributors
        """
        # Convert single contributor to list if needed
        if not isinstance(contributors, list):
            contributors = [contributors]
            
        # Use 'containsAny' operator for contributors array
        filters = [('Contributors', 'containsAny', contributors)]
        result = self.db_client.get_data(self.table_name, filters=filters)
        return result.data
    
    def filter_projects(self, filters):
        """
        Filter projects by multiple criteria using direct Supabase queries
        
        Args:
            filters (dict): Dictionary of filter criteria, e.g.:
                {
                    'category': ['AI - Agent', '#Labs'],
                    'tags': ['#AI', '#Agent'],
                    'owner': ['Abhishek Raol', 'John Doe']
                }
            
        Returns:
            List of project dictionaries matching all criteria
        """
        # Build the filter conditions list for Supabase query
        filter_conditions = []
        
        for key, value in filters.items():
            # Ensure values are lists for consistent handling
            if not isinstance(value, list):
                value = [value]
                
            if key == 'category':
                # For Category/Section (jsonb array), use containsAny to match any category
                filter_conditions.append(('Category/Section', 'containsAny', value))
            
            elif key == 'owner':
                # For Owner (text column), use 'in' operator
                filter_conditions.append(('Owner', 'in', value))
            
            elif key == 'tags':
                # For Tag (jsonb array), use containsAny to match any tag
                filter_conditions.append(('Tag', 'containsAny', value))
            
            elif key == 'connected_project':
                # For Connected Project (jsonb array), use containsAny
                filter_conditions.append(('Connected Project', 'containsAny', value))
                
            elif key == 'contributors':
                # For Contributors (jsonb array), use containsAny
                filter_conditions.append(('Contributors', 'containsAny', value))
        
        # Execute the query with all filter conditions
        if filter_conditions:
            result = self.db_client.get_data(self.table_name, filters=filter_conditions)
            return result.data
        else:
            # If no filters, return all projects
            return self.get_all_projects() 