# FlyRank Backend Platform — Project Overview

## Overview

FlyRank is a modular backend platform and developer internship track focused on building production-ready services. The system evolves through spec-driven milestones: establishing RESTful CRUD APIs, adding SQLite and containerized PostgreSQL database persistence, implementing secure identity management via Supabase Auth with JWT middleware, and building an idempotent, fault-tolerant web scraping pipeline for data ingestion.

## Goals

1. **Robust API Foundation**: Deliver standardized RESTful APIs with strict HTTP status code semantics, JSON request/response contracts, and interactive Swagger UI documentation.
2. **Flexible & Secure Persistence**: Transition from in-memory arrays to persistent SQLite (`tasks.db`) and containerized PostgreSQL, utilizing parameterized SQL queries and environment-based secrets.
3. **Identity & Access Control**: Protect system endpoints with Supabase Auth as the Identity Provider, enforcing JWT Bearer token verification via reusable middleware.
4. **Resilient Data Ingestion**: Build an automated, polite data scraping pipeline with request throttling, local HTML caching, Zod/Pydantic schema validation, and structured run reporting.

## Core User Flow

1. **Authentication**: Users sign up (`POST /auth/signup`) and log in (`POST /auth/login`) to receive a JWT access token.
2. **Accessing Protected Resources**: Clients send requests with `Authorization: Bearer <token>` to access private user profiles (`GET /protected/profile`) or execute session teardown (`POST /auth/logout`).
3. **Managing Resources (CRUD)**: Authenticated users manage task and SEO report resources (`GET /tasks`, `POST /tasks`, `PUT /tasks/:id`, `DELETE /tasks/:id`) with persistence across server and container restarts.
4. **Data Scraping & Ingestion**: The system politely fetches external target pages (e.g., Books to Scrape), caches raw HTML locally, extracts and normalizes fields, validates records against schemas, and writes valid outputs to `output/books.json` with a detailed `output/run-report.json`.

5. **Durable Asynchronous Execution**: Offload long-running operations (>1s) from HTTP request-response cycles using durable, event-driven background jobs and scheduled cron tasks with Inngest.
6. **Data-to-Document Reporting**: Transform relational database records into professional, multi-page PDF reports using SQL aggregations, HTML templates, and headless browser rendering (Playwright), served via the "store and link" artifact pattern.

## Core User Flow

1. **Authentication**: Users sign up (`POST /auth/signup`) and log in (`POST /auth/login`) to receive a JWT access token.
2. **Accessing Protected Resources**: Clients send requests with `Authorization: Bearer <token>` to access private user profiles (`GET /protected/profile`) or execute session teardown (`POST /auth/logout`).
3. **Managing Resources (CRUD)**: Authenticated users manage task and SEO report resources (`GET /tasks`, `POST /tasks`, `PUT /tasks/:id`, `DELETE /tasks/:id`) with persistence across server and container restarts.
4. **Data Scraping & Ingestion**: The system politely fetches external target pages (e.g., Books to Scrape), caches raw HTML locally, extracts and normalizes fields, validates records against schemas, and writes valid outputs to `output/books.json` with a detailed `output/run-report.json`.
5. **Background Job Orchestration**: Clients trigger slow workloads (`POST /reports`), immediately receiving `202 Accepted` with a tracking ID while Inngest executes multi-step functions in the background with automatic retries and backoff. Clients poll `GET /reports/:id` until status turns `done`.
6. **PDF Generation & File Serving**: Clients request report generation; the API aggregates SQL data, renders a styled PDF via headless Chromium (Playwright), stores it on disk (`reports/<id>.pdf`), and serves the file by link (`GET /reports/:id/file`) with once-per-day idempotency protection.

## Features

### 1. Core REST API & Swagger UI Documentation
- Health check (`GET /health`) and API metadata (`GET /`) endpoints.
- Full CRUD operations for resource management (`/tasks`, `/tasks/:id`).
- Input validation returning `400 Bad Request` for missing/empty fields.
- Interactive OpenAPI documentation rendered at `/docs` with Bearer auth support.

### 2. Database Persistence & Containerization
- Dual database support: SQLite (`tasks.db`) for lightweight local persistence and PostgreSQL for production-grade workloads.
- Startup auto-creation of database files and tables with first-run seeding logic.
- Single command multi-container orchestration via Docker Compose (`compose.yaml`) with persistent volume mapping (`taskdata`).
- Environment variable management using `.env` for secrets with `.env.example` committed.

### 3. Identity & Token Security
- Supabase Auth integration handling account registration and credential verification.
- Reusable JWT authentication middleware verifying Bearer tokens and injecting user context into requests.
- Endpoint classification: Public (`/public/info`) vs Protected (`/protected/profile`, `/auth/logout`).

### 4. Resilient Scraping Pipeline
- Target classification and `robots.txt` compliance verification.
- Local HTML caching (`cache/`) to avoid repeated network requests.
- Relative-to-absolute URL transformation for discovered pages.
- Data extraction, price normalization (`price_gbp`), and Zod/Pydantic schema validation.
- Non-blocking failure handling: 5xx retry logic, logging and skipping 404/broken pages without halting execution.
- Execution reporting (`output/run-report.json`) tracking timing, cache hits, valid/invalid records, and errors.

