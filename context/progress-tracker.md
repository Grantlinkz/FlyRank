# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W2 — Build your first CRUD API (Python / FastAPI Lane)**
- Implemented `main.py` with FastAPI, Pydantic models, in-memory storage, strict HTTP status codes (`200`, `201`, `204`, `400`, `404`), interactive Swagger UI at `/docs`, optional extras (`GET /stats`, `POST /reset`, query params), and comprehensive `README.md`.
- All 7 stages committed to Git following Conventional Commits (`feat:`, `docs:`, `chore:`).

## Current Goal

- Ready for Assignment W3 — Connecting your CRUD to the database (SQLite persistence).

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment A1 — Build your first CRUD API**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation, and Swagger UI at `/docs`.
- [x] **Assignment A2 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, and parameterized SQL queries (`?`).
- [x] **Assignment A3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment A4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment A9 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Zod/Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation based on `Tasks/` directory assignment requirements and conventional commit standards.

## In Progress

- None.

## Next Up

- Milestone W3: Database persistence with SQLite (`tasks.db`), table auto-creation, seed-once logic, and parameterized queries.

## Open Questions

- None. Language choice confirmed as Python (FastAPI).

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`src/repository/`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Environment Parity**: Local production simulation uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Zod/Pydantic) to ensure idempotent, non-destructive data ingestion.

## Session Notes

- All 6 context documents in `context/` have been updated to reflect the full 5-assignment curriculum of the FlyRank Backend Track.
