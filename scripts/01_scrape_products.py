"""
Flipkart Mobile Phone Price Scraper
Scrapes product title, price, MRP, discount, rating, reviews, specs, URL, image, and Assured badge.
Saves both a daily snapshot and an append-only price history log.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import os
import pandas as pd
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data_raw")

SEARCH_QUERY = "mobile phones"
MAX_PAGES = 400
PAGE_LOAD_WAIT = 2
COURTESY_DELAY = 3
STOP_AFTER_EMPTY_PAGES = 2


def run_scraper():
    driver = webdriver.Chrome()
    all_results = []
    today = date.today().isoformat()
    consecutive_empty_pages = 0

    for page_number in range(1, MAX_PAGES + 1):
        url = f"https://www.flipkart.com/search?q={SEARCH_QUERY.replace(' ', '+')}&page={page_number}"
        print(f"Scraping page {page_number}...")

        driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)

        # Fixed: use the outer <a class="k7wcnx"> as the card - it wraps both image and title/price
        cards = driver.find_elements(By.CLASS_NAME, "k7wcnx")
        print(f"  -> Found {len(cards)} product cards on this page")

        if len(cards) == 0:
            consecutive_empty_pages += 1
            print(f"  Warning: empty page ({consecutive_empty_pages} in a row)")
            if consecutive_empty_pages >= STOP_AFTER_EMPTY_PAGES:
                print(f"Stopping early: {STOP_AFTER_EMPTY_PAGES} consecutive empty pages.")
                break
            time.sleep(COURTESY_DELAY)
            continue
        else:
            consecutive_empty_pages = 0

        for card in cards:
            try:
                title = card.find_element(By.CLASS_NAME, "RG5Slk").text
            except:
                title = None
            try:
                price_text = card.find_element(By.CLASS_NAME, "hZ3P6w").text
                price_clean = re.sub(r"[^\d]", "", price_text)
                price = int(price_clean) if price_clean else None
            except:
                price = None
            try:
                mrp_text = card.find_element(By.CLASS_NAME, "kRYCnD").text
                mrp_clean = re.sub(r"[^\d]", "", mrp_text)
                mrp = int(mrp_clean) if mrp_clean else None
            except:
                mrp = None
            try:
                discount_text = card.find_element(By.CLASS_NAME, "HQe8jr").text
            except:
                discount_text = None
            try:
                rating = card.find_element(By.CLASS_NAME, "MKiFS6").text
            except:
                rating = None
            try:
                specs_text = card.find_element(By.CLASS_NAME, "CMXw7N").text
            except:
                specs_text = ""

            # Fixed: card itself IS the link now
            try:
                product_url = card.get_attribute("href")
            except:
                product_url = None

            # Fixed: image is now reachable since card wraps it
            try:
                image_url = card.find_element(By.CLASS_NAME, "UCc1lI").get_attribute("src")
            except:
                image_url = None

            try:
                rating_full_text = card.find_element(By.CLASS_NAME, "PvbNMB").text
                review_match = re.search(r"([\d,]+)\s*Reviews", rating_full_text)
                review_count = int(review_match.group(1).replace(",", "")) if review_match else None
            except:
                review_count = None
            try:
                card.find_element(By.CLASS_NAME, "eSKUUb")
                is_assured = True
            except:
                is_assured = False

            all_results.append({
                "title": title,
                "price": price,
                "mrp": mrp,
                "discount_text": discount_text,
                "rating": rating,
                "review_count": review_count,
                "specs": specs_text,
                "product_url": product_url,
                "image_url": image_url,
                "is_assured": is_assured,
                "scrape_date": today
            })

        print(f"Page {page_number} done. Total products so far: {len(all_results)}")
        time.sleep(COURTESY_DELAY)

    driver.quit()

    print(f"\nFinished! Total products scraped: {len(all_results)}")

    df = pd.DataFrame(all_results)
    print(df.head())

    os.makedirs(RAW_DIR, exist_ok=True)
    snapshot_path = os.path.join(RAW_DIR, "latest_snapshot.csv")
    history_path = os.path.join(RAW_DIR, "price_history.csv")

    df.to_csv(snapshot_path, index=False)
    print("Saved latest_snapshot.csv")

    try:
        history_df = pd.read_csv(history_path)
        combined_df = pd.concat([history_df, df], ignore_index=True)
    except FileNotFoundError:
        combined_df = df

    combined_df.to_csv(history_path, index=False)
    print(f"price_history.csv now has {len(combined_df)} total rows")


if __name__ == "__main__":
    run_scraper()