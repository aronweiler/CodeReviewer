from dotenv import dotenv_values

def get_openai_api_key(self):
    return dotenv_values().get("OPENAI_API_KEY")