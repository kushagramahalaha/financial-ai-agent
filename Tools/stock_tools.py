import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@tool
def get_stock_price(ticker: str) -> str:
    """
    Fetch the latest stock price for a given ticker symbol.
    Example: AAPL, TSLA
    """

    url = f"https://www.alphavantage.co/query"

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        price = data["Global Quote"]["05. price"]
        return f"The current price of {ticker} is ${price}"
    except:
        return "Could not retrieve stock data."