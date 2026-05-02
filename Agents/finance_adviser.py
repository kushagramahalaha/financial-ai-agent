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
    tools = [get_stock_price, get_financial_news, investment_cal, smart_portfolio_analyzer]
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = f"""
Query: {question}

Use the appropriate tools to help answer the user's query. You can use multiple tools if needed.
Extract the correct parameters like ticker symbols or topics from the query. If no tools are needed, do not call any.
"""
    
    try:
        response = llm_with_tools.invoke(prompt)
    except Exception as e:
        print("❌ LLM Tool Call Error:", e)
        response = None

    output_lines = []
    
    if response and getattr(response, "tool_calls", None):
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            try:
                if tool_name == "get_stock_price":
                    res = get_stock_price.invoke(tool_args)
                elif tool_name == "get_financial_news":
                    res = get_financial_news.invoke(tool_args)
                elif tool_name == "investment_cal":
                    res = investment_cal.invoke(tool_args)
                elif tool_name == "smart_portfolio_analyzer":
                    res = smart_portfolio_analyzer.invoke(tool_args)
                else:
                    res = "Unknown tool"
                output_lines.append(f"{tool_name} ({tool_args}) output:\n{res}")
            except Exception as e:
                output_lines.append(f"Error executing {tool_name}: {e}")
    else:
        output_lines.append("No tool needed")

    tool_output = "\n".join(output_lines)

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