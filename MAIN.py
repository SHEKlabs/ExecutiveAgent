# MAIN.py
from dotenv import load_dotenv
load_dotenv()  # Load env variables immediately

import os
import queue
from threading import Thread
from flask import Flask, render_template, request, jsonify, Response

# Import our new LangChain modules
from langchain_gsheets import GoogleSheetsConnector
from simple_agent import SimpleAgent

app = Flask(__name__)

# Initialize the Google Sheets connector
sheets_connector = GoogleSheetsConnector()

# Create tools from the sheets connector
projects_tool = sheets_connector.get_projects_tool()
search_projects_tool = sheets_connector.search_projects_tool()

# List of tools for the agent
tools = [projects_tool, search_projects_tool]

# For streaming responses
def generate_streaming_response(user_query):
    # Streaming not implemented yet with the simple agent
    yield "Streaming responses are currently not supported. Please try without streaming enabled."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    print(f"Received message: {user_input}")
    
    # Check if we're requesting a streaming response
    stream_response = request.form.get("stream") == "true"
    
    if stream_response:
        try:
            print("Attempting streaming response")
            return Response(generate_streaming_response(user_input), mimetype='text/event-stream')
        except Exception as e:
            print(f"Error setting up streaming response: {e}")
            # Fall back to non-streaming if there's an error
            stream_response = False
    
    # Non-streaming response
    if not stream_response:
        try:
            print("Using non-streaming response")
            # Initialize a new agent for each request (stateless)
            agent = SimpleAgent(tools=tools)
            print("Agent initialized, processing query...")
            response = agent.process_query(user_input)
            print(f"Response generated (first 100 chars): {response[:100]}...")  # Log first 100 chars of response
            
            # Check if response contains HTML table
            contains_html = "<table" in response and "</table>" in response
            
            if contains_html:
                print("Response contains HTML content - setting contains_html flag")
            
            return jsonify({
                "response": response,
                "contains_html": contains_html
            })
        except Exception as e:
            print(f"Error in non-streaming response: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"response": f"I encountered an error: {str(e)}", "contains_html": False})

# Legacy endpoint for testing
@app.route("/test_projects", methods=["GET"])
def test_projects():
    projects_data = sheets_connector.get_projects_raw()
    return jsonify({"data": projects_data})

# New endpoint for vector search
@app.route("/search_projects", methods=["POST"])
def search_projects():
    query = request.form.get("query")
    results = sheets_connector.search_projects(query)
    return jsonify({"results": results})

# New endpoint for direct tool testing
@app.route("/test_tool/<tool_name>", methods=["GET"])
def test_tool(tool_name):
    try:
        if tool_name == "GetProjects":
            result = sheets_connector.get_projects_raw()
            return jsonify({"success": True, "result": result})
        elif tool_name == "SearchProjects":
            query = request.args.get("query", "finance")
            result = sheets_connector.search_projects(query)
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "error": f"Unknown tool: {tool_name}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Something about creating necessary backend endpoint. FOr interactive table in the chatbot.
@app.route("/direct/projects_table", methods=["GET"])
def direct_projects_table():
    """
    Direct access to projects table without LLM processing
    Returns the HTML table that can be embedded in the chat interface
    """
    try:
        # Get raw HTML table
        html_table = sheets_connector.get_projects_raw()
        
        # Return HTML content with additional wrapper
        return jsonify({
            "success": True,
            "html_content": html_table
        })
    except Exception as e:
        print(f"Error generating direct projects table: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        })

# Add this to MAIN.py

@app.route("/direct/filtered_projects", methods=["POST"])
def filtered_projects_table():
    """
    Direct access to filtered projects table
    Returns HTML table filtered by the provided criteria
    """
    try:
        # Get filter criteria from request
        filter_params = request.json or {}
        query = filter_params.get('query', '')
        category = filter_params.get('category', '')
        owner = filter_params.get('owner', '')
        tags = filter_params.get('tags', '')
        
        # Log the received filters
        print(f"Filtering projects with: query={query}, category={category}, owner={owner}, tags={tags}")
        
        # Call the filtered version of get_projects
        html_table = sheets_connector.get_filtered_projects(
            query=query,
            category=category,
            owner=owner,
            tags=tags
        )
        
        # Return HTML content
        return jsonify({
            "success": True,
            "html_content": html_table,
            "filters_applied": {
                "query": query,
                "category": category,
                "owner": owner,
                "tags": tags
            }
        })
    except Exception as e:
        print(f"Error generating filtered projects table: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    # Check if we're running in test mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test mode...")
        print("\n=== Testing Google Sheets Connection ===")
        print("Fetching projects data:")
        projects_data = sheets_connector.get_projects_raw()
        print(projects_data)
        
        if len(sys.argv) > 2:
            search_query = sys.argv[2]
            print(f"\n=== Searching for: {search_query} ===")
            search_results = sheets_connector.search_projects(search_query)
            print(search_results)
        
        print("\nTest complete. Exit.")
        sys.exit(0)
    
    # Initialize data store on startup
    print("Loading data from Google Sheets...")
    try:
        sheets_connector.create_vector_store()
        print("Data store initialized!")
    except Exception as e:
        print(f"Warning: Error initializing vector store: {e}")
        print("Will continue with basic functionality")
    
    app.run(debug=True)