import json
import os
from datetime import datetime

FILE_PATH = "memory.json"


# -----------------------------
# DEFAULT MEMORY STRUCTURE
# -----------------------------
def default_memory():
    return {
        "user": {
            "user_id": "rahul_001",
            "name": "Rahul",
            "created_at": str(datetime.now())
        },

        "long_term": {
            "profile": {
                "income": None,
                "fixed_expenses": 0,
                "risk_tolerance": None
            },
            "goals": [],
            "portfolio": [],
            "transactions": []
        },

        "short_term": {
            "last_action": None,
            "last_transaction": None,
            "session_context": None
        },

        "derived": {},

        "alerts": []
    }


# -----------------------------
# LOAD MEMORY
# -----------------------------
def load_memory():
    if not os.path.exists(FILE_PATH):
        data = default_memory()
        save_memory(data)
        return data

    with open(FILE_PATH, "r") as f:
        return json.load(f)


# -----------------------------
# SAVE MEMORY
# -----------------------------
def save_memory(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# GET MEMORY
# -----------------------------
def get_memory():
    return load_memory()


# -----------------------------
# UPDATE PROFILE
# -----------------------------
def update_profile(key, value):
    data = load_memory()
    data["long_term"]["profile"][key] = value
    save_memory(data)


# -----------------------------
# ADD GOAL
# -----------------------------
def add_goal(goal):
    data = load_memory()

    goal_obj = {
        "goal": goal,
        "created_at": str(datetime.now())
    }

    data["long_term"]["goals"].append(goal_obj)
    save_memory(data)


# -----------------------------
# ADD STOCK
# -----------------------------
def add_stock(stock, amount):
    data = load_memory()

    portfolio = data["long_term"]["portfolio"]

    portfolio.append({
        "stock": stock,
        "invested_amount": amount,
        "date": str(datetime.now())
    })

    save_memory(data)


# -----------------------------
# ADD TRANSACTION
# -----------------------------
def add_transaction(txn):
    data = load_memory()

    txn["date"] = str(datetime.now())
    data["long_term"]["transactions"].append(txn)

    save_memory(data)


# -----------------------------
# UPDATE SHORT TERM
# -----------------------------
def update_short_term(key, value):
    data = load_memory()
    data["short_term"][key] = value
    save_memory(data)


# -----------------------------
# ADD ALERT
# -----------------------------
def add_alert(message):
    data = load_memory()

    alert = {
        "message": message,
        "date": str(datetime.now())
    }

    data["alerts"].append(alert)
    save_memory(data)