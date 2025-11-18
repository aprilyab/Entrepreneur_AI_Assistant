from src.llm.groq_llm import ask_groq

def risk_node(state, user_text=None):
    """
    Evaluates potential risks for the startup and ways to mitigate them.
    """
    prompt = f"List potential risks for the startup idea: '{state.current_idea}' and propose mitigation strategies."
    resp = ask_groq(prompt)
    
    state.ideas_data[state.current_idea]['risks'] = resp
    state.messages.append(resp)
    return state, resp
