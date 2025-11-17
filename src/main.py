from src.graph import graph
import uuid


def run_session():
    sid = str(uuid.uuid4())
    name = input("Your name (optional): ")
    consent = input("Save session locally? (yes/no): ").strip().lower() == 'yes'
    graph.start(session_id=sid, user_name=name or None, consent=consent)
    idea = input("Describe your startup idea: ")
    output = graph.run(idea)
    print("\n=== Your Entrepreneur Plan ===")
    print(output)


if __name__ == '__main__':
    run_session()