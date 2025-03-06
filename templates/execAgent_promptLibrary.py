# templates/execAgent_promptLibrary.py

# A dictionary mapping prompt titles to prompt templates.
PROMPT_LIBRARY = {
    "show_projects": (
        "User asked: {user_query}\n\n"
        "Here is a list of projects fetched from Google Sheets:\n{projects}\n\n"
        "Please output the above list exactly as provided, as a numbered list."
    ),
    "default": (
        "User asked: {user_query}\n\n"
        "Here is the data:\n{data}\n\n"
        "Please provide a helpful response."
    )
}

def get_prompt(prompt_title, **kwargs):
    """
    Retrieves a full prompt from the library by title, and formats it with the provided keyword arguments.
    """
    prompt_template = PROMPT_LIBRARY.get(prompt_title, PROMPT_LIBRARY["default"])
    return prompt_template.format(**kwargs)
