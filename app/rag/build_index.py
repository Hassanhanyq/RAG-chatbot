from .loader import load_all_pdfs
from .chunker import semantic_chunk_documents
from .embedder import get_embedder
from .vectorstore import build_faiss_vectorstore

pdfs = load_all_pdfs("app/data")
chunks = semantic_chunk_documents(pdfs)
embedder = get_embedder()

vs = build_faiss_vectorstore(chunks, embedder)

vs.save_local("index/faiss_index")
