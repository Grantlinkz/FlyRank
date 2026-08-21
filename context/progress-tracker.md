# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W3 — Connecting your CRUD to the database (Python / FastAPI Lane)**
- Migrated in-memory CRUD storage to SQLite database (`tasks.db`) via repository module `database.py`.
- Auto-creation of `tasks` table with seed-once logic (`SELECT COUNT(*)` check before initial seed).
- Implemented parameterized SQL queries (`?`) for all CRUD operations, status filtering (`?done=true`), title search (`?search=keyword`), metrics (`GET /stats`), and reset (`POST /reset`).
- Quarantine comparison (`ai-version/main.py`) completed with "AI vs Me" evaluation documented in `README.md`.

## Current Goal

- Ready for Assignment W3 (Containerize your stack) / W4 (Auth - Login).

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment A1 — Build your first CRUD API**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation, and Swagger UI at `/docs`.
- [x] **Assignment A2 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, and parameterized SQL queries (`?`).
- [x] **Assignment A3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment A4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment A9 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Zod/Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation based on `Tasks/` directory assignment requirements and conventional commit standards.

## In Progress

- None.

## Next Up

- Milestone W3 / W4: Containerization with Docker Compose or Supabase Identity Auth integration.

## Open Questions

- None. Language choice confirmed as Python (FastAPI).

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Environment Parity**: Local production simulation uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Zod/Pydantic) to ensure idempotent, non-destructive data ingestion.

## Session Notes

- Completed full migration to SQLite (`tasks.db`) with parameterized queries, seed-once logic, repository pattern, and AI rematch evaluation report.
