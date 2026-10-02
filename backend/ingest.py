
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from backend.document_processor import chunks

load_dotenv()

INDEX_NAME = "shopb-support"

# Connect to Pinecone
pc = Pinecone()
index = pc.Index(INDEX_NAME)

# Clear old vectors so the index contains only
# the newly processed chunks and metadata.
print("Clearing the existing demo index...")
index.delete(delete_all=True)

# Initialize the embedding model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# Upload the chunks and their metadata
print("Uploading updated documents to Pinecone...")

vector_store = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=INDEX_NAME
)

print(f"Successfully uploaded {len(chunks)} chunks.")
print("Pinecone metadata now includes section names.")