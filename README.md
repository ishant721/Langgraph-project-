# Adaptive Research & Content Generation Suite (Production Edition)

A robust, multi-agent AI system built with **LangGraph** that autonomously researches topics, writes technical reports, and iteratively refines them using professional editorial standards.

## 🚀 Key Features
- **Production-Grade Architecture:** Uses `Pydantic` models for strict state validation and type safety.
- **Structured AI Outputs:** Agents (Planner, Editor) return structured JSON objects, not raw text, ensuring reliability.
- **Multi-Agent Collaboration:**
  - **Planner:** Strategizes research questions.
  - **Researcher:** Uses Tavily API for real-time web data.
  - **Writer:** Synthesizes findings into Markdown reports.
  - **Editor:** Acts as a Supervisor, deciding whether to Approve, Request Revision, or Demand More Research.
  - **Publisher:** Exports the final approved report to a file.
- **Human-in-the-Loop (HIL):** Interactive CLI breakpoints allow you to review the Research Plan and the Final Draft before proceeding.
- **Persistence:** SQLite-based checkpointing (`checkpoints.sqlite`) allows sessions to be paused and resumed seamlessly.

## 🛠️ Tech Stack
- **Framework:** LangGraph, LangChain
- **Models:** OpenAI GPT-4o (Structured Output Mode)
- **Tools:** Tavily Search API
- **Validation:** Pydantic v2
- **Storage:** SQLite

## 📦 Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ishant721/Langgraph-project-.git
   cd Langgraph-project-
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file with your keys:
   ```bash
   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=tvly-...
   ```

## 🖥️ Usage

**Start a Research Session (CLI):**

```bash

python3 main.py

```



**Launch the Research Dashboard (Web):**

```bash

streamlit run dashboard.py

```

*The dashboard allows you to visualize the graph, track session history, and inspect the state of ongoing research.*



**Run Unit Tests:**


```bash
python3 -m unittest tests/test_graph.py
```

**Visualize Workflow:**
Generate a Mermaid diagram of the agent graph:
```bash
python3 visualize_graph.py
```
*(See `graph_diagram.md` for the output)*

## 📂 Project Structure
- `state.py`: Pydantic models defining the `AgentState`.
- `nodes.py`: Agent logic (Planner, Researcher, Writer, Editor, Publisher).
- `graph.py`: Graph topology, conditional routing, and persistence.
- `main.py`: Interactive CLI entry point.
- `tests/`: Unit tests verifying routing and structured outputs.