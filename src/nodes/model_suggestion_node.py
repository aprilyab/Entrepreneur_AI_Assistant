from typing import Tuple
from openai import OpenAI
from langchain.schema import HumanMessage, SystemMessage

client = OpenAI(api_key="YOUR_OPENAI_KEY")


MODEL = "gpt-4o-mini"    


def model_suggestion_node(state, user_text: str) -> Tuple:
    state.messages.append(user_text)

    prompt = (
        f"The user described this preference: '{user_text}'. "
        "Suggest 3–5 suitable business models for this startup, "
        "each with a short explanation."
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an AI startup mentor."},
            {"role": "user", "content": prompt},
        ]
    )

    output = response.choices[0].message.content
    suggestions = [line.strip() for line in output.split("\n") if line.strip()]

    state.chosen_model = suggestions[0] if suggestions else None

    msg = (
        "Possible business models:\n"
        + "\n".join(suggestions)
        + "\n\nWhich one do you prefer?"
    )

    return state, msg
