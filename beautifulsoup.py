import os
import time
import requests
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # ✅ Required
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# === Setup Chrome Options for Headless Mode ===
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# === Setup ChromeDriver with Service ===
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# === Constants ===
BASE_URL = "https://www.mosdac.gov.in"
DOWNLOAD_DIR = "mosdac_pdfs"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === List of missions to visit ===
mission_pages = [
    "https://mosdac.gov.in/insat-3dr",
    "https://mosdac.gov.in/insat-3d",
    "https://mosdac.gov.in/kalpana-1",
    "https://mosdac.gov.in/insat-3a",
    "https://mosdac.gov.in/megha-tropiques",
    "https://mosdac.gov.in/saral-altika",
    "https://mosdac.gov.in/oceansat-2",
    "https://mosdac.gov.in/oceansat-3",
    "https://mosdac.gov.in/scatsat-1",
    ""
]

# === Download PDF Function ===
def download_pdf(pdf_url):
    filename = os.path.basename(pdf_url)
    save_path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(save_path):
        try:
            print(f"📥 Downloading: {filename}")
            r = requests.get(pdf_url)
            with open(save_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"❌ Failed to download {pdf_url}: {e}")

# === Main Automation Loop ===
for mission_url in mission_pages:
    print(f"\n🔍 Visiting {mission_url}")
    driver.get(mission_url)
    time.sleep(3)  # Allow JS content to load

    # Find all <a> links
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and href.endswith(".pdf"):
            full_url = urljoin(BASE_URL, href)
            download_pdf(full_url)

driver.quit()
print("\n✅ All PDFs downloaded.")
