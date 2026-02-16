# LangGraph Research Suite: Project Documentation

## 1. Overview
**LangGraph Research Suite** is an autonomous, agentic research system built with [LangGraph](https://langchain-ai.github.io/langgraph/). It orchestrates a team of AI agents—Planner, Researcher, Writer, Editor, and Publisher—to conduct deep technical research, draft rigorous reports with mathematical derivations, and publish them. It features a **Streamlit** UI for user interaction, real-time feedback, and post-research Q&A.

**Key Features:**
*   **Multi-Agent Workflow:** Cyclic graph with specialized roles (Planner -> Researcher -> Writer -> Editor -> Publisher).
*   **Human-in-the-Loop:** Users review the research plan and the final draft before publication.
*   **Deep Technical Content:** Optimized for generating high-density technical reports with LaTeX-formatted math.
*   **Persistence:** Uses SQLite to save state, allowing sessions to be paused, resumed, and recovered.
*   **Interactive UI:** Streamlit interface for starting sessions, visualizing progress, downloading reports, and chatting with the research context.

## 2. Architecture

### 2.1 State Management (`state.py`)
The system maintains a shared state object (`AgentState`) across all nodes:
*   `topic`: The research subject.
*   `plan`: List of research questions.
*   `research_data`: Accumulated findings from the researcher.
*   `draft`: The current markdown report.
*   `critique`: Feedback from the editor.
*   `revision_count`: Tracks iteration cycles.
*   `chat_history`: Stores Q&A history for the post-research chat.

### 2.2 Nodes (`nodes.py`)
Each function represents a distinct agent or step in the graph:
*   **`planner_node`**: Generates specific, high-impact research questions using an LLM.
*   **`researcher_node`**: Uses `TavilySearch` to gather information for each question. Truncates results to manage token limits.
*   **`writer_node`**: Synthesizes research into a detailed technical draft. Enforces strict LaTeX formatting for math (`$$` for block, `$` for inline).
*   **`editor_node`**: Reviews the draft for quality, depth, and math formatting. Decides whether to approve or request revisions.
*   **`publisher_node`**: Saves the approved draft to a local Markdown file.
*   **`qa_node`**: (Used via UI) Answers user questions based on the final report context.

### 2.3 Graph Workflow (`graph.py`)
The `StateGraph` defines the execution flow:
1.  **Start** -> `planner`
2.  `planner` -> `researcher` (Interrupt before `researcher` for plan review)
3.  `researcher` -> `writer`
4.  `writer` -> `editor`
5.  `editor` -> **Conditional Edge**:
    *   If `approved`: -> `publisher` (Interrupt before `publisher` for final review)
    *   If `research_needed`: -> `researcher`
    *   If needs revision: -> `writer`
6.  `publisher` -> **End**

### 2.4 User Interface (`app_streamlit.py`)
*   **Session Management**: Generates unique `thread_id`s for each research run using timestamps.
*   **Rendering**: Displays the research report with support for LaTeX math.
*   **Chat**: Provides a streaming chat interface to ask follow-up questions about the generated report.

## 3. Setup & Installation

### Prerequisites
*   Python 3.10+
*   API Keys for **Groq** (LLM) and **Tavily** (Search).

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd langgraph
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```ini
    GROQ_API_KEY=your_groq_api_key
    TAVILY_API_KEY=your_tavily_api_key
    ```

## 4. Usage

### Running the UI
Launch the Streamlit application:
```bash
streamlit run app_streamlit.py
```

### Workflow Steps
1.  **Enter Topic**: Type your research topic in the sidebar and click "Start Research".
2.  **Plan Review**: The system will pause after planning. Review the questions in the UI. You can edit them or approve as is.
3.  **Research & Drafting**: The agents will conduct research and write the report. This may take a minute.
4.  **Final Review**: The system pauses again before publishing. You'll see the editor's feedback. Click "Confirm Publication".
5.  **View & Chat**: The final report is displayed. You can download the Markdown file or use the chat box below to ask questions about the findings.

## 5. Configuration

*   **Model**: Currently configured to use `openai/gpt-oss-120b` via Groq in `nodes.py`.
*   **Token Limits**: Research context is truncated to ~1500 chars per result to fit within Groq's free tier limits (8k tokens).
*   **Persistence**: Checkpoints are saved to `checkpoints.sqlite`.

## 6. Project Structure
```
langgraph/
├── app_streamlit.py    # Main UI application
├── graph.py            # LangGraph workflow definition
├── nodes.py            # Agent logic and tools
├── state.py            # Pydantic state schema
├── main.py             # CLI entry point (alternative to UI)
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
└── checkpoints.sqlite  # Session database (auto-generated)
```
