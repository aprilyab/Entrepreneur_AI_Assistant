from typing import Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model="gpt-4o-mini",   
    temperature=0.7,
    api_key="YOUR_OPENAI_KEY"
)

def clarifier_node(state) -> Tuple:
    if state.pending_clarifications:
        question = state.pending_clarifications.pop(0)

        response = llm([
            SystemMessage(content="You are an AI entrepreneur assistant."),
            HumanMessage(content=question)
        ])

        return state, response.content.strip()

    return state, None
