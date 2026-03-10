"""FAISS vector store management."""

from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings

_vector_store: FAISS | None = None
_embeddings: GoogleGenerativeAIEmbeddings | None = None


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )
    return _embeddings


def get_vector_store() -> FAISS | None:
    """Return the current in-memory vector store, loading from disk if available."""
    global _vector_store
    if _vector_store is None:
        index_path = settings.vector_store_dir / "index.faiss"
        if index_path.exists():
            _vector_store = FAISS.load_local(
                str(settings.vector_store_dir),
                _get_embeddings(),
                allow_dangerous_deserialization=True,
            )
    return _vector_store


def add_documents(chunks: list[Document]) -> None:
    """Embed chunks and add them to the FAISS vector store."""
    global _vector_store
    embeddings = _get_embeddings()
    if _vector_store is None:
        _vector_store = FAISS.from_documents(chunks, embeddings)
    else:
        _vector_store.add_documents(chunks)
    _vector_store.save_local(str(settings.vector_store_dir))


def similarity_search(query: str, k: int = 4) -> list[Document]:
    """Search the vector store for the most relevant chunks."""
    store = get_vector_store()
    if store is None:
        return []
    return store.similarity_search(query, k=k)


def clear_vector_store() -> None:
    """Remove the vector store from memory and disk."""
    global _vector_store
    _vector_store = None
    store_dir = settings.vector_store_dir
    for f in store_dir.glob("*"):
        f.unlink()


def list_indexed_sources() -> list[str]:
    """Return unique source filenames currently in the index."""
    store = get_vector_store()
    if store is None:
        return []
    sources = set()
    for doc_id in store.docstore._dict:
        doc = store.docstore._dict[doc_id]
        src = doc.metadata.get("source", "")
        if src:
            sources.add(src)
    return sorted(sources)
