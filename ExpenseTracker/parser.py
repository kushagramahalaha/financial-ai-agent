import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def safe_json_parse(text: str) -> dict:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        print("[ERROR] JSON parsing failed:", e)
        print("Raw response:", text)
        return {}

def parse_notification(message_text: str) -> dict:
    """
    Parses a raw message (like SMS or bank email alert) to check if it's a debit or credit notification,
    and extracts key transaction details.
    """
    prompt = f"""
Analyze the following message text to see if it indicates a financial transaction (credit/deposit or debit/withdrawal/deduction).

Message Text:
"{message_text}"

Rules:
1. Determine if the text represents a valid financial transaction.
2. If it is a transaction, identify if it is a "debit" (money deducted, spent, or withdrawn) or a "credit" (money received, deposited, or added).
3. Extract the exact numerical amount.
4. Detect the source (either "bank" for bank account transactions, "credit_card" for credit cards, or "unknown").
5. Extract a brief description or vendor name (e.g. "Amazon Pay", "Zomato", "Netflix", "Salary", "Self").
6. Set "is_transaction" to true. If the message is NOT a financial transaction (e.g., promotional spam, OTP, password change alert, or general queries), set "is_transaction" to false and all other fields to null.

Return ONLY a valid JSON object matching this schema:
{{
    "is_transaction": boolean,
    "type": "debit" | "credit" | null,
    "amount": number | null,
    "source": "bank" | "credit_card" | "unknown" | null,
    "description": string | null
}}
"""
    try:
        response = llm.invoke(prompt)
        return safe_json_parse(response.content)
    except Exception as e:
        print(f"[ERROR] Failed to invoke LLM: {e}")
        return {
            "is_transaction": False,
            "type": None,
            "amount": None,
            "source": None,
            "description": None
        }
