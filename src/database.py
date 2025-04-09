import sys
import os
from supabase import create_client
import json

# Create a Supabase client directly
supabase_url = "https://uhbzldqdbhdyfuxwkqcn.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoYnpsZHFkYmhkeWZ1eHdrcWNuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjE1MDkxNSwiZXhwIjoyMDU3NzI2OTE1fQ.JauAr1A-gaxwNLau9agXY7boGAm01kHJHDTfF-YMDSM"

class SupabaseClient:
    def __init__(self):
        # Create a new client instance for each SupabaseClient instance
        self.client = create_client(supabase_url, supabase_key)
        
        # Field mapping between database and frontend
        self.db_to_frontend = {
            "Project": "name",
            "Category/Section": "category",
            "Owner": "owner",
            "Tag": "tags",
            "Connected Project": "connected_project",
            "Contributors": "contributors",
            "Description": "description"
        }
        
        self.frontend_to_db = {
            "name": "Project",
            "category": "Category/Section",
            "owner": "Owner",
            "tags": "Tag",
            "connected_project": "Connected Project",
            "contributors": "Contributors",
            "description": "Description"
        }
    
    def execute_query(self, table, query_type, data=None, filters=None):
        """
        Execute a query against the Supabase client.
        
        Args:
            table (str): The table name to query
            query_type (str): Type of query ('select', 'insert', 'update', 'delete')
            data (dict, optional): Data for insert/update operations
            filters (list, optional): List of filter conditions for select/update/delete
            
        Returns:
            The query result
        """
        try:
            if query_type == 'select':
                query = self.client.table(table).select('*')
                
                # Initialize variables for tracking filters
                contains_any_filters = []
                
                # Process filters if provided
                if filters:
                    # Track if we need to handle containsAny separately
                    standard_filters = []
                    
                    # Separate containsAny filters from standard filters
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        
                        if operator == 'containsAny' and isinstance(value, list):
                            contains_any_filters.append((column, value))
                        else:
                            # Process other filters normally
                            if operator == 'cs' and isinstance(value, list):
                                # Convert the list to a proper JSON string
                                value = json.dumps(value)
                            elif operator == 'in' and isinstance(value, list):
                                # This will be handled by the in_ method
                                pass
                            
                            standard_filters.append((column, operator, value))
                    
                    # Apply standard filters first
                    for column, operator, value in standard_filters:
                        if operator == 'in' and isinstance(value, list):
                            query = query.in_(column, value)
                        else:
                            query = query.filter(column, operator, value)
                
                # Debug logging for query
                print(f"DEBUG: Executing query on table {table} with filters: {filters}")
                
                # Execute the query
                result = query.execute()
                
                # If we have containsAny filters, apply them client-side
                # (This is a fallback since Supabase JS client doesn't support OR conditions well)
                if contains_any_filters and result.data:
                    filtered_data = result.data
                    
                    for column, values in contains_any_filters:
                        # Filter client-side to mimic containsAny behavior
                        new_filtered_data = []
                        
                        for item in filtered_data:
                            column_data = item.get(column, [])
                            
                            # Handle case where data might not be a list
                            if not isinstance(column_data, list):
                                column_data = [column_data]
                            
                            # Check if any value matches
                            if any(value in column_data for value in values):
                                new_filtered_data.append(item)
                        
                        filtered_data = new_filtered_data
                    
                    # Update the result data
                    result.data = filtered_data
                
                # Convert field names from DB to frontend format
                if result.data:
                    result.data = self.map_db_to_frontend(result.data)
                
                return result
            
            elif query_type == 'insert':
                # Convert field names from frontend to DB format for insertion
                if data:
                    data = self.map_frontend_to_db(data)
                return self.client.table(table).insert(data).execute()
            
            elif query_type == 'update':
                # Convert field names from frontend to DB format for update
                if data:
                    data = self.map_frontend_to_db(data)
                
                query = self.client.table(table).update(data)
                
                # Initialize variables for tracking filters
                contains_any_filters = []
                
                # Process filters if provided
                if filters:
                    # Track if we need to handle containsAny separately
                    standard_filters = []
                    
                    # Separate containsAny filters from standard filters
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        
                        if operator == 'containsAny' and isinstance(value, list):
                            contains_any_filters.append((column, value))
                        else:
                            # Process other filters normally
                            if operator == 'cs' and isinstance(value, list):
                                # Convert the list to a proper JSON string
                                value = json.dumps(value)
                            elif operator == 'in' and isinstance(value, list):
                                # This will be handled by the in_ method
                                pass
                            
                            standard_filters.append((column, operator, value))
                    
                    # Apply standard filters first
                    for column, operator, value in standard_filters:
                        if operator == 'in' and isinstance(value, list):
                            query = query.in_(column, value)
                        else:
                            query = query.filter(column, operator, value)
                
                # If we have containsAny filters, we can't apply them for update
                # since client-side filtering won't work
                if contains_any_filters:
                    print("WARNING: containsAny filters are not supported for update operations")
                
                result = query.execute()
                
                # Convert field names from DB to frontend format for the response
                if result.data:
                    result.data = self.map_db_to_frontend(result.data)
                
                return result
            
            elif query_type == 'delete':
                query = self.client.table(table).delete()
                
                # Initialize variables for tracking filters
                contains_any_filters = []
                
                # Process filters if provided
                if filters:
                    # Track if we need to handle containsAny separately
                    standard_filters = []
                    
                    # Separate containsAny filters from standard filters
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        
                        if operator == 'containsAny' and isinstance(value, list):
                            contains_any_filters.append((column, value))
                        else:
                            # Process other filters normally
                            if operator == 'cs' and isinstance(value, list):
                                # Convert the list to a proper JSON string
                                value = json.dumps(value)
                            elif operator == 'in' and isinstance(value, list):
                                # This will be handled by the in_ method
                                pass
                            
                            standard_filters.append((column, operator, value))
                    
                    # Apply standard filters first
                    for column, operator, value in standard_filters:
                        if operator == 'in' and isinstance(value, list):
                            query = query.in_(column, value)
                        else:
                            query = query.filter(column, operator, value)
                
                # If we have containsAny filters, we can't apply them for delete
                # since client-side filtering won't work
                if contains_any_filters:
                    print("WARNING: containsAny filters are not supported for delete operations")
                
                result = query.execute()
                
                # Convert field names from DB to frontend format for the response
                if result.data:
                    result.data = self.map_db_to_frontend(result.data)
                
                return result
            
            else:
                raise ValueError(f"Invalid query type: {query_type}")
        
        except Exception as e:
            print(f"Database operation failed: {str(e)}")
            raise

    def map_db_to_frontend(self, data_list):
        """Map database field names to frontend field names"""
        if not data_list:
            return data_list
            
        result = []
        for item in data_list:
            new_item = {}
            # Keep id as is
            if 'id' in item:
                new_item['id'] = item['id']
                
            # Map other fields
            for db_field, frontend_field in self.db_to_frontend.items():
                if db_field in item:
                    new_item[frontend_field] = item[db_field]
            
            # Keep any other fields not in the mapping
            for key, value in item.items():
                if key not in self.db_to_frontend and key != 'id':
                    new_item[key] = value
                    
            result.append(new_item)
            
        return result
        
    def map_frontend_to_db(self, data):
        """Map frontend field names to database field names"""
        if not data:
            return data
            
        result = {}
        
        # Map fields
        for frontend_field, db_field in self.frontend_to_db.items():
            if frontend_field in data:
                result[db_field] = data[frontend_field]
        
        # Keep any other fields not in the mapping
        for key, value in data.items():
            if key not in self.frontend_to_db:
                result[key] = value
                
        return result
    
    def get_data(self, table, filters=None):
        """Helper method to get data from a table with optional filters"""
        return self.execute_query(table, 'select', filters=filters)
    
    def insert_data(self, table, data):
        """Helper method to insert data into a table"""
        return self.execute_query(table, 'insert', data=data)
    
    def update_data(self, table, data, filters):
        """Helper method to update data in a table"""
        return self.execute_query(table, 'update', data=data, filters=filters)
    
    def delete_data(self, table, filters):
        """Helper method to delete data from a table"""
        return self.execute_query(table, 'delete', filters=filters)
    
    def format_results_for_chatbot(self, results):
        """
        Format query results specifically for chatbot display
        
        Args:
            results: Query results from Supabase
            
        Returns:
            List[Dict]: Formatted results with clean keys and values
        """
        if not results or not results.data:
            return []
        
        formatted_results = []
        
        for item in results.data:
            # Create a new dict for the formatted item
            formatted_item = {}
            
            for key, value in item.items():
                # Skip empty values and internal fields
                if value is None or key.startswith('_'):
                    continue
                
                # Format key names for readability
                formatted_key = key.replace('_', ' ').title()
                
                # Format value based on type
                if isinstance(value, list):
                    # If the value is a list, keep it as is
                    formatted_item[formatted_key] = value
                elif isinstance(value, dict):
                    # If the value is a dict, convert to string representation
                    formatted_item[formatted_key] = str(value)
                else:
                    # For other types, convert to string
                    formatted_item[formatted_key] = str(value)
            
            formatted_results.append(formatted_item)
        
        return formatted_results
    
    def translate_nl_to_query(self, nl_query, table):
        """
        Translate natural language query to database query parameters
        
        Args:
            nl_query (str): Natural language query
            table (str): Table to query
            
        Returns:
            List: Filter conditions to use with execute_query
        """
        # This is a placeholder implementation
        # In a real implementation, use more sophisticated NLP techniques
        
        # Convert to lowercase for case-insensitive matching
        query_lower = nl_query.lower()
        
        # Initialize filter conditions
        filter_conditions = []
        
        # Check for category mentions
        if 'category' in query_lower:
            # Extract category names (simplified)
            start = query_lower.find('category') + len('category')
            rest = query_lower[start:].split('.')[0].strip()
            if rest:
                filter_conditions.append(('Category/Section', 'containsAny', [rest]))
        
        # Check for owner mentions
        if 'owner' in query_lower:
            # Extract owner names (simplified)
            start = query_lower.find('owner') + len('owner')
            rest = query_lower[start:].split('.')[0].strip()
            if rest:
                filter_conditions.append(('Owner', 'in', [rest]))
        
        # Check for tag mentions
        if 'tag' in query_lower:
            # Extract tag names (simplified)
            start = query_lower.find('tag') + len('tag')
            rest = query_lower[start:].split('.')[0].strip()
            if rest:
                filter_conditions.append(('Tag', 'containsAny', [rest]))
        
        return filter_conditions 