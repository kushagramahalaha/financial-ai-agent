import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from dotenv import load_dotenv
load_dotenv()
from Tools.stock_tools import get_stock_price

try:
    res = get_stock_price.invoke({"ticker": "AAPL"})
    print("RESULT:", res)
except Exception as e:
    print("ERROR:", e)
