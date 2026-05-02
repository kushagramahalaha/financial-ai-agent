from Memory.user_memory import get_memory, add_alert, save_memory

def check_rules():
    data = get_memory()

    income = data["long_term"]["profile"].get("income")
    expenses = data["long_term"]["profile"].get("fixed_expenses", 0)

    if income and expenses:
        if expenses > income * 0.7:
            alert_msg = "⚠️ You are overspending!"
            # Check if alert already exists to prevent spamming the user
            if not any(a["message"] == alert_msg for a in data["alerts"]):
                add_alert(alert_msg, data=data)
                save_memory(data)