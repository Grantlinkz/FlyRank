# 📝 FlyRank Backend Platform — Master Task Tracker & Specifications

This document tracks all tasks, curriculum milestones, specifications, and endpoint references for the **FlyRank Internship Backend Track**.

---

## 📊 Milestone Summary & Progress Overview

| Milestone | Target / Topic | Technology Stack | Status |
| :--- | :--- | :--- | :--- |
| **W1 & W2** | RESTful CRUD API Foundation | Python, FastAPI, Pydantic, Swagger UI | ✅ Completed |
| **W3 (DB)** | Database Persistence Layer | SQLite (`sqlite3`), PostgreSQL (`psycopg3`), SQL Parameterization | ✅ Completed |
| **W3 (Docker)**| Multi-Container Orchestration | Docker, Docker Compose (`compose.yaml`), Volume Mapping | ✅ Completed |
| **W4** | Identity Provider & JWT Security | Supabase Auth, Bearer Token Middleware, FastAPI Security | ✅ Completed |
| **W5** | Polite Data Scraping Pipeline | Requests, BeautifulSoup4, Local Disk Cache, Pydantic Schema | ✅ Completed |
| **W6** | Put an LLM Behind Your API (`/tasks/triage`) | OpenAI SDK, OpenRouter/Ollama, Pydantic v2, Prompt Engineering | ✅ Completed |
| **W7 (A7)** | Your First Background Job | Inngest, Event-driven steps, Durable workflows, Cron scheduler | ⏳ Up Next |
| **W7b (A8)** | PDF Report Generator | SQLite Aggregation, HTML Templates, Playwright Headless Chromium | ⏳ Up Next |

---

## 📋 Comprehensive Task Matrix

### Milestone W1 & W2: Build your first CRUD API

- [x] **Task 1.1**: Initialize FastAPI application framework with standard OpenAPI metadata (`title`, `version`, `description`) in [`main.py`](main.py).
- [x] **Task 1.2**: Implement system liveness check (`GET /health`) and root endpoint (`GET /`).
- [x] **Task 1.3**: Implement complete Task CRUD lifecycle:
  - [x] `GET /tasks` - List all task items with optional `done` status filtering and `search` query parameters.
  - [x] `GET /tasks/{id}` - Fetch single task by unique integer ID (`404 Not Found` if missing).
  - [x] `POST /tasks` - Create task with input validation (`400 Bad Request` if `title` is missing/empty).
  - [x] `PUT /tasks/{id}` - Update task `title` and/or `done` status with atomic partial validation.
  - [x] `DELETE /tasks/{id}` - Delete task by ID returning `204 No Content` (`404 Not Found` if missing).
- [x] **Task 1.4**: Implement extra utility endpoints:
  - [x] `GET /stats` - Return aggregate metrics (`total`, `done`, `open`).
  - [x] `POST /reset` - Re-seed initial sample tasks into database.
- [x] **Task 1.5**: Verify interactive Swagger UI documentation rendered at `http://localhost:8000/docs`.

---

### Milestone W3: Connecting your CRUD to the Database

- [x] **Task 3.1**: Create dedicated database repository pattern in [`database.py`](database.py).
- [x] **Task 3.2**: Support dual database engines via `DATABASE_URL` environment variable (PostgreSQL primary, SQLite `tasks.db` fallback).
- [x] **Task 3.3**: Enforce 100% SQL parameterization (`?` placeholders for SQLite, `%s` for PostgreSQL) to prevent SQL injection vulnerabilities.
- [x] **Task 3.4**: Implement database lifecycle initialization (`init_db`) with `CREATE TABLE IF NOT EXISTS` and first-run idempotent seed data loading.
- [x] **Task 3.5**: Refactor all FastAPI route handlers to interact exclusively with repository helper functions (`get_all_tasks`, `create_task`, `update_task`, `delete_task`, `get_task_stats`, `reset_db`).
- [x] **Task 3.6**: Implement atomic connection management ensuring database cursors close properly after query execution.

---

### Milestone W3: Containerize your Stack

- [x] **Task 3.7**: Create production [`Dockerfile`](Dockerfile) using Python 3.11-slim base image and Uvicorn ASGI server.
- [x] **Task 3.8**: Create [`compose.yaml`](compose.yaml) defining multi-container orchestration:
  - [x] `api` service: FastAPI application on port 8000.
  - [x] `db` service: PostgreSQL 16 Alpine container on port 5432.
- [x] **Task 3.9**: Configure Docker named volume `taskdata` mapped to `/var/lib/postgresql/data` ensuring data persistence across `docker compose down && docker compose up`.
- [x] **Task 3.10**: Set up environment configuration isolation with `.env` (git-ignored) and committed `.env.example`.

---

### Milestone W4: Auth - Login & Protected Endpoints

