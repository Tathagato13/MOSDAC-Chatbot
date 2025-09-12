# retriever.py
# -------------------------------------------------
# All your original imports & functions remain unchanged.
# I am only adding the FAQ-first retrieval code at the bottom.

from collections import deque
import json
import re
import requests
import faiss
import numpy as np
from bs4 import BeautifulSoup
import spacy
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import google.generativeai as genai
from .query_engine import query_question, load_vector_store

# ----------------------------
# ORIGINAL SETUP (UNCHANGED)
# ----------------------------

pdf_index, pdf_chunks = load_vector_store()
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def load_knowledge_graph(path):
    with open(path, "r", encoding="utf-8") as f:
        kg = json.load(f)

    section_names = []
    section_map = {}
    text_map = {}
    for satellite_key, pages in kg.items():
        for page in pages:
            title = page.get("title", "").strip()
            if not title:
                continue
            key = title.lower()
            paragraphs = page.get("paragraphs", [])
            lists = page.get("lists", [])
            combined_text = "\n".join(paragraphs + lists)
            section_names.append(key)
            section_map[key] = title
            text_map[key] = combined_text
    return section_names, section_map, text_map

section_names, section_map, text_map = load_knowledge_graph("data/full_satellite_data.json")
section_embeddings = embedder.encode(section_names).astype("float32")
index = faiss.IndexFlatL2(section_embeddings.shape[1])
index.add(section_embeddings)

class ConversationManager:
    def __init__(self, max_history=10):
        self.conversations = {}
        self.max_history = max_history
    def get_conversation(self, session_id):
        if session_id not in self.conversations:
            self.conversations[session_id] = deque(maxlen=self.max_history)
        return self.conversations[session_id]
    def add_message(self, session_id, role, content):
        conv = self.get_conversation(session_id)
        conv.append({"role": role, "content": content})
    def get_history(self, session_id):
        return list(self.get_conversation(session_id))

conversation_manager = ConversationManager()

def extract_url(text):
    match = re.search(r"(https?://[^\s]+)", text)
    return match.group(1) if match else None

def scrape_page_content_raw(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        blocks = []
        for tag in soup.find_all(["p", "li", "h2", "div", "span"]):
            text = tag.get_text(strip=True)
            if text and len(text.split()) > 3:
                blocks.append(text)
        return "\n".join(blocks[:12]) if blocks else "No readable content found."
    except Exception as e:
        return f"❌ Failed to fetch content from URL: {str(e)}"

def extract_keywords(text):
    doc = nlp(text)
    return {token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "PROPN") and not token.is_stop}

def normalize_question_with_gemini(original_question: str) -> str:
    prompt = f"""
You are helping a chatbot understand and rephrase user questions.
Reword the following question to be more standard and search-friendly, keeping the same meaning.

Question:
"{original_question}"

Rephrased:
"""
    try:
        response = model.generate_content(prompt)
        normalized = response.text.strip()
        if len(normalized.split()) < 3:
            return original_question
        return normalized
    except Exception as e:
        print(f"⚠️ Gemini normalization failed: {e}")
        return original_question

def generate_answer_with_rag(context_text, question, conversation_history):
    history_str = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history)
    prompt = f"""
You are a helpful assistant for the Indian Space Research Organisation (ISRO). 
Maintain context from previous messages in this conversation.

Previous conversation:
{history_str}

Current context from MOSDAC:
{context_text}

Current question:
{question}

Provide a helpful answer that considers both the current context and previous conversation. 
If the question refers to something mentioned earlier, maintain continuity.
Answer:""".strip()
    try:
        response = model.generate_content(prompt)
        output = response.text.strip()
        if len(output) < 10 or "no info" in output.lower():
            return "🛰️ Sorry, I couldn't find useful information related to your question. Try rephrasing or visit MOSDAC.gov.in for details."
        return output
    except Exception as e:
        return f"❌ Gemini failed: {str(e)}"

def get_response(user_input: str, session_id: str) -> str:
    user_input = user_input.strip().lower()
    conversation_manager.add_message(session_id, "user", user_input)
    normalized_query = normalize_question_with_gemini(user_input)
    print(f"🧠 Normalized Query: {normalized_query}")
    user_keywords = extract_keywords(normalized_query)
    keyword_scores = {
        section_key: len(user_keywords & set(section_key.split()))
        for section_key in section_names
    }
    best_keyword_match = max(keyword_scores, key=keyword_scores.get)
    keyword_score = keyword_scores[best_keyword_match]
    user_vec = embedder.encode([normalized_query]).astype("float32")
    _, I = index.search(user_vec, k=1)
    best_faiss_match = section_names[I[0][0]]
    final_match = best_keyword_match if keyword_score >= 2 else best_faiss_match
    section_name = section_map[final_match]
    kg_context = text_map.get(section_name.lower(), "")
    pdf_results = query_question(normalized_query, pdf_index, pdf_chunks)
    pdf_context = "\n\n".join(pdf_results[:2])
    full_context = f"""
[MOSDAC Knowledge Graph Section: {section_name}]
{kg_context}

[Extracted PDF Chunks]
{pdf_context}
""".strip()
    print(f"\n🎯 FINAL MATCH: {section_name}")
    print(f"🔍 User Query: {user_input}")
    print("📄 CONTEXT SENT TO GEMINI:")
    print(full_context[:500] + "..." if len(full_context) > 500 else full_context)
    conversation_history = conversation_manager.get_history(session_id)
    bot_response = generate_answer_with_rag(full_context, user_input, conversation_history)
    conversation_manager.add_message(session_id, "assistant", bot_response)
    return bot_response

# ----------------------------
# FAQ-FIRST RETRIEVER (NEW)
# ----------------------------

FAQ_FILE = "data/full_satellite_kg_with_faqs"

def load_faq_entries():
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ FAQ file not found: {FAQ_FILE}")
        return []
    faq_entries = []
    if isinstance(data, dict) and "FAQ_entries" in data:
        for item in data["FAQ_entries"]:
            q = item.get("title", "").strip()
            a = "\n".join(item.get("paragraphs", []))
            if q and a:
                faq_entries.append({"question": q, "answer": a})
    return faq_entries

faq_entries_list = load_faq_entries()
if faq_entries_list:
    faq_questions = [f["question"] for f in faq_entries_list]
    faq_embeddings = embedder.encode(faq_questions, convert_to_numpy=True)
    norms = np.linalg.norm(faq_embeddings, axis=1, keepdims=True)
    faq_embeddings = (faq_embeddings / norms).astype("float32")
    faq_index = faiss.IndexFlatIP(faq_embeddings.shape[1])
    faq_index.add(faq_embeddings)
else:
    faq_index = None

def search_faq(normalized_query, threshold=0.72):
    if not faq_index or not faq_entries_list:
        return None
    q_emb = embedder.encode([normalized_query], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)
    q_emb = q_emb.astype("float32")
    D, I = faq_index.search(q_emb, 1)
    score = float(D[0][0])
    if score >= threshold:
        return faq_entries_list[I[0][0]]["answer"]
    return None

def get_response_with_faq_first(user_input: str, session_id: str, threshold=0.72):
    normalized_query = normalize_question_with_gemini(user_input)
    faq_ans = search_faq(normalized_query, threshold)
    if faq_ans:
        conversation_manager.add_message(session_id, "user", user_input)
        conversation_manager.add_message(session_id, "assistant", faq_ans)
        return faq_ans
    return get_response(user_input, session_id)
