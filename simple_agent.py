# simple_agent.py
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.utils.function_calling import convert_to_openai_function

class SimpleAgent:
    def __init__(self, tools=None):
        """
        Initialize a simple agent with OpenAI function calling
        
        Args:
            tools: List of LangChain tools
        """
        self.tools = tools or []
        
        # Initialize the LLM
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Format our tools for the OpenAI function calling format
        llm_with_tools = self.llm.bind(
            functions=[convert_to_openai_function(t) for t in self.tools]
        )
        
        # Create a prompt template that includes agent_scratchpad
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Executive Assistant AI that helps manage projects and tasks.
You have access to Google Sheets data containing project information.
Be concise, helpful, and professional in your responses.
Always use the tools available to you when responding to questions about projects."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=llm_with_tools,
            prompt=prompt,
            tools=self.tools
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    def process_query(self, user_query):
        """
        Process a user query using the agent
        
        Args:
            user_query: String containing the user's query
        
        Returns:
            Agent's response as a string
        """
        try:
            result = self.agent_executor.invoke({"input": user_query})
            return result.get("output", "I couldn't process your request.")
        except Exception as e:
            print(f"Error in agent processing: {e}")
            import traceback
            traceback.print_exc()
            return f"I encountered an error while processing your request. Please try again."