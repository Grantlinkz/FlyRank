# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W6 — Put an LLM behind your API (`POST /tasks/triage`)**
- Built single, high-leverage LLM decision step for classifying, prioritizing, and estimating inbound tasks.
- Enforced strict closed enums (`category`, `urgency`, `estimated_effort`), non-empty bounds validation, and "when unsure" fallback rules.
- Implemented isolated user message injection defense (JSON-encoded content), single automated repair retry, quarantine logging (`logs/quarantine.jsonl`), explicit 30s timeout, selective retry backoff (429/5xx), and operational kill switch (`LLM_ENABLED=false`).
- Achieved **87.5% passing score** on 8-case benchmark suite (`evals/run_evals.py`) with successful self-healing repair retry on live OpenRouter calls.
- Completed Stage 6 AI rematch audit against `ai-version/llm/` and documented findings in `README.md`.

## Current Goal

- Completed W2, W3 (Database), W3 (Containerization), W4 (Auth), W5 (Scraper), and W6 (LLM). Ready to implement **Milestone W7 (Your First Background Job)** and **Milestone W7b (PDF Report Generator)**.

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment W3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment W4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment W5 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Assignment W6 — Put an LLM behind your API (`POST /tasks/triage`)**: Pydantic schemas, versioned prompt (`prompts/task-triage-v1.md`), single-repair retry loop, quarantine logging, 30s timeout, rate-limit backoff, telemetry logging, stub mode, kill switch, benchmark runner (`evals/run_evals.py`), and AI rematch audit.
- [x] **Context Synchronization**: Comprehensive update of `context/` documentation incorporating W7 (Background Jobs with Inngest) and W7b (PDF Report Generator with Playwright & SQL aggregation).

## In Progress

- None.

## Next Up

### Milestone W7 / A7 — Your First Background Job (Inngest)
- [ ] **Stage 0**: Hello, server — Verify `GET /health` on port 8000.
- [ ] **Stage 1**: Connect Inngest client (`report-api`), register `say-hello` with 5-second sleep step, mount `/api/inngest`, test via Inngest Dev Server dashboard (`:8288`).
- [ ] **Stage 2**: Fast door — `POST /reports` returns HTTP 202 Accepted in <1s, triggers `report/requested` event; Inngest runs `make-report` (8s sleep + build step); status endpoint `GET /reports/:id` tracks `pending` $\rightarrow$ `done`.
- [ ] **Stage 3**: Retries & Error Handling — Simulate failure on topic `"fail"`, observe 3 attempts with backoff in dashboard ending `Failed`; reject missing topic with `400 Bad Request` without creating jobs.
- [ ] **Stage 4**: Cron Heartbeat — Add `heartbeat` cron function running every minute (`* * * * *`) logging system counts.
- [ ] **Stage 5**: Publish & Documentation — Document API and Dev Server commands, endpoints/functions table, and 202+polling proof.
- [ ] **Stage 6**: AI Rematch — Quarantine generation in `ai-version/jobs/`, test diffing, and "AI vs Me" audit.

### Milestone W7b / A8 — PDF Report Generator (Playwright & SQL Aggregation)
- [ ] **Stage 0**: Setup — Install Playwright and headless Chromium (`playwright install chromium`).
- [ ] **Stage 1**: Dataset Seeding — Seed SQLite `report.db` (reusing scraped `books.json` or orders dataset) with idempotent clean rerun logic.
- [ ] **Stage 2**: SQL Aggregation — Implement 4-section aggregation query (`COUNT`, `SUM`, `AVG`, `GROUP BY`) returning structured summary JSON.
- [ ] **Stage 3**: Render HTML to PDF — HTML template with print CSS (`tr { break-inside: avoid; }`, `<thead>` repeat), rendered via Playwright (`page.pdf`) $\ge 2$ clean pages.
- [ ] **Stage 4**: Serve by Link — `POST /reports` runs pipeline, stores in `reports/<id>.pdf` and `report.db`, returns `201 Created` + file link; `GET /reports/:id/file` streams PDF via `FileResponse`.
- [ ] **Stage 5**: Idempotency Check — Same-day duplicate `POST /reports` returns existing report with `200 OK` (one file created); `{ "force": true }` generates fresh file.
- [ ] **Stage 6**: Publish & Documentation — Document SQL queries, run instructions, and PDF screenshot.
- [ ] **Stage 7**: AI Rematch — Quarantine generation in `ai-version/reports/`, test diffing, and "AI vs Me" audit.

## Open Questions

- None. Language choice confirmed as Python.

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Container Parity**: Full stack execution uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Pydantic) to ensure idempotent, non-destructive data ingestion.
- **Durable Background Execution (Inngest)**: Slow operations (>1s) are offloaded to Inngest step functions. API returns `202 Accepted` immediately, preventing request timeouts and double-execution while providing status polling.
- **Store & Link Artifact Pattern (Playwright)**: Generated PDFs are rendered using headless Chromium with print CSS page-break rules, stored on disk (`reports/<id>.pdf`), and served via direct file links (`FileResponse`). JSON responses never pass binary blobs.
- **Report Idempotency**: Daily report requests are deduplicated by checking `report.db` before running expensive browser rendering, saving resources unless bypassed with `{ "force": true }`.

## Session Notes

- Synchronized `context/` documentation across all 6 core files to incorporate complete specifications for Assignment A7 (Your first background job) and Assignment A8 (PDF report generator). Ready for implementation.
