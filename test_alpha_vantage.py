import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
print(f"API Key present: {bool(API_KEY)}")

url = "https://www.alphavantage.co/query"
params = {
    "function": "GLOBAL_QUOTE",
    "symbol": "AAPL",
    "apikey": API_KEY
}
response = requests.get(url, params=params)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
