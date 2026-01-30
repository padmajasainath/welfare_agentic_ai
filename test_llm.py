from google import genai
import sys

api_key = "AIzaSyBKASLtfLXEQXNvkkcAM_XYIDw8pN5_Teo"
client = genai.Client(api_key=api_key)

try:
    print("Testing Gemini connection with new SDK...")
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents="Say hello in a professional aviation tone."
    )
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"FAILED: {str(e)}")
    sys.exit(1)
