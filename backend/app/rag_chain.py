"""RAG chain using LangChain + Gemini for conversational Q&A with citations."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

from app.config import settings
from app.vector_store import similarity_search


SYSTEM_PROMPT = """\
You are DocuMind, an intelligent document assistant. Answer the user's question \
based ONLY on the provided context from their uploaded documents. \
If the context does not contain enough information to answer, say so honestly.

Rules:
1. Ground every claim in the provided context.
2. Cite your sources using [Source: filename, Page: N] after each relevant statement.
3. Be concise and accurate.
4. If you don't know, say "I don't have enough information in the uploaded documents to answer that."

Context:
{context}
"""

_llm: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model=settings.chat_model,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
    return _llm


def _format_context(docs: list[Document]) -> str:
    """Format retrieved documents into a context string."""
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        parts.append(f"[{i}] (Source: {source}, Page: {page})\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def _build_chat_history(history: list[dict]) -> list[HumanMessage | AIMessage]:
    """Convert raw chat history dicts to LangChain message objects."""
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages


def query(question: str, chat_history: list[dict] | None = None) -> dict:
    """
    Run a RAG query: retrieve relevant chunks, build prompt, get LLM answer.

    Returns a dict with 'answer' and 'sources'.
    """
    if chat_history is None:
        chat_history = []

    # Retrieve relevant chunks
    retrieved_docs = similarity_search(question, k=5)

    if not retrieved_docs:
        return {
            "answer": "No documents have been uploaded yet. Please upload a PDF or DOCX file first.",
            "sources": [],
        }

    context = _format_context(retrieved_docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    llm = _get_llm()
    chain = prompt | llm

    lc_history = _build_chat_history(chat_history)

    response = chain.invoke(
        {
            "context": context,
            "chat_history": lc_history,
            "question": question,
        }
    )

    # Build source citations list
    sources = []
    seen = set()
    for doc in retrieved_docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        key = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append({"source": source, "page": page})

    return {
        "answer": response.content,
        "sources": sources,
    }
