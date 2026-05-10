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

    context_data = get_rag_context(state["user_query"])
    context_str = context_data.get("context", "") if isinstance(context_data, dict) else str(context_data)

    print("RAG CONTEXT:", context_str[:200])

    return {"rag_context": context_str}


# -----------------------------
# TOOL NODE (FIXED)
# -----------------------------
def tool_node(state):
    print("\n🛠 TOOL NODE RUNNING")

    query = state["user_query"]
    context = state.get("rag_context", "")

    # -------- Decision using LLM --------
    tools = [get_stock_price, get_financial_news, investment_cal, smart_portfolio_analyzer]
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = f"""
Query: {query}
Context: {context}

Use the appropriate tools to help answer the user's query. You can use multiple tools if needed (e.g. fetching stock price and news at the same time).
Extract the correct parameters like ticker symbols or topics from the query. If no tools are needed, do not call any.
"""

    try:
        response = llm_with_tools.invoke(prompt)
    except Exception as e:
        print("❌ LLM Decision Error:", e)
        return {"tool_output": "Tool execution failed"}

    output_lines = []

    if getattr(response, "tool_calls", None):
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"TOOL DECISION: {tool_name} {tool_args}")
            try:
                if tool_name == "get_stock_price":
                    res = get_stock_price.invoke(tool_args)
                elif tool_name == "get_financial_news":
                    res = get_financial_news.invoke(tool_args)
                elif tool_name == "investment_cal":
                    res = investment_cal.invoke(tool_args)
                elif tool_name == "smart_portfolio_analyzer":
                    res = smart_portfolio_analyzer.invoke(tool_args)
                else:
                    res = "Unknown tool"
                output_lines.append(f"{tool_name} ({tool_args}) output:\n{res}")
            except Exception as e:
                print("❌ TOOL EXECUTION ERROR:", e)
                output_lines.append(f"Error executing {tool_name}: {e}")
    else:
        print("TOOL DECISION: none")
        output_lines.append("No tool needed")

    output = "\n".join(output_lines)
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