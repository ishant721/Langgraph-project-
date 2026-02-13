import streamlit as st
import sqlite3
import pandas as pd
from graph import app
from state import AgentState
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LangGraph Research Dashboard", layout="wide")

st.title("🛡️ LangGraph Adaptive Research Dashboard")

# Sidebar for session management
st.sidebar.header("Session Management")
conn = sqlite3.connect("checkpoints.sqlite")
try:
    sessions = pd.read_sql_query("SELECT DISTINCT thread_id FROM checkpoints", conn)
    selected_thread = st.sidebar.selectbox("Select Research Thread", sessions['thread_id'] if not sessions.empty else ["None"])
except Exception:
    st.sidebar.warning("No sessions found yet.")
    selected_thread = "None"

# Graph Visualization
st.header("🗺️ Workflow Visualization")
try:
    # Generate Mermaid
    mermaid_code = app.get_graph().draw_mermaid()
    st.markdown(f"```mermaid
{mermaid_code}
```")
    st.info("💡 Tip: Use a browser extension or paste into Mermaid Live Editor to see the full rendered diagram.")
except Exception as e:
    st.error(f"Error drawing graph: {e}")

# Session Details
if selected_thread != "None":
    st.header(f"📊 State for Thread: {selected_thread}")
    config = {"configurable": {"thread_id": selected_thread}}
    state = app.get_state(config)
    
    if state.values:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Current Topic")
            st.write(state.values.get("topic", "N/A"))
            
            st.subheader("Research Plan")
            for q in state.values.get("plan", []):
                st.write(f"- {q}")
        
        with col2:
            st.subheader("Metadata")
            st.write(f"Revisions: {state.values.get('revision_count', 0)}")
            st.write(f"Status: {'✅ Approved' if state.values.get('approved') else '⏳ In Progress'}")
            st.write(f"Report Path: {state.values.get('report_path', 'N/A')}")

        st.divider()
        st.subheader("Latest Draft Preview")
        st.text_area("Draft Content", state.values.get("draft", ""), height=300)
        
        st.subheader("Editor's Critique")
        st.info(state.values.get("critique", "No critique yet."))
    else:
        st.write("No data found for this thread.")

st.sidebar.divider()
if st.sidebar.button("Refresh Dashboard"):
    st.rerun()
