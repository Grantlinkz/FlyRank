# FlyRank Backend Platform — Specifications & Milestones

A modern, Spec-Driven RESTful Platform and Data Ingestion Pipeline built with Python 3.10+, FastAPI, Pydantic, PostgreSQL, Docker Compose, Supabase Auth, and BeautifulSoup for the FlyRank Internship Backend Track.

---

## Milestone W5: The Polite Scraper (Data Ingestion Pipeline)

### 1. Target Classification

- **Target Site**: Books to Scrape (`https://books.toscrape.com`)
- **Site Purpose**: Public sandbox built specifically for web scraping practice and learning.
- **Scope**: Exactly the first 3 catalogue pages (`page-1.html`, `page-2.html`, `page-3.html`), discovering 60 unique book detail pages.
- **`robots.txt` Result**: `https://books.toscrape.com/robots.txt` returned HTTP `404 Not Found`.
- **Data Collected**: `title`, `product_url`, `price_text`, `price_gbp`, `availability_text`, `rating_text`, `description`, `source_page`, `fetched_at`.
- **Ethics Note**: *"I will not reuse this code on another site without checking its rules and terms first."*

---

### 2. Politeness Rules & Pipeline Architecture

- **Honest User-Agent**: Identifies as `FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)`.
- **Timeout**: 10-second timeout on all network requests.
- **Throttling Delay**: Minimum `500ms` delay between consecutive live network fetches.
- **Local Disk Caching**: HTML snapshots saved in `scraper/cache/` (git-ignored). Reruns read from local cache (`CACHE HIT`), producing 0 live network requests and identical 60 records (**Idempotency**).
- **Non-Blocking Resilience**: Single detail page failures (404s, timeouts) are logged and skipped without halting execution.

---

### 3. Execution Command

```bash
python scraper/main.py
```

Generated Output Artifacts:
- `scraper/output/books.json`: Exactly 60 schema-validated book records.
- `scraper/output/errors.json`: Any invalid/malformed records.
- `scraper/output/run-report.json`: Pipeline execution metrics report.

---

### 4. Verified Sample Run Report (`output/run-report.json`)

```json
{
  "target": "Books to Scrape (https://books.toscrape.com)",
  "scope": "First 3 catalogue pages (60 books)",
  "start_time": "2026-08-21T02:13:51.020166+00:00",
  "duration_seconds": 28.88,
  "catalogue_pages_visited": 3,
  "total_book_urls_discovered": 61,
  "pages_fetched_live": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "politeness": {
    "user_agent": "FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)",
    "timeout_seconds": 10,
    "delay_seconds": 0.5
  }
}
```

---

### 5. AI Rematch ("AI vs Me") — Stage 7 Scraper Audit Report

As required by Stage 7 of Assignment W5, an AI assistant was prompted in quarantine (`ai-version/scraper/main.py`) to build the same scraping pipeline:

#### Full AI Prompt Used
> *"Write a Python web scraper using BeautifulSoup and Requests to crawl the first 3 catalogue pages of Books to Scrape (`https://books.toscrape.com`), collect 60 book detail pages, extract title, price, and description, normalize price into numeric GBP float, validate records with Pydantic, cache HTML locally, enforce a 500ms delay and honest user-agent, survive 404 page errors, and generate a JSON run report."*

#### Three Concrete Differences Found

| Category | Hand-Crafted Code (`scraper/`) | AI-Generated Code (`ai-version/scraper/`) |
| :--- | :--- | :--- |
| **URL Resolution** | Used `urllib.parse.urljoin(page_url, href)` to resolve relative catalogue links safely. | Used raw string concatenation (`"https://books.toscrape.com/catalogue/" + href.replace("../", "")`), which breaks on nested paths. |
| **Local Caching & Idempotency** | Checks `scraper/cache/` before requesting network; reruns output `CACHE HIT` with 0 live fetches. | Re-fetched all 60 pages over the network on every run, hammering the target server and ignoring caching rules. |
| **Failure Resilience & Reporting** | Wraps detail fetches in try/except, skips 404s cleanly without halting, and outputs structured `run-report.json`. | Threw uncaught `AttributeError` or `IndexError` when a missing element or broken URL was encountered, halting execution. |

---

## Endpoint Reference Table (API Stack)

| Category | HTTP Method | Endpoint | Auth Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Public Gate** | `GET` | `/public/info` | None | Public welcome endpoint |
| **User Auth** | `POST` | `/auth/signup` | None | User registration via Supabase Auth |
| **User Auth** | `POST` | `/auth/login` | None | User login returning JWT access token |
| **User Auth** | `POST` | `/auth/logout` | Bearer Token | Invalidates user session |
| **Protected Profile**| `GET` | `/protected/profile` | Bearer Token | Returns verified user profile metadata |
| **Task CRUD** | `GET`, `POST`, `PUT`, `DELETE` | `/tasks`, `/tasks/{id}` | None | PostgreSQL/SQLite task management |
