# src/graph.py
from src.state import AppState
from src.memory import memory_store
from src.nodes.idea_node import idea_node
from src.nodes.optional_info_node import optional_info_node
from src.nodes.market_analysis_node import market_analysis_node
from src.nodes.business_model_node import business_model_node
from src.nodes.decision_node import decision_node
from src.nodes.risk_assessment_node import risk_node
from src.nodes.growth_node import growth_node
from src.nodes.business_plan_node import business_plan_node

class EntrepreneurGraph:
    def __init__(self, session_id: str = "001", user_name: str = None):
        self.state = AppState(session_id=session_id, user_name=user_name)
        self.memory = memory_store.MemoryStore()

    def run(self, user_text: str):
        # Step 1: Idea
        self.state = idea_node(self.state, user_text)

        # Step 2: Optional info
        self.state = optional_info_node(self.state)

        # Step 3: Business Model
        self.state = business_model_node(self.state)

        # Step 4: Decision Node
        self.state = decision_node(self.state)  # if decision_node also now returns state only

        # Step 5: Branch based on decision
        if self.state.go_to_risk:
            self.state = risk_node(self.state)
        else:
            self.state = growth_node(self.state)

        # Step 6: Generate final plan
        self.state = business_plan_node(self.state)


        # Step 7: Final Business Plan
        self.state = business_plan_node(self.state)

        # Step 8: Save session to memory
        self.memory.save_session({
            "session_id": self.state.session_id,
            "user_name": self.state.user_name,
            "idea": self.state.idea,
            "plan": self.state.full_plan,
        })

        return self.state
