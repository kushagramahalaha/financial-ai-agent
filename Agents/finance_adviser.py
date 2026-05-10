import os
from dotenv import load_dotenv

from Memory.user_memory import get_memory
from Memory.extractor import process_and_store
from graph.builder import build_graph

load_dotenv()

# -----------------------------
# Simple Cache (IMPORTANT)
# -----------------------------
cache = {}

def get_cached(query):
    return cache.get(query)

def set_cache(query, response):
    cache[query] = response

def main():
    print("Welcome to the Financial AI Advisor (CLI Mode)")
    graph = build_graph()
    
    while True:
        question = input("\nAsk a financial question (or 'exit' to quit): ")
        
        if question.lower() in ["exit", "quit"]:
            break
            
        # Check cache first
        cached_answer = get_cached(question)
        if cached_answer:
            print("\nAI Answer (Cached):\n")
            print(cached_answer)
            continue
            
        # Update memory based on user input
        process_and_store(question)
        memory = get_memory()
        
        try:
            # Run LangGraph
            result = graph.invoke({
                "user_query": question,
                "memory": memory
            })
            
            answer = result.get("final_answer", "No answer provided.")
            
            # Save to cache
            set_cache(question, answer)
            
            print("\nAI Answer:\n")
            print(answer)
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()