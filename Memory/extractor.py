from dotenv import load_dotenv
import json
from langchain_google_genai import ChatGoogleGenerativeAI

from Memory.user_memory import (
    update_profile,
    add_goal,
    add_stock,
    add_transaction,
    update_short_term,
    get_memory,
    save_memory
)

from Memory.rule_engin import check_rules

# -----------------------------
# INIT
# -----------------------------
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


# -----------------------------
# SAFE JSON PARSER
# -----------------------------
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


# -----------------------------
# EXTRACT FINANCIAL INFO
# -----------------------------
def extract_financial_info(user_input: str) -> dict:

    prompt = f"""
Extract structured financial information from the user input.

User Input:
"{user_input}"

Rules:
- Extract name if user says "I am Rahul"
- Extract income (annual/monthly if possible)
- Extract expenses
- Extract goal (car, house, etc.)
- Extract stock name if present
- Extract investment amount
- Detect action: buy / sell / expense / none

Return ONLY valid JSON:

{{
    "name": string or null,
    "income": number or null,
    "expenses": number or null,
    "risk_tolerance": "low/medium/high" or null,
    "goal": string or null,
    "stock": string or null,
    "investment_amount": number or null,
    "action": "buy/sell/expense/none"
}}
"""

    response = llm.invoke(prompt)

    return safe_json_parse(response.content)


# -----------------------------
# MAIN PROCESS FUNCTION
# -----------------------------
def process_and_store(user_input: str):

    extracted = extract_financial_info(user_input)

    if not extracted:
        return

    # -----------------------------
    # LOAD MEMORY ONCE
    # -----------------------------
    memory = get_memory()

    # -----------------------------
    # NAME UPDATE
    # -----------------------------
    if extracted.get("name"):
        memory["user"]["name"] = extracted["name"]

    # -----------------------------
    # PROFILE UPDATE
    # -----------------------------
    if extracted.get("income") is not None:
        update_profile("income", extracted["income"])

    if extracted.get("risk_tolerance"):
        update_profile("risk_tolerance", extracted["risk_tolerance"])

    # -----------------------------
    # EXPENSE UPDATE
    # -----------------------------
    if extracted.get("expenses") is not None:
        current = memory["long_term"]["profile"]["fixed_expenses"]
        new_total = current + extracted["expenses"]

        update_profile("fixed_expenses", new_total)

        add_transaction({
            "type": "expense",
            "amount": extracted["expenses"]
        })

    # -----------------------------
    # GOAL UPDATE
    # -----------------------------
    if extracted.get("goal"):
        add_goal(extracted["goal"])

    # -----------------------------
    # STOCK TRANSACTION (FIXED BUG)
    # -----------------------------
    stock = extracted.get("stock")
    amount = extracted.get("investment_amount")
    action = extracted.get("action")

    if action == "buy" and stock and amount:
        add_stock(stock, amount)

        add_transaction({
            "type": "buy",
            "asset": stock,
            "amount": amount
        })

        update_short_term("last_action", "buy")
        update_short_term("last_transaction", f"{stock} {amount}")

    # -----------------------------
    # SAVE UPDATED MEMORY
    # -----------------------------
    save_memory(memory)

    # -----------------------------
    # RULE ENGINE CHECK
    # -----------------------------
    check_rules()