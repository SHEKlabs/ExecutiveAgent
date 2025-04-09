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
            
        # Expand the owner list with variations to improve matching
        expanded_owners = set()
        for owner in owners:
            # Original name
            expanded_owners.add(owner)
            
            # Handle specific common cases
            if 'abhishek' in owner.lower():
                expanded_owners.add('Abhishek')
                expanded_owners.add('Abhishek Raol')
            
            if 'john' in owner.lower():
                expanded_owners.add('John')
                expanded_owners.add('John Doe')
        
        # Convert back to list
        owners_list = list(expanded_owners)
        print(f"DEBUG: Expanded owner names for search: {owners_list}")
            
        # For text columns like Owner, use 'in' operator with multiple values
        filters = [('Owner', 'in', owners_list)]
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
    
    def filter_projects(self, filters, match_all=False):
        """
        Filter projects by multiple criteria using direct Supabase queries
        
        Args:
            filters (dict): Dictionary of filter criteria, e.g.:
                {
                    'category': ['AI - Agent', '#Labs'],
                    'tags': ['#AI', '#Agent'],
                    'owner': ['Abhishek Raol', 'John Doe']
                }
            match_all (bool): If True, projects must match ALL filter criteria
                              If False, projects can match ANY filter criteria
            
        Returns:
            List of project dictionaries matching the criteria
        """
        # If we want to match ANY of the filters (instead of ALL),
        # we need to query separately for each filter type and combine the results
        if not match_all and len(filters) > 1:
            print(f"DEBUG: Using ANY match mode for filters: {filters}")
            all_matching_projects = []
            seen_ids = set()
            
            # Query each filter type separately
            for key, value in filters.items():
                single_filter = {key: value}
                # Use recursive call with single filter
                matching_projects = self.filter_projects(single_filter, match_all=True)
                
                # Add to results if not already included
                for project in matching_projects:
                    if project['id'] not in seen_ids:
                        all_matching_projects.append(project)
                        seen_ids.add(project['id'])
            
            print(f"DEBUG: Found {len(all_matching_projects)} total projects matching ANY criteria")
            return all_matching_projects
        
        # Build the filter conditions list for Supabase query (standard AND logic)
        filter_conditions = []
        
        for key, value in filters.items():
            # Ensure values are lists for consistent handling
            if not isinstance(value, list):
                value = [value]
                
            # Debug
            print(f"DEBUG: Filtering by {key} with values: {value}")
                
            if key == 'category':
                # Use the actual database column name
                filter_conditions.append(('Category/Section', 'containsAny', value))
            
            elif key == 'owner':
                # Special handling for text fields like Owner
                # Convert list of names to include variations
                owner_variations = set()
                for owner_name in value:
                    # Original name
                    owner_variations.add(owner_name)
                    
                    # Handle specific common cases
                    if 'abhishek' in owner_name.lower():
                        owner_variations.add('Abhishek')
                        owner_variations.add('Abhishek Raol')
                    
                    if 'john' in owner_name.lower():
                        owner_variations.add('John')
                        owner_variations.add('John Doe')
                
                # Convert to list and use 'in' operator
                owner_list = list(owner_variations)
                print(f"DEBUG: Expanded owner names: {owner_list}")
                
                # Use the actual database column name with 'in' operator
                filter_conditions.append(('Owner', 'in', owner_list))
            
            elif key == 'tags':
                # Use the actual database column name
                # Special handling for tags - remove # prefix if needed for comparison
                # and handle case sensitivity
                normalized_tags = []
                for tag in value:
                    # Get the original tag (both with and without #)
                    normalized_tags.append(tag)
                    
                    # Add lowercase version
                    normalized_tags.append(tag.lower())
                    
                    # Add uppercase version
                    normalized_tags.append(tag.upper())
                    
                    # Add capitalized version
                    normalized_tags.append(tag.capitalize())
                    
                    # Handle # prefix/suffix variations
                    if tag.startswith('#'):
                        tag_without_hash = tag[1:]
                        # Add without hash
                        normalized_tags.append(tag_without_hash)
                        # Add lowercase without hash
                        normalized_tags.append(tag_without_hash.lower())
                        # Add uppercase without hash
                        normalized_tags.append(tag_without_hash.upper())
                        # Add capitalized without hash
                        normalized_tags.append(tag_without_hash.capitalize())
                    else:
                        tag_with_hash = f'#{tag}'
                        # Add with hash
                        normalized_tags.append(tag_with_hash)
                        # Add lowercase with hash
                        normalized_tags.append(tag_with_hash.lower())
                        # Add uppercase with hash
                        normalized_tags.append(tag_with_hash.upper())
                        # Add capitalized with hash
                        normalized_tags.append(tag_with_hash.capitalize())
                
                # Remove duplicates
                normalized_tags = list(set(normalized_tags))
                
                print(f"DEBUG: Normalized tags for search: {normalized_tags}")
                filter_conditions.append(('Tag', 'containsAny', normalized_tags))
            
            elif key == 'connected_project':
                # Use the actual database column name
                filter_conditions.append(('Connected Project', 'containsAny', value))
                
            elif key == 'contributors':
                # Use the actual database column name
                filter_conditions.append(('Contributors', 'containsAny', value))
        
        # Execute the query with all filter conditions
        if filter_conditions:
            print(f"DEBUG: Final filter conditions: {filter_conditions}")
            result = self.db_client.get_data(self.table_name, filters=filter_conditions)
            return result.data
        else:
            # If no filters, return all projects
            return self.get_all_projects() 
    
    def process_nl_query(self, query_text):
        """
        Process a natural language query to extract filter criteria and return projects
        
        Args:
            query_text (str): Natural language query from the user
            
        Returns:
            List of project dictionaries matching the extracted criteria
        """
        # Extract filter criteria from the query text
        filters = self.extract_filters_from_text(query_text)
        
        # If filters were extracted, use them to filter projects
        if filters:
            return self.filter_projects(filters)
        else:
            # If no filters were found, return all projects
            return self.get_all_projects()
    
    def extract_filters_from_text(self, text):
        """
        Extract filter criteria from natural language text
        
        Args:
            text (str): Natural language text to analyze
            
        Returns:
            Dict of filter criteria extracted from the text
        """
        # Initialize filters dictionary
        filters = {}
        
        # Convert text to lowercase for easier pattern matching
        text_lower = text.lower()
        original_text = text
        
        # Direct detection of hashtags in the original text (preserve case)
        hashtags = []
        for word in text.split():
            word_lower = word.lower()
            
            # Special handling for common terms
            if word_lower in ['#ai', 'ai', '#artificial', 'artificial intelligence']:
                hashtags.append('#AI')
                continue
                
            if word_lower in ['#ml', 'ml', '#machine', 'machine learning']:
                hashtags.append('#ML')
                continue
            
            if word_lower in ['#foundation', 'foundation']:
                hashtags.append('#Foundation')
                continue
            
            if word_lower in ['#code', 'code']:
                hashtags.append('#code')
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
        
        # If we found hashtags, add them as tags
        if hashtags:
            filters['tags'] = hashtags
            
        # Check for multiple filter types in the text
        # Define keywords for each filter type
        filter_keywords = {
            'category': ['category', 'section', 'type', 'kind', 'group'],
            'owner': ['owner', 'owned by', 'belongs to', 'assigned to', 'by'],
            'tags': ['tag', 'tags', 'labeled', 'labelled', 'marked as', 'hashtag', 'hashtags'],
            'contributors': ['contributor', 'contributors', 'worked on by', 'team']
        }
        
        # Check for specific owners directly in the message
        common_owners = ['Abhishek', 'Abhishek Raol', 'John', 'John Doe']
        found_owners = []
        for owner in common_owners:
            if owner in original_text:
                found_owners.append(owner)
                print(f"DEBUG: Found specific owner in text: {owner}")
        
        if found_owners:
            filters['owner'] = found_owners
        
        # Find all filter keyword positions in the text
        filter_matches = {}
        for filter_type, keywords in filter_keywords.items():
            filter_matches[filter_type] = []
            for keyword in keywords:
                # Find all occurrences of this keyword
                start_pos = 0
                while True:
                    pos = text_lower.find(keyword, start_pos)
                    if pos == -1:
                        break
                    filter_matches[filter_type].append((pos, keyword))
                    start_pos = pos + len(keyword)
        
        # Sort all found positions across all filter types
        all_positions = []
        for filter_type, positions in filter_matches.items():
            for pos, keyword in positions:
                all_positions.append((pos, keyword, filter_type))
        
        # Sort by position in the text
        all_positions.sort()
        
        # Process each filter mention in order
        for i, (pos, keyword, filter_type) in enumerate(all_positions):
            # Skip if we already have this filter type from hashtags or specific owners
            if filter_type == 'tags' and 'tags' in filters:
                continue
            if filter_type == 'owner' and 'owner' in filters:
                continue
            
            # Find the end of this filter's value (either next filter or end of text)
            end_pos = len(text_lower)
            if i < len(all_positions) - 1:
                end_pos = all_positions[i+1][0]
            
            # Extract the text after the keyword up to the next filter or end
            after_keyword = text_lower[pos + len(keyword):end_pos].strip()
            
            # Clean up the value
            value = after_keyword.strip(".,;: ")
            
            if not value:
                continue
            
            # Process based on filter type
            if filter_type == 'category':
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
                    
            elif filter_type == 'tags':
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
                    if isinstance(filters['tags'], list):
                        filters['tags'].extend(tag_values)
                    else:
                        filters['tags'] = [filters['tags']] + tag_values
                    # Remove duplicates
                    filters['tags'] = list(set(filters['tags']))
                    
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
            if term in text_lower:
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
        
        print(f"DEBUG: Extracted filters from text: {filters}")
        return filters
    
    def format_projects_for_chat(self, projects):
        """
        Format projects for display in chat interface using 'Column: Values' format
        
        Args:
            projects (list): List of project dictionaries
            
        Returns:
            str: Formatted string representation of projects
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
    
    def search_projects_by_text(self, search_term):
        """
        Search projects for text matching in name, description, or other fields
        
        Args:
            search_term (str): The text to search for
            
        Returns:
            List of project dictionaries containing the search term
        """
        # Get all projects first
        all_projects = self.get_all_projects()
        
        # Convert search term to lowercase for case-insensitive matching
        search_term_lower = search_term.lower()
        
        # Filter projects that contain the search term in any text field
        matching_projects = []
        
        for project in all_projects:
            # Check name field
            if 'name' in project and project['name'] and search_term_lower in project['name'].lower():
                matching_projects.append(project)
                continue
                
            # Check description field
            if 'description' in project and project['description'] and search_term_lower in project['description'].lower():
                matching_projects.append(project)
                continue
                
            # Check owner field
            if 'owner' in project and project['owner'] and search_term_lower in project['owner'].lower():
                matching_projects.append(project)
                continue
                
            # Check tags (array field)
            if 'tags' in project and project['tags']:
                tags_str = ' '.join([str(tag).lower() for tag in project['tags']])
                if search_term_lower in tags_str:
                    matching_projects.append(project)
                    continue
                    
            # Check category (array field)
            if 'category' in project and project['category']:
                if isinstance(project['category'], list):
                    category_str = ' '.join([str(cat).lower() for cat in project['category']])
                    if search_term_lower in category_str:
                        matching_projects.append(project)
                        continue
                elif search_term_lower in str(project['category']).lower():
                    matching_projects.append(project)
                    continue
                    
            # Check contributors (array field)
            if 'contributors' in project and project['contributors']:
                if isinstance(project['contributors'], list):
                    contributors_str = ' '.join([str(c).lower() for c in project['contributors']])
                    if search_term_lower in contributors_str:
                        matching_projects.append(project)
                        continue
                elif search_term_lower in str(project['contributors']).lower():
                    matching_projects.append(project)
                    continue
        
        return matching_projects 