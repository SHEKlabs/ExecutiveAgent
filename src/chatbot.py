# chatbot.py
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
def init_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    openai.api_key = api_key
    return openai.OpenAI(api_key=api_key)

# Get response from OpenAI
def get_response(prompt, model="gpt-3.5-turbo"):
    client = init_openai()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()
