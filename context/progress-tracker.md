# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W6 — Put an LLM behind your API (`POST /tasks/triage`)**
- Built single, high-leverage LLM decision step for classifying, prioritizing, and estimating inbound tasks.
- Enforced strict closed enums (`category`, `urgency`, `estimated_effort`), non-empty bounds validation, and "when unsure" fallback rules.
- Implemented isolated user message injection defense (JSON-encoded content), single automated repair retry, quarantine logging (`logs/quarantine.jsonl`), explicit 30s timeout, selective retry backoff (429/5xx), and operational kill switch (`LLM_ENABLED=false`).
- Achieved **87.5% passing score** on 8-case benchmark suite (`evals/run_evals.py`) with successful self-healing repair retry on live OpenRouter calls.
- Completed Stage 6 AI rematch audit against `ai-version/llm/` and documented findings in `README.md`.

## Current Goal

- Completed W2, W3 (Database), W3 (Containerization), W4 (Auth), W5 (Scraper), and W6 (LLM). Ready for Milestone W7 (Background Jobs).

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment W3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment W4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment W5 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Assignment W6 — Put an LLM behind your API (`POST /tasks/triage`)**: Pydantic schemas, versioned prompt (`prompts/task-triage-v1.md`), single-repair retry loop, quarantine logging, 30s timeout, rate-limit backoff, telemetry logging, stub mode, kill switch, benchmark runner (`evals/run_evals.py`), and AI rematch audit.
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
