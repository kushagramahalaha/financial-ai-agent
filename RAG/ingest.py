import os
from dotenv import load_dotenv
import voyageai

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings

# Load environment variables
load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# Initialize Voyage client
client = voyageai.Client(api_key=VOYAGE_API_KEY)


# Custom LangChain Embedding Wrapper
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

    print("Loading financial knowledge...")

    loader = TextLoader("../data/finance.txt")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = text_splitter.split_documents(documents)

    print(f"Total chunks created: {len(docs)}")

    embeddings = VoyageEmbeddings()

    print("Creating vector database...")

    vector_db = FAISS.from_documents(
        docs,
        embeddings
    )

    vector_db.save_local("../vector_db")

    print("Vector database successfully created.")


if __name__ == "__main__":
    main()