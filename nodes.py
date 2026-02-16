import os
import logging
import requests
import time
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ResearchSuite")

# Initialize the LLM
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
search = TavilySearch(max_results=3)

# Structured Output Models
class ResearchPlan(BaseModel):
    questions: List[str] = Field(..., description="List of 3-4 specific technical research questions.")

class EditorFeedback(BaseModel):
    approved: bool = Field(..., description="Whether the draft is ready for publication.")
    feedback: str = Field(..., description="A short summary of required changes or 'APPROVED'.")
    research_needed: bool = Field(default=False, description="Whether more research is required.")

def planner_node(state: AgentState):
    logger.info("Starting planning phase")
    planner_llm = llm.with_structured_output(ResearchPlan)
    prompt = f"Create a targeted research plan for: {state.topic}. Focus on core architecture and essential mathematical derivations. Aim for high information density."
    response = planner_llm.invoke([
        SystemMessage(content="You are a senior research strategist specializing in concise yet deep technical analysis."),
        HumanMessage(content=prompt)
    ])
    return {"plan": response.questions}

def researcher_node(state: AgentState):
    logger.info("Starting research phase")
    results = []
    for question in state.plan[:4]: 
        logger.info(f"Researching: {question}")
        try:
            search_results = search.invoke(question)
            results.append(f"Q: {question}\nA: {str(search_results)[:1500]}") 
        except Exception as e:
            logger.error(f"Search failed for {question}: {e}")
    
    return {"research_data": results}

def writer_node(state: AgentState):
    logger.info(f"Writing draft (Revision {state.revision_count + 1})")
    data_context = "\n\n".join(state.research_data)
    
    prompt = r"""
    Topic: """ + state.topic + r"""
    Research Context: """ + data_context + r"""
    
    TASK: Write a RIGOROUS technical report.
    
    MATHEMATICAL REQUIREMENTS (CRITICAL):
    1. Every single mathematical symbol, variable (like x, y, n), and formula MUST be in LaTeX.
    2. For BLOCK formulas (on a new line), you MUST use double dollar signs: $$ formula $$.
    3. For INLINE math (within a sentence), you MUST use single dollar signs: $ symbol $.
    4. DO NOT use \[ \], \( \), or any other delimiters. ONLY $ and $$.
    
    STRUCTURE:
    - Use clear headings.
    - Provide deep mathematical derivations for all core concepts.
    - Address any previous critique: """ + state.critique + r"""
    """
    response = llm.invoke([
        SystemMessage(content="You are a world-class technical author. You strictly follow formatting rules for math."),
        HumanMessage(content=prompt)
    ])
    
    content = response.content
    
    # Post-processing to fix common LaTeX delimiter mistakes
    content = content.replace(r"\[", "$$").replace(r"\]", "$$")
    content = content.replace(r"\(", "$").replace(r"\)", "$")
    
    return {
        "draft": content,
        "revision_count": state.revision_count + 1
    }

def editor_node(state: AgentState):
    logger.info("Editing draft - waiting 5s to avoid rate limits")
    time.sleep(5)
    
    try:
        editor_llm = llm.with_structured_output(EditorFeedback)
        prompt = f"Critically review this draft for topic '{state.topic}'. Ensure it has math ($$). Be concise.\n\nDraft: {state.draft[:4000]}"
        response = editor_llm.invoke([
            SystemMessage(content="You are a meticulous editor-in-chief. Use concise feedback."),
            HumanMessage(content=prompt)
        ])
    except Exception as e:
        logger.error(f"Structured output failed: {e}")
        return {
            "approved": False,
            "critique": "Draft needs more depth and mathematical rigor.",
            "next_node": "writer"
        }
    
    return {
        "approved": response.approved,
        "critique": response.feedback,
        "next_node": "researcher" if response.research_needed else "writer" if not response.approved else "publisher"
    }

def qa_node(state: AgentState, user_question: str):
    logger.info(f"Answering user question: {user_question}")
    prompt = f"""
    You are a technical expert on the topic: {state.topic}.
    Research Context: {state.draft}
    USER QUESTION: {user_question}
    """
    response = llm.invoke([
        SystemMessage(content="Analyse the context and answer the user question politely. If off-topic, decline."),
        HumanMessage(content=prompt)
    ])
    
    new_history = state.chat_history + [{"role": "user", "content": user_question}, {"role": "assistant", "content": response.content}]
    return {"chat_history": new_history}

def publisher_node(state: AgentState):
    logger.info("Publishing report")
    filename = f"report_{state.topic.lower().replace(' ', '_')}.md"
    filename = "".join([c for c in filename if c.isalnum() or c in ("_", ".")]).strip()
    
    try:
        with open(filename, "w") as f:
            f.write(state.draft)
        return {"report_path": filename, "approved": True}
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
        return {"approved": False}
