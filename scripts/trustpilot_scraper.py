import os
import time
import logging
import chromedriver_autoinstaller
import sqlite3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ✅ Auto-install compatible ChromeDriver
chromedriver_autoinstaller.install()

# ✅ Ensure necessary directories exist
BASE_DIR = os.getcwd()  # Works in both local & GitHub Actions
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Set up logging with a universal path
log_file = os.path.join(LOG_DIR, "scraper_log.txt")  # ✅ This works in all environments

logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# ✅ Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for efficiency
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")

# ✅ Start WebDriver
driver = webdriver.Chrome(options=options)

# ✅ Database Setup
db_path = "C:\\Users\\acer\\trustpilot_review_tracker\\data\\trustpilot_reviews.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

def init_db():
    """Creates database table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            timestamp TEXT,
            time_text TEXT,
            rating TEXT,
            text TEXT,
            country TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ✅ Function to scroll down the page
def scroll_down():
    """Scroll down to load more reviews dynamically."""
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

# ✅ XPath mapping
XPATHS = {
    "review_container": '//article[contains(@class, "styles_reviewCard")]',
    "text": './/section/div[2]/p[1]',
    "timestamp": './/section/div[1]/div[2]/time',
    "rating": './/section/div[1]/div[1]//img',
    "country": './/aside/div/a/div/div'
}

# ✅ Scraping Function
def scrape_trustpilot(company_name, page_links):
    all_reviews = []
    now = datetime.utcnow()
    time_threshold = now - timedelta(days=1)

    for page_url in page_links:
        driver.get(page_url)
        time.sleep(5)  # Allow page to load fully
        scroll_down()

        review_elements = driver.find_elements(By.XPATH, XPATHS["review_container"])
        if not review_elements:
            print(f"❌ No reviews found for {company_name} - {page_url}!")
            logging.warning(f"No reviews found for {company_name} - {page_url}")
            continue

        for review in review_elements:
            try:
                text = review.find_element(By.XPATH, XPATHS["text"]).text.strip()

                time_element = review.find_element(By.XPATH, XPATHS["timestamp"])
                review_time = datetime.strptime(time_element.get_attribute("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
                time_text = time_element.text

                rating_element = review.find_element(By.XPATH, XPATHS["rating"])
                rating = rating_element.get_attribute("alt").split(" ")[1] if rating_element else "N/A"

                try:
                    country = review.find_element(By.XPATH, XPATHS["country"]).text.strip()
                except:
                    country = "Unknown"

                # ✅ Filtering reviews within last 24 hours
                if review_time >= time_threshold:
                    print(f"✅ Keeping: {review_time} | Time Text: {time_text} | Rating: {rating} | Country: {country}")
                    all_reviews.append((company_name, str(review_time), time_text, rating, text, country))
                else:
                    print(f"⏳ Skipped (Older than 24 hours): {review_time} | Time Text: {time_text}")
            except Exception as e:
                logging.error(f"Error scraping {company_name}: {e}")

    return all_reviews

# ✅ Firm URLs (Fixed 5 Pages Each)
COMPANY_URLS = {
    "FundedNext": [
        "https://www.trustpilot.com/review/fundednext.com?sort=recency",
        "https://www.trustpilot.com/review/fundednext.com?page=2&sort=recency",
        "https://www.trustpilot.com/review/fundednext.com?page=3&sort=recency",
        "https://www.trustpilot.com/review/fundednext.com?page=4&sort=recency",
        "https://www.trustpilot.com/review/fundednext.com?page=5&sort=recency"
    ],
    "FTMO": [
        "https://www.trustpilot.com/review/ftmo.com?sort=recency",
        "https://www.trustpilot.com/review/ftmo.com?page=2&sort=recency",
        "https://www.trustpilot.com/review/ftmo.com?page=3&sort=recency",
        "https://www.trustpilot.com/review/ftmo.com?page=4&sort=recency",
        "https://www.trustpilot.com/review/ftmo.com?page=5&sort=recency"
    ],
    "FundingPips": [
        "https://www.trustpilot.com/review/fundingpips.com?sort=recency",
        "https://www.trustpilot.com/review/fundingpips.com?page=2&sort=recency",
        "https://www.trustpilot.com/review/fundingpips.com?page=3&sort=recency",
        "https://www.trustpilot.com/review/fundingpips.com?page=4&sort=recency",
        "https://www.trustpilot.com/review/fundingpips.com?page=5&sort=recency"
    ],
    "The5%ers": [
        "https://www.trustpilot.com/review/the5ers.com?sort=recency",
        "https://www.trustpilot.com/review/the5ers.com?page=2&sort=recency",
        "https://www.trustpilot.com/review/the5ers.com?page=3&sort=recency",
        "https://www.trustpilot.com/review/the5ers.com?page=4&sort=recency",
        "https://www.trustpilot.com/review/the5ers.com?page=5&sort=recency"
    ],
    "Alpha Capital": [
        "https://www.trustpilot.com/review/alphacapitalgroup.uk?sort=recency",
        "https://www.trustpilot.com/review/alphacapitalgroup.uk?page=2&sort=recency",
        "https://www.trustpilot.com/review/alphacapitalgroup.uk?page=3&sort=recency",
        "https://www.trustpilot.com/review/alphacapitalgroup.uk?page=4&sort=recency",
        "https://www.trustpilot.com/review/alphacapitalgroup.uk?page=5&sort=recency"
    ]
}

all_reviews = []
for company, pages in COMPANY_URLS.items():
    logging.info(f"Scraping {company}...")
    reviews = scrape_trustpilot(company, pages)
    all_reviews.extend(reviews)

driver.quit()

# ✅ Save to SQLite Database
if all_reviews:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO reviews (company, timestamp, time_text, rating, text, country) VALUES (?, ?, ?, ?, ?, ?)", all_reviews)
    conn.commit()
    conn.close()
    print(f"✅ Saved {len(all_reviews)} reviews to database!")
else:
    print("⚠️ No recent reviews to save - Check filtering logic!")
