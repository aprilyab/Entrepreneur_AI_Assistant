import os
from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")



def ask_groq(prompt: str, model: str = None, temperature: float = 0.2) -> str:
    """Send prompt to Groq-compatible model and return text response.
    Replace the internals with your provider's SDK call.
    """
    model = model or GROQ_MODEL
    return f"[LLM response placeholder for model={model}]\n{prompt}"