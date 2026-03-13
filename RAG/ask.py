import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv
import voyageai

from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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
# Custom Voyage Embedding Wrapper
# -----------------------------

class VoyageEmbeddings(Embeddings):

    def embed_documents(self, texts):
        result = voyage_client.embed(
            texts,
            model="voyage-3-large"
        )
        return result.embeddings

    def embed_query(self, text):
        result = voyage_client.embed(
            [text],
            model="voyage-3-large"
        )
        return result.embeddings[0]


# -----------------------------
# Load Vector Database
# -----------------------------

embeddings = VoyageEmbeddings()

db = FAISS.load_local(
    "../vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_kwargs={"k":3})


# -----------------------------
# Gemini LLM
# -----------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temprature=0.7
)


# -----------------------------
# Prompt Template
# -----------------------------

prompt = ChatPromptTemplate.from_template(
"""
You are a financial assistant.

Use the following financial knowledge to answer the question clearly.

Context:
{context}

Question:
{question}
"""
)


# -----------------------------
# Output Parser
# -----------------------------

parser = StrOutputParser()


# -----------------------------
# Format Retrieved Documents
# -----------------------------


def format_docs(docs):

    context = "\n\n".join(doc.page_content for doc in docs)

    print("\n Context sent to Gemini:\n")
    print(context)

    return context


# -----------------------------
# RAG Chain (LCEL)
# -----------------------------

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | parser
)


# -----------------------------
# Ask Questions
# -----------------------------

while True:

    question = input("\nAsk a financial question: ")

    if question.lower() in ["exit", "quit"]:
        break

    answer = rag_chain.invoke(question)

    print("\nAI Answer:\n")
    print(answer)