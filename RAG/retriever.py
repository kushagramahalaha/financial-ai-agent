import os
from dotenv import load_dotenv
import voyageai

from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

client = voyageai.Client(api_key=VOYAGE_API_KEY)


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


def main():

    embeddings = VoyageEmbeddings()

    db = FAISS.load_local(
        "../vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(search_kwargs={"k": 3})

    query = input("Ask a financial question: ")

    docs = retriever.get_relevant_documents(query)

    print("\nRelevant Knowledge:\n")

    for doc in docs:
        print(doc.page_content)
        print("-" * 40)


if __name__ == "__main__":
    main()