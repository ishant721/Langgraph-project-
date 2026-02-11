import unittest
from unittest.mock import MagicMock, patch
import os

# Set dummy env vars for testing
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["TAVILY_API_KEY"] = "fake-key"

from state import AgentState
from nodes import planner_node, editor_node
from graph import should_continue

class TestGraphNodes(unittest.TestCase):

    def test_planner_node(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "- Question 1\n- Question 2\n- Question 3"
        mock_llm.invoke.return_value = mock_response

        with patch('nodes.llm', mock_llm):
            state = {"topic": "AI Agents"}
            result = planner_node(state)
            self.assertEqual(len(result["plan"]), 3)

    def test_editor_node_research_needed(self):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "RESEARCH_NEEDED: We need more data on GPT-5."
        mock_llm.invoke.return_value = mock_response

        with patch('nodes.llm', mock_llm):
            state = {"draft": "Data on GPT-4."}
            result = editor_node(state)
            self.assertFalse(result["approved"])
            self.assertIn("RESEARCH_NEEDED", result["critique"])

    def test_routing_to_researcher(self):
        state = {
            "approved": False,
            "revision_count": 1,
            "critique": "RESEARCH_NEEDED: missing facts."
        }
        next_node = should_continue(state)
        self.assertEqual(next_node, "researcher")

    def test_routing_to_writer(self):
        state = {
            "approved": False,
            "revision_count": 1,
            "critique": "Fix the formatting."
        }
        next_node = should_continue(state)
        self.assertEqual(next_node, "writer")

    def test_routing_to_end(self):
        state = {"approved": True}
        self.assertEqual(should_continue(state), "end")
        
        state = {"approved": False, "revision_count": 3}
        self.assertEqual(should_continue(state), "end")

if __name__ == "__main__":
    unittest.main()
