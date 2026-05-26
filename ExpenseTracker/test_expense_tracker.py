import os
import json
import shutil
from tracker import process_notification_message

MEMORY_FILE = "memory.json"
BACKUP_FILE = "memory.json.bak"

def setup_mock_memory():
    # Backup existing memory
    if os.path.exists(MEMORY_FILE):
        shutil.copy(MEMORY_FILE, BACKUP_FILE)
        print("Backed up existing memory.json")
    
    # Initialize a controlled mock memory structure
    mock_data = {
        "user": {
            "user_id": "test_user_999",
            "name": "Test User",
            "created_at": "2026-05-26"
        },
        "long_term": {
            "profile": {
                "income": 80000.0,
                "fixed_expenses": 35000.0,  # Starts at 35k
                "risk_tolerance": "Medium"
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
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(mock_data, f, indent=4)
    print("Set up mock memory.json (Income: ₹80,000, Current Expenses: ₹35,000)")

def restore_memory():
    # Restore original memory
    if os.path.exists(BACKUP_FILE):
        shutil.copy(BACKUP_FILE, MEMORY_FILE)
        os.remove(BACKUP_FILE)
        print("Restored original memory.json")
    elif os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        print("Cleaned up temporary mock memory.json")

def run_tests():
    test_cases = [
        {
            "name": "Debit Transaction (Low spend, shouldn't trigger alert)",
            "message": "Dear Customer, your Acct XXXXX123 was debited for INR 5,000.00 on 2026-05-26 for AMAZON SHOPPING."
        },
        {
            "name": "Debit Transaction (High spend, should exceed 70% of 80k = 56k)",
            # 35k start + 5k (Amazon) + 20k (Zomato) = 60k, which is > 56k
            "message": "Transaction Alert: INR 20,000.00 was spent on your HDFC credit card ending 9876 at ZOMATO on 2026-05-26."
        },
        {
            "name": "Credit Transaction",
            "message": "Your account XXXXX123 has been credited with Salary of INR 80,000.00 on 2026-05-26."
        },
        {
            "name": "Non-transaction Spam Message",
            "message": "Congratulations! You have won a free coupon. Click here to claim your prize now."
        }
    ]

    try:
        setup_mock_memory()
        
        print("\n--- Starting Tests ---")
        for i, tc in enumerate(test_cases, 1):
            print(f"\nTest #{i}: {tc['name']}")
            print(f"Input Message: \"{tc['message']}\"")
            result = process_notification_message(tc["message"])
            print("Output:")
            print(json.dumps(result, indent=2))
            
            # Read current expenses state from memory
            with open(MEMORY_FILE, "r") as f:
                current_mem = json.load(f)
            print(f"Current Total Expenses: ₹{current_mem['long_term']['profile']['fixed_expenses']}")
            print(f"Current Alerts Count: {len(current_mem['alerts'])}")
            
        print("\n--- Tests Completed Successfully ---")
        
    finally:
        restore_memory()

if __name__ == "__main__":
    run_tests()
