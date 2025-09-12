import os
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
import time
import hashlib
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
JSON_OUTPUT_FILE = "full_satellite_data.json"
METADATA_FILE = "content_metadata.json"
LOG_FILE = "scraper.log"
DOCUMENTS_ARCHIVE_FOLDER = "mosdac_documents_archive"
# Allowed file types to download
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# --- Global Data ---
satellite_data = {}
content_hashes = {}

# --- Helper Functions ---
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def load_previous_data():
    """Loads existing scraped data and metadata hashes from files."""
    global satellite_data, content_hashes
    if os.path.exists(JSON_OUTPUT_FILE):
        try:
            with open(JSON_OUTPUT_FILE, 'r', encoding='utf-8') as f:
                satellite_data = json.load(f)
            logging.info(f"Loaded existing data from {JSON_OUTPUT_FILE}")
        except json.JSONDecodeError:
            logging.warning(f"{JSON_OUTPUT_FILE} is corrupted. Starting fresh.")
            satellite_data = {}

    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                content_hashes = json.load(f)
            logging.info(f"Loaded content hashes from {METADATA_FILE}")
        except json.JSONDecodeError:
            logging.warning(f"{METADATA_FILE} is corrupted. Starting fresh.")
            content_hashes = {}

def save_metadata():
    """Saves the updated content hash metadata file."""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(content_hashes, f, indent=4)
    logging.info(f"✅ Content hashes saved to: {METADATA_FILE}")

def process_page_content(page_source, page_url, base_path):
    """
    Processes the HTML source of a page, extracts data, and downloads documents.
    This function is used by both Requests and Selenium to ensure identical logic.
    """
    global satellite_data, content_hashes
    current_hash = hashlib.sha256(page_source.encode('utf-8')).hexdigest()
    old_hash = content_hashes.get(page_url)

    if current_hash == old_hash:
        logging.info(f"      ✅ Skipping (no changes): {page_url}")
        return

    logging.info(f"      🔄 Scraping (updated content): {page_url}")

    page = BeautifulSoup(page_source, "html.parser")
    entry = {
        "url": page_url,
        "title": page.title.text.strip() if page.title else "",
        "meta_description": "",
        "headings": [clean_text(h.text) for h in page.find_all(re.compile("^h[1-6]$"))],
        "paragraphs": [clean_text(p.text) for p in page.find_all("p")],
        "lists": [clean_text(li.text) for li in page.find_all("li")],
        "tables": [clean_text(td.text) for td in page.find_all("td")],
        "documents": [],
        "faqs": []
    }

    meta = page.find("meta", attrs={"name": "description"})
    if meta: entry["meta_description"] = clean_text(meta.get("content", ""))

    # This selector is specifically for MOSDAC's FAQ page structure
    for q_container in page.select('a[href*="#collapse-"]'):
        question = clean_text(q_container.get_text())
        answer_div = q_container.find_next('div', class_='collapse')
        if question and answer_div:
            answer = clean_text(answer_div.get_text())
            entry["faqs"].append({"question": question, "answer": answer})
    
    # Download linked documents
    for a_tag in page.find_all("a", href=True):
        href = a_tag["href"]
        if href and os.path.splitext(href)[1].lower() in ALLOWED_EXTENSIONS:
            file_url = urljoin(page_url, href)
            filename = os.path.basename(urlparse(file_url).path)
            filepath = os.path.join(DOCUMENTS_ARCHIVE_FOLDER, filename)
            try:
                file_res = requests.get(file_url, timeout=20)
                if file_res.ok:
                    with open(filepath, "wb") as f: f.write(file_res.content)
                    entry["documents"].append(filepath)
            except requests.RequestException as e:
                logging.warning(f"      ⚠️ Download failed: {file_url} — {e}")

    # Update data dictionaries
    satellite_data[base_path] = [e for e in satellite_data.get(base_path, []) if e.get('url') != page_url]
    satellite_data[base_path].append(entry)
    content_hashes[page_url] = current_hash


# --- Main Script ---
if __name__ == "__main__":
    os.makedirs(DOCUMENTS_ARCHIVE_FOLDER, exist_ok=True)
    load_previous_data()

    # --- Step 1: Initialize Selenium WebDriver (only if needed) ---
    driver = None
    try:
        logging.info("🚀 Setting up Selenium WebDriver for potential FAQ pages...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("✅ WebDriver initialized successfully.")
    except Exception as e:
        logging.critical(f"❌ CRITICAL: Failed to initialize WebDriver: {e}")
        exit()

    # --- Step 2: Fetch sitemap and find satellite pages ---
    sitemap_url = "https://mosdac.gov.in/sitemap"
    base_url = "https://mosdac.gov.in"
    all_links = []
    try:
        logging.info(f"🌐 Fetching sitemap: {sitemap_url}")
        resp = requests.get(sitemap_url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
        all_links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)]
    except requests.RequestException as e:
        logging.critical(f"❌ CRITICAL: Could not fetch sitemap: {e}")
        if driver: driver.quit()
        exit()

    satellite_base_links = [
        url for url in all_links
        if re.fullmatch(r"https://mosdac.gov.in/[a-z0-9\-]+", url)
    ]
    logging.info(f"📡 Found {len(satellite_base_links)} potential satellite sections to explore.")

    # --- Step 3: Scrape pages using the hybrid approach ---
    try:
        for base_link in satellite_base_links:
            base_path = urlparse(base_link).path.strip("/")
            logging.info(f"\n🔍 Processing Satellite Section: {base_path}")

            # Get all subpages related to this satellite
            subpages = {base_link}
            try:
                response = requests.get(base_link, timeout=15)
                response.raise_for_status()
                main_soup = BeautifulSoup(response.text, "html.parser")
                for a in main_soup.find_all("a", href=True):
                    href = a.get("href", "")
                    if href.startswith(f"/{base_path}") or href.startswith(base_path):
                         subpages.add(urljoin(base_url, href))
            except requests.RequestException as e:
                logging.error(f"  ❌ Could not get subpages for {base_link}: {e}")
                continue

            logging.info(f"  🔗 Found {len(subpages)} subpages for '{base_path}'. Checking for updates...")
            if base_path not in satellite_data:
                satellite_data[base_path] = []

            # Loop through subpages and decide which tool to use
            for page_url in sorted(list(subpages)):
                try:
                    # ✨ HYBRID LOGIC ✨
                    if "faq" in page_url.lower():
                        # --- Use Selenium for FAQ pages ---
                        logging.info(f"    - Using Selenium for: {page_url}")
                        driver.get(page_url)
                        time.sleep(2) # Allow time for dynamic content to load
                        page_source = driver.page_source
                    else:
                        # --- Use Requests for all other pages ---
                        logging.info(f"    - Using Requests for: {page_url}")
                        response = requests.get(page_url, timeout=15)
                        response.raise_for_status()
                        page_source = response.text

                    # Process the content using the shared function
                    process_page_content(page_source, page_url, base_path)

                except Exception as e:
                    logging.error(f"    ❌ Failed to process page {page_url}: {e}")

    finally:
        if driver:
            logging.info("\nShutting down Selenium WebDriver...")
            driver.quit()

    # --- Step 4: Save all data ---
    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(satellite_data, f, indent=4, ensure_ascii=False)
    logging.info(f"\n🎉 Done! All scraped data has been saved to: {JSON_OUTPUT_FILE}")
    save_metadata()