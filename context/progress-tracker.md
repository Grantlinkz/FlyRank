# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed Assignment W7 (A7) — Your First Background Job & Cron Schedules**
- Integrated Inngest Python SDK (`app_id="report-api"`) with FastAPI server at `/api/inngest`.
- Implemented fast-door asynchronous pattern: `POST /reports` returns HTTP `202 Accepted` in <50ms with a unique tracking ID (`rep_<hex>`).
- Implemented durable multi-step background workflow `make-report`: 8s sleep step (`step.sleep`) + build step (`step.run`), transitioning report state from `pending` to `done` (eventual consistency).
- Enforced strict gatekeeper boundary validation: missing or empty `topic` returns HTTP `400 Bad Request` without dispatching background events.
- Added failure injection and automated retry with exponential backoff on topic `"fail"`, configuring `retries=2` and an `on_failure` handler.
- Implemented clock-driven scheduled cron function `heartbeat` (`* * * * *`) aggregating and logging system metrics.
- Completed Bonus Stage 6 AI Rematch in `ai-version/jobs/` with side-by-side audit documented in `README.md`.
- Verified 100% pass rate on 9-test automated suite (`test_jobs.py`).

## Current Goal

- Completed W2 (CRUD), W3 (Database & Docker), W4 (Auth), W5 (Scraper), W6 (LLM Triage), and W7 (Background Jobs). Ready to implement **Milestone W7b (A8): PDF Report Generator** using Playwright and SQL aggregation.

## Completed Tasks

- [x] **Assignment W2 — Build your first CRUD API (Python Lane)**: Standardized JSON responses, status code semantics, `/tasks` CRUD endpoints, input validation (`400 Bad Request`), Swagger UI at `/docs`, extras (`/stats`, `/reset`, query filtering), and Conventional Commits history.
- [x] **Assignment W3 — Connecting your CRUD to the database**: SQLite (`tasks.db`) integration, table auto-creation, seed-once logic, parameterized SQL queries (`?`), repository pattern separation (`database.py`), and AI rematch evaluation (`ai-version/`).
- [x] **Assignment W3 — Containerize your stack**: PostgreSQL containerization, Docker Compose orchestration (`compose.yaml`), volume mapping (`taskdata`), `.env` configuration, and Repository pattern layer separation.
- [x] **Assignment W4 — Auth - Login & protect**: Supabase Auth IdP integration, `/auth/signup`, `/auth/login`, `/auth/logout`, protected `/protected/profile` route, JWT verification middleware, and Swagger UI Bearer Auth setup.
- [x] **Assignment W5 — The polite scraper**: Books to Scrape ingestion pipeline, target classification, local HTML snapshot caching (`cache/`), Pydantic validation (`books.json` / `errors.json`), error resilience, and structured reporting (`run-report.json`).
- [x] **Assignment W6 — Put an LLM behind your API (`POST /tasks/triage`)**: Pydantic schemas, versioned prompt (`prompts/task-triage-v1.md`), single-repair retry loop, quarantine logging, 30s timeout, rate-limit backoff, telemetry logging, stub mode, kill switch, benchmark runner (`evals/run_evals.py`), and AI rematch audit.
- [x] **Assignment W7 (A7) — Your First Background Job (Inngest)**:
  - [x] **Stage 0**: Hello, server — Verify `GET /health` on port 8000 and dependencies.
  - [x] **Stage 1**: Connect Inngest client (`report-api`), register `say-hello` with 5-second sleep step, mount `/api/inngest`, test via Inngest Dev Server dashboard (`:8288`).
  - [x] **Stage 2**: Fast door — `POST /reports` returns HTTP 202 Accepted in <1s, triggers `report/requested` event; Inngest runs `make-report` (8s sleep + build step); status endpoint `GET /reports/:id` tracks `pending` $\rightarrow$ `done`.
  - [x] **Stage 3**: Retries & Error Handling — Simulate failure on topic `"fail"`, observe 3 attempts with backoff in dashboard ending `Failed`; reject missing topic with `400 Bad Request` without creating jobs.
  - [x] **Stage 4**: Cron Heartbeat — Add `heartbeat` cron function running every minute (`* * * * *`) logging system counts.
  - [x] **Stage 5**: Publish & Documentation — Document API and Dev Server commands, endpoints/functions table, and 202+polling proof.
  - [x] **Stage 6**: AI Rematch — Quarantine generation in `ai-version/jobs/`, test diffing, and "AI vs Me" audit.

## In Progress

- None.

## Next Up

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
