# MOSDAC-Chatbot
The repo contains the project about an AI power Chatbot for MOSDAC website of ISRO which contain all the structural and unistructural information about the website and return those as a conversional manner 



A Python-based chatbot project with web integration. This repository contains the core logic, web templates, and supporting scripts to run and extend the chatbot.

---

## 📂 Project Structure


Directories

artifacts/ → Stores generated embeddings, vector indexes, or model output files
chatbot_logic/ → Core chatbot logic (retriever, query engine, vector store, chunker, scraper, file extractors)
data/ → Raw scraped pages, cleaned text, metadata, and knowledge JSON files
files/ → Any uploaded/downloadable files used during testing or demo
logs/ → Scraper logs, runtime logs, and system diagnostics
scripts/ → Helper utilities, ingestion scripts, testing scripts, batch operations
static/ → Frontend static assets (CSS, JS, images, favicon)
templates/ → HTML templates for the frontend UI

Files (Root Level)

main.py → Entry point; starts the chatbot backend or triggers ingestion workflows
query_engine.py → Coordinates retrieval and LLM response generation with citations
retriever.py → Performs similarity search on the vector store; returns top-k chunks
vector_store.py → Handles embedding, index creation, loading, saving, and similarity search
mosdac_scraper.py → Scrapes MOSDAC website pages; saves raw and cleaned content
chunker.py → Splits cleaned text into semantic chunks with metadata
file_extractor.py → Extracts structured text from HTML/PDF and normalizes content
ask_question.py → Simple CLI tool to ask one question and get an answer
ask_question_multi.py → Multi-query / interactive CLI for repeated testing
full_satellite_kg_with_faqs.json → Knowledge graph + FAQs used as a prebuilt dataset
content_metadata.json → Metadata for all scraped/ingested files (URLs, titles, hashes)
scraper.log → Log output produced during scraping runs
index.html → Main user-interface page for the chatbot
script.js → Frontend logic to send user queries to backend and display answers
style.css → UI styling for chatbot frontend
requirements.txt → List of Python dependencies required for the project
.gitignore → Specifies which generated files and folders Git must ignore

---
