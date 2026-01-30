import os
from google import genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class BaseAgent:
    def __init__(self, name):
        self.name = name
        # Load API key from environment
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.0-flash"

    def run(self, input_data):
        raise NotImplementedError("Agents must implement run()")