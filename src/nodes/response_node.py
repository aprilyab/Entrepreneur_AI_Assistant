from src.llm.groq_llm import ask_groq

def response_node(state, user_text=None):
    """
    Consolidates all the previous outputs into a final plan for the user.
    """
    idea = state.current_idea or "N/A"
    data = state.ideas_data.get(idea, {})
    
    prompt = f"""
You are an entrepreneurial assistant. Summarize a complete startup plan for the idea: '{idea}'.
Include:
- Idea overview
- Market research
- Funding advice
- Business model
- Schedule
- Marketing
- Validation
- Risks
- Growth strategies
Use the following info if available: {data}
"""
    resp = ask_groq(prompt)
    state.messages.append(resp)
    return resp, data
