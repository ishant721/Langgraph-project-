import streamlit as st
import os
import time
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from graph import app
from state import AgentState

st.set_page_config(page_title="LangGraph Research Suite", layout="wide")

st.title("🚀 LangGraph Research Suite")
st.markdown("Automated Technical Research with Human-in-the-Loop")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None

with st.sidebar:
    st.header("Settings")
    topic = st.text_input("Research Topic", placeholder="e.g. Quantum Computing")
    start_btn = st.button("Start Research")
    
    if start_btn and topic:
        # Use timestamp to ensure a completely new research session every time
        st.session_state.thread_id = f"st_{topic.replace(' ', '_')[:10]}_{int(time.time())}"
        st.session_state.final_report = None
        st.success("New session started!")

if st.session_state.thread_id:
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    state = app.get_state(config)
    
    # 1. Start or Resume
    if not state.values:
        with st.status("Initializing Graph..."):
            for event in app.stream({"topic": topic}, config, stream_mode="values"):
                pass
        st.rerun()

    # 2. Handle Interrupts
    if state.next:
        next_step = state.next[0]
        
        if next_step == "researcher":
            st.warning("📋 **Action Required: Review Research Plan**")
            questions = state.values.get("plan", [])
            edited_questions = []
            for i, q in enumerate(questions):
                edited_q = st.text_input(f"Question {i+1}", value=q, key=f"q_{i}")
                edited_questions.append(edited_q)
            
            col1, col2 = st.columns(2)
            if col1.button("Approve & Continue"):
                app.update_state(config, {"plan": edited_questions})
                with st.spinner("Conducting Research..."):
                    for event in app.stream(None, config, stream_mode="values"): pass
                st.rerun()
            
        elif next_step == "publisher":
            st.info("🧐 **Action Required: Final Review**")
            st.markdown(f"**Revision Count:** {state.values.get('revision_count')}")
            st.markdown(f"**Editor Feedback:** {state.values.get('critique')}")
            
            if st.button("Confirm Publication"):
                with st.spinner("Saving Report..."):
                    for event in app.stream(None, config, stream_mode="values"): pass
                st.rerun()
        
        else:
            # Auto-run internal nodes (writer, editor)
            with st.status(f"Running {next_step}..."):
                for event in app.stream(None, config, stream_mode="values"): pass
            st.rerun()
    else:
        # Finished
        st.success("✅ Research Completed!")
        final_values = state.values
        
        # 1. Display and Download Report first
        if final_values.get("report_path"):
            report_path = final_values["report_path"]
            if os.path.exists(report_path):
                with open(report_path, "r") as f:
                    content = f.read()
                    st.session_state.final_report = content
            else:
                st.error(f"Report file not found: {report_path}. It might have failed to save.")
                st.session_state.final_report = None
                
        if st.session_state.final_report:
            content = st.session_state.final_report
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.subheader(f"📄 Research Report: {final_values.get('topic')}")
            with col2:
                st.download_button("📥 Download Markdown", content, file_name=final_values.get("report_path", "report.md"))
            
            # Show report with custom rendering for images
            with st.container():
                st.markdown("---")
                import re
                parts = re.split(r'(!\[.*?\]\(.*?\))', content)
                for part in parts:
                    img_match = re.match(r'!\[(.*?)\]\((.*?)\)', part)
                    if img_match:
                        caption, img_path = img_match.groups()
                        img_path = img_path.strip()
                        if os.path.exists(img_path):
                            st.image(img_path, caption=caption, use_container_width=True)
                        else:
                            st.error(f"Image not found: {img_path}")
                    else:
                        st.markdown(part)
                st.markdown("---")

            st.subheader("💬 Have questions? Ask below!")
            st.info(f"I can only answer questions related to: **{final_values.get('topic')}**")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for msg in final_values.get("chat_history", []):
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
            
            # Chat input at the bottom
            if prompt := st.chat_input("Ask a question about this research..."):
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    from nodes import llm
                    from langchain_core.messages import HumanMessage, SystemMessage
                    
                    qa_prompt = f"""
                    You are a technical expert on the topic: {final_values.get('topic')}.
                    Research Context: {content}
                    USER QUESTION: {prompt}
                    """
                    
                    full_response = ""
                    message_placeholder = st.empty()
                    
                    for chunk in llm.stream([
                        SystemMessage(content="Analyse the context and answer the user question politely. If off-topic, decline."),
                        HumanMessage(content=qa_prompt)
                    ]):
                        full_response += chunk.content
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                
                # Update state
                new_history = final_values.get("chat_history", []) + [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": full_response}
                ]
                app.update_state(config, {"chat_history": new_history})
                st.rerun()
else:
    st.info("Enter a topic in the sidebar to begin.")
