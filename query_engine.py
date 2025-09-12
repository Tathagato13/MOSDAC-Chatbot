from sentence_transformers import SentenceTransformer
import faiss
import pickle
import numpy as np

def load_vector_store(index_file="data/vector_store.faiss", meta_file="data/chunk_data.pkl"):
    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

def query_question(question, index, chunks, top_k=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding), top_k)

    results = [chunks[i] for i in I[0]]
    return results
