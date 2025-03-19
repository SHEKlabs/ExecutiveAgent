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
                if filters:
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        # Handle array values for 'cs' operator
                        if operator == 'cs' and isinstance(value, list):
                            # Convert the list to a proper JSON string
                            value = json.dumps(value)
                        query = query.filter(column, operator, value)
                return query.execute()
            
            elif query_type == 'insert':
                return self.client.table(table).insert(data).execute()
            
            elif query_type == 'update':
                query = self.client.table(table).update(data)
                if filters:
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        # Handle array values for 'cs' operator
                        if operator == 'cs' and isinstance(value, list):
                            # Convert the list to a proper JSON string
                            value = json.dumps(value)
                        query = query.filter(column, operator, value)
                return query.execute()
            
            elif query_type == 'delete':
                query = self.client.table(table).delete()
                if filters:
                    for filter_condition in filters:
                        column, operator, value = filter_condition
                        # Handle array values for 'cs' operator
                        if operator == 'cs' and isinstance(value, list):
                            # Convert the list to a proper JSON string
                            value = json.dumps(value)
                        query = query.filter(column, operator, value)
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