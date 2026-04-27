import requests
import os
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")


@tool
def get_financial_news(topic: str) -> str:
    """
    Fetch latest financial news for a given topic.
    Example topics: stock market, Tesla, inflation
    """

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic,
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 3
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = data.get("articles", [])

    if not articles:
        return "No news found."

    news_list = []
    for article in articles:
        title = article["title"]
        news_list.append(title)

    return "Latest news:\n" + "\n".join(news_list)