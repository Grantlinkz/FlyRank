# Polite Scraper Pipeline — Books to Scrape

## Target Classification

- **Target Site**: Books to Scrape (`https://books.toscrape.com`)
- **Site Type**: Public practice sandbox built specifically for web scraping practice.
- **Scope**: First 3 catalogue pages (`page-1.html`, `page-2.html`, `page-3.html`), discovering 60 unique book detail pages.
- **`robots.txt` Result**: `https://books.toscrape.com/robots.txt` returned HTTP `404 Not Found`.
- **Data Collected**: Title, canonical product URL, raw price text, numeric price in GBP (`price_gbp`), availability status, star rating, description, source catalogue page URL, and ISO 8601 fetch timestamp.
- **Ethics Statement**: *"I will not reuse this code on another site without checking its rules and terms first."*

---

## Politeness Rules & Infrastructure

1. **Honest User-Agent**: Identifies as `FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)`.
2. **Request Timeout**: 10-second timeout on all network requests.
3. **Throttling Delay**: Minimum `500ms` delay between consecutive live HTTP GET requests.
4. **Local Disk Caching**: HTML snapshots are saved in `scraper/cache/` (git-ignored). Subsequent runs read from local cache (`CACHE HIT`) in `<1` second without sending repeated requests to the server.
5. **Non-Blocking Resilience**: Single detail page failures (404s, timeouts) are logged and skipped without crashing the pipeline. Single retry for 5xx/timeouts (no retry for 404/403).

---

## Execution Command

```bash
python scraper/main.py
```

Outputs generated:
- `scraper/output/books.json`: Exactly 60 schema-validated book records.
- `scraper/output/errors.json`: Any invalid/malformed records.
- `scraper/output/run-report.json`: Execution timing, counts, cache hits, and failure metrics.
