# chatbot.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_response(prompt, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful executive assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        # Return the assistant's reply from the response
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {e}"
