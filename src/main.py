from src.state import EntrepreneurState
from src.nodes.idea_node import idea_node
import uuid

def run_graph():
    state = EntrepreneurState(session_id=str(uuid.uuid4()))
    current_node = idea_node

    while current_node is not None:
        state, output, next_node = current_node(state)
        print("\n", output, "\n")
        current_node = next_node

if __name__ == "__main__":
    run_graph()
