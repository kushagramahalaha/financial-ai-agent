# agents/goal_agent.py
def goal_node(state):

    goals = state["memory"].get("goals", [])

    if any("house" in g.lower() for g in goals):
        return {"goal": "Long Term"}

    elif any("car" in g.lower() for g in goals):
        return {"goal": "Medium Term"}

    else:
        return {"goal": "General"}
