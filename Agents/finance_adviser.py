import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv
import voyageai

from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# -----------------------------
# Import Agents & Tools
# -----------------------------
from Agents.risk_agent import risk_agent
from Agents.goal_agent import goal_agent
from Memory.user_memory import get_user

from Tools.investment_cal import investment_cal
from Tools.stock_tools import get_stock_price
from Tools.news_tool import get_financial_news
from Tools.smart_portfolio_analyzer import smart_portfolio_analyzer

# -----------------------------
# Load API keys
# -----------------------------
load_dotenv()
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# -----------------------------
# Voyage Client
# -----------------------------
voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)

# -----------------------------
# Embedding Class (REQUIRED)
# -----------------------------
class VoyageEmbeddings(Embeddings):

    def embed_documents(self, texts):
        result = voyage_client.embed(texts, model="voyage-3-large")
        return result.embeddings

    def embed_query(self, text):
        result = voyage_client.embed([text], model="voyage-3-large")
        return result.embeddings[0]

# -----------------------------
# Load Vector DB
# -----------------------------
embeddings = VoyageEmbeddings()

db = FAISS.load_local(
    "../vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_kwargs={"k": 3})

# -----------------------------
# Gemini LLM (ONLY USED ONCE)
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# -----------------------------
# Format Docs
# -----------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -----------------------------
# Get RAG Context (NO LLM)
# -----------------------------
def get_rag_context(query):
    docs = retriever.invoke(query)
    return format_docs(docs)

# -----------------------------
# Simple Cache (IMPORTANT)
# -----------------------------
cache = {}

def get_cached(prompt):
    return cache.get(prompt)

def set_cache(prompt, response):
    cache[prompt] = response

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    question = input("\nAsk a financial question: ")

    if question.lower() in ["exit", "quit"]:
        break

    # -------------------------
    # 1. MEMORY
    # -------------------------
    user_data = get_user("user1")  # static ID (you can improve later)

    # -------------------------
    # 2. RAG (NO LLM)
    # -------------------------
    context = get_rag_context(question)

    # -------------------------
    # 3. RISK & GOAL (NO LLM)
    # -------------------------
    risk = risk_agent(user_data)["risk"]
    goal = goal_agent(user_data)["goal_type"]

    # -------------------------
    # 4. TOOL CALLING (DIRECT)
    # -------------------------
    tool_output = ""

    if "stock" in question.lower():
        tool_output = get_stock_price("AAPL")

    elif "news" in question.lower():
        tool_output = get_financial_news()

    elif "investment" in question.lower():
        tool_output = investment_cal(10000, 5, 10)

    elif "portfolio" in question.lower():
        tool_output = smart_portfolio_analyzer(user_data)

    # -------------------------
    # 5. FINAL PROMPT
    # -------------------------
    final_prompt = f"""
You are a smart financial advisor.

User Question:
{question}

User Profile:
{user_data}

Risk Level:
{risk}

Goal Type:
{goal}

Financial Knowledge:
{context}

Tool Output:
{tool_output}

Give clear, practical financial advice.
"""

    # -------------------------
    # 6. CACHE CHECK
    # -------------------------
    cached = get_cached(final_prompt)

    if cached:
        answer = cached
    else:
        answer = llm.invoke(final_prompt)
        set_cache(final_prompt, answer)

    # -------------------------
    # OUTPUT
    # -------------------------
    print("\nAI Answer:\n")
    print(answer)