from src.nodes.idea_node import idea_node
from src.state import EntrepreneurState

def test_idea_node_sets_state():
    state = EntrepreneurState(session_id='t1')
    state, resp = idea_node(state, 'I want to build an app that helps students learn math')
    assert state.current_idea is not None
    assert 'students' in state.current_idea
