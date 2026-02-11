import os
import sys
from dotenv import load_dotenv
from graph import app

load_dotenv()

def run_research(topic: str):
    config = {"configurable": {"thread_id": "session_1"}}
    
    # Initial input
    initial_state = {
        "topic": topic,
        "plan": [],
        "research_data": [],
        "draft": "",
        "critique": "",
        "revision_count": 0,
        "approved": False
    }
    
    # Start the graph
    print(f"\nStarting research on: {topic}")
    
    while True:
        # Run until the next interrupt or end
        for event in app.stream(None if app.get_state(config).next else initial_state, config, stream_mode="values"):
            pass # We use stream to drive the graph, values are updated in state

        snapshot = app.get_state(config)
        
        # If the graph is finished
        if not snapshot.next:
            break
            
        current_node = snapshot.next[0]
        
        if current_node == "researcher":
            print("\n--- BREAKPOINT: REVIEW RESEARCH PLAN ---")
            for i, q in enumerate(snapshot.values['plan'], 1):
                print(f"{i}. {q}")
            
            choice = input("\n(A)pprove Plan, (M)odify Plan, or (Q)uit? ").strip().lower()
            if choice == 'a':
                print("Continuing to research...")
            elif choice == 'm':
                new_plan_str = input("Enter new questions separated by semicolon (;): ")
                new_plan = [q.strip() for q in new_plan_str.split(";") if q.strip()]
                app.update_state(config, {"plan": new_plan})
                print("Plan updated. Continuing...")
            else:
                print("Stopping session.")
                return

        elif current_node == "editor":
            print("\n--- BREAKPOINT: REVIEWING DRAFT ---")
            print(f"Draft Version: {snapshot.values.get('revision_count', 0)}")
            # Just letting the user know it's about to edit
            print("The editor is about to review the draft. Press Enter to continue.")
            input()

    # Final result
    final_state = app.get_state(config).values
    print("\n" + "="*50)
    print("FINAL RESEARCH REPORT")
    print("="*50)
    print(final_state["draft"])
    print("="*50)
    print(f"\nStatus: {'Approved' if final_state.get('approved') else 'Max revisions reached'}")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment. Please add it to .env")
        sys.exit(1)
    
    user_topic = input("Enter a research topic: ")
    if user_topic:
        run_research(user_topic)