# agents/risk_agent.py

def risk_node(state, llm):

    memory = state["memory"]

    prompt = f"""
    Based on this user:

    Income: {memory.get("income")}
    Expenses: {memory.get("expenses")}

    Classify risk level: Low, Medium, or High
    """

    response = llm.invoke(prompt)

    return {"risk": response.content.strip()}