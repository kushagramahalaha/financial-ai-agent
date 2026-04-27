from langchain.tools import tool

@tool
def analyze_portfolio(stocks: list) -> str:
    """
    Analyze portfolio diversification.
    Example input: ["AAPL", "MSFT", "GOOGL"]
    """

    tech_stocks = ["AAPL","MSFT","GOOGL","NVDA","META","TSLA"]

    tech_count = sum(1 for stock in stocks if stock in tech_stocks)

    if tech_count > len(stocks) / 2:
        return "Your portfolio is heavily concentrated in tech stocks. Consider diversifying into ETFs, bonds, or other sectors."

    return "Your portfolio appears reasonably diversified."