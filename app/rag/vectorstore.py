import faiss
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings


def build_faiss_vectorstore(
    documents: List[Document],
    embedding_model: Embeddings
) -> FAISS:
    """
    Builds an in-memory FAISS vector store from a list of documents and an embedding model.

    Args:
        documents (List[Document]): List of LangChain Document objects to index.
        embedding_model (Embeddings): An embedding model that implements `embed_query()` and `embed_documents()`.

    Returns:
        FAISS: A vector store object containing the document index.
    """
    
    dim = len(embedding_model.embed_query("hello world"))
    index = faiss.IndexFlatL2(dim)

    
    docstore = InMemoryDocstore()
    index_to_docstore_id = {}

    
    vector_store = FAISS(
        embedding_function=embedding_model,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )

    #Add documents to vector store
    vector_store.add_documents(documents)

    return vector_store
def load_faiss_vectorstore(
    index_path: str,
    embedding_model: Embeddings
) -> FAISS:
    """
    Loads a FAISS vector store from disk using a saved FAISS index and embedding model.

    Args:
        index_path (str): Path to the FAISS index directory (should contain index.faiss and index.pkl).
        embedding_model (Embeddings): The same embedding model used when the index was built.

    Returns:
        FAISS: The loaded FAISS vector store.
    """
    return FAISS.load_local(
        folder_path=index_path,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True  
    )
