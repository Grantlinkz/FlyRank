# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W4 / A4 — Auth · Login & protect (Python / FastAPI / Supabase Auth)**
- Integrated Supabase Auth Identity Provider (`auth.py`) using `SUPABASE_URL` and `SUPABASE_KEY` from `.env`.
- Implemented user endpoints: `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`, `GET /public/info`, `GET /protected/profile`.
- Built reusable FastAPI security dependency (`get_current_user`) verifying Bearer JWTs and enforcing `401 Unauthorized` on missing/tampered tokens.
- Configured FastAPI `HTTPBearer` for interactive Swagger UI `/docs` Bearer authorization padlock.
- Completed Stage 7 AI rematch quarantine evaluation (`ai-version/`) and documented security audit in `README.md`.

## Current Goal

- Ready for Assignment W5 — The Polite Scraper (Data ingestion pipeline).

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment A3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment A4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment A1 — Build your first CRUD API**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation, and Swagger UI at `/docs`.
- [x] **Assignment A2 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, and parameterized SQL queries (`?`).
- [x] **Assignment A9 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Zod/Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation based on `Tasks/` directory assignment requirements and conventional commit standards.

## In Progress

- None.

## Next Up

- Milestone W5: Polite scraping pipeline with throttling, local caching, schema validation, and run reporting.

## Open Questions

- None. Language choice confirmed as Python (FastAPI).

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Environment Parity**: Local production simulation uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Zod/Pydantic) to ensure idempotent, non-destructive data ingestion.

## Session Notes

- Completed Supabase Auth integration with signup, login, logout, public/protected gates, OpenAPI HTTPBearer padlock support, and AI rematch security audit.