- [x] **Task 4.1**: Integrate Supabase Auth client SDK in [`auth.py`](auth.py).
- [x] **Task 4.2**: Implement user registration endpoint `POST /auth/signup` accepting email and password credentials.
- [x] **Task 4.3**: Implement user login endpoint `POST /auth/login` returning Supabase JWT access token and refresh token.
- [x] **Task 4.4**: Implement reusable FastAPI security dependency `get_current_user` enforcing Bearer token presence and verifying JWT signatures against Supabase Auth.
- [x] **Task 4.5**: Protect user profile endpoint `GET /protected/profile` requiring valid Bearer JWT.
- [x] **Task 4.6**: Implement session teardown `POST /auth/logout` revoking user session in Supabase Auth.
- [x] **Task 4.7**: Protect system administration endpoint `POST /reset` with JWT authentication dependency.
- [x] **Task 4.8**: Configure OpenAPI `HTTPBearer` security scheme in Swagger UI (`/docs`) allowing interactive Bearer token testing via the authorization padlock button.

---

### Milestone W5: The Polite Scraper (Data Ingestion Pipeline)

- [x] **Task 5.1**: Target classification & compliance audit:
  - Target: Books to Scrape (`https://books.toscrape.com`).
  - `robots.txt` verification: Fetched `https://books.toscrape.com/robots.txt` (`404 Not Found`).
- [x] **Task 5.2**: Build polite network request layer ([`scraper/fetcher.py`](scraper/fetcher.py)):
  - Honest User-Agent: `FlyRankInternship-W5/1.0 (+https://github.com/Grantlinkz/FlyRank)`.
  - Timeout: 10-second timeout per network request.
  - Throttling: Mandatory `500ms` delay between live network calls.
  - Local Disk Caching: Cached raw HTML snapshots in `scraper/cache/` enabling 100% idempotent offline reruns (`CACHE HIT`).
- [x] **Task 5.3**: Build DOM parser ([`scraper/parser.py`](scraper/parser.py)):
  - URL Discovery: Extracted book detail URLs across catalogue pages using `urllib.parse.urljoin`.
  - Next Link Crawling: Automated pagination discovery across catalogue pages (`page-1.html` through `page-3.html`).
  - Detail Extraction: Extracted 8 raw fields (`title`, `product_url`, `price_text`, `availability_text`, `rating_text`, `description`, `source_page`, `fetched_at`).
- [x] **Task 5.4**: Build runtime validator ([`scraper/validator.py`](scraper/validator.py)):
  - Pydantic Model (`BookRecord`): Validated type safety and URL schemas.
  - Price Normalization: Extracted float value (`price_gbp`) from raw string (e.g. `'£51.77'` -> `51.77`).
  - Canonical Deduplication: Ensured no duplicate `product_url` records in final output.
- [x] **Task 5.5**: Build main pipeline orchestrator ([`scraper/main.py`](scraper/main.py)):
  - Failure Resilience: Skipped 404/500 broken pages cleanly without crashing.
  - Test Injection: Injected 1 fake broken URL to verify error isolation.
  - Output Artifact Generation:
    - [`scraper/output/books.json`](scraper/output/books.json): 60 schema-validated book records.
    - [`scraper/output/errors.json`](scraper/output/errors.json): Array of logged page errors.
    - [`scraper/output/run-report.json`](scraper/output/run-report.json): Metric execution summary.
- [x] **Task 5.6**: Execute AI Rematch Audit ("AI vs Me"):
  - Prompted AI assistant in quarantine environment ([`ai-version/scraper/main.py`](ai-version/scraper/main.py)).
  - Audited AI output vs production code across URL resolution, disk caching, failure resilience, and error handling.

---

### Milestone W7: Your First Background Job (Assignment A7)

- [ ] **Task 7.1**: Setup baseline health endpoint (`GET /health`).
- [ ] **Task 7.2**: Connect Inngest client (`report-api`), define initial `say-hello` function with 5-second sleep step, mount FastAPI serve endpoint at `/api/inngest`, and connect Inngest Dev Server (`localhost:8288`).
- [ ] **Task 7.3**: Implement fast-door endpoint `POST /reports` returning HTTP `202 Accepted` + `{ "id": ..., "status": "pending" }` in <1s and dispatching `report/requested` event.
- [ ] **Task 7.4**: Implement durable background function `make-report` with `step.sleep("8s")` and `step.run("build-report")` updating in-memory status to `done`.
- [ ] **Task 7.5**: Implement polling status endpoint `GET /reports/{id}` returning lifecycle status (`pending`, `done`, `failed`) and result.
- [ ] **Task 7.6**: Implement error handling and retry mechanism (`retries=2`) simulating failure on topic `"fail"` with exponential backoff.
- [ ] **Task 7.7**: Add boundary input validation on `POST /reports` returning `400 Bad Request` on missing topic without dispatching background events.
- [ ] **Task 7.8**: Implement scheduled cron function `heartbeat` triggered every minute (`TriggerCron(cron="* * * * *")`) logging job metrics.
- [ ] **Task 7.9**: Execute AI Rematch Audit in `ai-version/jobs/` comparing prompt precision, retry policy, and durable execution.

---

