from query_engine import load_vector_store, query_question

index, chunks = load_vector_store()

question = input("Ask a question: ")
results = query_question(question, index, chunks)

print("\nTop Answers:")
for i, res in enumerate(results, 1):
    print(f"\n--- Result {i} ---\n{res}")
