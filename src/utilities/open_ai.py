from dotenv import dotenv_values

def get_openai_api_key():
    return dotenv_values().get("OPENAI_API_KEY")