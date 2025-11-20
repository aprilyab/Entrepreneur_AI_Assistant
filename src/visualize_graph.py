# src/visualize_graph.py
from graphviz import Digraph

nodes = [
    'Start',
    'Idea Node',
    'Optional Info Node',
    'Follow-up Questions',
    'Market Analysis Node',
    'Business Model Node',
    'Validation Node',
    'Risk Assessment Node',
    'Financial Node',
    'Business Plan Node',
    'End'
]

edges = [
    ('Start', 'Idea Node'),
    ('Idea Node', 'Optional Info Node'),
    # Branch: follow-up or skip
    ('Optional Info Node', 'Follow-up Questions'),
    ('Optional Info Node', 'Market Analysis Node'),
    ('Follow-up Questions', 'Market Analysis Node'),
    ('Market Analysis Node', 'Business Model Node'),
    ('Business Model Node', 'Validation Node'),
    ('Validation Node', 'Risk Assessment Node'),
    ('Risk Assessment Node', 'Financial Node'),
    ('Financial Node', 'Business Plan Node'),
    ('Business Plan Node', 'End')
]

dot = Digraph(comment='Entrepreneur AI Graph with Branch')
for node in nodes:
    dot.node(node, node)
for start, end in edges:
    dot.edge(start, end)

dot.render('entrepreneur_graph', view=True)
