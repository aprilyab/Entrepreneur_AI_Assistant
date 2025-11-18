from src.llm.groq_llm import ask_groq

def validation_node(state, user_text=None):
    """
    Suggests ways to validate the startup idea (customer feedback, MVP, etc.).
    """
    prompt = f"Provide validation strategies for the startup idea: '{state.current_idea}'."
    resp = ask_groq(prompt)
    
    state.ideas_data[state.current_idea]['validation'] = resp
    state.messages.append(resp)
    return state, resp
