import os
from dotenv import load_dotenv
import voyageai

from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

client = voyageai.Client(api_key=VOYAGE_API_KEY)


# -----------------------------
# Embedding Class
# -----------------------------
class VoyageEmbeddings(Embeddings):

    def embed_documents(self, texts):
        result = client.embed(
            texts,
            model="voyage-3-large"
        )
        return result.embeddings

    def embed_query(self, text):
        result = client.embed(
            [text],
            model="voyage-3-large"
        )
        return result.embeddings[0]


# -----------------------------
# LOAD DB (GLOBAL - IMPORTANT)
# -----------------------------
embeddings = VoyageEmbeddings()

db = FAISS.load_local(
    "vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(
    search_kwargs={
        "k": 5
    }
)
# llm can decide what file to select for the query search based on the query type (investment, stock, tax, general)

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def classify_query(query):
    prompt = f"""
Classify the query into one of these:
- investment
- stock
- tax
- general

Query: {query}

Return only one word.
"""
    return llm.invoke(prompt).content.strip().lower()
# -----------------------------
# ✅ FUNCTION USED BY GRAPH
# -----------------------------
def get_rag_context(query):

    docs = retriever.invoke(query)

    context = ""
    sources = []

    for doc in docs[:3]:
        context += doc.page_content + "\n\n"
        sources.append(doc.metadata.get("source", "unknown"))

    return {
        "context": context,
        "sources": list(set(sources))
    }


# -----------------------------
# OPTIONAL TEST (you can keep)
# -----------------------------
if __name__ == "__main__":

    query = input("Ask a financial question: ")

    docs = retriever.invoke(query)

    print("\nRelevant Knowledge:\n")

    for doc in docs:
        print(doc.page_content)
        print("-" * 40)