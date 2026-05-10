import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
tools = [get_stock_price, get_financial_news]
llm_with_tools = llm.bind_tools(tools)

query = "can you give me the stock price of AAPL"
prompt = f"Query: {query}\nExtract the correct parameters like ticker symbols. If no tools are needed, do not call any."
try:
    response = llm_with_tools.invoke(prompt)
    print("Tool Calls:", getattr(response, "tool_calls", None))
except Exception as e:
    print("Error:", e)
