from typing import Annotated, List, TypedDict, Union
import operator

class AgentState(TypedDict):
    topic: str
    plan: List[str]
    research_data: Annotated[List[str], operator.add]
    draft: str
    critique: str
    revision_count: int
    approved: bool
