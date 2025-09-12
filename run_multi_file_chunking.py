import os
from file_extractor import extract_text_from_file
from chunker import chunk_text
from vector_store import build_vector_store

FOLDER = "files"  # Folder with mixed files

all_chunks = []

for filename in os.listdir(FOLDER):
    if filename.lower().endswith((".pdf", ".docx", ".xlsx")):
        file_path = os.path.join(FOLDER, filename)
        print(f" Processing: {filename}")

        text = extract_text_from_file(file_path)
        chunks = chunk_text(text)
        tagged_chunks = [f"[{filename}] {chunk}" for chunk in chunks]
        all_chunks.extend(tagged_chunks)

build_vector_store(all_chunks)
