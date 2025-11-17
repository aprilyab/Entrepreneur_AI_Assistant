from typing import Tuple
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


llm = ChatOpenAI(
    model="gpt-4o-mini",  
    temperature=0.7,
    api_key="YOUR_OPENAI_KEY"
)

def schedule_node(state) -> Tuple:
    if not state.steps:
        return state, "No steps to schedule."

    prompt = (
        "Suggest realistic timelines for these startup steps:\n"
        + "\n".join([t.description for t in state.steps])
    )

    response = llm([
        SystemMessage(content="You are an AI startup mentor."),
        HumanMessage(content=prompt)
    ])

    schedule_lines = response.content.strip().split('\n')
    now = datetime.now()

    # Assign schedules to each step
    for t, sched in zip(state.steps, schedule_lines):
        t.scheduled_at = sched.strip() or (now + timedelta(days=7)).isoformat()

    msg = "Timelines generated. Ready to see the full plan?"

    return state, msg
