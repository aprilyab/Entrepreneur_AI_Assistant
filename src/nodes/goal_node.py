from typing import Tuple
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", openai_api_key="YOUR_OPENAI_KEY")


def goal_node(state, user_text: str) -> Tuple:
    state.messages.append(user_text)
    prompt = f"The user wants to start a business: '{user_text}'. Summarize this idea concisely and ask for clarification about the preferred business model (online, offline, hybrid)."
    response = llm([SystemMessage(content="You are an AI entrepreneur assistant."), HumanMessage(content=prompt)])
    state.startup_idea = user_text
    return state, response.content.strip()