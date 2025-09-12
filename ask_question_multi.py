from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import pickle

# Load FAISS index and chunks
def load_vector_store(index_file="vector_store.faiss", meta_file="chunk_data.pkl"):
    index = faiss.read_index(index_file)
    with open(meta_file, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks

# Multi-query retriever
def query_question_multi(question, index, chunks, top_k=2, variant_count=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    variants = [question]
    if variant_count >= 2:
        variants.append(f"What is meant by: {question}?")
    if variant_count >= 3:
        variants.append(f"Explain: {question}")

    query_embeddings = model.encode(variants)
    all_results = []
    seen_indexes = set()

    for emb in query_embeddings:
        D, I = index.search(np.array([emb]), top_k)
        for idx in I[0]:
            if idx not in seen_indexes:
                all_results.append(chunks[idx])
                seen_indexes.add(idx)

    return all_results

# Run the multi-query search
if __name__ == "__main__":
    index, chunks = load_vector_store()

    question = input("Ask a question: ")
    results = query_question_multi(question, index, chunks, top_k=2, variant_count=3)

    print("\nTop Answers:")
    for i, res in enumerate(results, 1):
        print(f"\n--- Result {i} ---\n{res}")
