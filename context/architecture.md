# Architecture Context — FlyRank Platform

## Stack

| Layer | Technology | Role |
| ----- | ---------- | ---- |
| Server Framework | Node.js (Express) or Python (FastAPI) | HTTP routing, request handling, response serialization |
| UI & API Docs | Swagger UI (`swagger-ui-express` or FastAPI `/docs`) | Interactive OpenAPI spec rendering & Bearer auth testing |
| Identity & Auth | Supabase Auth (`@supabase/supabase-js` or `supabase` PyPI) | Account management, JWT issuance & verification |
| Local Database | SQLite (`better-sqlite3` or `sqlite3`) | Single-file zero-config persistent storage (`tasks.db`) |
| Containerized DB | PostgreSQL (`pg` or `psycopg3` / `SQLModel`) | Production relational storage engine |
| Containerization | Docker & Docker Compose (`compose.yaml`) | Multi-service orchestration and environment parity |
| Scraping Engine | Cheerio (Node) or Beautiful Soup (Python) | HTML parsing and DOM selector extraction |
| Schema Validation | Zod (Node) or Pydantic (Python) | Untrusted data runtime validation & normalization |
| LLM Service Engine | OpenAI Python SDK (OpenRouter / Ollama) | Deterministic task classification, urgency & effort triage |
| Background Jobs & Cron | Inngest (`inngest` PyPI) & Inngest Dev Server | Durable multi-step workflows, exponential retries & cron scheduler |
| PDF Rendering Engine | Playwright (`playwright` PyPI / Chromium) | Headless browser HTML-to-PDF document generation |

## System Boundaries

- `src/`  — Route definitions, controller logic, server initialization.
- `src/repository/` — Standalone data access layer encapsulating all SQL queries and DB connections.
- `src/middleware/` — Authentication guard verifying Bearer JWTs via Supabase Auth.
- `src/llm/` — LLM client provider, schema definitions, repair retry loop, and telemetry logging.
- `src/jobs/` or `src/inngest/` — Inngest client (`report-api`), background functions (`say-hello`, `make-report`, `heartbeat`), and `/api/inngest` serve mount.
- `src/reports/` — SQL aggregation queries, HTML report templating, and Playwright PDF generation logic.
- `reports/` — Local disk storage for produced PDF artifacts (`reports/<id>.pdf`), git-ignored.
- `report.db` — Standalone SQLite database for reporting datasets and report bookkeeping, git-ignored.
- `prompts/` — Version-controlled prompt engineering templates (`task-triage-v1.md`).
- `evals/` — Benchmark evaluation cases (`cases.json`) and automated test runner (`run_evals.py`).
- `logs/` — Runtime quarantine logs recording unrepairable model failures (`quarantine.jsonl`).
- `scraper/` — Data scraping pipeline entry point, crawler logic, and URL discovery.
- `scraper/cache/` — Local storage for raw HTML snapshots to prevent redundant network fetches.
- `scraper/output/` — Ingestion artifacts (`books.json`, `errors.json`, `run-report.json`).

## Storage Model

- **Relational Database (SQLite / Postgres)**: Stores primary application records in a `tasks` table (`id` integer/serial primary key, `title` text, `done` boolean/integer, `created_at`/`updated_at` timestamps).
- **Reporting Database (`report.db`)**: Standalone SQLite database with data tables (e.g., `orders` or scraped `books`) and a `reports` bookkeeping table (`id` integer primary key, `path` text, `created_at` timestamp).
- **File Artifact Storage (`reports/*.pdf`)**: Local filesystem storage holding rendered PDF documents referenced by path in the database.
- **Local File Storage (`scraper/cache/`)**: Snapshot storage for cached target HTML pages (`catalogue-page-1.html`, etc.).
- **Structured JSON Artifacts (`scraper/output/`)**: Standardized output files holding validated scraped records (`books.json`), validation errors (`errors.json`), and pipeline execution metrics (`run-report.json`).
- **Quarantine Failure Stream (`logs/quarantine.jsonl`)**: Structured NDJSON failure records documenting unrepairable model validation failures for auditability.

## Auth and Access Model

- **Identity Provider**: Supabase Auth handles user account storage, password hashing, and token issuance. Application code never directly touches plain-password hashing.
- **Token Format**: Standard JSON Web Tokens (JWT) issued on login and sent in the HTTP `Authorization` header as `Bearer <token>`.
- **Middleware Guard**: Intercepts requests to protected endpoints, calls `supabase.auth.getUser(token)`, and attaches the verified user metadata (`req.user`) to the request context.
- **Access Tiers**:
  - *Public*: `GET /`, `GET /health`, `GET /public/info`, `POST /auth/signup`, `POST /auth/login`, `GET /docs`, `POST /tasks/triage`, `POST /reports` (fast door 202/201), `GET /reports/:id`, `GET /reports/:id/file`, `/api/inngest` (Inngest dispatch endpoint).
  - *Protected*: `POST /auth/logout`, `GET /protected/profile`, `GET /tasks`, `POST /tasks`, `PUT /tasks/:id`, `DELETE /tasks/:id`, `POST /reset`.

## Architecture Invariants

1. **Zero Hardcoded Credentials**: Database passwords, secret keys, and API keys must live in `.env` files. `.env` is git-ignored, while `.env.example` is committed with placeholder values.
2. **Strict SQL Parameterization**: All database queries must use parameterized placeholders (`?`, `$1`, `%s`). Concatenating raw user input into SQL strings is strictly forbidden to prevent SQL injection.
3. **Storage Layer Separation**: Route handlers must not directly execute database queries or manage connection pools. All database interactions are contained within a dedicated `repository` module.
4. **Polite & Idempotent Scraping**: The scraper must identify itself via a custom `User-Agent`, enforce request timeouts, insert delays (>=500ms) between live requests, read from local HTML cache during development, and produce identical record sets on repeated runs.
5. **Non-Blocking Failure Isolation**: Individual page failures (e.g., 404s or malformed HTML) must be logged and skipped without crashing the entire scraping job or corrupting valid output sets.
6. **Untrusted Model Boundary & Closed Output**: Model output is untrusted external data. It must pass through strict Pydantic schema parsing, single repair retry, and quarantine logging before downstream use. User inputs are placed strictly inside the `user` message role as JSON to prevent prompt injection.
7. **Zero Quota Bleed via Stub Mode**: Support `LLM_STUB=1` for zero-token local testing and `LLM_ENABLED=false` kill switch for instant service degradation.
8. **Store and Link, Never Pass Bytes Around**: Produced artifacts (PDF documents, exports) must be saved to disk (`reports/<id>.pdf`) and served by dedicated link (`GET /reports/:id/file`). JSON responses must never contain raw binary bytes or base64 blobs.
9. **Accept Fast, Work in the Background**: Operations exceeding normal HTTP tolerances (>1s) must return `202 Accepted` immediately with a resource ID, deferring durable execution to background steps/workers. Progress is polled via `GET /reports/:id` (eventual consistency).
10. **Gatekeeper Bad Input, Retry Only Transient Failures**: Invalid request payloads (e.g. missing topic) must fail fast with `400 Bad Request` at the boundary without triggering background jobs. Automated retries with exponential backoff are strictly reserved for transient errors (network hiccups, external service drops).
11. **Artifact Idempotency**: Duplicate report generation requests on the same day must return the existing report record and link with `200 OK` without creating duplicate files, unless explicitly overridden with `{ "force": true }`.
