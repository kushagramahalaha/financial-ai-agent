import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st


from Memory.user_memory import get_memory
from Memory.extractor import process_and_store
from graph.builder import build_graph



# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Financial AI Advisor",
    layout="wide"
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

st.sidebar.write("**Name:**", memory["user"]["name"])
st.sidebar.write("**Income:**", memory["long_term"]["profile"]["income"])
st.sidebar.write("**Expenses:**", memory["long_term"]["profile"]["fixed_expenses"])
st.sidebar.write("**Risk:**", memory["long_term"]["profile"]["risk_tolerance"])

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

    st.subheader("📊 Portfolio")

    portfolio = memory["long_term"]["portfolio"]

    if portfolio:
        for p in portfolio:
            st.write(f"• {p['stock']} → ₹{p['invested_amount']}")
    else:
        st.info("No investments yet")

    # -------------------------
    st.subheader("💳 Transactions")

    transactions = memory["long_term"]["transactions"]

    if transactions:
        for t in transactions:
            st.write(t)
    else:
        st.info("No transactions yet")