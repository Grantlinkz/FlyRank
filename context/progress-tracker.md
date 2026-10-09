# Progress Tracker — FlyRank Platform

## Current Phase

- **Completed All Milestones: W1-W2 (CRUD), W3 (Persistence & Docker), W4 (Auth), W5 (Scraper), W6 (LLM Triage), W7 (Background Jobs), and W7b (PDF Report Generator)**
- **Milestone W6 (A17 — Put an LLM behind your API)**: Integrated OpenAI SDK / OpenRouter with versioned prompt specification (`prompts/task-triage-v1.md`), strict Pydantic v2 enums, zero-cost stub mode (`LLM_STUB=1`), 30s timeout, custom retry policy with backoff and jitter, repair retry loop with quarantine logging (`logs/quarantine.jsonl`), operational kill switch (`LLM_ENABLED=false`), and 8-case eval benchmark (`evals/run_evals.py`).
- **Milestone W7 (A7 — Your First Background Job & Cron Schedules)**: Integrated Inngest Python SDK (`report-api`) with FastAPI server at `/api/inngest`. Implemented fast door `POST /reports` returning HTTP `202 Accepted` (<50ms), multi-step durable workflow `make-report` (`step.sleep` 8s + `step.run`), eventual consistency polling (`pending` -> `done`), `retries=2` on topic `"fail"`, boundary input validation (`400 Bad Request`), and every-minute scheduled heartbeat cron (`* * * * *`).
- **Milestone W7b (A8 — PDF Report Generator)**: Implemented full Store & Link reporting pipeline: SQLite `report.db` idempotent seeding (60 books), pure SQL aggregations (`COUNT`, `AVG`, `SUM`, top 5, rating breakdown), defensive print CSS (`tr { break-inside: avoid; }`, repeating `<thead>`), Playwright headless Chromium PDF rendering ($\ge 2$ pages), API endpoints (`POST /reports` 201/200, `GET /reports/{id}`, `GET /reports/{id}/file` via `FileResponse`), and double-click idempotency protection (`DATE(created_at) = DATE('now')`).
- **100% Automated Test Suite Passing**: 16/16 tests passing cleanly across `test_jobs.py` and `test_reports.py`.
- **Comprehensive AI Rematch Audits**: Completed for W5 (Scraper), W6 (LLM), W7 (Jobs), and W7b (PDF Generator) in `ai-version/` with comparative diffs and documentation.

## Current Goal

- Production readiness, deployment verification, and platform maintenance. All curriculum track assignments (W1 through W7b) are fully implemented and verified.

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
- [x] **Assignment W7b (A8) — PDF Report Generator (Playwright & SQL Aggregation)**:
  - [x] **Stage 0**: Setup — Installed Playwright and headless Chromium (`playwright install chromium`).
  - [x] **Stage 1**: Dataset Seeding — Seeded SQLite `report.db` with 60 validated book records with idempotent rerun protection (`src/reports/seed.py`).
  - [x] **Stage 2**: SQL Aggregation — Implemented 4-section SQL aggregations (`COUNT`, `AVG`, `SUM`, top 5, rating breakdown) in `src/reports/queries.py`.
  - [x] **Stage 3**: Render HTML to PDF — Executive HTML template with print CSS (`tr { break-inside: avoid; }`, repeating `<thead>`), rendered via Playwright (`page.pdf`) $\ge 2$ clean pages without sliced rows.
  - [x] **Stage 4**: Serve by Link — `POST /reports` executes pipeline, stores in `reports/<id>.pdf` and `report.db`, returns `201 Created` + file link; `GET /reports/:id/file` streams PDF binary via `FileResponse`.
  - [x] **Stage 5**: Idempotency Check — Same-day duplicate `POST /reports` returns existing report with `200 OK` (0 duplicate files generated); `{ "force": true }` generates fresh file with `201 Created`.
  - [x] **Stage 6**: Publish & Documentation — Documented SQL queries, run instructions, download proofs, and architectural answers in `README.md`.
  - [x] **Stage 7**: AI Rematch — Quarantine generation in `ai-version/reports/`, diffing, and "AI vs Me" comparative audit.

## In Progress

- None (All milestones W1 through W7b fully completed and verified).

## Next Up

- Continuous integration, performance benchmarking, and cloud deployment pipelines.

## Open Questions

- None. Python lane architecture fully established.

## Architecture Decisions

- **Storage Decoupling**: Database access logic is encapsulated in a dedicated Repository module (`database.py`), preventing route handlers from executing direct SQL queries.
- **Identity Provider Delegation**: All authentication credentials, password hashing, and token signatures are handled via Supabase Auth, keeping server code cryptography-free.
- **Container Parity**: Full stack execution uses Docker Compose with named volume mounts (`taskdata`) to guarantee data persistence across container restarts.
- **Polite Scraping Architecture**: Scraper employs local HTML snapshot caching, mandatory request throttling (>=500ms delay), custom `User-Agent`, and schema validation (Pydantic) to ensure idempotent, non-destructive data ingestion.
- **Durable Background Execution (Inngest)**: Slow operations (>1s) are offloaded to Inngest step functions. API returns `202 Accepted` immediately, preventing request timeouts and double-execution while providing status polling.
- **Store & Link Artifact Pattern (Playwright)**: Generated PDFs are rendered using headless Chromium with print CSS page-break rules, stored on disk (`reports/<id>.pdf`), and served via direct file links (`FileResponse`). JSON responses never pass binary blobs.
- **Report Idempotency**: Daily report requests are deduplicated by checking `report.db` before running expensive browser rendering, saving resources unless bypassed with `{ "force": true }`.
- **Quarantined AI Rematch Audits**: Every major subsystem includes an isolated implementation in `ai-version/` to systematically evaluate AI code generation against human-engineered production safety patterns.

## Session Notes

- Completed verification and testing of Milestones W6, W7, and W7b. All 16 automated tests in `test_jobs.py` and `test_reports.py` pass cleanly.
- Updated `Tasks.md`, `README.md`, and `context/progress-tracker.md` to reflect full completion status across all milestones.

