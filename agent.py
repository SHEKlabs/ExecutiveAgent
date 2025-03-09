# agent.py
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.callbacks.base import BaseCallbackHandler

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token, **kwargs):
        self.queue.put(token)

class ExecutiveAgent:
    def __init__(self, tools=None, streaming_queue=None, model="gpt-4"):
        self.tools = tools or []
        
        # Create LLM instance
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.5,
            streaming=True if streaming_queue else False,
            callbacks=[StreamingCallbackHandler(streaming_queue)] if streaming_queue else None
        )
        
        # Using a simpler prompt template for ReAct
        system_template = """You are an Executive Assistant AI that helps manage projects and tasks. 
You have access to Google Sheets data containing project information.
Be concise, helpful, and professional in your responses.
When asked about projects, utilize the GetProjects tool to fetch the latest data.
When asked specifically about certain project details, use the SearchProjects tool.

When displaying project information:
1. Present data in the exact table format it's provided to you
2. Maintain the markdown table structure for readability
3. Don't reformat or simplify the data structure provided by the tools
4. If a user asks for specific details about projects, use the SearchProjects tool"""
        
        # Create prompt template that handles agent_scratchpad as messages
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create a memory instance
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
    
    def process_query(self, user_query):
        """Process a user query through the agent"""
        try:
            response = self.agent_executor.invoke({"input": user_query})
            return response.get('output', "I couldn't generate a response. Please try again.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error processing query: {e}")
            return f"I encountered an error while processing your request. Please try again with a different question or phrase."