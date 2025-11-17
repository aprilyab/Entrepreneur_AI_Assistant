from src.state import EntrepreneurState
from src.nodes.goal_node import goal_node
from src.nodes.model_suggestion_node import model_suggestion_node
from src.nodes.clarifier_node import clarifier_node
from src.nodes.plan_node import plan_node
from src.nodes.priority_node import priority_node
from src.nodes.schedule_node import schedule_node
from src.nodes.response_node import response_node
from uuid import uuid4


class EntrepreneurGraph:
    def __init__(self):
        self.state = None


    def start(self, session_id: str, user_name: str = None, consent: bool = False):

        self.state = EntrepreneurState(session_id=session_id, user_name=user_name, consent=consent)
        return self.state


    def run(self, user_input: str) -> str:
        self.state, _ = goal_node(self.state, user_input)
        self.state, _ = model_suggestion_node(self.state, user_input)
        self.state, _ = clarifier_node(self.state)
        self.state, _ = plan_node(self.state)
        self.state, _ = priority_node(self.state)
        self.state, _ = schedule_node(self.state)
        final = response_node(self.state)
        return final


graph = EntrepreneurGraph()