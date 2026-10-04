import os

from dotenv import load_dotenv
from pinecone import Pinecone

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# ============================================================
# 1. AI MODEL
# ============================================================

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# ============================================================
# 2. OPENAI EMBEDDINGS
# ============================================================

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# ============================================================
# 3. PINECONE CONNECTION
# ============================================================

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "shopb-support"
)

if not PINECONE_API_KEY:
    raise ValueError(
        "PINECONE_API_KEY is not configured."
    )


pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    PINECONE_INDEX_NAME
)


# ============================================================
# 4. FORMAT CONVERSATION HISTORY
# ============================================================

def format_history(history):

    if not history:
        return "No previous conversation."

    formatted_history = []

    for message in history[-6:]:

        role = message.get(
            "role",
            "user"
        )

        content = message.get(
            "content",
            ""
        )

        if role == "user":

            formatted_history.append(
                f"User: {content}"
            )

        elif role == "assistant":

            formatted_history.append(
                f"Assistant: {content}"
            )

    return "\n".join(
        formatted_history
    )


# ============================================================
# 5. QUESTION REWRITING PROMPT
# ============================================================

rewrite_prompt = ChatPromptTemplate.from_template(
    """
You are a search-query assistant for ShopB.Africa.

Your job is to convert the user's latest question into a
standalone search query for the ShopB.Africa knowledge base.

Conversation history:
{history}

Latest user question:
{question}

Rules:

- Keep the original meaning.
- Use conversation history when necessary.
- Make the question clear and searchable.
- Do not answer the question.
- Return only the search query.
"""
)


rewrite_chain = rewrite_prompt | llm


# ============================================================
# 6. ANSWER PROMPT
# ============================================================

answer_prompt = ChatPromptTemplate.from_template(
    """
You are the AI customer support assistant for ShopB.Africa.

Use ONLY the provided knowledge base context to answer
the customer's question.

Conversation history:
{history}

Knowledge base context:
{context}

Customer question:
{question}

Rules:

1. Answer using information from the knowledge base.
2. Do not invent company policies.
3. Do not invent prices.
4. Do not invent delivery times.
5. Do not invent refund or return policies.
6. Do not invent phone numbers or addresses.
7. Do not claim access to live orders or customer accounts.
8. If the information is not available, say that you
   do not have enough verified information.
9. Keep the answer professional and easy to understand.
10. If appropriate, explain what the customer should do next.
"""
)


answer_chain = answer_prompt | llm


# ============================================================
# 7. SUPPORT ASSESSMENT PROMPT
# ============================================================

assessment_prompt = ChatPromptTemplate.from_template(
    """
You are checking whether the ShopB.Africa knowledge base
contains enough information to answer a customer question.

Knowledge base context:
{context}

Customer question:
{question}

If the context contains enough information to answer the
question accurately, return:

SUPPORTED

If the context does not contain enough information, return:

INSUFFICIENT

Return ONLY one of these two words.
"""
)


assessment_chain = assessment_prompt | llm


# ============================================================
# 8. EXTRACT SOURCES
# ============================================================

def extract_sources(matches):

    sources = []
    seen_sources = set()

    for match in matches:

        metadata = match.get(
            "metadata",
            {}
        ) or {}

        source_name = metadata.get(
            "source",
            metadata.get(
                "source_name",
                "ShopB.Africa Knowledge Base"
            )
        )

        section_name = metadata.get(
            "section",
            metadata.get(
                "section_name",
                "General Information"
            )
        )

        source_key = (
            source_name,
            section_name
        )

        if source_key not in seen_sources:

            seen_sources.add(
                source_key
            )

            sources.append(
                {
                    "source": source_name,
                    "section": section_name
                }
            )

    return sources


# ============================================================
# 9. SEARCH PINECONE
# ============================================================

def search_pinecone(query, top_k=5):

    # Create query embedding
    query_vector = embeddings.embed_query(
        query
    )

    # Search Pinecone
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )

    return results.get(
        "matches",
        []
    )


# ============================================================
# 10. CREATE KNOWLEDGE CONTEXT
# ============================================================

def create_context(matches):

    context_parts = []

    for match in matches:

        metadata = match.get(
            "metadata",
            {}
        ) or {}

        text = metadata.get(
            "text",
            metadata.get(
                "page_content",
                ""
            )
        )

        if text:

            context_parts.append(
                text
            )

    return "\n\n---\n\n".join(
        context_parts
    )


# ============================================================
# 11. MAIN RAG FUNCTION
# ============================================================

def ask_shopb(
    question,
    history=None
):

    try:

        # ----------------------------------------------------
        # STEP 1: Format conversation history
        # ----------------------------------------------------

        history_text = format_history(
            history
        )


        # ----------------------------------------------------
        # STEP 2: Rewrite question
        # ----------------------------------------------------

        rewrite_response = rewrite_chain.invoke(
            {
                "history": history_text,
                "question": question
            }
        )

        search_query = (
            rewrite_response.content
            .strip()
        )


        # ----------------------------------------------------
        # STEP 3: Search Pinecone
        # ----------------------------------------------------

        matches = search_pinecone(
            search_query,
            top_k=5
        )


        # ----------------------------------------------------
        # STEP 4: No documents found
        # ----------------------------------------------------

        if not matches:

            return {
                "answer": (
                    "I couldn't find enough verified information "
                    "about that in the ShopB.Africa knowledge base."
                ),
                "sources": [],
                "search_query": search_query,
                "assessment": "insufficient"
            }


        # ----------------------------------------------------
        # STEP 5: Create knowledge context
        # ----------------------------------------------------

        context = create_context(
            matches
        )


        # ----------------------------------------------------
        # STEP 6: Extract sources
        # ----------------------------------------------------

        sources = extract_sources(
            matches
        )


        # ----------------------------------------------------
        # STEP 7: Check if answer is supported
        # ----------------------------------------------------

        assessment_response = assessment_chain.invoke(
            {
                "context": context,
                "question": question
            }
        )

        assessment = (
            assessment_response.content
            .strip()
            .upper()
        )


        # ----------------------------------------------------
        # STEP 8: Safe fallback
        # ----------------------------------------------------

        if "INSUFFICIENT" in assessment:

            return {
                "answer": (
                    "I couldn't find enough verified information "
                    "in the ShopB.Africa knowledge base to answer "
                    "that accurately. Please contact ShopB.Africa "
                    "support for further assistance."
                ),
                "sources": sources,
                "search_query": search_query,
                "assessment": "insufficient"
            }


        # ----------------------------------------------------
        # STEP 9: Generate final answer
        # ----------------------------------------------------

        answer_response = answer_chain.invoke(
            {
                "history": history_text,
                "context": context,
                "question": question
            }
        )

        answer = (
            answer_response.content
            .strip()
        )


        # ----------------------------------------------------
        # STEP 10: Return result
        # ----------------------------------------------------

        return {
            "answer": answer,
            "sources": sources,
            "search_query": search_query,
            "assessment": "supported"
        }


    except Exception as error:

        print(
            "RAG ERROR:",
            str(error)
        )

        return {
            "answer": (
                "Sorry, I encountered a temporary problem "
                "while processing your question. Please try again."
            ),
            "sources": [],
            "search_query": question,
            "assessment": "error"
        }
