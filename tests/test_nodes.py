# tests/test_nodes.py
import unittest
from src.state import AppState
from src.nodes.idea_node import idea_node
from src.nodes.optional_info_node import optional_info_node
from src.nodes.market_analysis_node import market_analysis_node
from src.nodes.business_plan_node import business_plan_node
from src.nodes.validation_node import validation_node
from src.nodes.risk_assessment_node import risk_assessment_node
from src.nodes.financial_node import financial_node
from src.nodes.business_plan_node import business_plan_node

class TestEntrepreneurWorkflow(unittest.TestCase):
    def setUp(self):
        self.state = AppState()

    def test_full_flow(self):
        # Provide default test idea to avoid interactive prompt
        self.state = idea_node(self.state, "I want to build a mini company for recycling with 100,000 ETB initial capital.")
        self.assertTrue(self.state.idea and len(self.state.idea) > 0)

        self.state = optional_info_node(self.state)  # will use LLM to decide/store
        self.assertTrue(self.state.extra_info and len(self.state.extra_info) > 0)

        self.state = market_analysis_node(self.state)
        self.assertTrue(self.state.market_analysis and len(self.state.market_analysis) > 0)

        self.state = business_plan_node(self.state)
        self.assertTrue(self.state.business_model and len(self.state.business_model) > 0)

        self.state = validation_node(self.state)
        self.assertTrue(self.state.validation_strategy and len(self.state.validation_strategy) > 0)

        self.state = risk_assessment_node(self.state)
        self.assertTrue(self.state.risks and len(self.state.risks) > 0)

        self.state = financial_node(self.state)
        self.assertTrue(self.state.financials and len(self.state.financials) > 0)

        self.state = business_plan_node(self.state)
        self.assertTrue(self.state.full_plan and len(self.state.full_plan) > 0)

if __name__ == "__main__":
    unittest.main()
