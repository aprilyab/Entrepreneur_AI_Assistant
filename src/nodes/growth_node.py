from src.llm.groq_llm import ask_groq

def growth_node(state, user_text=None):
    """
    Suggests growth strategies, scaling, and expansion paths.
    """
    prompt = f"Provide growth and scaling strategies for the startup idea: '{state.current_idea}'."
    resp = ask_groq(prompt)
    
    state.ideas_data[state.current_idea]['growth'] = resp
    state.messages.append(resp)
    return state, resp
