import unittest
from unittest.mock import MagicMock, patch
import os
from pydantic import BaseModel

# Mock env
os.environ["OPENAI_API_KEY"] = "fake"
os.environ["TAVILY_API_KEY"] = "fake"

from state import AgentState
from nodes import planner_node, editor_node
from graph import router_logic

class TestProductionGraph(unittest.TestCase):

    def test_planner_structured(self):
        mock_llm = MagicMock()
        # Simulate structured output
        class MockOutput(BaseModel):
            questions: list = ["Q1", "Q2"]
        
        mock_llm.with_structured_output.return_value.invoke.return_value = MockOutput()

        with patch('nodes.llm', mock_llm):
            state = AgentState(topic="AI")
            result = planner_node(state)
            self.assertEqual(len(result["plan"]), 2)

    def test_router_logic_publisher(self):
        # Test max revisions
        state = AgentState(topic="AI", revision_count=3, approved=False)
        self.assertEqual(router_logic(state), "publisher")
        
        # Test editor recommendation
        state = AgentState(topic="AI", revision_count=1, next_node="researcher")
        self.assertEqual(router_logic(state), "researcher")

    def test_editor_structured(self):
        mock_llm = MagicMock()
        class MockEditor(BaseModel):
            approved: bool = True
            feedback: str = "Good"
            research_needed: bool = False
            
        mock_llm.with_structured_output.return_value.invoke.return_value = MockEditor()
        
        with patch('nodes.llm', mock_llm):
            state = AgentState(topic="AI", draft="Great draft")
            result = editor_node(state)
            self.assertTrue(result["approved"])
            self.assertEqual(result["next_node"], "publisher")

if __name__ == "__main__":
    unittest.main()