import os
from dotenv import load_dotenv
from google import genai  # Make sure you installed `google-genai` SDK

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

def ask_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    """
    Sends a prompt to Gemini and returns the text response.
    """
    resp = client.models.generate_content(
        model=model,
        contents=[{"text": prompt}],
    )
    return resp.text
