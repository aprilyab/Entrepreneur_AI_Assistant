# src/llm/gemini_llm.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment (.env).")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

def ask_gemini(prompt: str) -> str:
    llm = get_llm()
    resp = llm.invoke(prompt)
    return resp.content
