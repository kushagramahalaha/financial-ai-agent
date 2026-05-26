import sys
import os
# Add root directory to python path to resolve modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ExpenseTracker.parser import parse_notification
from Memory.user_memory import get_memory, save_memory, add_transaction, update_profile, add_alert

def process_notification_message(message_text: str) -> dict:
    """
    Parses the message, updates the user's transactions and total expenses,
    checks if the budget has been exceeded, and returns the result details.
    """
    parsed = parse_notification(message_text)
    
    if not parsed or not parsed.get("is_transaction"):
        return {
            "processed": False,
            "reason": "Not a financial transaction notification.",
            "parsed_data": parsed,
            "alert_triggered": False,
            "alert_message": None
        }
        
    amount = parsed.get("amount", 0)
    tx_type = parsed.get("type")
    source = parsed.get("source", "unknown")
    description = parsed.get("description", "Unknown Vendor")
    
    if not amount or amount <= 0:
        return {
            "processed": False,
            "reason": "Invalid transaction amount.",
            "parsed_data": parsed,
            "alert_triggered": False,
            "alert_message": None
        }

    # Load current memory state
    memory = get_memory()
    profile = memory["long_term"]["profile"]
    
    income = profile.get("income") or 0.0
    current_expenses = profile.get("fixed_expenses") or 0.0
    
    alert_triggered = False
    alert_message = None
    
    if tx_type == "debit":
        # Calculate new total expenses
        new_expenses = current_expenses + amount
        
        # Update profile and add the transaction record
        update_profile("fixed_expenses", new_expenses, data=memory)
        add_transaction({
            "type": "expense",
            "amount": amount,
            "source": source,
            "description": f"Debit: {description}"
        }, data=memory)
        
        # Budget warning check (e.g. 70% threshold if income is defined)
        if income > 0:
            threshold = income * 0.70
            if new_expenses > threshold:
                alert_triggered = True
                alert_message = f"⚠️ Budget Alert: Your total expenses (₹{new_expenses:.2f}) have exceeded 70% of your monthly income (₹{income:.2f})!"
                # Add alert to user memory to persist it
                add_alert(alert_message, data=memory)
        else:
            # Fallback if income is not set: warn on high individual debit (e.g., > ₹50,000)
            if amount > 50000:
                alert_triggered = True
                alert_message = f"⚠️ High Value Spend Alert: A large transaction of ₹{amount:.2f} was detected from {source}."
                add_alert(alert_message, data=memory)
                
    elif tx_type == "credit":
        # Handle credit transactions (e.g., deposit, salary)
        add_transaction({
            "type": "credit",
            "amount": amount,
            "source": source,
            "description": f"Credit: {description}"
        }, data=memory)
        
    # Save the updated memory state back to memory.json
    save_memory(memory)
    
    return {
        "processed": True,
        "reason": "Transaction processed successfully.",
        "parsed_data": parsed,
        "alert_triggered": alert_triggered,
        "alert_message": alert_message
    }
