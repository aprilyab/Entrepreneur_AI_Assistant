from src.llm.groq_llm import ask_groq

def marketing_node(state, user_text=None):
    """
    Generates marketing ideas and strategies for the current startup idea.
    """
    prompt = f"Suggest marketing strategies for the startup idea: '{state.current_idea}'. Include channels, approach, and key messaging."
    resp = ask_groq(prompt)
    
    state.ideas_data[state.current_idea]['marketing'] = resp
    state.messages.append(resp)
    return state, resp
