from scripts.trustpilot_scraper import *

if __name__ == "__main__":
    print("🚀 Running Trustpilot Scraper...")
    all_reviews = []
    
    for company, url in COMPANY_URLS.items():
        reviews = scrape_trustpilot(company, url)
        all_reviews.extend(reviews)

    if all_reviews:
        save_to_db(all_reviews)
        print(f"✅ {len(all_reviews)} reviews saved to database!")
    else:
        print("⚠️ No reviews collected!")
