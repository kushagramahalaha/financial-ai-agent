import re
from typing import List, Dict
from langchain.tools import tool
from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)

def extract_price_from_string(price_str: str) -> float:
    """
    Extracts the float price from a string like: "The current price of AAPL is $308.8200"
    """
    match = re.search(r'\$(\d+(?:\.\d+)?)', price_str)
    if match:
        return float(match.group(1))
    return 0.0

def generate_portfolio_report_data(portfolio: List[Dict]) -> Dict:
    """
    Loops through the portfolio, retrieves live stock prices and news,
    calculates profits/losses, and compiles data.
    """
    enriched_portfolio = []
    total_invested = 0.0
    total_current_value = 0.0
    
    for item in portfolio:
        stock = item.get("stock")
        buy_price = float(item.get("buy_price", 0.0))
        quantity = float(item.get("quantity", 0.0))
        
        # Calculate investment
        invested_amount = buy_price * quantity
        total_invested += invested_amount
        
        # Fetch current price
        try:
            price_res = get_stock_price.invoke({"ticker": stock})
            current_price = extract_price_from_string(price_res)
        except Exception as e:
            print(f"[ERROR] Failed to fetch price for {stock}: {e}")
            current_price = 0.0
            
        # If current_price failed, fallback to buy_price to keep calculations sane
        if current_price == 0.0:
            current_price = buy_price
            
        current_value = current_price * quantity
        total_current_value += current_value
        
        profit_loss = current_value - invested_amount
        percentage = (profit_loss / invested_amount * 100.0) if invested_amount > 0 else 0.0
        
        # Fetch news
        try:
            news_res = get_financial_news.invoke({"topic": stock})
        except Exception as e:
            print(f"[ERROR] Failed to fetch news for {stock}: {e}")
            news_res = "No news available."
            
        enriched_portfolio.append({
            "stock": stock,
            "buy_price": buy_price,
            "quantity": quantity,
            "current_price": current_price,
            "invested_amount": invested_amount,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "percentage": percentage,
            "news": news_res
        })
        
    net_profit_loss = total_current_value - total_invested
    net_percentage = (net_profit_loss / total_invested * 100.0) if total_invested > 0 else 0.0
    
    return {
        "portfolio": enriched_portfolio,
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "net_profit_loss": net_profit_loss,
        "net_percentage": net_percentage
    }

def get_ai_portfolio_report(report_data: Dict) -> str:
    """
    Sends the compiled profit/loss calculations and news to Gemini to generate the advisory report.
    """
    if not report_data or not report_data.get("portfolio"):
        return "No investments found in your portfolio. Add some stocks first to generate a report!"
        
    portfolio_summary = ""
    for item in report_data["portfolio"]:
        status = "PROFIT" if item["profit_loss"] >= 0 else "LOSS"
        portfolio_summary += (
            f"- **{item['stock']}**: Bought {item['quantity']} shares at ${item['buy_price']:.2f} each. "
            f"Current price is ${item['current_price']:.2f}. "
            f"Invested: ${item['invested_amount']:.2f} | Current Value: ${item['current_value']:.2f}. "
            f"Profit/Loss: ${item['profit_loss']:.2f} ({item['percentage']:.2f}%) -> {status}.\n"
        )
        
    news_summary = ""
    for item in report_data["portfolio"]:
        news_summary += f"### Recent News for {item['stock']}:\n{item['news']}\n\n"
        
    prompt = f"""
You are an AI Financial Advisor. Analyze the user's stock portfolio performance and recent stock news, then write a comprehensive, professional, and actionable report.

Portfolio Performance Data:
{portfolio_summary}

Total Invested: ${report_data['total_invested']:.2f}
Total Current Value: ${report_data['total_current_value']:.2f}
Net Profit/Loss: ${report_data['net_profit_loss']:.2f} ({report_data['net_percentage']:.2f}%)

Recent News context:
{news_summary}

Please structure the report with the following sections in clean Markdown:
1.  **📊 Portfolio Executive Summary**: State total investment, current value, net profit/loss (with return percentage), and a general health statement.
2.  **🔍 Individual Stock Analysis**: Discuss each stock's profit/loss status. Evaluate if the stock is a major driver of profit/loss.
3.  **📰 News Sentiment & Market Impact**: Analyze how the latest news stories might affect the future outlook of these stocks.
4.  **💡 Actionable Recommendations**: Give clear Hold/Sell/Buy recommendations for each stock based on the math and the news sentiment.
"""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"⚠️ Failed to generate AI report: {e}"
