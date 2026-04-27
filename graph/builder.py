from langgraph.graph import StateGraph
from graph.state import AgentState

from Agents.risk_agent import risk_node
from Agents.goal_agent import goal_node
from Agents.advisor_agent import advisor_node

from RAG.retriever import get_rag_context

from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news
from Tools.investment_cal import investment_cal
from Tools.smart_portfolio_analyzer import smart_portfolio_analyzer

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


# -----------------------------
# RAG NODE
# -----------------------------
def rag_node(state):
    print("\n🔍 RAG NODE RUNNING")

    context = get_rag_context(state["user_query"])

    print("RAG CONTEXT:", str(context)[:200])

    return {"rag_context": context}


# -----------------------------
# TOOL NODE (FIXED)
# -----------------------------
def tool_node(state):
    print("\n🛠 TOOL NODE RUNNING")

    query = state["user_query"]
    context = state.get("rag_context", "")

    # -------- Decision using LLM --------
    prompt = f"""
Decide the best tool:

Query: {query}
Context: {context}

Options:
- stock
- news
- investment
- portfolio
- none

Return only one word.
"""

    try:
        decision = llm.invoke(prompt).content.strip().lower()
    except Exception as e:
        print("❌ LLM Decision Error:", e)
        decision = "none"

    print("TOOL DECISION:", decision)

    output = "No tool needed"

    # -------- Tool Execution --------
    try:
        if decision == "stock":
            output = get_stock_price.invoke({"ticker": "AAPL"})

        elif decision == "news":
            output = get_financial_news.invoke({"topic": "stock market"})

        elif decision == "investment":
            output = investment_cal.invoke({
                "monthly_investment": 5000,
                "annual_return": 10,
                "years": 10
            })

        elif decision == "portfolio":
            output = smart_portfolio_analyzer.invoke({
                "stocks": ["AAPL", "MSFT", "NVDA"]
            })

    except Exception as e:
        print("❌ TOOL EXECUTION ERROR:", e)
        output = "Tool execution failed"

    print("TOOL OUTPUT:", str(output)[:200])

    return {"tool_output": output}


# -----------------------------
# BUILD GRAPH
# -----------------------------
def build_graph():

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("risk", lambda state: risk_node(state, llm))
    builder.add_node("goal", goal_node)
    builder.add_node("rag", rag_node)
    builder.add_node("tools", tool_node)
    builder.add_node("advisor", lambda state: advisor_node(state, llm))

    # Flow
    builder.set_entry_point("risk")

    builder.add_edge("risk", "goal")
    builder.add_edge("goal", "rag")
    builder.add_edge("rag", "tools")
    builder.add_edge("tools", "advisor")

    builder.set_finish_point("advisor")

    return builder.compile()