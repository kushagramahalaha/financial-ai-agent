from typing import TypedDict

class AgentState(TypedDict):
    user_query: str
    memory: dict
    risk: str
    goal: str
    rag_context: str
    tool_output: str
    final_answer: str