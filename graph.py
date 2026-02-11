import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from state import AgentState
from nodes import planner_node, researcher_node, writer_node, editor_node

def should_continue(state: AgentState):
    if state.get("approved", False) or state.get("revision_count", 0) >= 3:
        return "end"
    
    critique = state.get("critique", "")
    if "RESEARCH_NEEDED" in critique.upper():
        return "researcher"
    
    return "writer"

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

# Set entry point
workflow.set_entry_point("planner")

# Add edges
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "editor")

# Add conditional edge
workflow.add_conditional_edges(
    "editor",
    should_continue,
    {
        "end": END,
        "writer": "writer",
        "researcher": "researcher"
    }
)

# Initialize persistent checkpointer
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile the graph
# We interrupt before researcher (to approve plan) and before END (to approve final report)
app = workflow.compile(checkpointer=memory, interrupt_before=["researcher", "editor"])