### 5. Deterministic LLM Task Triage (`POST /tasks/triage`)
- Production-grade LLM decision step for classification, urgency assessment, and effort estimation.
- Closed enum output guarantees with strict negative constraints (no Markdown code fences or free text).
- Untrusted user input isolation via JSON-encoded user message payloads to prevent prompt injection.
- Single repair retry loop with error feedback on validation/JSON decode failure.
- Quarantine failure logging (`logs/quarantine.jsonl`) returning HTTP 422 Unprocessable Entity.
- Zero-cost stub mode (`LLM_STUB=1`), operational kill switch (`LLM_ENABLED=false`), and 30s client timeout.

### 6. Durable Background Jobs & Cron Scheduling (Milestone W7)
- Immediate fast-door response: `POST /reports` returns HTTP `202 Accepted` + `{ "id": ..., "status": "pending" }` in <1 second.
- Event-driven orchestration: dispatches events (e.g. `report/requested`) to Inngest client (`report-api`).
- Durable multi-step workflows: isolated `step.sleep()` and `step.run()` execution surviving server restarts.
- Automatic retry with exponential backoff: transient failures retry up to configured limits (e.g. `retries=2`); bad inputs reject at the door with `400 Bad Request` without triggering jobs.
- Status endpoint polling: `GET /reports/:id` returns lifecycle state (`pending`, `done`, `failed`) and result payloads (eventual consistency).
- Scheduled cron heartbeat: clock-triggered recurring background task (`inngest.TriggerCron(cron="* * * * *")`) logging system state without HTTP request triggers.

### 7. Data-to-Document PDF Report Generator (Milestone W7b)
- 4-step reporting pipeline: Query $\rightarrow$ Render $\rightarrow$ Store $\rightarrow$ Serve.
- SQL aggregation: computes summary metrics via `COUNT`, `SUM`, `AVG`, and `GROUP BY` (e.g. total books, average price, top 5 by price, books by star rating).
- Headless Chromium rendering: uses Playwright (`page.set_content` + `page.pdf`) with A4 format and background graphics enabled.
- Print CSS layout control: prevents broken table rows with `tr { break-inside: avoid; }` and repeats table headers across page breaks via `<thead>`.
- Store and link pattern: generated PDFs live on disk (`reports/<id>.pdf`); metadata recorded in `report.db` `reports` table; binary bytes served strictly by link (`GET /reports/:id/file`) via `FileResponse`.
- Request idempotency: repeated generation requests on the same calendar day return existing report ID/link with `200 OK` (one file created); optional `{ "force": true }` payload forces new file generation.

## Scope

### In Scope
- Node.js (Express) or Python (FastAPI) REST API endpoints.
- SQLite (`tasks.db`, `report.db`) and PostgreSQL storage layers using parameterized queries.
- Dockerfile and Docker Compose setup for local environment parity.
- Supabase Auth SDK integration and JWT middleware.
- Books to Scrape ingestion pipeline with local file caching and JSON outputs (`output/books.json`).
- LLM task triage decision step backed by OpenAI SDK, versioned prompts, and evaluation harnesses.
- Inngest background job orchestration and local Inngest Dev Server (`localhost:8288`).
- Playwright headless Chromium PDF generation and local artifact storage (`reports/`).

### Out of Scope
- Custom password hashing or rolling custom cryptography.
- Unthrottled scraping or bypassing website paywalls/logins.
- Free-form open-ended chatbot conversational systems.
- Heavy distributed task queue infrastructure (e.g. RabbitMQ/Redis/Celery clusters) — Inngest handles durable step orchestration.
- Passing raw binary PDF bytes or base64 blobs inside JSON API responses (all files served by dedicated URL links).
- Direct mutation of third-party DOMs or external database schemas.

## Success Criteria

1. **CRUD & Spec Adherence**: Complete CRUD cycle functions via curl and Swagger UI with correct HTTP status codes (200, 201, 204, 400, 401, 404).
2. **Verified Persistence**: Data survives full server and container restarts (`docker compose down && docker compose up`).
3. **Auth Enforcement**: Protected routes successfully reject missing/tampered tokens with `401 Unauthorized` and permit valid tokens with `200 OK`.
4. **Pipeline Resilience**: Scraping pipeline processes 60 unique book records idempotently, handles deliberate 404 failures gracefully, and generates valid `output/run-report.json`.
5. **LLM Contract & Safety**: Triage endpoint rejects invalid/empty inputs with `400 Bad Request`, achieves >=80% on evaluation benchmark, defends against prompt injections, and automatically recovers via repair retry.
6. **Durable Background Jobs (W7)**: `POST /reports` returns `202 Accepted` in <1s; `GET /reports/:id` transitions from `pending` to `done` after background sleep/build steps; failure simulation with topic `"fail"` retries with backoff and finishes `Failed` in Inngest dashboard; `heartbeat` cron executes every minute on schedule.
7. **PDF Report Pipeline & Idempotency (W7b)**: Database seeded cleanly (idempotent row count); aggregation query produces accurate 4-metric summary; rendered PDF opens cleanly with $\ge 2$ pages and no sliced table rows; `POST /reports` returns `201` + file link, `GET /reports/:id/file` streams valid PDF; repeated POST on the same day returns `200` + existing ID without generating duplicate files.
