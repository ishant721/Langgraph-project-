from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
import operator

class AgentState(BaseModel):
    topic: str = Field(..., description="The main topic of research")
    plan: List[str] = Field(default_factory=list, description="List of research questions")
    research_data: Annotated[List[str], operator.add] = Field(default_factory=list, description="Gathered research findings")
    draft: str = Field(default="", description="The current version of the report")
    critique: str = Field(default="", description="Feedback from the editor")
    revision_count: int = Field(default=0, description="Number of revisions made")
    approved: bool = Field(default=False, description="Whether the report is finalized")
    report_path: Optional[str] = Field(default=None, description="Path to the saved report")
    next_node: Optional[str] = Field(default=None, description="The next node to execute (for supervisor logic)")
    chat_history: List[dict] = Field(default_factory=list, description="History of Q&A sessions")
    image_urls: List[str] = Field(default_factory=list, description="List of generated image URLs for the report")
