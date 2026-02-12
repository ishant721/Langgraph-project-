import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import AgentState
from nodes import planner_node, researcher_node, writer_node, editor_node, publisher_node

def router_logic(state: AgentState):
    # If max revisions reached, force to publisher
    if state.revision_count >= 3 and not state.approved:
        return "publisher"
    
    # Use the next_node determined by the editor
    return state.next_node or "writer"

# Define the graph with Pydantic state
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)
workflow.add_node("publisher", publisher_node)

# Entry point
workflow.set_entry_point("planner")

# Static edges
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "editor")
workflow.add_edge("publisher", END)

# Conditional routing from editor
workflow.add_conditional_edges(
    "editor",
    router_logic,
    {
        "publisher": "publisher",
        "writer": "writer",
        "researcher": "researcher"
    }
)

# Persistence
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile with interrupts for HIL (Human-in-the-Loop)
app = workflow.compile(
    checkpointer=memory, 
    interrupt_before=["researcher", "publisher"]
)