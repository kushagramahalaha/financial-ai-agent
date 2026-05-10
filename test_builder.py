import os
from dotenv import load_dotenv
load_dotenv()
from graph.builder import build_graph
from Memory.user_memory import get_memory

graph = build_graph()
result = graph.invoke({
    "user_query": "can you give me the current stock price of AAPL",
    "memory": get_memory()
})
print("FINAL ANSWER:", result.get("final_answer"))
