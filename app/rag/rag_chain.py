from openai import OpenAI
from .embedder import get_embedder
from .vectorstore import load_faiss_vectorstore
from langchain_openai import ChatOpenAI
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from .reranker import LocalReranker

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


def initialize_retriever(index_path: str = "index/faiss_index", top_k: int = 20):
    """
    Initializes and returns a FAISS-based retriever.

    Args:
        index_path (str): Path to the saved FAISS index directory.
        top_k (int): Number of documents to retrieve per query.

    Returns:
        BaseRetriever: A retriever object ready for RAG.
    """
    embeddings = get_embedder()
    faiss_db = load_faiss_vectorstore(index_path, embeddings)
    retriever = faiss_db.as_retriever(search_kwargs={"k": top_k})
    return retriever


def RAG_pipeline(query: str, system_prompt: str = "You are a helpful therapist.") -> str:
    """
    Executes the full RAG pipeline:
    - Retrieves relevant documents
    - Reranks them using a cross-encoder
    - Injects top context into the prompt
    - Sends to LM Studio for completion

    Args:
        query (str): The user's input question.
        system_prompt (str): Optional system message for the LLM.

    Returns:
        str: The assistant's generated answer.
    """
    retriever = initialize_retriever()
    retrieved_docs = retriever.get_relevant_documents(query)

    reranker = LocalReranker()
    reranked_docs = reranker.rerank(query, retrieved_docs, top_k=3)

    context = "\n\n".join([doc.page_content for doc in reranked_docs])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]

    completion = client.chat.completions.create(
        model="local-model",  
        messages=messages,
        temperature=0.7,
        stream=True,
        max_completion_tokens=10000
    )

    return completion.choices[0].message.content.strip()

