from typing import Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


llm = ChatOpenAI(
    model="gpt-4o-mini",  
    temperature=0.7,
    api_key="YOUR_OPENAI_KEY"
)

def priority_node(state) -> Tuple:
    if not state.steps:
        return state, "No steps to prioritize."

    prompt = (
        "Prioritize the following startup steps based on impact and feasibility:\n"
        + "\n".join([t.description for t in state.steps])
    )

    response = llm([
        SystemMessage(content="You are an AI startup mentor."),
        HumanMessage(content=prompt)
    ])

    priorities = response.content.strip().split('\n')

    # Assign priorities to each task
    for t, p in zip(state.steps, priorities):
        t.priority = p.strip() if p else "Medium"

    msg = "Steps have been prioritized. Shall I suggest a timeline?"

    return state, msg
