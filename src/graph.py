from src.state import EntrepreneurState
from src.nodes.idea_node import idea_node
from src.nodes.idea_selector_node import idea_selector_node
from src.nodes.goal_node import goal_node
from src.nodes.market_node import market_node
from src.nodes.business_model_node import business_model_node
from src.nodes.validation_node import validation_node
from src.nodes.decision_node import decision_node
from src.nodes.risk_node import risk_node
from src.nodes.growth_node import growth_node
from src.nodes.response_node import response_node


class EntrepreneurGraph:
    def __init__(self):
        self.state = None

    def start(self, session_id: str, user_name: str = None, consent: bool = False):
        """Initialize the session state."""
        self.state = EntrepreneurState(session_id=session_id, user_name=user_name, consent=consent)
        return self.state

    def run_full_flow(self, user_text: str):
        """Run the full LangGraph workflow with branching logic."""
        # --- Step 1: Get Idea ---
        self.state, _ = idea_node(self.state, user_text)

        # --- Step 2: Selector (online/offline/hybrid) ---
        self.state, _ = idea_selector_node(self.state, "online")  # default for now

        # --- Step 3: Goal Node ---
        self.state, _ = goal_node(self.state)

        # --- Step 4: Branch: Market or Business Model first ---
        if getattr(self.state, "branch_to_market", True):
            self.state, _ = market_node(self.state)
            self.state, _ = validation_node(self.state)
            self.state, _ = decision_node(self.state)
        else:
            self.state, _ = business_model_node(self.state)
            self.state, _ = validation_node(self.state)
            self.state, _ = decision_node(self.state)

        # --- Step 5: Branch based on decision ---
        if getattr(self.state, "go_to_risk", True):
            self.state, _ = risk_node(self.state)
        else:
            self.state, _ = growth_node(self.state)

        # --- Step 6: Final response ---
        final_text, data = response_node(self.state)
        return final_text, data


# Instantiate the graph
graph = EntrepreneurGraph()
