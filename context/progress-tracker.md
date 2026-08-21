# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W3 / A3 — Containerize your stack (Python / FastAPI / PostgreSQL / Docker Compose)**
- Migrated storage engine to containerized PostgreSQL 16 using `psycopg 3` driver.
- Configured `.env` environment secrets (git-ignored) with committed `.env.example` template.
- Built application `Dockerfile` and multi-service `compose.yaml` with persistent volume `taskdata`.
- Completed Stage 6 AI rematch quarantine comparison (`ai-version/`) and documented findings in `README.md`.

## Current Goal

- Ready for Assignment W4 — Auth - Login & Protect (Supabase Auth IdP integration).

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment A3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment A1 — Build your first CRUD API**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation, and Swagger UI at `/docs`.
- [x] **Assignment A2 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, and parameterized SQL queries (`?`).
- [x] **Assignment A4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment A9 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Zod/Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation based on `Tasks/` directory assignment requirements and conventional commit standards.

## In Progress

- None.

## Next Up

- Milestone W4: Identity management and authentication with Supabase Auth (JWT verification middleware).

## Open Questions

- None. Language choice confirmed as Python (FastAPI).

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Environment & Secrets Parity**: All database credentials and connection strings are managed via `.env` environment variables loaded at runtime.
- **Container Parity**: Full stack execution uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Zod/Pydantic) to ensure idempotent, non-destructive data ingestion.

## Session Notes

- Completed full containerization of FastAPI app + PostgreSQL database using Docker Compose, `.env` secrets, `psycopg 3`, and volume persistence.
