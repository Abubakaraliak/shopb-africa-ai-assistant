
from rag_pipeline import ask_shopb


# Test questions
questions = [
    "How long does delivery take?",
    "Can I return a damaged product?",
    "How can I become a vendor?",
    "What payment methods are available?",
    "Can you tell me the status of my order?"
]


# Run the RAG assistant
for question in questions:

    print("\n" + "=" * 60)
    print("CUSTOMER QUESTION:")
    print(question)

    print("\nAI ASSISTANT:")

    try:
        result = ask_shopb(question)

        print(result["answer"])

        print("\nSOURCES:")
        for source in result["sources"]:
            print(source)

    except Exception as error:
        print(f"Error: {error}")

    print("=" * 60)