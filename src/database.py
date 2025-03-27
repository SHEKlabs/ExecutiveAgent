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
                
                return result
            
            elif query_type == 'insert':
                return self.client.table(table).insert(data).execute()
            
            elif query_type == 'update':
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
                
                return query.execute()
            
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
                
                return query.execute()
            
            else:
                raise ValueError(f"Invalid query type: {query_type}")
        
        except Exception as e:
            print(f"Database operation failed: {str(e)}")
            raise
    
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