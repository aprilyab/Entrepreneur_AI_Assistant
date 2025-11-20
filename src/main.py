# src/main.py
from src.graph import EntrepreneurGraph
from src.nodes.followup_node import followup_node

def main():
    print("=== Entrepreneur AI Assistant ===")
    idea_text = input("Enter your startup idea: ").strip()

    # Initialize graph
    graph = EntrepreneurGraph(session_id="001", user_name="Henok")

    # Run full workflow
    final_state = graph.run(idea_text)

    # Show full plan
    print("\n=== Full Business Plan ===")
    print(final_state.full_plan or "[No plan generated]")

    # Ask follow-up questions
    print("\nYou can now ask follow-up questions. Type 'exit' to quit.")
    while True:
        question = input("\nYour question: ").strip()
        if question.lower() == "exit":
            print("Goodbye!")
            break
        _, answer = followup_node(final_state, question)
        print("\nAnswer:\n", answer)

if __name__ == "__main__":
    main()
