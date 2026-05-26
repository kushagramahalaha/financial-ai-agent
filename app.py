import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st


from Memory.user_memory import get_memory, save_memory, add_goal
from Memory.extractor import process_and_store
from graph.builder import build_graph



# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Financial AI Advisor",
    layout="wide"
)

# Hide the "Press Enter to submit form" text
st.markdown(
    """
    <style>
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# TITLE
# -----------------------------
st.title("💰 Financial AI Advisor")

# -----------------------------
# LOAD MEMORY
# -----------------------------
memory = get_memory()

# -----------------------------
# SIDEBAR (PROFILE)
# -----------------------------
st.sidebar.title("👤 User Profile")

with st.sidebar.form("profile_form"):
    st.subheader("Update Information")
    
    current_name = memory["user"].get("name", "")
    current_income = memory["long_term"]["profile"].get("income") or 0.0
    current_expenses = memory["long_term"]["profile"].get("fixed_expenses") or 0.0
    
    new_name = st.text_input("Name", value=current_name)
    new_income = st.number_input("Monthly Salary (₹)", value=float(current_income), step=1000.0)
    new_expenses = st.number_input("Monthly Expenses (₹)", value=float(current_expenses), step=1000.0)
    
    new_monthly_goal = st.text_input("Goal of the Month", placeholder="e.g. Save ₹5000")
    new_long_term_goal = st.text_input("Long Term Goal", placeholder="e.g. Buy a house")
    
    submit_button = st.form_submit_button("Save Profile")
    
    if submit_button:
        memory["user"]["name"] = new_name
        memory["long_term"]["profile"]["income"] = new_income
        memory["long_term"]["profile"]["fixed_expenses"] = new_expenses
        
        if new_monthly_goal.strip():
            add_goal(f"Monthly: {new_monthly_goal}", data=memory)
        if new_long_term_goal.strip():
            add_goal(f"Long Term: {new_long_term_goal}", data=memory)
            
        save_memory(memory)
        st.success("Profile Updated!")
        st.rerun()

st.sidebar.write("**Risk Tolerance:**", memory["long_term"]["profile"].get("risk_tolerance", "Unknown"))

# -----------------------------
# GOALS
# -----------------------------
st.sidebar.subheader("🎯 Goals")

if memory["long_term"]["goals"]:
    for goal in memory["long_term"]["goals"]:
        st.sidebar.write("-", goal["goal"])
else:
    st.sidebar.write("No goals added")

# -----------------------------
# ALERTS
# -----------------------------
st.sidebar.subheader("⚠️ Alerts")

if memory["alerts"]:
    for alert in memory["alerts"]:
        st.sidebar.warning(alert["message"])
else:
    st.sidebar.write("No alerts")

# -----------------------------
# SIMULATE NOTIFICATION MESSAGE
# -----------------------------
st.sidebar.subheader("📱 SMS Notification Simulator")
with st.sidebar.expander("Simulate bank/card alert"):
    sms_text = st.text_area("SMS text:", placeholder="Dear Customer, your Acct was debited for INR 2,500.00...")
    if st.button("Simulate Notification"):
        if sms_text.strip():
            from ExpenseTracker.tracker import process_notification_message
            res = process_notification_message(sms_text)
            if res["processed"]:
                st.sidebar.success(f"Processed: {res['parsed_data']['type'].capitalize()} of ₹{res['parsed_data']['amount']}")
                if res["alert_triggered"]:
                    st.sidebar.error(res["alert_message"])
                st.rerun()
            else:
                st.sidebar.warning(f"Ignored: {res['reason']}")

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["💬 Chat", "📊 Dashboard"])

# =============================
# 💬 CHAT TAB
# =============================
with tab1:

    # SESSION STATE
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # DISPLAY CHAT HISTORY
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # INPUT
    user_input = st.chat_input("Ask your financial question...")

    if user_input:

        # -------------------------
        # STEP 1: STORE MEMORY
        # -------------------------
        process_and_store(user_input)

        # -------------------------
        # STEP 2: DISPLAY USER
        # -------------------------
        with st.chat_message("user"):
            st.write(user_input)

        # -------------------------
        # STEP 3: GET AI RESPONSE
        # -------------------------
        try:
            graph = build_graph()

            result = graph.invoke({
            "user_query": user_input,
           "memory": memory
     })
            response = result["final_answer"]
            
        except Exception as e:
            response = f"⚠️ Error: {e}"

        # -------------------------
        # STEP 4: DISPLAY AI
        # -------------------------
        with st.chat_message("assistant"):
            st.write(response)

        # -------------------------
        # STEP 5: SAVE CHAT
        # -------------------------
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # OPTIONAL: refresh sidebar data
        st.rerun()


# =============================
# 📊 DASHBOARD TAB
# =============================
with tab2:
    st.subheader("📊 Stock Portfolio")

    # Form to add stock
    with st.expander("➕ Add Stock Investment"):
        with st.form("add_stock_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                stock_ticker = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g. AAPL, TSLA")
            with col2:
                buy_price = st.number_input("Purchase Price ($)", min_value=0.01, value=150.0, step=1.0)
            with col3:
                quantity = st.number_input("Number of Shares", min_value=0.01, value=10.0, step=1.0)
            
            submit_stock = st.form_submit_button("Add to Portfolio")
            
            if submit_stock:
                if stock_ticker.strip():
                    from Memory.user_memory import add_stock
                    add_stock(stock_ticker.strip(), buy_price * quantity, buy_price, quantity)
                    st.success(f"Added {quantity} shares of {stock_ticker.upper()}!")
                    st.rerun()
                else:
                    st.error("Please enter a valid stock ticker.")

    # Render portfolio table with live calculations
    portfolio = memory["long_term"].get("portfolio", [])

    if portfolio:
        from Tools.portfolio_reporter import generate_portfolio_report_data, get_ai_portfolio_report
        
        # We wrap this in a spinner to fetch live prices
        with st.spinner("Fetching live stock prices and news..."):
            report_data = generate_portfolio_report_data(portfolio)
            
        # Display Summary Cards
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Total Invested", f"${report_data['total_invested']:.2f}")
        with m_col2:
            st.metric("Current Value", f"${report_data['total_current_value']:.2f}")
        with m_col3:
            net_pl = report_data['net_profit_loss']
            net_pct = report_data['net_percentage']
            st.metric(
                "Net Profit/Loss", 
                f"${net_pl:+.2f} ({net_pct:+.2f}%)",
                delta=f"{net_pct:+.2f}%"
            )
            
        # Build DataFrame/table
        table_rows = []
        for p in report_data["portfolio"]:
            status = "🟢 Profit" if p["profit_loss"] >= 0 else "🔴 Loss"
            table_rows.append({
                "Stock": p["stock"],
                "Buy Price": f"${p['buy_price']:.2f}",
                "Quantity": f"{p['quantity']:.2f}",
                "Current Price": f"${p['current_price']:.2f}",
                "Invested": f"${p['invested_amount']:.2f}",
                "Current Value": f"${p['current_value']:.2f}",
                "Profit/Loss": f"${p['profit_loss']:+.2f} ({p['percentage']:+.2f}%)",
                "Status": status
            })
            
        st.dataframe(table_rows, use_container_width=True)
        
        # AI Performance Report Button
        st.subheader("🤖 AI Investment Advisor Report")
        
        # Check if report has already been generated and cached in session state to prevent API spamming
        if st.button("Generate AI Performance Report"):
            with st.spinner("AI is analyzing portfolio health and news sentiment..."):
                report = get_ai_portfolio_report(report_data)
                st.session_state.ai_report = report
                
        if "ai_report" in st.session_state:
            st.markdown(st.session_state.ai_report)
            
    else:
        st.info("No investments in your portfolio yet. Use the 'Add Stock Investment' panel above to add one!")

    # -------------------------
    st.subheader("💳 Transaction History")

    transactions = memory["long_term"]["transactions"]

    if transactions:
        # Show transactions in reverse chronological order
        for t in reversed(transactions):
            date_str = t.get("date", "")[:19]
            if t.get("type") == "expense":
                st.error(f"💸 **Expense Deduction**: -₹{t.get('amount')} | {t.get('description', '')} ({t.get('source', '')}) | *{date_str}*")
            elif t.get("type") == "credit":
                st.success(f"💰 **Credit Deposit**: +₹{t.get('amount')} | {t.get('description', '')} ({t.get('source', '')}) | *{date_str}*")
            else:
                st.info(f"💼 **Transaction**: {t} | *{date_str}*")
    else:
        st.info("No transactions yet")