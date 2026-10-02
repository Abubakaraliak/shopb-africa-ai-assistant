from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()


# -----------------------------------------
# 1. Create embedding model
# -----------------------------------------

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# -----------------------------------------
# 2. Connect to Pinecone
# -----------------------------------------

vector_store = PineconeVectorStore(
    index_name="shopb-support",
    embedding=embeddings
)


# -----------------------------------------
# 3. Customer question
# -----------------------------------------

question = question = "I received a damaged product. Can I return it?"

# -----------------------------------------
# 4. Search Pinecone
# -----------------------------------------

results = vector_store.similarity_search(
    question,
    k=1
)


# -----------------------------------------
# 5. Display results
# -----------------------------------------

print("\nSEARCH QUESTION:")
print(question)

print("\nRELEVANT DOCUMENTS:")

for i, result in enumerate(results, start=1):
    print("\n" + "=" * 60)
    print(f"RESULT {i+1}")
    print("=" * 60)

    print(result.page_content)

    print("\nMetadata:")
    print(result.metadata)