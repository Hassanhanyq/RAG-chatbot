from langchain.embeddings import HuggingFaceEmbeddings

def get_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """
    Returns a HuggingFace embedding model.

    Args:
        model_name (str): Model name from Hugging Face.

    Returns:
        HuggingFaceEmbeddings: Initialized embedding model.
    """
    return HuggingFaceEmbeddings(model_name=model_name)
