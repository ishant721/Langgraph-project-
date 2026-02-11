# Adaptive Research & Content Generation Suite

This project demonstrates a multi-agent research and writing system built with **LangGraph**.

## Features
- **Multi-Agent Coordination**: Orchestrates specialized agents for planning, research, writing, and editing.
- **Human-in-the-Loop**: Interrupts the workflow to allow user approval or modification of the research plan.
- **Persistence**: Uses SQLite-based checkpointers (can be easily swapped) to save state across sessions.
- **Cyclic Refinement**: The Editor agent can send the draft back to the Writer for improvements.

## Prerequisites
- Python 3.10+
- OpenAI API Key
- Tavily API Key (for search)

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` and add your API keys.

## Running the Application
To start a research session, run:
```bash
python3 main.py
```

## Running Tests
To run the unit tests:
```bash
python3 -m unittest tests/test_graph.py
```

## Project Structure
- `state.py`: Defines the graph state schema.
- `nodes.py`: Contains the logic for individual agents.
- `graph.py`: Defines the graph structure and edges.
- `main.py`: CLI interface and human-in-the-loop logic.
- `tests/`: Unit tests for the system.
