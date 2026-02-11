import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from state import AgentState

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o")

# Initialize the Search Tool
search = TavilySearch(max_results=3)

def planner_node(state: AgentState):
    print("---PLANNING RESEARCH---")
    topic = state["topic"]
    prompt = f"Create a list of 3-5 specific research questions to investigate the topic: {topic}. Return only the questions as a bulleted list."
    response = llm.invoke([SystemMessage(content='You are a research planner.'), HumanMessage(content=prompt)])
    questions = [q.strip("- ") for q in response.content.split("\n") if q.strip()]
    return {"plan": questions}

def researcher_node(state: AgentState):
    print("---RESEARCHING---")
    questions = state["plan"]
    # We only research questions that haven't been answered well yet
    # For simplicity in this demo, we research the whole plan
    results = []
    for question in questions:
        print(f"Searching for: {question}")
        try:
            search_results = search.invoke(question)
            results.append(f"Question: {question}\nAnswer: {str(search_results)}")
        except Exception as e:
            results.append(f"Question: {question}\nError: Could not perform search ({str(e)})")
    
    return {"research_data": results}

def writer_node(state: AgentState):
    print("---WRITING DRAFT---")
    topic = state["topic"]
    data = "\n\n".join(state["research_data"])
    critique = state.get("critique", "No critique yet.")
    
    prompt = f"""
    Topic: {topic}
    Research Data: {data}
    Previous Critique: {critique}
    
    Write a comprehensive report in Markdown format based on the research data and addressing the critique if any.
    If you are revising, focus heavily on fixing the specific issues mentioned in the critique.
    """
    response = llm.invoke([SystemMessage(content="You are a professional technical writer."), HumanMessage(content=prompt)])
    return {"draft": response.content, "revision_count": state.get("revision_count", 0) + 1}

def editor_node(state: AgentState):
    print("---EDITING DRAFT---")
    draft = state["draft"]
    
    prompt = f"""
    Review the following draft for accuracy, clarity, and tone. 
    If it's excellent and needs no more work, say 'APPROVED'. 
    Otherwise, provide specific constructive feedback.
    If you think more research is needed, start your feedback with 'RESEARCH_NEEDED:'.
    
    Draft:
    {draft}
    """
    response = llm.invoke([SystemMessage(content="You are an expert editor."), HumanMessage(content=prompt)])
    
    content = response.content
    if "APPROVED" in content.upper() and len(content) < 20:
        return {"approved": True, "critique": ""}
    else:
        return {"approved": False, "critique": content}
