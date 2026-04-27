import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from Tools.investment_cal import investment_cal
from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news
from Tools.portfolio_analyser import analyze_portfolio
from Tools.smart_portfolio_analyzer import smart_portfolio_analyzer
from Memory.user_memory import get_memory
from Memory.extractor import process_and_store
#check of tools seprately
# Test Investment Calculator
# print("Investment Calculator Test:")
# print(investment_cal.invoke({
#     "monthly_investment": 5000,
#     "annual_return": 12,
#     "years": 10
# }))


# # Test Stock Price Tool
# print("\nStock Price Test:")
# print(get_stock_price.invoke({
#     "ticker": "TSLA"
# }))


# # Test Financial News Tool
# print("\nFinancial News Test:")
# print(get_financial_news.invoke({
#     "topic": "Tesla"
# }))


# # Test Portfolio Analyzer
# print("\nPortfolio Analyzer Test:")
# print(analyze_portfolio.invoke({
#     "stocks": ["AAPL", "MSFT", "NVDA"]
# }))
#check smart_portfolio_analyser
# if __name__ == "__main__":
#     stocks = ["AAPL", "MSFT", "NVDA", "XOM"]

#     result = smart_portfolio_analyzer.invoke({"stocks": stocks})

#     print("\n📊 Portfolio Analysis Result:\n")
#     print(result)

#check memory
# user_input = "I earn ₹80,000 and my monthly expenses are ₹30,000 and my year goal to buy new car"

# process_and_store(user_input)

# print(get_memory())
# main.py

from langchain_google_genai import ChatGoogleGenerativeAI
from graph.builder import build_graph
from Memory.user_memory import get_memory

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def main():
    graph = build_graph(llm)   # build once (better performance)

    while True:
        query = input("\nEnter your query (type 'exit' to quit): ")

        # ✅ EXIT CONDITION
        if query.lower() in ["exit", "quit"]:
            print("Exiting... Goodbye!")
            break

        # ✅ Update memory
        process_and_store(query)

        state = {
            "user_query": query,
            "memory": get_memory(),
            "risk": "",
            "goal": "",
            "rag_context": "",
            "tool_output": "",
            "final_answer": ""
        }

        result = graph.invoke(state)

        print("\nFinal Answer:\n")
        print(result["final_answer"])

if __name__ == "__main__":
 main()