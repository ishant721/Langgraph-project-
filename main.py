import os
import sys
import logging
from dotenv import load_dotenv
from graph import app
from state import AgentState

load_dotenv()

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)

def run_suite(topic: str):
    thread_id = f"prod_{topic.replace(' ', '_')[:10]}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check for existing state
    current_state = app.get_state(config)
    
    if not current_state.values:
        print(f"\n🌟 Initializing new research session: {topic}")
        # Start initial run
        for event in app.stream({"topic": topic}, config, stream_mode="values"):
            pass
    else:
        print(f"\n🔄 Resuming existing session for: {topic}")

    while True:
        snapshot = app.get_state(config)
        
        # If finished
        if not snapshot.next:
            break
            
        next_step = snapshot.next[0]
        
        if next_step == "researcher":
            print("\n--- [ACTION REQUIRED: PLAN REVIEW] ---")
            questions = snapshot.values.get("plan", [])
            for i, q in enumerate(questions, 1):
                print(f"{i}. {q}")
            
            ans = input("\nApprove plan? (y/n) or edit questions (e): ").lower()
            if ans == 'y':
                print("Proceeding...")
                for event in app.stream(None, config, stream_mode="values"): pass
            elif ans == 'e':
                new_q = input("Enter questions (sep by ;): ").split(";")
                app.update_state(config, {"plan": [q.strip() for q in new_q if q.strip()]})
                for event in app.stream(None, config, stream_mode="values"): pass
            else:
                print("Session paused.")
                break

        elif next_step == "publisher":
            print("\n--- [FINAL REVIEW] ---")
            print(f"Revision Count: {snapshot.values.get('revision_count')}")
            print(f"Editor's Final Note: {snapshot.values.get('critique')}")
            
            ans = input("\nPublish report? (y/n): ").lower()
            if ans == 'y':
                for event in app.stream(None, config, stream_mode="values"): pass
            else:
                print("Publication cancelled.")
                break
        
        else:
            # For other nodes (writer, editor), just continue
            for event in app.stream(None, config, stream_mode="values"): pass

    final = app.get_state(config).values
    if final.get("report_path"):
        print(f"\n✅ SUCCESS: Report generated at {final['report_path']}")
    else:
        print("\n⚠️ Session ended without publication.")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY missing.")
        sys.exit(1)
        
    topic = input("Enter research topic: ").strip()
    if topic:
        run_suite(topic)