from Memory.user_memory import get_memory, add_alert

def check_rules():
    data = get_memory()

    income = data["long_term"]["profile"]["income"]
    expenses = data["long_term"]["profile"]["fixed_expenses"]

    if income and expenses:
        if expenses > income * 0.7:
            add_alert("⚠️ You are overspending!")