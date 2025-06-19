from sentence_transformers import CrossEncoder
from langchain.docstore.document import Document
from typing import List


class LocalReranker:
    """
    Reranks retrieved documents using a cross-encoder model.

    Default: Uses BAAI/bge-reranker-large for dense relevance scoring.

    Methods:
        rerank(query, docs, top_k): Returns top_k most relevant documents.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[Document], top_k: int = 3) -> List[Document]:
        """
        Reranks a list of documents based on relevance to the query.

        Args:
            query (str): The input user query.
            docs (List[Document]): List of LangChain Document objects.
            top_k (int): Number of top documents to return.

        Returns:
            List[Document]: Top-k documents ranked by cross-encoder relevance.
        """
        
        pairs = [(query, doc.page_content) for doc in docs]

        
        scores = self.model.predict(pairs)

        
        reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in reranked[:top_k]]
