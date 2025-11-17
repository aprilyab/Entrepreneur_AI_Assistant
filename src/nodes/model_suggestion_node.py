from typing import Tuple
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key="YOUR_OPENAI_KEY")


def model_suggestion_node(state, user_text: str) -> Tuple:
    state.messages.append(user_text)
    prompt = f"The user described their preference: '{user_text}'. Suggest 3-5 suitable business models for this startup, each with a short explanation."
    response = llm([SystemMessage(content="You are an AI startup mentor."), HumanMessage(content=prompt)])
    suggestions = [line.strip() for line in response.content.split('\n') if line.strip()]
    state.chosen_model = suggestions[0] if suggestions else None
    msg = f"Possible business models:\n{'\n'.join(suggestions)}\nWhich one do you prefer?"
    return state, msg