# MOSDAC-Chatbot
The repo contains the project about an AI power Chatbot for MOSDAC website of ISRO which contain all the structural and unistructural information about the website and return those as a conversional manner 



A Python-based chatbot project with web integration. This repository contains the core logic, web templates, and supporting scripts to run and extend the chatbot.

---

## 📂 Project Structure


Directories

artifacts/
Generated artifacts such as embeddings, vector indexes, or model outputs.

chatbot_logic/
Core chatbot logic including retriever, query engine, vector store, chunker, scraper, and file extractors.

data/
Datasets, raw scraped pages, cleaned text, and metadata JSON files.

files/
Uploaded or downloadable files used by the application.

logs/
Application logs, scraper logs, and diagnostic outputs.

scripts/
Helper or utility scripts for ingestion, batch testing, or automation.

static/
Frontend static assets (CSS, JavaScript, images, favicon).

templates/
HTML templates used by the frontend UI.

Files (Root Level)

main.py
Entry point of the project; runs the backend server and ingestion workflows.

query_engine.py
Handles LLM prompting, context construction, and answer generation with citations.

retriever.py
Performs similarity search on the vector store and returns ranked text chunks.

vector_store.py
Manages embedding creation, vector index building, saving, loading, and searching.

mosdac_scraper.py
Scraper/crawler for MOSDAC pages; collects raw HTML and cleaned text.

chunker.py
Splits extracted text into smaller semantic chunks with metadata for retrieval.

file_extractor.py
Extracts text from HTML/PDF and performs cleaning, normalization, and formatting.

ask_question.py
Command-line tool for answering a single query via the chatbot pipeline.

ask_question_multi.py
CLI tool for running multiple queries interactively or in batches.

full_satellite_kg_with_faqs.json
Pre-built knowledge graph and FAQ dataset used for testing/demo.

content_metadata.json
Metadata file storing information about all scraped or processed pages.

scraper.log
Log file generated during scraping (should be ignored in production).

index.html
Main chatbot user interface served to the browser.

script.js
Frontend logic for handling user input and sending requests to backend.

style.css
Styling for the chatbot web interface.

requirements.txt
Python dependency list for installing the environment.

.gitignore
Defines which files/folders Git should ignore.

---
