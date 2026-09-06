# 🚀 FlyRank Backend Platform & Data Ingestion Pipeline

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-red.svg)](https://docs.pydantic.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker Compose](<https://img.shields.io/badge/Docker%20Compose-v2-2496ED.svg>)](https://docs.docker.com/compose/)
[![Supabase Auth](https://img.shields.io/badge/Supabase-Auth-3ECF8E.svg)](https://supabase.com/docs/guides/auth)

A production-grade, spec-driven RESTful API service and resilient web data ingestion pipeline built for the **FlyRank Backend Track**.

FlyRank evolves through spec-driven milestones: establishing RESTful CRUD services, integrating SQLite and containerized PostgreSQL database persistence with parameterized queries, enforcing secure JWT authentication using Supabase Auth as the Identity Provider, and deploying an automated, polite data scraping pipeline with request throttling, local HTML caching, Pydantic runtime schema validation, and execution metric reporting.

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [API Endpoint Reference](#-api-endpoint-reference)
- [Environment Setup](#-environment-setup)
- [Running the Application](#-running-the-application)
  - [Option A: Local Development (FastAPI + SQLite / PostgreSQL)](#option-a-local-development)
  - [Option B: Containerized Stack (Docker Compose)](#option-b-containerized-stack)
- [Polite Data Scraping Pipeline](#-polite-data-scraping-pipeline)
- [Milestone W6: Put an LLM Behind Your API (`POST /tasks/triage`)](#-milestone-w6-put-an-llm-behind-your-api-post-taskstriage)
- [Milestone W7: Your First Background Job & Cron Schedules](#-milestone-w7-your-first-background-job--cron-schedules)
- [Milestone W7b: PDF Report Generator (Assignment A8)](#-milestone-w7b-pdf-report-generator-assignment-a8)
- [AI Rematch Audit: LLM Triage vs Background Jobs vs PDF Reports](#️-ai-rematch-audit)
- [Verification & Testing](#-verification--testing)
- [License](#-license)

---

## ✨ Key Features

### 1. 🛠️ Spec-Driven RESTful CRUD API

- **Standardized Endpoints**: Full lifecycle management for `/tasks` and `/tasks/{id}` with strict HTTP status code semantics (`200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`).
- **Input Validation**: Strict request payload validation using Pydantic v2 models, rejecting empty or whitespace-only inputs.
- **Analytics & Maintenance**: Includes `/stats` for real-time task metrics and protected `/reset` endpoint for automated table re-seeding.
- **Interactive Documentation**: Self-documenting OpenAPI / Swagger UI at `/docs` and ReDoc at `/redoc` with integrated Bearer Token authentication testing.

### 2. 🔐 Identity Management & JWT Middleware

- **Identity Provider (IdP)**: Integrated with **Supabase Auth** for secure user registration (`/auth/signup`), login (`/auth/login`), and token revocation/session teardown (`/auth/logout`).
- **Security Middleware**: Reusable FastAPI `Depends(get_current_user)` middleware extracting and validating Bearer JWTs, injecting authenticated user metadata into route execution contexts.
- **Zero In-House Cryptography**: Password hashing, salt management, and token signatures are safely delegated to Supabase.

### 3. 💾 Dual Storage Engine & Persistence Layer

- **Environment-Driven Engine**: Dynamically switches between lightweight local **SQLite** (`tasks.db`) and production-grade **PostgreSQL 16**.
- **Repository Pattern**: Strict decoupling of HTTP controllers from database operations inside [`database.py`](database.py).
- **SQL Injection Prevention**: 100% parameterized SQL query execution (`?` for SQLite, `%s` for PostgreSQL).
- **Auto-Initialization & Seeding**: Idempotent table creation on startup with first-run default data seeding.

### 4. 🐳 Multi-Container Orchestration

- **Docker Compose**: Single-command startup ([`compose.yaml`](compose.yaml)) orchestrating the FastAPI application container and a PostgreSQL 16 Alpine database container.
- **Data Persistence**: Named Docker volume (`taskdata`) ensuring database state persists across container restarts and updates.

### 5. 🕷️ Polite Data Ingestion Pipeline

- **Target Site**: Sandbox Books to Scrape (`https://books.toscrape.com`).
- **Politeness Protocol**: Custom user agent (`FlyRankInternship-W5/1.0`), 10-second request timeouts, and mandatory `500ms` request throttling delays.
- **Local Disk Caching**: Raw HTML cached in `scraper/cache/` (git-ignored) enabling 100% idempotent offline reruns (`CACHE HIT`).
- **Fault Resilience**: Non-blocking try-except guards gracefully logging and skipping `404` / broken pages without halting pipeline execution.
- **Schema Validation & Reporting**: Pydantic normalization (`price_gbp`), deduplication, URL validation, and structured metric output (`run-report.json`, `books.json`, `errors.json`).

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[Client / Swagger UI / cURL] -->|HTTP Requests| FastAPI[FastAPI App - main.py]
  
    subgraph Authentication
        FastAPI -->|JWT Bearer Check| AuthMiddleware[Auth Middleware - auth.py]
        AuthMiddleware -->|Verify / Issue Tokens| Supabase[Supabase Auth IdP]
    end
  
    subgraph Data Access Layer
        FastAPI -->|Call Operations| Repo[Repository Layer - database.py]
        Repo -->|Parameterized SQL| SQLite[(SQLite - tasks.db)]
        Repo -->|Parameterized SQL| Postgres[(PostgreSQL 16 - Docker)]
    end

    subgraph Data Ingestion Pipeline
        Scraper[Scraper CLI - scraper/main.py] -->|Check Rules| Robots[robots.txt]
        Scraper -->|Polite Fetch (500ms Delay)| Target[Books to Scrape]
        Scraper -->|Save / Read HTML| Cache[(Local Disk Cache - scraper/cache/)]
        Scraper -->|BeautifulSoup Parsing| Parser[parser.py]
        Parser -->|Validate & Normalize| Validator[validator.py - Pydantic]
        Validator -->|Write Output| OutputFiles[scraper/output/ - books.json & run-report.json]
    end
```

---

## 📁 Repository Structure

```
FlyRank/
├── main.py                     # FastAPI application entry point, route definitions & OpenAPI specs
├── database.py                 # Database repository layer (SQLite & PostgreSQL parameterized queries)
├── auth.py                     # Supabase Auth client integration & FastAPI JWT dependency middleware
├── requirements.txt            # Python dependencies (FastAPI, Pydantic v2, Supabase, BeautifulSoup4, etc.)
├── Dockerfile                  # Container build instructions for FastAPI backend
├── compose.yaml                # Docker Compose multi-container stack configuration (API + Postgres)
├── .env                        # Local environment secrets & connection strings (git-ignored)
├── .env.example                # Template for environment configuration
│
├── scraper/                    # Polite Data Ingestion Pipeline (Milestone W5)
│   ├── main.py                 # Scraper runner, URL discovery, crawler loop & report generator
│   ├── fetcher.py              # Network requester with User-Agent, delay, timeout & disk caching
│   ├── parser.py               # BeautifulSoup HTML parsing functions for links and detail pages
│   ├── validator.py            # Pydantic schema model (BookRecord), price float converter & deduplication
│   ├── README.md               # Dedicated documentation for the scraper pipeline
│   ├── cache/                  # Local HTML disk snapshot cache (git-ignored)
│   └── output/                 # Ingestion pipeline outputs
│       ├── books.json          # 60 schema-validated book records
│       ├── errors.json         # Invalid or malformed record details
│       └── run-report.json     # Execution timing, cache hits & politeness metrics
│
├── ai-version/                 # AI Rematch Audit Quarantine Environment ("AI vs Me")
│   ├── main.py                 # AI-generated FastAPI app quarantine benchmark
│   └── scraper/
│       └── main.py             # AI-generated scraper quarantine benchmark
│
├── context/                    # Project Documentation & Architecture Specifications
│   ├── project-overview.md     # High-level goals, core user flow & scope definitions
│   ├── architecture.md        # Architectural layers, storage models & safety invariants
│   ├── code-standards.md       # Coding conventions, database rules & auth guidelines
│   ├── progress-tracker.md     # Milestone progress tracker and architectural decisions
│   ├── ai-workflow-rules.md   # Guidelines for AI collaboration and audit protocols
│   ├── ui-context.md          # OpenAPI / Swagger UI design and user interaction specs
│   └── zContext.md            # Directory index and context overview
│
└── Tasks/                      # Curriculum Milestone Specifications & Tasks
    ├── Tasks.md                # Task matrix, endpoints reference & W5 assignment breakdown
    ├── W2 - Build your first CRUD API.pdf
    ├── W3 - Connecting your CRUD to the database.pdf
    ├── W3 - Containerize your stack(2).pdf
    ├── W4 - Auth - Login.pdf
    └── W5 - The polite scraper.pdf
```

---

## 🔌 API Endpoint Reference

All REST API endpoints are documented interactively via OpenAPI at `http://localhost:8000/docs`.

| Category         | HTTP Method | Endpoint               | Auth Required    | Description                                                   | Status Codes                                       |
| :--------------- | :---------- | :--------------------- | :--------------- | :------------------------------------------------------------ | :------------------------------------------------- |
| **System** | `GET`     | `/`                  | None             | API root metadata and navigation endpoints                    | `200 OK`                                         |
| **System** | `GET`     | `/health`            | None             | Service liveness probe for monitoring                         | `200 OK`                                         |
| **Public** | `GET`     | `/public/info`       | None             | Public welcome information endpoint                           | `200 OK`                                         |
| **Auth**   | `POST`    | `/auth/signup`       | None             | User registration via Supabase Auth                           | `201 Created`, `400 Bad Request`               |
| **Auth**   | `POST`    | `/auth/login`        | None             | Authenticates user & returns JWT access token                 | `200 OK`, `401 Unauthorized`                   |
| **Auth**   | `POST`    | `/auth/logout`       | `Bearer Token` | Terminates user session in Supabase Auth                      | `204 No Content`, `401 Unauthorized`           |
| **Auth**   | `GET`     | `/protected/profile` | `Bearer Token` | Returns verified user profile & role metadata                 | `200 OK`, `401 Unauthorized`                   |
| **Tasks**  | `GET`     | `/tasks`             | None             | List tasks with optional `done` and `search` query filters | `200 OK`                                         |
| **Tasks**  | `GET`     | `/tasks/{id}`        | None             | Fetch a single task by numerical ID                           | `200 OK`, `404 Not Found`                      |
| **Tasks**  | `POST`    | `/tasks`             | None             | Create a new task item (`title` required)                   | `201 Created`, `400 Bad Request`               |
| **Tasks**  | `PUT`     | `/tasks/{id}`        | None             | Update task `title` and/or `done` status                   | `200 OK`, `400 Bad Request`, `404 Not Found` |
| **Tasks**  | `DELETE`  | `/tasks/{id}`        | None             | Delete task by ID                                             | `204 No Content`, `404 Not Found`              |
| **Extras** | `GET`     | `/stats`             | None             | Retrieve task count metrics (total, completed, open)          | `200 OK`                                         |
| **Extras** | `POST`    | `/reset`             | `Bearer Token` | Re-seeds database table with initial 3 sample tasks           | `200 OK`, `401 Unauthorized`                   |

---

## ⚙️ Environment Setup

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Configure your `.env` variables:

```env
# Database URL (Default PostgreSQL for Docker Compose service 'db', or postgresql://postgres:dev@localhost:5432/tasks / sqlite:///tasks.db for local execution)
DATABASE_URL=postgresql://postgres:dev@db:5432/tasks
POSTGRES_PASSWORD=dev

# Supabase Auth Credentials
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

---

## 🚀 Running the Application

### Option A: Local Development

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
2. **Run FastAPI Development Server**:

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
3. **Access Interactive Docs**:

   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Option B: Containerized Stack

Launch both the FastAPI service and PostgreSQL 16 container with a single command:

```bash
# Build and start services in background
docker compose up -d --build

# View container logs
docker compose logs -f api

# Stop container stack
docker compose down
```

---

## 🕷️ Polite Data Scraping Pipeline

The scraping module [`scraper/main.py`](scraper/main.py) automates book metadata extraction from Books to Scrape.

### Execution Command

```bash
python scraper/main.py
```

### Key Pipeline Behaviors

1. **Robots.txt Check**: Verifies crawl allowance before fetching catalogue pages.
2. **Honest User-Agent**: Sends `FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)`.
3. **Throttled Network Access**: Enforces `500ms` delay between live fetches.
4. **Local Disk Snapshot Caching**: Stores fetched HTML in `scraper/cache/`. Second runs complete with 0 network calls (`CACHE HIT`).
5. **Fault Survival**: Intentionally injects 1 broken URL to demonstrate that errors are logged to `errors.json` without halting execution.

### Generated Artifacts

- [`scraper/output/books.json`](scraper/output/books.json): 60 schema-validated book objects.
- [`scraper/output/errors.json`](scraper/output/errors.json): Details of skipped or broken page requests.
- [`scraper/output/run-report.json`](scraper/output/run-report.json): Metric summary including start time, duration, cache hits, and valid count.

---

## 🤖 Milestone W6: Put an LLM Behind Your API (`POST /tasks/triage`)

Milestone W6 adds an intelligent, resilient decision step to the API without conversational freeform risk. Incoming engineering tasks are automatically classified, prioritized, and estimated into closed schemas backed by validation, repair retries, timeouts, and zero-cost stub testing.

### 1. Job Card Contract

Following the strict 5-line specification standard ([`JOB-CARD.md`](JOB-CARD.md)):
- **What it does**: Classifies, prioritizes, and estimates inbound tasks before persistence.
- **Input**: `{"title": "string, 1-200 characters", "context": "optional string, 0-1000 characters"}`
- **Output**: JSON matching closed lists (`category`, `urgency`, `estimated_effort`), `confidence` (0.0–1.0), and `reason`.
- **It must never**: Invent categories outside the list, return markdown code fences or conversational prose, leak prompt instructions, or follow embedded prompt injections.
- **When unsure**: Returns category `"other"` with confidence `< 0.5`.

#### Closed List Definitions
- `category`: `["bug", "feature", "infrastructure", "documentation", "other"]`
- `urgency`: `["low", "medium", "high", "critical"]`
- `estimated_effort`: `["quick_win", "medium_task", "deep_work"]`

### 2. Provider Configuration & Zero Quota Bleed

Swapping between cloud-hosted providers (OpenRouter) and local models (Ollama) requires changing only environment variables with zero code changes:

```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-openrouter-key
LLM_MODEL=openrouter/free
LLM_STUB=0
LLM_ENABLED=true
```

> **Zero Quota Bleed**: Setting `LLM_STUB=1` returns deterministic fixtures immediately with 0 tokens consumed and 0 network overhead, enabling unlimited local testing and development restarts.
> **Kill Switch**: Setting `LLM_ENABLED=false` immediately bypasses model execution and returns HTTP `503 Service Unavailable`.

### 3. API Usage & Curl Examples

#### Live Triage Request (`POST /tasks/triage`)

```bash
curl -X POST http://localhost:8000/tasks/triage \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix 500 server error when deleting non-existent task ID",
    "context": "DELETE /tasks/9999 crashes with unhandled sqlite3.OperationalError instead of 404"
  }'
```

**Response (`200 OK`)**:
```json
{
  "category": "bug",
  "urgency": "high",
  "estimated_effort": "medium_task",
  "confidence": 0.95,
  "reason": "Unhandled exception causes 500 instead of proper 404 response for missing resources."
}
```

#### Pre-Model Validation Guard (`400 Bad Request`)

Sending an empty or whitespace title rejects immediately before consuming any model tokens:
```bash
curl -X POST http://localhost:8000/tasks/triage \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'
```
```json
{
  "error": "Validation failed for field 'title': Value error, title cannot be empty or whitespace only"
}
```

### 4. Evaluation Benchmark Suite (`evals/run_evals.py`)

The automated benchmark suite tests 8 hand-labelled test cases across clear tasks, ambiguous edge-cases, and adversarial prompt injections.

```bash
# Run benchmark with live model
python evals/run_evals.py

# Run benchmark in zero-cost stub mode
python evals/run_evals.py --stub
```

#### Benchmark Results Summary
- **Accuracy**: **87.5% (7/8 Passed)**
- **Prompt Injection Defense**: **100% Passed** (Adversarial attack was cleanly classified as `other` with `confidence: 0.10`).
- **Self-Healing Repair Loop**: Triggered and validated on malformed JSON outputs without failing the client request (`repaired: true`).

### 5. Telemetry & Cost Projection (10,000 req/day)

Every invocation logs a structured, single-line JSON telemetry record to `stdout`:
```json
{"telemetry": {"prompt_version": "task-triage-v1", "model": "openrouter/free", "input_tokens": 795, "output_tokens": 952, "duration_ms": 3420.5, "repaired": false}}
```

#### Cost Calculation for 10,000 Tasks/Day

| Provider / Model | Avg In / Out Tokens | Input Cost (10k reqs) | Output Cost (10k reqs) | Total Projected Cost / Day |
| :--- | :--- | :--- | :--- | :--- |
| **OpenRouter / Free Tier** | 800 in / 450 out | $0.00 | $0.00 | **$0.00 / day** |
| **Local Ollama (Llama 3.2)** | 800 in / 450 out | $0.00 | $0.00 | **$0.00 / day** (Self-hosted) |
| **OpenAI gpt-4o-mini** | 800 in / 450 out | 8.0M tokens ($1.20) | 4.5M tokens ($2.70) | **~$3.90 / day** |
| **OpenAI gpt-4o** | 800 in / 450 out | 8.0M tokens ($20.00) | 4.5M tokens ($45.00) | **~$65.00 / day** |

---

## ⚖️ AI Rematch Audit ("AI vs Me")

In Milestone W6, an unhardened reference implementation was created under [`ai-version/llm/`](ai-version/llm/) to benchmark raw AI generation against safety-hardened production engineering.

```bash
git diff --no-index src/llm/ ai-version/llm/
```

### Architectural Comparison Findings

| Engineering Domain | Production Hardened (`src/llm/`) | Unhardened AI Quarantine (`ai-version/llm/`) |
| :--- | :--- | :--- |
| **Timeout Configuration** | Explicit `timeout=30.0` passed to SDK client; mapped to HTTP 504. | No timeout configured (defaults to 10 minutes or infinite hang under network drop). |
| **Prompt Injection Defense** | System prompt separated from user input; input JSON-encoded inside `user` role. | Dangerous f-string interpolation (`f"Task title: {request.title}"`) into system prompt. |
| **Schema Validation & Enums** | Strict Pydantic v2 closed enums (`TaskCategory`, `TaskUrgency`, `TaskEffort`). | Loose raw `str` fields, permitting arbitrary hallucinatory categories. |
| **Parsing & Repair Retry** | Markdown fence stripping regex + single automated repair retry with validation error feedback. | Naive `json.loads()`; crashes immediately on markdown code fences or invalid keys. |
| **Quarantine & Error Isolation** | Persistent failures written to `logs/quarantine.jsonl` with structured failure metadata. | No failure record or quarantine; fails unhandled with HTTP 500. |
| **Retry & Rate-Limit Policy** | Exponential backoff with jitter on 429/5xx; respects `Retry-After`; fails fast on 401/403. | Unchecked retries or crashes on transient rate limits. |
| **Observability & Kill Switch** | Single-line JSON telemetry per request + `LLM_ENABLED=false` kill switch. | No execution metrics, no token tracking, and no kill switch. |

---

## ⚡ Milestone W7: Your First Background Job & Cron Schedules

Offload long-running operations (>1s) from standard HTTP request-response cycles into durable background jobs and scheduled clock-triggered tasks using the **Inngest Python SDK** and **Inngest Dev Server**.

### 1. Dual Startup Commands

Running the full background jobs stack requires two terminal processes:

```bash
# Terminal 1: Start FastAPI Application Server (Port 8000)
uvicorn main:app --reload --port 8000

# Terminal 2: Start Inngest Local Dev Server & Visual Dashboard (Port 8288)
npx inngest-cli@latest dev -u http://localhost:8000/api/inngest
```

- **API Documentation**: `http://localhost:8000/docs`
- **Inngest Dashboard**: `http://localhost:8288`

---

### 2. Endpoints & Background Functions Reference Table

| Execution Category | Route / Trigger | Handler / ID | Status / Behavior | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Request / Response** | `GET /health` | `get_health()` | `200 OK` | Instant health probe returning `{"status": "ok"}`. |
| **Fast Door (Accept)** | `POST /reports` | `create_report_endpoint()` | `202 Accepted` (<100ms) | Validates input (`400` on empty/whitespace), saves state (`pending`), dispatches event `report/requested`. |
| **Status Polling** | `GET /reports/{id}` | `get_report_endpoint()` | `200 OK` / `404 Not Found` | Status endpoint returning `pending` first, then `done` with report result payload (eventual consistency). |
| **Control Panel** | `GET /reports` | `list_reports()` | `200 OK` | Returns full list of tracked reports and their current statuses. |
| **Inngest Serve Mount**| `/api/inngest` | `inngest.fast_api.serve` | `200 OK` (GET/POST/PUT) | Protocol handshake and execution endpoint connecting FastAPI to Inngest Dev Server. |
| **Durable Function** | Event `test/hello` | `say-hello` | Step Sleep (5s) | Durable test workflow sleeping 5 seconds and returning greeting. |
| **Durable Workflow** | Event `report/requested` | `make-report` | Step Sleep (8s) + Step Run | Simulates slow compute (8s), injects error on topic `"fail"`, updates status to `done`, retries with backoff up to 2 times. |
| **Scheduled Cron** | Cron `* * * * *` | `heartbeat` | Schedule-Driven | Runs every minute on the clock alone without HTTP trigger; logs pending, done, failed counts to stdout. |

---

### 3. Pasted Terminal Proof: Fast 202 Door & Status Polling

Below is the verified terminal execution demonstrating immediate `<100ms` acceptance followed by status polling:

```bash
# 1. Trigger asynchronous report (Accept fast door)
$ time curl -i -X POST http://localhost:8000/reports \
    -H "Content-Type: application/json" \
    -d '{"topic": "cats"}'

HTTP/1.1 202 Accepted
content-length: 44
content-type: application/json

{"id":"rep_d7880e89","status":"pending"}
real    0m0.048s
user    0m0.012s
sys     0m0.016s

# 2. Poll immediately (Expect pending)
$ curl -i http://localhost:8000/reports/rep_d7880e89

HTTP/1.1 200 OK
content-type: application/json

{"id":"rep_d7880e89","topic":"cats","status":"pending","result":null,"created_at":"2026-09-06T00:20:50.123456+00:00","attempts":0,"error":null}

# 3. Poll after background sleep & build steps complete (~10 seconds later)
$ curl -i http://localhost:8000/reports/rep_d7880e89

HTTP/1.1 200 OK
content-type: application/json

{"id":"rep_d7880e89","topic":"cats","status":"done","result":"Report on 'cats' generated successfully.","created_at":"2026-09-06T00:20:50.123456+00:00","attempts":1,"error":null}
```

---

### 4. Core Conceptual Explanations

#### Stage 3: Retrying vs. Input Validation Gatekeeper
> **"A wrong input must be rejected at the door with `400 Bad Request` without creating background work; only a wrong moment (a transient network hiccup or temporary service outage) deserves an automated retry with exponential backoff."**

- **Reject at the door (`400 Bad Request`)**: Missing or empty parameters (e.g. `POST /reports` with `{}`) will never succeed no matter how many times a worker retries. Retrying bad data wastes worker CPU, clogs queues, and corrupts databases.
- **Retry with backoff (`retries=2`)**: A transient downstream failure (e.g. database connection pool saturation, external AI API hiccup, network timeout) is temporary. Backoff introduces progressive delay (e.g. 5s, 30s, 2m) to allow dependent services time to recover.

#### Stage 4: Cron Expressions Decoded
- **Run every day at 08:00 UTC**: `0 8 * * *`  
  *(Minute 0, Hour 8, Every day-of-month, Every month, Every day-of-week)*
- **Run every Sunday at 22:00 UTC**: `0 22 * * 0`  
  *(Minute 0, Hour 22, Every day-of-month, Every month, Day 0 = Sunday)*

---

### 5. 🤖 AI Rematch Audit: Background Jobs ("AI vs Me")

In Stage 6, an independent AI assistant was prompted from memory in quarantine (`ai-version/jobs/`) to build the background jobs system.

#### The AI Prompt Used
```text
Build a FastAPI background job system using Inngest with an in-memory dictionary for reports.
Include:
1. POST /reports: Fast door returning HTTP 202 in <1s with unique report id and pending status, dispatching report/requested event.
2. Strict validation: if topic is missing or whitespace, return 400 Bad Request and send zero events.
3. Inngest function make-report: 8-second sleep step, build step updating report to done. If topic is 'fail', raise an error with retries=2.
4. Status endpoint GET /reports/:id returning pending first, then done with result. Return 404 for unknown id.
5. Inngest cron function heartbeat running on '* * * * *' logging counts of pending, done, and failed reports.
```

#### Side-by-Side Architectural Audit (`git diff --no-index src/jobs ai-version/jobs`)

| Feature & Failure Mode | Hand-Crafted Production (`src/jobs/` + `main.py`) | Quarantined AI (`ai-version/jobs/`) |
| :--- | :--- | :--- |
| **Input Boundary Validation** | Strict check for missing, empty string, and whitespace-only (`.strip()`), returning clean HTTP `400 Bad Request`. | Relies on basic Pydantic model (`topic: str`). Accepts whitespace strings like `"   "` without validation; returns `422` instead of `400` on missing keys. |
| **Error Contract Shape** | Standardized JSON error contract `{"error": "Descriptive message"}` across all endpoints (400, 404). | Uses FastAPI default `HTTPException(404, detail="Not found")`, returning mismatched `{"detail": "..."}` shape. |
| **Retry & Failure Handling** | Configured `retries=2` with `on_failure` handler capturing final failure state in in-memory registry (`status="failed"`). | Omitted explicit retry count or on_failure listener; failed runs remain permanently in `"pending"` status in database. |
| **Step Durability & Types** | Typed `timedelta(seconds=8)` with separate callback steps and request timeout protection. | Used raw integer milliseconds `8000` with inline nested closures; prone to serialization issues on restarts. |
| **Heartbeat Cron Reporting** | Aggregates and logs granular metrics: `pending`, `done`, and `failed` count breakdown. | Only printed generic count `len(ai_reports)` without status classification. |

#### Rematch Evolution Note
Upon updating the prompt to explicitly enforce `400 Bad Request` on whitespace input and explicit `retries=2` with on-failure recording, the AI implemented custom string validators, proving that AI code quality is directly bounded by specification precision.

---

## 📊 Milestone W7b: PDF Report Generator (Assignment A8)

Milestone W7b implements the classic enterprise **Store and Link** document reporting pipeline:
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   1. QUERY   │ ──> │  2. RENDER   │ ──> │   3. STORE   │ ──> │   4. SERVE   │
│ SQL Aggregates│     │HTML+Playwright│    │Save to Disk  │     │Serve by Link │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

Rather than passing heavy binary blobs in JSON requests, the server aggregates data via pure SQL, renders a styled document through headless Chromium (`Playwright`), saves the produced artifact to disk (`reports/<id>.pdf`), registers metadata in SQLite (`report.db`), and hands out an address link (`/reports/<id>/file`).

### 1. Dataset Selection: Option B (The Bookstore)
This implementation reuses the **60 validated book records** collected during **Milestone W5** from [books.toscrape.com](https://books.toscrape.com) stored in [`scraper/output/books.json`](scraper/output/books.json).
- **Idempotent Seeding**: The seeding script (`src/reports/seed.py`) executes `DELETE FROM books` before batch-inserting parameterized tuples. Running the seed command multiple times always guarantees exactly 60 records remain.
- **Rating Normalization**: Text ratings (`"One"`, `"Two"`, `"Three"`, `"Four"`, `"Five"`) are mapped to clean 1–5 integers.

### 2. How to Run

```bash
# Step 1: Install Playwright & Headless Chromium
pip install playwright
python -m playwright install chromium

# Step 2: Seed the database idempotently
python -m src.reports.seed
# Output: Seeding complete. Total books in report.db: 60

# Step 3: Launch FastAPI server
uvicorn main:app --reload --port 8000
```

### 3. Pure SQL Aggregation Queries
All four business metrics are calculated directly inside SQLite queries in [`src/reports/queries.py`](src/reports/queries.py) rather than in application memory:

```sql
-- 1. Total Catalog Count
SELECT COUNT(*) FROM books;

-- 2. Average Unit Price & Total Inventory Valuation
SELECT ROUND(AVG(price), 2), ROUND(SUM(price), 2), ROUND(MIN(price), 2), ROUND(MAX(price), 2) FROM books;

-- 3. Top 5 Most Expensive Titles
SELECT title, price, rating, url FROM books ORDER BY price DESC LIMIT 5;

-- 4. Rating Distribution Breakdown
SELECT rating, COUNT(*) as count FROM books GROUP BY rating ORDER BY rating DESC;

-- 5. Full Inventory Catalog (Multi-Page Print Document)
SELECT id, title, price, rating, url FROM books ORDER BY id ASC;
```

### 4. Print CSS Defenses Against Classic Traps
To ensure production-grade document quality across multiple pages, [`src/reports/template.py`](src/reports/template.py) implements the essential print CSS rules:
- **No Sliced Table Rows**: `tr { break-inside: avoid; page-break-inside: avoid; }` forces complete table rows onto subsequent pages rather than slicing them horizontally across page breaks.
- **Repeating Column Headers**: `thead { display: table-header-group; }` instructs Chromium to repeat the column header row at the top of every generated page.
- **Standard A4 Geometry**: `@page { size: A4; margin: 16mm 14mm 16mm 14mm; }` with exact background printing enabled (`-webkit-print-color-adjust: exact !important`).

### 5. Terminal Execution Proof (POST → Download → Idempotency)

```bash
# 1. Generate Report (Store and Link, creates reports/1.pdf)
curl -i -X POST http://localhost:8000/reports
# HTTP/1.1 201 Created
# Content-Type: application/json
# {"id": 1, "file": "/reports/1/file"}

# 2. Download the binary PDF file directly by link
curl -o my-report.pdf http://localhost:8000/reports/1/file
# Result: Downloads valid 3-page A4 PDF (size ~133 KB, magic bytes %PDF-)

# 3. Double-Click Idempotency: Immediate second POST returns existing report without re-rendering
curl -i -X POST http://localhost:8000/reports
# HTTP/1.1 200 OK
# Content-Type: application/json
# {"id": 1, "file": "/reports/1/file"}
# reports/ directory gains zero duplicate files

# 4. Force Regeneration: Bypass daily idempotency cache
curl -i -X POST -H "Content-Type: application/json" -d '{"force": true}' http://localhost:8000/reports
# HTTP/1.1 201 Created
# Content-Type: application/json
# {"id": 2, "file": "/reports/2/file"}
```

### 6. Architectural Reflection Questions

> **Stage 4 Reflection: At what point would you move this work out of the request?**  
> We would move this work out of the request into an asynchronous background job when generation latency exceeds acceptable interactive thresholds (>2–3 seconds), when reports process thousands of rows requiring significant compute or memory, or when high user concurrency threatens to exhaust web worker pools by blocking server threads during headless browser printing.

> **Stage 5 Reflection: What your check protects against, and one real-world example where a missing check like this costs money.**  
> This idempotency check protects server resources from redundant headless browser rendering, disk exhaustion, and CPU spikes triggered by impatient users double-clicking the "Generate Report" button. A critical real-world example where a missing check costs money is in automated invoice or statement generation paired with an email dispatch trigger (the workshop's "never email a customer twice" rule) or transactional billing where double-clicking a "Generate & Purchase Report" button could double-bill a customer's credit card.

---

### 7. 🥊 Bonus Stage: The AI Rematch (PDF Report Generator)

We prompted an AI assistant to implement the entire PDF report pipeline in quarantine ([`ai-version/reports/main.py`](ai-version/reports/main.py)) from the specification prompt below and conducted a comparative audit.

#### The AI Prompt Used
```text
Build a PDF report generation feature in Python using FastAPI, SQLite, and Playwright.
The dataset is in report.db (table books: id, title, price, rating, url).
1. Provide an idempotent seed script that loads books from a JSON file into report.db.
2. Write SQL aggregations calculating: total books, average price, top 5 most expensive books,
   and rating breakdown.
3. Render an HTML page displaying these metrics and a full table of all books.
   Print to A4 PDF using Playwright headless Chromium.
4. Implement endpoints:
   - POST /reports: generates PDF, saves to reports/<id>.pdf, records in reports table,
     returns HTTP 201 with {"id": ..., "file": "/reports/<id>/file"}.
   - GET /reports/{id}: returns report metadata.
   - GET /reports/{id}/file: serves binary PDF via FileResponse.
5. Idempotency: If a report was already generated today, return the existing report with 200 OK.
   Accept {"force": true} to force fresh generation.
```

#### Side-by-Side Audit (`git diff --no-index src/reports ai-version/reports`)

| Feature & Failure Mode | Hand-Crafted Production (`src/reports/` + `main.py`) | Quarantined AI (`ai-version/reports/main.py`) |
| :--- | :--- | :--- |
| **Page-Break Traps** | Defensive print CSS with `tr { break-inside: avoid; }` and repeating table headers (`thead { display: table-header-group; }`). Multi-page catalog renders cleanly without sliced rows. | Omitted page-break CSS entirely. Relied on default browser flow, causing table rows to slice horizontally across page breaks and subsequent pages to lack headers. |
| **Visual Styling & KPI Cards** | Rich executive dashboard layout with metric cards, rating distribution bar visuals, typography hierarchy, and star badges. | Bare-bones unstyled HTML with default table borders and raw text dumps. |
| **Database Atomicity & Paths** | Multi-table schema management with explicit foreign keys, parameterized queries, and safe path resolution using `Path.resolve()`. | Minimal single-file script using hardcoded relative paths; missing file existence checks before returning existing records. |
| **API Error Contract Shape** | Consistent JSON error envelopes `{"error": "..."}` matching project-wide REST conventions. | Defaulted to FastAPI `HTTPException(404, detail="...")` yielding mismatched `{"detail": "..."}` responses. |

#### Concrete Takeaways
1. **What the AI did better**: The AI wrote concise, readable async Playwright context manager code with very little boilerplate.
2. **What it got wrong**: The AI completely missed the print CSS page-break trap — it did not include `break-inside: avoid` on `<tr>` or repeat headers via `<thead>`, which is the #1 failure mode in real-world document printing.
3. **What the prompt forgot to specify**: The prompt did not specify visual design aesthetics or error response envelope shapes, leading the AI to pick plain table formatting and default exception handlers.

---

## 🔍 Verification & Testing

### 1. API Health Check

```bash
curl -s http://localhost:8000/health
# Output: {"status":"ok"}
```

### 2. Task CRUD Flow

```bash
# Create Task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete FlyRank Documentation"}'

# List Tasks
curl -s http://localhost:8000/tasks
```

### 3. Run Ingestion Pipeline

```bash
python scraper/main.py
```

---

## 📄 License

This repository is maintained as part of the **FlyRank AI Backend Internship Track**. All rights reserved.
