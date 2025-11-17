from typing import Tuple
from uuid import uuid4
from src.state import Task
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


llm = ChatOpenAI(
    model="gpt-4o-mini",   
    temperature=0.7,
    api_key="YOUR_OPENAI_KEY"
)

def plan_node(state) -> Tuple:
    prompt = (
        f"The user wants to start a company: '{state.startup_idea}'. "
        "Generate 4-6 actionable, ordered steps to start this company. "
        "Each step should be a concise sentence."
    )

    response = llm([
        SystemMessage(content="You are an AI startup mentor."),
        HumanMessage(content=prompt)
    ])

   
    steps_text = response.content.strip().split('\n')
    steps = [
        Task(id=str(uuid4()), description=line.strip())
        for line in steps_text if line.strip()
    ]

    state.steps.extend(steps)
    msg = "LLM-generated plan steps have been created. Do you want to prioritize them?"

    return state, msg