### Milestone W7b: PDF Report Generator (Assignment A8)

- [ ] **Task 8.1**: Setup Playwright headless Chromium environment (`playwright install chromium`).
- [ ] **Task 8.2**: Create reporting SQLite database `report.db` and write idempotent seed script (reusing `books.json` or orders dataset).
- [ ] **Task 8.3**: Write SQL aggregation query module extracting 4 key business metrics (`COUNT`, `SUM`, `AVG`, `GROUP BY`).
- [ ] **Task 8.4**: Build HTML template with print CSS rules (`tr { break-inside: avoid; }`, repeating `<thead>`) and render $\ge 2$ page PDF via Playwright.
- [ ] **Task 8.5**: Implement "store and link" API endpoints:
  - `POST /reports` - Executes pipeline, saves `reports/<id>.pdf` and DB record, returns `201 Created` + file link.
  - `GET /reports/{id}` - Returns report metadata and download link.
  - `GET /reports/{id}/file` - Streams binary PDF file via `FileResponse`.
- [ ] **Task 8.6**: Implement double-click idempotency: same-day duplicate requests return `200 OK` with existing report ID (no duplicate file created); support `{ "force": true }` bypass.
- [ ] **Task 8.7**: Execute AI Rematch Audit in `ai-version/reports/` auditing page-break CSS, file-serving patterns, and SQL aggregations.

---

## 🔍 Detailed Endpoint Reference Table

| Category | Method | Endpoint | Auth Required | Request Payload | Success Response | Error Responses |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **System** | `GET` | `/` | None | None | `200 OK` (API Metadata) | N/A |
| **System** | `GET` | `/health` | None | None | `200 OK` `{"status":"ok"}` | N/A |
| **Public** | `GET` | `/public/info` | None | None | `200 OK` (Lobby message) | N/A |
| **Auth** | `POST` | `/auth/signup` | None | `{"email": "...", "password": "..."}` | `201 Created` (User object) | `400 Bad Request` |
| **Auth** | `POST` | `/auth/login` | None | `{"email": "...", "password": "..."}` | `200 OK` (Access JWT token) | `401 Unauthorized` |
| **Auth** | `POST` | `/auth/logout` | Bearer Token | Header: `Authorization: Bearer <jwt>` | `204 No Content` | `401 Unauthorized` |
| **Protected**| `GET` | `/protected/profile`| Bearer Token | Header: `Authorization: Bearer <jwt>` | `200 OK` (User metadata) | `401 Unauthorized` |
| **Tasks** | `GET` | `/tasks` | None | Query params: `done`, `search` | `200 OK` (Array of Tasks) | N/A |
| **Tasks** | `GET` | `/tasks/{id}` | None | Path param: `id` (int) | `200 OK` (Task object) | `404 Not Found` |
| **Tasks** | `POST` | `/tasks` | None | `{"title": "..."}` | `201 Created` (Task object) | `400 Bad Request` |
| **Tasks** | `PUT` | `/tasks/{id}` | None | `{"title": "...", "done": true}` | `200 OK` (Task object) | `400 Bad Request`, `404 Not Found` |
| **Tasks** | `DELETE` | `/tasks/{id}` | None | Path param: `id` (int) | `204 No Content` | `404 Not Found` |
| **Tasks / LLM** | `POST` | `/tasks/triage` | None | `{"title": "...", "context": "..."}` | `200 OK` (`TaskTriageResponse`) | `400 Bad Request`, `422 Unprocessable`, `503 Unavailable`, `504 Timeout` |
| **Jobs (W7)**| `POST` | `/reports` | None | `{"topic": "cats"}` | `202 Accepted` (`{"id":..., "status":"pending"}`) | `400 Bad Request` |
| **Jobs (W7)**| `GET` | `/reports/{id}` | None | Path param: `id` | `200 OK` (`{"status":"done", ...}`) | `404 Not Found` |
| **Jobs (W7)**| `POST/GET`| `/api/inngest` | None | Internal Inngest protocol | Inngest function handlers | N/A |
| **Reports (W7b)**| `POST`| `/reports` | None | Optional: `{"force": true}` | `201 Created` / `200 OK` (`{"id":..., "file":"..."}`) | `400 Bad Request` |
| **Reports (W7b)**| `GET` | `/reports/{id}/file`| None | Path param: `id` | `200 OK` (`application/pdf` stream) | `404 Not Found` |
| **Extras** | `GET` | `/stats` | None | None | `200 OK` (Counts object) | N/A |
| **Extras** | `POST` | `/reset` | Bearer Token | Header: `Authorization: Bearer <jwt>` | `200 OK` (Reset Tasks array) | `401 Unauthorized` |

---

## 🧪 Quick Verification Commands

```bash
# 1. Verify project compilation
python -m py_compile main.py database.py auth.py scraper/main.py

# 2. Run scraper pipeline
python scraper/main.py

# 3. Start local API server
uvicorn main:app --reload --port 8000

# 4. Run Docker stack
docker compose up -d --build
```
