# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W5 — The polite scraper (Python / Requests / BeautifulSoup / Pydantic)**
- Built polite data ingestion pipeline in `scraper/` targeting Books to Scrape (`https://books.toscrape.com`).
- Discovered 60 book detail URLs across 3 catalogue pages using `urljoin`.
- Extracted 8 raw fields, normalized `price_gbp` numeric float, validated schema via Pydantic (`validator.py`).
- Implemented disk caching (`cache/`), politeness rules (`User-Agent`, 10s timeout, 500ms delay), page failure survival, and run reporting (`output/run-report.json`).
- Completed Stage 7 AI rematch quarantine evaluation (`ai-version/scraper/`) and documented audit report in `README.md`.

## Current Goal

- Completed W2, W3 (Database), W3 (Containerization), W4 (Auth), and W5 (Scraper). Ready for next curriculum milestone.

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment W3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment W4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment W5 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation based on `Tasks/` directory assignment requirements and conventional commit standards.

## In Progress

- None.

## Next Up

- Next backend curriculum milestone or capstone project.

## Open Questions

- None. Language choice confirmed as Python.

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Container Parity**: Full stack execution uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Pydantic) to ensure idempotent, non-destructive data ingestion.

## Session Notes

- Completed full polite scraping pipeline with target classification, local HTML caching, BeautifulSoup parsing, Pydantic validation, failure resilience, and run reporting.
