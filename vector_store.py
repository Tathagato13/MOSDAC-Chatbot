from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

def build_vector_store(chunks, index_file="vector_store.faiss", meta_file="chunk_data.pkl"):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Light and fast
    embeddings = model.encode(chunks, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    faiss.write_index(index, index_file)

    # Save chunks (to get answers later)
    with open(meta_file, "wb") as f:
        pickle.dump(chunks, f)

    print(f" Stored {len(chunks)} chunks in FAISS.")
