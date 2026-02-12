import os
import logging
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ResearchSuite")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
search = TavilySearch(max_results=3)

# Structured Output Models
class ResearchPlan(BaseModel):
    questions: List[str] = Field(..., description="List of 3-5 specific research questions.")

class EditorFeedback(BaseModel):
    approved: bool = Field(..., description="Whether the draft is ready for publication.")
    feedback: str = Field(..., description="Constructive feedback or 'APPROVED'.")
    research_needed: bool = Field(default=False, description="Whether more research is required.")

def planner_node(state: AgentState):
    logger.info("Starting planning phase")
    planner_llm = llm.with_structured_output(ResearchPlan)
    prompt = f"Create a comprehensive research plan for the topic: {state.topic}. Focus on technical accuracy and current trends."
    response = planner_llm.invoke([
        SystemMessage(content="You are a senior research strategist."),
        HumanMessage(content=prompt)
    ])
    return {"plan": response.questions}

def researcher_node(state: AgentState):
    logger.info("Starting research phase")
    results = []
    for question in state.plan:
        logger.info(f"Researching: {question}")
        try:
            search_results = search.invoke(question)
            results.append(f"Q: {question}\nA: {str(search_results)}")
        except Exception as e:
            logger.error(f"Search failed for {question}: {e}")
            results.append(f"Q: {question}\nError: Search unavailable.")
    
    return {"research_data": results}

def writer_node(state: AgentState):
    logger.info(f"Writing draft (Revision {state.revision_count + 1})")
    data_context = "\n\n".join(state.research_data)
    prompt = f"""
    Topic: {state.topic}
    Research Context: {data_context}
    Previous Feedback: {state.critique}
    
    Write a professional technical report in Markdown. If feedback exists, address it specifically.
    """
    response = llm.invoke([
        SystemMessage(content="You are a world-class technical writer."),
        HumanMessage(content=prompt)
    ])
    return {
        "draft": response.content,
        "revision_count": state.revision_count + 1
    }

def editor_node(state: AgentState):
    logger.info("Editing draft")
    editor_llm = llm.with_structured_output(EditorFeedback)
    prompt = f"Critically review this draft for accuracy and depth:\n\n{state.draft}"
    response = editor_llm.invoke([
        SystemMessage(content="You are a meticulous editor-in-chief."),
        HumanMessage(content=prompt)
    ])
    
    return {
        "approved": response.approved,
        "critique": response.feedback,
        "next_node": "researcher" if response.research_needed else "writer" if not response.approved else "publisher"
    }

def publisher_node(state: AgentState):
    logger.info("Publishing report")
    filename = f"report_{state.topic.lower().replace(' ', '_')}.md"
    filename = "".join([c for c in filename if c.isalnum() or c in ("_", ".")]).strip()
    
    try:
        with open(filename, "w") as f:
            f.write(state.draft)
        logger.info(f"Report saved to {filename}")
        return {"report_path": filename, "approved": True}
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        return {"approved": False}
