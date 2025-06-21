"""

Initializes the embedding model, vector store, and reranker once at import time,
and provides lightweight getter functions to access these shared instances.
"""

from .embedder import get_embedder
from .vectorstore import load_faiss_vectorstore
from .reranker import LocalReranker


_embedder = get_embedder()
_vectorstore = load_faiss_vectorstore("index/faiss_index", _embedder)
_reranker = LocalReranker()


def get_retriever(k=20):
    """
    Returns a retriever object for document search over the FAISS vector store.

    Args:
        k (int): Number of top documents to retrieve. Default is 20.

    Returns:
        BaseRetriever: Configured retriever for semantic search.
    """
    return _vectorstore.as_retriever(search_kwargs={"k": k})


def get_reranker():
    """
    Returns the singleton instance of the reranker.

    Returns:
        LocalReranker: Pre-initialized reranker using a cross-encoder model.
    """
    return _reranker
