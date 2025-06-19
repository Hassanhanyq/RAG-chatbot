from typing import List, Dict
from langchain.docstore.document import Document
from langchain_experimental.text_splitter import SemanticChunker
from .embedder import get_embedder


def semantic_chunk_documents(
    extracted_texts: List[Dict[str, str]],
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> List[Document]:
    """
    Applies semantic chunking to a list of text documents using LangChain's SemanticChunker.

    Args:
        extracted_texts (List[Dict[str, str]]): 
            List of dicts with 'filename' and 'text' keys from PDF loader.
        embedding_model_name (str): 
            HuggingFace model name used for computing embeddings.

    Returns:
        List[Document]: A list of semantically chunked LangChain Document objects.
    """
    embedder = get_embedder(embedding_model_name)
    chunker = SemanticChunker(embeddings=embedder)

    all_chunks = []

    for item in extracted_texts:
        filename = item["filename"]
        text = item["text"]

        #Create semantic chunks with metadata
        chunks = chunker.create_documents([text], metadatas=[{"source": filename}])
        all_chunks.extend(chunks)

    return all_chunks
