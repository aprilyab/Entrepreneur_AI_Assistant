def response_node(state) -> str:
    pieces = [f"Startup Idea: {state.startup_idea}"]
    pieces.append(f"Chosen Model: {state.chosen_model}")
    pieces.append("\nPlanned Steps:")

    for t in state.steps:
        line = f"- {t.description} | Priority: {t.priority} | Scheduled: {t.scheduled_at}"
        pieces.append(line)

    return "\n".join(pieces)
