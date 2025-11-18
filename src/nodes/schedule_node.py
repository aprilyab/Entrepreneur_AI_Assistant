from src.llm.groq_llm import ask_groq

def schedule_node(state, user_text=None):
    """
    Suggests scheduling/timeline for tasks or startup milestones.
    """
    prompt = f"Based on the startup idea '{state.current_idea}', suggest a timeline or schedule for implementing key steps."
    resp = ask_groq(prompt)
    
    # Save in state
    state.ideas_data[state.current_idea]['schedule'] = resp
    state.messages.append(resp)
    return state, resp
