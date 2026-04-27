from langchain.tools import tool
from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news
from langchain_google_genai import ChatGoogleGenerativeAI
llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

@tool
def smart_portfolio_analyzer(stocks: list) -> str:
    """
    Analyze portfolio using stock data and sector logic.
    """

    # 🔹 Sector Mapping
    sector_map = {
        "AAPL": "Tech",
        "MSFT": "Tech",
        "NVDA": "Tech",
        "TSLA": "Tech",
        "JPM": "Finance",
        "XOM": "Energy"
    }

    # 🔹 Step 1: Count sectors
    sector_count = {}

    for stock in stocks:
        sector = sector_map.get(stock, "Other")
        sector_count[sector] = sector_count.get(sector, 0) + 1

    # 🔹 Step 2: Convert to insights
    total = len(stocks)

    analysis = []
    risk_flags = []

    for sector, count in sector_count.items():
        percentage = (count / total) * 100

        analysis.append(f"{sector}: {percentage:.2f}%")

        # 🔥 Risk detection
        if percentage > 50:
            risk_flags.append(f"High exposure to {sector}")

    # 🔹 Step 3: Diversification check
    if len(sector_count) == 1:
        risk_flags.append("No diversification (all stocks in one sector)")


    stock_data = {}

    for stock in stocks:
        try:
            price = get_stock_price.invoke({"ticker": stock})
            stock_data[stock] = price
        except:
            stock_data[stock] = "Data not available"

    # 🔹 Step 4: News Data
    news_data = {}
    for stock in stocks:
        try:
            news = get_financial_news.invoke({"topic": stock})
            news_data[stock] = news
        except:
            news_data[stock] = "No news available"
        
    analysis_data = {
        "stocks": stocks,
        "sector_distribution": sector_count,
        "stock_data": stock_data,
        "news": news_data
    }

    # 🔹 Step 5: LLM Reasoning(For the detailed output user get this )
    # prompt = f"""
    # Analyze this investment portfolio:

    # Stocks: {stocks}

    # Sector Distribution:
    # {sector_count}

    # Stock Prices:
    # {stock_data}

    # News:
    # {news_data}

    # Provide:
    # 1. Overall risk level (Low / Medium / High)
    # 2. Key insights
    # 3. Suggestions
    # 4. Warnings based on news
    # """
#step 5 for the small output which is best and user friendly
    prompt= f"""
Analyze this investment portfolio:
Stocks: {stocks}
Sector Distribution: {sector_count}
Stock Prices: {stock_data}
News: {news_data}

Provide output in TWO parts:

1. SHORT SUMMARY (max 5 lines)
   - Risk level
   - 2 key insights
   - 2 suggestions

2. DETAILED ANALYSIS (optional)
"""

    response = llm.invoke(prompt)

    # 🔹 Final Output
    return response.content
