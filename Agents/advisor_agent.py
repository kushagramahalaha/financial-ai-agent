# agents/advisor_agent.py

def advisor_node(state, llm):

    prompt = f"""
    You are a financial advisor.

    User Query:
    {state["user_query"]}

    User Profile:
    {state["memory"]}

    Risk Level:
    {state["risk"]}

    Goal:
    {state["goal"]}

    Financial Knowledge:
    {state["rag_context"]}

    Tool Output:
    {state["tool_output"]}

    Give clear financial advice.
    """

    response = llm.invoke(prompt)

    return {"final_answer": response.content}