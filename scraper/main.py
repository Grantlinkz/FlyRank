import os
import sys
import site

# Ensure user site-packages and current script directory are in sys.path
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    site.addsitedir(user_site)

script_dir = os.path.abspath(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import json
import time
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any

from fetcher import fetch_html, USER_AGENT, TIMEOUT
from parser import extract_book_links, extract_next_catalogue_url, extract_raw_book_details
from validator import validate_and_normalize_records

from urllib.robotparser import RobotFileParser

BASE_URL = "https://books.toscrape.com/catalogue/page-1.html"
ROBOTS_URL = "https://books.toscrape.com/robots.txt"
OUTPUT_DIR = os.path.join(script_dir, "output")

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_robots_txt() -> RobotFileParser:
    """Request robots.txt once, parse rules, and return a RobotFileParser instance."""
    print("Checking robots.txt...")
    rp = RobotFileParser()
    rp.set_url(ROBOTS_URL)
    try:
        res = requests.get(ROBOTS_URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        if res.status_code == 200:
            rp.parse(res.text.splitlines())
            print(f"robots.txt checked ({len(res.text)} bytes)")
        else:
            print(f"Notice: robots.txt returned status {res.status_code}")
            rp.parse([])
    except Exception as e:
        print(f"Notice: robots.txt request note: {e}")
        rp.parse([])
    return rp

def run_scraper(limit_catalogue_pages: int = 3, add_fake_failure: bool = True):
    """Run the polite scraping pipeline end-to-end."""
    ensure_output_dir()
    start_time_dt = datetime.now(timezone.utc)
    start_time_iso = start_time_dt.isoformat()
    start_ts = time.time()
    
    rp = check_robots_txt()
    
    total_pages_fetched = 0
    total_cache_hits = 0
    failed_pages_count = 0
    
    # 1. Discover catalogue pages & book URLs
    catalogue_url = BASE_URL
    catalogue_pages_visited = 0
    all_book_urls: List[str] = []
    
    print("\n--- STAGE 1 & 2: Discovering Catalogue Pages ---")
    while catalogue_url and catalogue_pages_visited < limit_catalogue_pages:
        if not rp.can_fetch(USER_AGENT, catalogue_url):
            print(f"Skipping robots.txt disallowed catalogue URL: {catalogue_url}")
            break
            
        catalogue_pages_visited += 1
        cache_name = f"catalogue-page-{catalogue_pages_visited}.html"
        
        try:
            html, is_hit, _ = fetch_html(catalogue_url, cache_name)
            if is_hit:
                total_cache_hits += 1
            else:
                total_pages_fetched += 1
                
            book_urls = extract_book_links(html, catalogue_url)
            for url in book_urls:
                if url not in all_book_urls:
                    all_book_urls.append(url)
                    
            catalogue_url = extract_next_catalogue_url(html, catalogue_url)
        except Exception as err:
            print(f"Error fetching catalogue page {catalogue_url}: {err}")
            failed_pages_count += 1
            break
            
    discovered_url_count = len(all_book_urls)
    print(f"Discovered {discovered_url_count} unique book URLs across {catalogue_pages_visited} catalogue pages.")
    
    # Intentionally inject 1 fake/broken URL to prove failure resilience
    injected_urls_count = 0
    if add_fake_failure:
        fake_url = "https://books.toscrape.com/catalogue/non-existent-broken-book_9999/index.html"
        all_book_urls.append(fake_url)
        injected_urls_count = 1
        print(f"Injected 1 fake broken URL for failure resilience verification: {fake_url}")
        
    # 2. Extract Raw Details for Each Book
    print("\n--- STAGE 3: Extracting Book Details ---")
    raw_books: List[Dict[str, Any]] = []
    
    for idx, book_url in enumerate(all_book_urls, 1):
        if not rp.can_fetch(USER_AGENT, book_url):
            print(f"Skipping robots.txt disallowed book URL: {book_url}")
            continue

        slug = book_url.split("/")[-2] if "/" in book_url else f"book-{idx}"
        cache_name = f"book-{slug}.html"
        fetched_at_str = datetime.now(timezone.utc).isoformat()
        
        html_content = None
        is_hit = False
        
        for attempt in range(2):
            try:
                html_content, is_hit, _ = fetch_html(book_url, cache_name)
                break
            except Exception as err:
                if "404" in str(err) or "403" in str(err):
                    print(f"Skipping 404/403 page without retry: {book_url}")
                    break
                print(f"Fetch attempt {attempt+1} failed for {book_url}: {err}")
                time.sleep(1)
                
        if not html_content:
            print(f"Failed to fetch book detail page: {book_url}")
            failed_pages_count += 1
            continue
            
        if is_hit:
            total_cache_hits += 1
        else:
            total_pages_fetched += 1
            
        try:
            raw_data = extract_raw_book_details(
                detail_html=html_content,
                product_url=book_url,
                source_page=f"https://books.toscrape.com/catalogue/page-{(idx-1)//20 + 1}.html",
                fetched_at=fetched_at_str
            )
            raw_books.append(raw_data)
        except Exception as err:
            print(f"Parser error on detail page {book_url}: {err}")
            failed_pages_count += 1

    # 3. Validate & Normalize Records
    print("\n--- STAGE 4: Validating & Normalizing Records ---")
    valid_books, error_records = validate_and_normalize_records(raw_books)
    
    # Save outputs
    books_json_path = os.path.join(OUTPUT_DIR, "books.json")
    with open(books_json_path, "w", encoding="utf-8") as f:
        json.dump(valid_books, f, indent=2)
    print(f"Saved {len(valid_books)} validated book records to {books_json_path}")
    
    errors_json_path = os.path.join(OUTPUT_DIR, "errors.json")
    with open(errors_json_path, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2)
    print(f"Saved {len(error_records)} error records to {errors_json_path}")
    
    # 4. Generate Run Report
    duration = round(time.time() - start_ts, 2)
    report = {
        "target": "Books to Scrape (https://books.toscrape.com)",
        "scope": f"First {catalogue_pages_visited} catalogue pages ({discovered_url_count} books)",
        "start_time": start_time_iso,
        "duration_seconds": duration,
        "catalogue_pages_visited": catalogue_pages_visited,
        "total_book_urls_discovered": discovered_url_count,
        "injected_urls_count": injected_urls_count,
        "total_urls_requested": len(all_book_urls),
        "pages_fetched_live": total_pages_fetched,
        "cache_hits": total_cache_hits,
        "valid_records": len(valid_books),
        "invalid_records": len(error_records),
        "failed_pages": failed_pages_count,
        "politeness": {
            "user_agent": USER_AGENT,
            "timeout_seconds": TIMEOUT,
            "delay_seconds": 0.5
        }
    }
    
    report_json_path = os.path.join(OUTPUT_DIR, "run-report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print("\n--- STAGE 5: RUN REPORT ---")
    print(json.dumps(report, indent=2))
    print(f"\nRun report successfully saved to {report_json_path}")

if __name__ == "__main__":
    run_scraper()

