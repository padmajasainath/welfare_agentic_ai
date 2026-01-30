from google import genai
import sys

api_key = "AIzaSyBKASLtfLXEQXNvkkcAM_XYIDw8pN5_Teo"
client = genai.Client(api_key=api_key)

try:
    print("Listing available models...")
    for model in client.models.list():
        print(f"Model ID: {model.name}")
except Exception as e:
    print(f"FAILED: {str(e)}")
    sys.exit(1)
