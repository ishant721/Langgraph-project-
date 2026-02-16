import os
# Set dummy env vars so we can import app without real keys
os.environ["GROQ_API_KEY"] = "dummy"
os.environ["TAVILY_API_KEY"] = "dummy"

from graph import app

def save_graph_image():
    try:
        # Generate mermaid graph
        mermaid_graph = app.get_graph().draw_mermaid()
        
        with open("graph_diagram.md", "w") as f:
            f.write("# LangGraph Workflow Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_graph)
            f.write("\n```")
        
        print("Graph diagram saved to graph_diagram.md")
    except Exception as e:
        print(f"Could not generate graph diagram: {e}")

if __name__ == "__main__":
    save_graph_image()
