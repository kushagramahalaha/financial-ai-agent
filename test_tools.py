from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news

print("STOCK TEST:", get_stock_price.invoke({"ticker": "AAPL"}))
print("NEWS TEST:", get_financial_news.invoke({"topic": "apple"}))
