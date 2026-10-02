from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_store = PineconeVectorStore(
    index_name="shopb-support",
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)


test_questions = [
    {
        "question": "How long does delivery take?",
        "expected_section": "Shipping & Delivery"
    },
    {
        "question": "Can I return a damaged product?",
        "expected_section": "Returns & Refunds"
    },
    {
        "question": "How can I become a vendor?",
        "expected_section": "Vendor Policies"
    },
    {
        "question": "What payment methods are available?",
        "expected_section": "Payments"
    },
    {
        "question": "How do I create an account?",
        "expected_section": "Accounts"
    }
]


print("\n==============================")
print("SHOPB.AFRICA RAG EVALUATION")
print("==============================\n")


correct = 0

for test in test_questions:

    question = test["question"]
    expected = test["expected_section"]

    documents = retriever.invoke(question)

    retrieved_sections = [
        doc.metadata.get(
            "section",
            "Unknown"
        )
        for doc in documents
    ]

    print(f"Question: {question}")
    print(f"Expected: {expected}")
    print(f"Retrieved: {retrieved_sections}")

    if expected in retrieved_sections:
        print("Result: PASS")
        correct += 1
    else:
        print("Result: FAIL")

    print("-" * 50)


accuracy = (
    correct / len(test_questions)
) * 100


print("\n==============================")
print(f"Retrieval Accuracy: {accuracy:.1f}%")
print("==============================")