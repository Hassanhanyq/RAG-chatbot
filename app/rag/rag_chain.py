from openai import OpenAI
from .initlization import get_reranker, get_retriever
from langchain_openai import ChatOpenAI
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever


client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")



def RAG_pipeline(query: str, system_prompt: str = "You are a helpful therapist."):
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
    retriever = get_retriever()
    reranker = get_reranker()

    retrieved_docs = retriever.get_relevant_documents(query)
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
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
           yield chunk.choices[0].delta.content

